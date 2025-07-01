import shutil
import os

# HuggingFace Transformers cache
hf_cache = os.path.expanduser("~/.cache/huggingface")
if os.path.exists(hf_cache):
    print(f"Deleting HuggingFace cache at: {hf_cache}")
    shutil.rmtree(hf_cache)
else:
    print(f"No HuggingFace cache found at: {hf_cache}")

# SentenceTransformers cache (sometimes uses this path)
st_cache = os.path.expanduser("~/.cache/torch/sentence_transformers")
if os.path.exists(st_cache):
    print(f"Deleting SentenceTransformers cache at: {st_cache}")
    shutil.rmtree(st_cache)
else:
    print(f"No SentenceTransformers cache found at: {st_cache}")

print("Cache clearing complete.")