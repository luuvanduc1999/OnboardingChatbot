import openai
from sentence_transformers import SentenceTransformer
import sqlite3
import json
from tqdm import tqdm
import numpy as np
from pathlib import Path

from openai import OpenAI
client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="XXXXX",
)
MODEL_NAME = "intfloat/multilingual-e5-base"

embedder = SentenceTransformer(MODEL_NAME)

# Tạo DB
conn = sqlite3.connect(".\database\qa.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS qa (
    id INTEGER PRIMARY KEY,
    question TEXT,
    answer TEXT,
    embedding BLOB
)''')
conn.commit()

def generate_qa_pairs(chunk):
    prompt = f"""
Đọc đoạn văn sau và tạo 3-5 cặp câu hỏi - câu trả lời khi nhân viên mới vào làm có thể hỏi:

"{chunk}"

Định dạng: 
Q: [câu hỏi]
A: [câu trả lời đầy đủ dựa trên thông tin trong đoạn văn]

Q: [câu hỏi tiếp theo]
A: [câu trả lời tiếp theo]
"""
    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    
    content = response.choices[0].message.content.strip()
    qa_pairs = []
    
    lines = content.split('\n')
    current_q = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Q:'):
            current_q = line[2:].strip()
        elif line.startswith('A:') and current_q:
            answer = line[2:].strip()
            qa_pairs.append((current_q, answer))
            current_q = None
    
    return qa_pairs

def paraphrase_question(q):
    prompt = f"""
Viết lại câu hỏi sau theo 3 cách khác nhau có cùng ý nghĩa:

"{q}"
"""
    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    variations = response.choices[0].message.content.strip().split("\n")
    return [v.strip("-• ") for v in variations if v.strip()]

# Load chunks

listChunks = Path("./data").glob("*.json")
for file in listChunks:
    print(f"Processing {file.name}")

    with open(file, "r", encoding="utf-8") as f:
        chunksJson = json.load(f)
    chunks = [chunk["title"] + " - " + chunk["text"] for chunk in chunksJson]

    # Process
    for chunk in tqdm(chunks, desc="Ingesting"):
        try:
            qa_pairs = generate_qa_pairs(chunk)
            for question, answer in qa_pairs:
                try:
                    all_versions = [question] + paraphrase_question(question)
                    for version in all_versions:
                        vec = embedder.encode([version])[0]
                        blob = vec.astype(np.float32).tobytes()
                        c.execute("INSERT INTO qa (question, answer, embedding) VALUES (?, ?, ?)", 
                                (version, answer, blob))
                except Exception as e:
                    print(f"❌ Paraphrase error: {e}")
        except Exception as e:
            print(f"❌ QA generation error: {e}")

conn.commit()
conn.close()
print("✅ Done!")