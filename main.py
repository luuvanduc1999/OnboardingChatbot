import sqlite3
import os
from openai import OpenAI
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Model name for sentence embeddings
MODEL_NAME = "intfloat/multilingual-e5-base"

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= os.environ.get("OPENAI_API_KEY")
)

# Load the sentence transformer model
embedder = SentenceTransformer(MODEL_NAME)

def search(query, top_k=3):
    """
    Search for the top_k most similar questions in the database to the input query.
    Prints the top results with their similarity scores.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect("./database/qa.db")
    c = conn.cursor()
    # Encode the query to get its embedding
    vec_q = embedder.encode([query])[0]

    results = []
    # Iterate through all questions in the database
    for row in c.execute("SELECT question, answer, embedding FROM qa"):
        question, answer, blob = row
        # Convert the stored embedding from bytes to numpy array
        vec = np.frombuffer(blob, dtype=np.float32)
        # Compute cosine similarity between query and stored question
        score = cosine_similarity([vec_q], [vec])[0][0]
        results.append((score, question, answer))

    conn.close()

    # Sort results by similarity score in descending order and get top_k
    results = sorted(results, key=lambda x: x[0], reverse=True)[:top_k]
    for score, q, a in results:
        print(f"❓ {q}\n💡 {a}\n🔍 Similarity: {score:.2f}\n" + "-" * 40)

def openAI_generate_answer(user_question, results):
    """
    Use OpenAI API with function calling to generate an answer based on the top results.
    If no relevant result, generate an answer based on user_question.
    """


    # Prepare context from results
    if results:
        context = "\n".join([f"Q: {q}\nA: {a}" for _, q, a in results])
        system_prompt = (
            "You are a helpful assistant. Use the following Q&A pairs as context. "
            "If the user's question matches any context, answer based on it. "
            "If not, generate a helpful answer based on the user's question. Anwser in Vietnamese."
        )
        user_content = f"User question: {user_question}\nContext:\n{context}"
    else:
        system_prompt = (
            "You are a helpful assistant. There is no relevant context. "
            "Generate a helpful answer based on the user's question. Anwser in Vietnamese."
        )
        user_content = f"User question: {user_question}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=messages,
        max_tokens=150
    )

    return response.choices[0].message.content

def get_answer(user_question, top_k=3, threshold=0.8):
    """
    Find the most similar question in the database to the user's question.
    If the similarity score is above the threshold, print the answer.
    Otherwise, ask the user to clarify.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect("./database/qa.db")
    c = conn.cursor()
    # Encode the user's question
    vec_q = embedder.encode([user_question])[0]

    results = []
    # Iterate through all questions in the database
    for row in c.execute("SELECT question, answer, embedding FROM qa"):
        question, answer, blob = row
        # Convert the stored embedding from bytes to numpy array
        vec = np.frombuffer(blob, dtype=np.float32)
        # Compute cosine similarity
        score = cosine_similarity([vec_q], [vec])[0][0]
        results.append((score, question, answer))

    conn.close()
    # Sort results by similarity score in descending order
    results.sort(reverse=True)

    # Call OpenAI API to generate an answer
    answer = openAI_generate_answer(user_question, results[:top_k])
    print(f"💡{answer}")


# Clear the terminal screen
os.system('cls' if os.name == 'nt' else 'clear')

# Main loop: prompt user for questions and provide answers
while True:
    user_question = input("🔍 ")
    if user_question.lower() == 'exit':
        break
    get_answer(user_question)
