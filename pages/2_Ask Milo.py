import streamlit as st
import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Page title
st.title("🧠 Injury Assistant (Ask Milo)")


# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "diagnostic_tests" not in st.session_state:
    st.session_state.diagnostic_tests = ""
if "awaiting_test_input" not in st.session_state:
    st.session_state.awaiting_test_input = False
if "initial_query" not in st.session_state:
    st.session_state.initial_query = ""

# Load vectorstore and embeddings
embeddings = HuggingFaceEmbeddings(model_name="./models/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("pages/data/milo_index", embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="similarity", k=5)

# Set up LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

# Step 1: Describe symptoms and get diagnostic tests
if not st.session_state.awaiting_test_input:
    st.subheader("Step 1: Describe your issue")
    query = st.text_area("❓ What's bothering you?", placeholder="e.g., My lower back hurts when I deadlift")

    if st.button("🔍 Get Diagnostic Tests") and query.strip() != "":
        with st.spinner("Analyzing symptoms and generating diagnostic tests..."):  #loading
            prompt_1 = PromptTemplate(
                input_variables=["question", "context"],
                template="""
                        You are Milo, a top injury rehab expert. A patient says:
                        "{question}"

                        Using the context below, list 2–3 diagnostic tests the user should try to identify the root issue. Only include the names and brief descriptions of the tests.
                        talk to patient in first person and explain them easily
                        Context:
                        {context}
                        """
            )
            qa_chain_1 = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                combine_docs_chain_kwargs={"prompt": prompt_1}
            )
            response_1 = qa_chain_1.run({
                "question": query,
                "chat_history": []
            })

            st.session_state.diagnostic_tests = response_1
            st.session_state.initial_query = query
            st.session_state.awaiting_test_input = True

# Step 2: Show tests and ask user to confirm
if st.session_state.awaiting_test_input:
    st.subheader("Step 2: Confirm test results")
    st.markdown("**Milo recommends the following diagnostic tests:**")
    st.markdown(st.session_state.diagnostic_tests)

    user_followup = st.text_area("✏️ Describe what happened when you performed the tests.",
                                 placeholder="e.g., Neer's test was painful but Hawkins-Kennedy was okay")

    if st.button("✅ Get Fixes") and user_followup.strip() != "":
        with st.spinner("Analyzing test outcomes and generating corrective plan..."):
            combined_input = f"Original issue: {st.session_state.initial_query}\n\nTest results: {user_followup}"
            prompt_2 = PromptTemplate(
                input_variables=["question", "context"],
                template="""
                        You are Milo, a top injury rehab expert. A user said:

                        {question}

                        Based on this and the reference material below, provide specific corrective exercises, mobility drills, and activity modifications.
                         keep it crisp and easy

                        Context:
                        {context}
                        """
            )
            qa_chain_2 = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                combine_docs_chain_kwargs={"prompt": prompt_2}
            )
            response_2 = qa_chain_2.run({
                "question": combined_input,
                "chat_history": st.session_state.chat_history
            })

            st.subheader("🛠️ Corrective Plan")
            st.markdown(response_2)

            # Save full conversation
            st.session_state.chat_history.append((combined_input, response_2))

            # Save latest injury
            latest_injury = {
                "query": st.session_state.initial_query,
                "tests": st.session_state.diagnostic_tests,
                "test_results": user_followup,
                "response": response_2
            }
            with open("pages/data/latest_injury.json", "w") as f:
                json.dump(latest_injury, f)

            # Reset for next session
            st.session_state.awaiting_test_input = False
