from sentence_transformers import SentenceTransformer
import faiss
import os
import ollama


embedder = SentenceTransformer('all-MiniLM-L6-v2')  # free local embedding model
texts = []
for fname in os.listdir("sops"):
    with open(os.path.join("sops", fname), 'r', encoding='utf-8') as f:
        texts.append(f.read())

# Create embeddings
embeddings = embedder.encode(texts, convert_to_numpy=True)

# Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save for later
faiss.write_index(index, "sop_index.faiss")
with open("sop_texts.txt", "w", encoding="utf-8") as f:
    for t in texts:
        f.write(t.replace("\n", " ") + "\n<|END|>\n")





index = faiss.read_index("sop_index.faiss")
with open("sop_texts.txt", "r", encoding="utf-8") as f:
    raw_text = f.read().split("<|END|>\n")

# Embed query
query = "who is mira lantern story "
query_vec = embedder.encode([query], convert_to_numpy=True)
D, I = index.search(query_vec, k=2)  # top 2 results
context = "\n".join([raw_text[i] for i in I[0]])

# Call Gemma-2B
prompt = f"""you are story explainer
pleae find answer from below story 

SOP:
{context}

quetion:
{query}
"""
response = ollama.generate(model="gemma:2b", prompt=prompt)
print(response['response'])
