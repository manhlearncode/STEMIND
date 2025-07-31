import json
from dotenv import load_dotenv
import os
import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Đặt API key Gemini

load_dotenv()  # Tải biến môi trường từ file .env
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Hàm chunking tài liệu
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

# Hàm tạo embedding dùng Gemini
def create_embedding(text):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return embeddings.embed_query(text)

# Phần 1: Xử lý dữ liệu từ SQLite và lưu JSON
def process_documents(db_path, query, output_json='embeddings.json'):
    if not os.path.exists(db_path):
        print(f"Database không tồn tại: {db_path}")
        return

    all_chunks = []
    all_embeddings = []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        text = row[0]
        if not text:
            continue

        chunks = chunk_text(text)
        for chunk in chunks:
            embedding = create_embedding(chunk)
            all_chunks.append(chunk)
            all_embeddings.append(embedding)

    data = {
        'chunks': all_chunks,
        'embeddings': all_embeddings
    }
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Đã lưu {len(all_chunks)} chunks và embeddings từ SQLite vào {output_json}")

# Phần 2: Xử lý câu hỏi người dùng
def answer_question(query, json_path='embeddings.json', top_k=1):
    if not os.path.exists(json_path):
        print(f"JSON không tồn tại: {json_path}")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    chunks = data['chunks']
    embeddings = np.array(data['embeddings'])

    # Embed câu hỏi
    query_embedding = np.array(create_embedding(query)).reshape(1, -1)

    # Tính cosine similarity
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Lấy top_k chunk giống nhất
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    top_chunks = [chunks[i] for i in top_indices]
    top_scores = [similarities[i] for i in top_indices]

    print("Kết quả so sánh:")
    for i, (chunk, score) in enumerate(zip(top_chunks, top_scores)):
        print(f"Top {i+1}: Similarity = {score:.4f}\nChunk: {chunk[:200]}...")

    # Generate response dùng Gemini dựa trên chunk
    context = "\n".join(top_chunks)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Context: {context}\nCâu hỏi: {query}")
    generated_answer = response.text

    return generated_answer

# Ví dụ sử dụng
if __name__ == "__main__":
    db_path = 'path/to/your/database.sqlite'
    query = "SELECT content FROM documents"
    process_documents(db_path, query)

    user_query = "Câu hỏi của người dùng ở đây?"
    answer = answer_question(user_query)
    print("\nCâu trả lời generated:", answer)