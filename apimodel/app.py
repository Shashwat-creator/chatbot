from sentence_transformers import SentenceTransformer
import faiss
import os
import requests
GROQ_API_KEY="dddd"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

index = faiss.read_index("sop_index.faiss")
with open("sop_texts.txt", "r", encoding="utf-8") as f:
    raw_text = f.read().split("<|END|>\n")

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Embed query only
query = "who is mira lantern story"
query_vec = embedder.encode([query], convert_to_numpy=True)

# Search top matches
D, I = index.search(query_vec, k=2)
context = "\n".join([raw_text[i] for i in I[0]])

# Call LLM (Gemma-2B or phi3:mini etc.)
prompt = f"""You are a story explainer.
Find the answer from the below story and explain simply in hindi.

Story Context:
{context}

Question:
{query}
"""
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama3-8b-8192",  # fast Groq model
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 300,
    "temperature": 0.3
}

response = requests.post(GROQ_URL, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code, response.text)
