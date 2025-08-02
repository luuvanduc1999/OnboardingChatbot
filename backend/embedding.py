import chromadb
from openai import OpenAI
import os
import json
from pathlib import Path
from tqdm import tqdm

embedding_client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= os.environ.get("EMBEDDING_API_KEY")
)
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= os.environ.get("OPENAI_API_KEY")
)

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

def get_embedding(text):
    response = embedding_client.embeddings.create(
        input=text,
        model= EMBEDDING_MODEL
    )
    return response.data[0].embedding 

def generate_qa_pairs(chunk):
    """
    Generate 3-5 question-answer pairs from a text chunk using OpenAI function calling.
    """
    prompt = f"""
Đọc đoạn văn sau và tạo 3-5 cặp câu hỏi - câu trả lời khi nhân viên mới vào làm có thể hỏi:

"{chunk}"

Tạo các câu hỏi thực tế và hữu ích mà nhân viên mới có thể quan tâm, với câu trả lời đầy đủ dựa trên thông tin trong đoạn văn.
Đảm bảo câu trả lời ngắn gọn và dễ hiểu.
"""
    try:
        response = client.chat.completions.create(
            model="GPT-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            tools=[{"type": "function", "function": QA_FUNCTION_SCHEMA}],
            tool_choice={"type": "function", "function": {"name": "generate_qa_pairs"}},
            temperature=0.5
        )
        
        tool_call = response.choices[0].message.tool_calls[0] if response.choices[0].message.tool_calls else None
        if tool_call:
            result = json.loads(tool_call.function.arguments)
            return [(qa["question"], qa["answer"]) for qa in result["qa_pairs"]]
        return []
    except Exception as e:
        print(f"❌ Function calling error in generate_qa_pairs: {e}")
        return []

def paraphrase_question(q):
    """
    Generate 2 paraphrased versions of a question using OpenAI function calling.
    """
    prompt = f"""
Viết lại câu hỏi sau theo 2 cách khác nhau có cùng ý nghĩa:

"{q}"

Đảm bảo các phiên bản khác nhau về cách diễn đạt nhưng giữ nguyên ý nghĩa.
"""
    try:
        response = client.chat.completions.create(
            model="GPT-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            tools=[{"type": "function", "function": PARAPHRASE_FUNCTION_SCHEMA}],
            tool_choice={"type": "function", "function": {"name": "paraphrase_questions"}},
            temperature=0.7
        )
        
        tool_call = response.choices[0].message.tool_calls[0] if response.choices[0].message.tool_calls else None
        if tool_call:
            result = json.loads(tool_call.function.arguments)
            return result["paraphrases"][:2]  # Limit to 2 paraphrases
        return []
    except Exception as e:
        print(f"❌ Function calling error in paraphrase_question: {e}")
        return []

chroma_client = chromadb.PersistentClient(path="./database")
collection = chroma_client.get_or_create_collection(
    name="qa_collection",
    metadata={"hnsw:space": "cosine"}
)

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
                    paraphrases = paraphrase_question(question)
                    all_versions = [question] + paraphrases
                    
                    # Prepare data for ChromaDB batch insert
                    documents = []
                    metadatas = []
                    embeddings = []
                    ids = []
                    
                    for i, version in enumerate(all_versions):
                        if version.strip():  # Skip empty versions
                            # Generate embedding
                            embedding = get_embedding(version)
                            
                            documents.append(version)
                            metadatas.append({
                                "answer": answer, 
                                "original_question": question,
                                "is_paraphrase": i > 0
                            })
                            embeddings.append(embedding)
                            ids.append(f"{abs(hash(version + answer))}_{i}")
                    
                    # Insert batch into ChromaDB
                    if documents:  # Only insert if we have documents
                        collection.add(
                            documents=documents,
                            metadatas=metadatas,
                            embeddings=embeddings,
                            ids=ids
                        )
                        print(f"✅ Added {len(documents)} question variants")
                        
                except Exception as e:
                    print(f"❌ Paraphrase error: {e}")
        except Exception as e:
            print(f"❌ QA generation error: {e}")

print(f"✅ Done! Total entries in database: {collection.count()}")



