import os
from openai import OpenAI
import chromadb

embedding_client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= os.environ.get("EMBEDDING_API_KEY")
)
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= os.environ.get("OPENAI_API_KEY")
)


# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./database")
collection = chroma_client.get_or_create_collection(name="qa_collection")

def get_embedding(text):
    """Get embedding from OpenAI API"""
    response = embedding_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def search(query, top_k=3):
    """
    Search for the top_k most similar questions in ChromaDB to the input query.
    Prints the top results with their similarity scores.
    """
    try:
        # Check if collection is empty
        if collection.count() == 0:
            print("❌ No data in the database. Please run the embedding script first.")
            return
            
        # Get embedding for the query
        query_embedding = get_embedding(query)
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        
        # Print results
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                question = results['documents'][0][i]
                answer = results['metadatas'][0][i]['answer']
                distance = results['distances'][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                print(f"❓ {question}\n💡 {answer}\n🔍 Similarity: {similarity:.2f}\n" + "-" * 40)
        else:
            print("❌ No results found.")
    except Exception as e:
        print(f"❌ SeaopenAI_generate_answerrch error: {e}")

def openAI_generate_answer(user_question, results):
    """
    Use OpenAI API to generate an answer based on the top results.
    If no relevant result, generate an answer based on user_question.
    """
    try:
        # Prepare context from results
        if results and results['documents'][0]:
            context_parts = []
            for i in range(len(results['documents'][0])):
                question = results['documents'][0][i]
                answer = results['metadatas'][0][i]['answer']
                context_parts.append(f"Q: {question}\nA: {answer}")
            
            context = "\n".join(context_parts)
            system_prompt = (
                "You are a helpful assistant for new employees. Use the following Q&A pairs as context. "
                "If the user's question matches one or more context, answer based on all context matching. "
                "If not, generate a helpful answer based on the user's question. Answer in Vietnamese."
            )
            user_content = f"User question: {user_question}\nContext:\n{context}"
        else:
            system_prompt = (
                "You are a helpful assistant for new employees. There is no relevant context. "
                "Generate a helpful answer based on the user's question. Answer in Vietnamese."
            )
            user_content = f"User question: {user_question}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = client.chat.completions.create(
            model="GPT-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error generating answer: {e}"

def get_answer(user_question, top_k=5, threshold=0.2):
    """
    Find the most similar question in ChromaDB to the user's question.
    Generate answer using OpenAI API based on retrieved context.
    """
    try:
        # Check if collection is empty
        if collection.count() == 0:
            print("❌ Database is empty. Please run the embedding script first.")
            return
            
        # Get embedding for the user's question
        query_embedding = get_embedding(user_question)
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        # Filter results by threshold
        filtered_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                similarity = 1 - results['distances'][0][i]
                if similarity >= threshold:
                    filtered_results['documents'][0].append(results['documents'][0][i])
                    filtered_results['metadatas'][0].append(results['metadatas'][0][i])
                    filtered_results['distances'][0].append(results['distances'][0][i])

        print(filtered_results)
        # Call OpenAI API to generate an answer
        answer = openAI_generate_answer(user_question, filtered_results)
        return answer
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_stats():
    """Show database statistics"""
    try:
        count = collection.count()
        print(f"📊 Database contains {count} entries")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

# Clear the terminal screen
os.system('cls' if os.name == 'nt' else 'clear')

print("🤖 Chatbot for New Employees")
print("Commands: 'search <query>' to search, 'stats' for database info, 'exit' to quit")
print("-" * 60)



# Main loop: prompt user for questions and provide answers
# while True:
#     user_input = input("🔍 ").strip()
    
#     if user_input.lower() == 'exit':
#         print("👋 Goodbye!")
#         break
#     elif user_input.lower() == 'stats':
#         show_stats()
#     elif user_input.lower().startswith('search '):
#         query = user_input[7:]  # Remove 'search ' prefix
#         search(query)
#     elif user_input:
#         get_answer(user_input)
#     else:
#         print("❓ Please enter a question or command.")
