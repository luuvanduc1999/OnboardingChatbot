import os
from openai import OpenAI
import chromadb
from personalized_roadmap import roadmap_manager
from content_generator import content_generator
from document_extractor import document_extractor

embedding_client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= "sk-AtDMlHQInyQArPQ_ZyvFBA"
)
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key= "sk-xvI5gYSbiDQ3c4blptwn0A"
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
    Also handle special commands for new features.
    """
    try:
        # Kiểm tra các lệnh đặc biệt cho chức năng mới
        user_question_lower = user_question.lower().strip()
        
        # Lệnh tạo lộ trình onboarding
        if any(keyword in user_question_lower for keyword in ['lộ trình', 'roadmap', 'onboarding', 'học tập']):
            if any(keyword in user_question_lower for keyword in ['tạo', 'gợi ý', 'đề xuất']):
                # Trích xuất vị trí từ câu hỏi
                positions = roadmap_manager.get_available_positions()
                for pos in positions:
                    if pos in user_question_lower:
                        roadmap = roadmap_manager.generate_personalized_roadmap(pos)
                        return f"🎯 **Lộ trình onboarding cho vị trí {pos}:**\n\n{roadmap}"
                
                return """🎯 **Tạo lộ trình onboarding cá nhân hóa**

Tôi có thể tạo lộ trình onboarding cho các vị trí sau:
- Developer (Lập trình viên)
- Designer (Thiết kế UI/UX)  
- Marketing
- HR (Nhân sự)
- Sales (Kinh doanh)

Hãy cho tôi biết vị trí bạn quan tâm, ví dụ: "Tạo lộ trình cho developer" hoặc "Gợi ý học tập cho marketing"."""

        # Lệnh tạo nội dung tự động
        if any(keyword in user_question_lower for keyword in ['email', 'tóm tắt', 'câu hỏi', 'checklist']):
            if 'email chào mừng' in user_question_lower or 'welcome email' in user_question_lower:
                return """📧 **Tạo email chào mừng tự động**

Tôi có thể tạo email chào mừng cho nhân viên mới. Cần thông tin:
- Tên nhân viên
- Vị trí công việc
- Ngày bắt đầu
- Phòng ban
- Tên quản lý

Sử dụng API endpoint: `/api/content/welcome-email`"""

            if 'tóm tắt' in user_question_lower:
                return """📄 **Tóm tắt tài liệu tự động**

Tôi có thể tóm tắt tài liệu theo các kiểu:
- Tóm tắt tổng quan (general)
- Điểm chính (key_points)  
- Hành động cần thực hiện (action_items)

Sử dụng API endpoint: `/api/content/summarize`"""

            if 'câu hỏi' in user_question_lower and 'đào tạo' in user_question_lower:
                return """❓ **Sinh câu hỏi đào tạo tự động**

Tôi có thể tạo câu hỏi đào tạo từ nội dung:
- Trắc nghiệm (multiple_choice)
- Đúng/Sai (true_false)
- Hỗn hợp (mixed)

Sử dụng API endpoint: `/api/content/training-questions`"""

        # Lệnh trích xuất thông tin
        if any(keyword in user_question_lower for keyword in ['cv', 'hồ sơ', 'trích xuất', 'tự động điền']):
            return """🔍 **Trích xuất thông tin tự động**

Tôi có thể xử lý các loại tài liệu:
- CV/Resume
- CMND/CCCD  
- Bằng cấp
- Tài liệu khác

Và tự động điền vào các biểu mẫu:
- Thông tin nhân viên
- Thông tin hợp đồng

Sử dụng API endpoints:
- `/api/extract/upload` - Upload file
- `/api/extract/process-complete` - Xử lý hoàn chỉnh"""

        # Lệnh trợ giúp
        if any(keyword in user_question_lower for keyword in ['help', 'trợ giúp', 'hướng dẫn', 'chức năng']):
            return """🤖 **Chatbot Onboarding - Hướng dẫn sử dụng**

**Chức năng cơ bản:**
- Hỏi đáp về chính sách, quy trình, phúc lợi công ty

**Chức năng mới:**

🎯 **1. Lộ trình onboarding cá nhân hóa**
- "Tạo lộ trình cho developer"
- "Gợi ý học tập cho marketing"

📧 **2. Tạo nội dung tự động**  
- "Tạo email chào mừng"
- "Tóm tắt tài liệu"
- "Sinh câu hỏi đào tạo"

🔍 **3. Trích xuất thông tin tự động**
- "Xử lý CV"
- "Trích xuất thông tin từ giấy tờ"
- "Tự động điền biểu mẫu"

Hãy thử các lệnh trên hoặc hỏi bất kỳ câu hỏi nào về onboarding!"""

        # Xử lý câu hỏi thông thường
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
        return f"❌ Đã xảy ra lỗi: {e}"

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
