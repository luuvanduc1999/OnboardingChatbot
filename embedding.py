import os
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import sqlite3
import json
from tqdm import tqdm
import numpy as np
from pathlib import Path

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= os.environ.get("OPENAI_API_KEY")
)

# Model name for sentence embeddings
MODEL_NAME = "intfloat/multilingual-e5-base"
embedder = SentenceTransformer(MODEL_NAME)

# Create/connect to SQLite database
conn = sqlite3.connect("./database/qa.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS qa (
        id INTEGER PRIMARY KEY,
        question TEXT,
        answer TEXT,
        embedding BLOB
    )
''')
conn.commit()

# Function schemas for OpenAI function calling
QA_FUNCTION_SCHEMA = {
    "name": "generate_qa_pairs",
    "description": "Generate question-answer pairs from text content",
    "parameters": {
        "type": "object",
        "properties": {
            "qa_pairs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The question"},
                        "answer": {"type": "string", "description": "The answer"}
                    },
                    "required": ["question", "answer"]
                }
            }
        },
        "required": ["qa_pairs"]
    }
}

PARAPHRASE_FUNCTION_SCHEMA = {
    "name": "paraphrase_questions",
    "description": "Generate paraphrased versions of a question",
    "parameters": {
        "type": "object",
        "properties": {
            "paraphrases": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of paraphrased questions"
            }
        },
        "required": ["paraphrases"]
    }
}

def generate_qa_pairs(chunk):
    """
    Generate 3-5 question-answer pairs from a text chunk using OpenAI function calling.
    """
    prompt = f"""
Đọc đoạn văn sau và tạo 3-5 cặp câu hỏi - câu trả lời khi nhân viên mới vào làm có thể hỏi:

"{chunk}"

Tạo các câu hỏi thực tế và hữu ích mà nhân viên mới có thể quan tâm, với câu trả lời đầy đủ dựa trên thông tin trong đoạn văn.
"""
    try:
        response = client.chat.completions.create(
            model="GPT-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            functions=[QA_FUNCTION_SCHEMA],
            function_call={"name": "generate_qa_pairs"},
            temperature=0.5
        )
        
        function_call = response.choices[0].message.function_call
        if function_call:
            result = json.loads(function_call.arguments)
            return [(qa["question"], qa["answer"]) for qa in result["qa_pairs"]]
        return []
    except Exception as e:
        print(f"❌ Function calling error in generate_qa_pairs: {e}")
        return []

def paraphrase_question(q):
    """
    Generate 3 paraphrased versions of a question using OpenAI function calling.
    """
    prompt = f"""
Viết lại câu hỏi sau theo 3 cách khác nhau có cùng ý nghĩa:

"{q}"

Đảm bảo các phiên bản khác nhau về cách diễn đạt nhưng giữ nguyên ý nghĩa.
"""
    try:
        response = client.chat.completions.create(
            model="GPT-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            functions=[PARAPHRASE_FUNCTION_SCHEMA],
            function_call={"name": "paraphrase_questions"},
            temperature=0.7
        )
        
        function_call = response.choices[0].message.function_call
        if function_call:
            result = json.loads(function_call.arguments)
            print(result["paraphrases"])
            return result["paraphrases"]
        return []
    except Exception as e:
        print(f"❌ Function calling error in paraphrase_question: {e}")
        return []

# Load all chunk files from the ./chunk directory
listChunks = Path("./chunk").glob("*.json")
for file in listChunks:
    print(f"Processing {file.name}")

    # Load JSON content
    with open(file, "r", encoding="utf-8") as f:
        chunksJson = json.load(f)
    # Combine title and text for each chunk
    chunks = [chunk["title"] + " - " + chunk["text"] for chunk in chunksJson]

    # Process each chunk
    for chunk in tqdm(chunks, desc="Ingesting"):
        try:
            qa_pairs = generate_qa_pairs(chunk)
            for question, answer in qa_pairs:
                try:
                    # Get original and paraphrased questions
                    all_versions = [question] + paraphrase_question(question)
                    for version in all_versions:
                        # Generate embedding
                        vec = embedder.encode([version])[0]
                        blob = vec.astype(np.float32).tobytes()
                        # Insert into database
                        c.execute(
                            "INSERT INTO qa (question, answer, embedding) VALUES (?, ?, ?)", 
                            (version, answer, blob)
                        )
                except Exception as e:
                    print(f"❌ Paraphrase error: {e}")
        except Exception as e:
            print(f"❌ QA generation error: {e}")

# Commit changes and close connection
conn.commit()
conn.close()
print("✅ Done!")