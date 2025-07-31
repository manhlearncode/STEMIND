import os
import json
import sqlite3
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load API key từ file .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 1. Đọc tài liệu từ SQLite
def load_stem_documents(db_path, query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    docs = [row[0] for row in rows if row[0]]
    return docs

# 2. Chunking tài liệu
def chunk_text(text, max_chunk_size=500):
    words = text.split()
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

# 3. Tạo embedding cho từng chunk sử dụng Gemini
def get_gemini_embedding(text):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return embeddings.embed_query(text)

# 4. Lưu embedding vào file JSON
def process_and_save_embeddings(db_path, query, output_json='stem_embeddings.json'):
    docs = load_stem_documents(db_path, query)
    all_chunks = []
    all_embeddings = []
    for doc in docs:
        chunks = chunk_text(doc)
        for chunk in chunks:
            embedding = get_gemini_embedding(chunk)
            all_chunks.append(chunk)
            all_embeddings.append(embedding)
    data = {
        'chunks': all_chunks,
        'embeddings': all_embeddings
    }
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu {len(all_chunks)} chunks và embeddings vào {output_json}")

# 5. Trả lời câu hỏi người dùng
def answer_question(query, json_path='stem_embeddings.json', top_k=3):
    if not os.path.exists(json_path):
        print(f"File embedding không tồn tại: {json_path}")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chunks = data['chunks']
    embeddings = np.array(data['embeddings'])

    # Tạo embedding cho câu hỏi
    query_embedding = np.array(get_gemini_embedding(query)).reshape(1, -1)

    # Tính cosine similarity
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    top_chunks = [chunks[i] for i in top_indices]
    top_scores = [similarities[i] for i in top_indices]

    print("Các đoạn tài liệu phù hợp nhất:")
    for i, (chunk, score) in enumerate(zip(top_chunks, top_scores)):
        print(f"Top {i+1}: Similarity = {score:.4f}\nChunk: {chunk[:200]}...\n")

    # Tạo prompt cho Gemini
    context = "\n".join(top_chunks)
    prompt = f"""Dựa trên các đoạn tài liệu STEM sau, hãy trả lời câu hỏi của người dùng một cách chi tiết, dễ hiểu và chính xác.

Tài liệu liên quan:
{context}

Câu hỏi: {query}

Trả lời:"""

    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(prompt)
    answer = response.text
    print("\nCâu trả lời của AI:\n", answer)
    return top_chunks, answer

# Ví dụ sử dụng
if __name__ == "__main__":
    db_path = 'File_sharing_platform/db.sqlite3'
    query = "SELECT url FROM files"
    process_and_save_embeddings(db_path, query)

    user_query = "Giải thích nguyên lý hoạt động của động cơ điện."
    answer_question(user_query)