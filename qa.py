import sqlite3
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "intfloat/multilingual-e5-base"

embedder = SentenceTransformer(MODEL_NAME)

def search(query, top_k=3):
    conn = sqlite3.connect(".\database\qa.db")
    c = conn.cursor()
    vec_q = embedder.encode([query])[0]

    results = []
    for row in c.execute("SELECT question, answer, embedding FROM qa"):
        question, answer, blob = row
        vec = np.frombuffer(blob, dtype=np.float32)
        score = cosine_similarity([vec_q], [vec])[0][0]
        results.append((score, question, answer))

    conn.close()

    results = sorted(results, key=lambda x: x[0], reverse=True)[:top_k]
    for score, q, a in results:
        print(f"❓ {q}\n💡 {a}\n🔍 Similarity: {score:.2f}\n" + "-" * 40)

def get_answer(user_question, top_k=3, threshold=0.8):
    conn = sqlite3.connect("qa.db")
    c = conn.cursor()
    vec_q = embedder.encode([user_question])[0]

    results = []
    for row in c.execute("SELECT question, answer, embedding FROM qa"):
        question, answer, blob = row
        vec = np.frombuffer(blob, dtype=np.float32)
        score = cosine_similarity([vec_q], [vec])[0][0]
        results.append((score, question, answer))

    conn.close()
    results.sort(reverse=True)

    top_score, top_q, top_a = results[0]
    if top_score >= threshold:
        #print question and answer
        print(f"🗨️  {top_a}")
    else:
        print("🤔 Xin lỗi, tôi chưa rõ câu hỏi. Bạn có thể hỏi lại chi tiết hơn không?")

os.system('cls' if os.name == 'nt' else 'clear')
# Dùng thử
while True:
    user_question = input("🔍 ")
    if user_question.lower() == 'exit':
        break
    get_answer(user_question)

