from flask import Flask, request, jsonify, Response
import json
import re
from openai import OpenAI
import chatbot
import tts
from personalized_roadmap import roadmap_manager
from content_generator import content_generator
from document_extractor import document_extractor
from flask_cors import CORS
from datetime import datetime
import os
from stt import transcribe, STT_AVAILABLE
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

@app.route('/api/chatbot/suggestions', methods=['POST'])
def chatbot_suggestions():
    """Trả về gợi ý câu hỏi dựa trên lịch sử câu hỏi của user"""
    try:
        data = request.json
        history = data.get('history', [])
        suggestions = chatbot.get_smart_suggestions(history)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"suggestions": ["help"]})
CORS(app)

# Cấu hình upload file
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/chatbot', methods=['POST'])
def chatbot_search():
    data = request.json
    query = data.get('question', '')
    #return sample mock message
    if not query:
        return Response(
            json.dumps({"error": "No query provided"}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
            status=400
        )

    # Lấy câu trả lời từ chatbot
    get_answer = chatbot.get_answer(query, top_k=5, threshold=0.2)

    # Chuyển về string UTF-8, bỏ ký tự không decode được
    if isinstance(get_answer, str):
        answer_text = get_answer.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    else:
        answer_text = str(get_answer)

    # Loại bỏ ###, #### và **
    clean_text = re.sub(r'#+\s*', '', answer_text)
    clean_text = re.sub(r'\*\*', '', clean_text)

    # Trả JSON UTF-8 chuẩn
    response_json = json.dumps({"response": clean_text}, ensure_ascii=False)
    return Response(response_json, mimetype='application/json; charset=utf-8')

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        audio_buffer = tts.generate_tts_audio(text)
        return Response(
            audio_buffer.getvalue(),
            mimetype='audio/wav',
            headers={
                'Content-Disposition': 'attachment; filename=speech.wav',
                'Content-Type': 'audio/wav'
            }
        )

    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

@app.route("/api/stt", methods=["POST"])
def api_stt():
    if not STT_AVAILABLE:
        return jsonify({"error": "STT model not available"}), 500

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Lưu file tạm thời
    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio_file.save(tmp_path)

    try:
        text = transcribe(tmp_path)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoints cho lộ trình onboarding cá nhân hóa
@app.route('/api/roadmap/positions', methods=['GET'])
def get_positions():
    """Lấy danh sách các vị trí có sẵn"""
    try:
        positions = roadmap_manager.get_available_positions()
        return jsonify({"positions": positions})
    except Exception as e:
        return jsonify({"error": f"Failed to get positions: {str(e)}"}), 500

@app.route('/api/roadmap/generate', methods=['POST'])
def generate_roadmap():
    """Tạo lộ trình onboarding cá nhân hóa"""
    try:
        data = request.json
        position = data.get('position', '')
        experience_level = data.get('experience_level', 'fresher')
        specific_interests = data.get('specific_interests', [])
        
        if not position:
            return jsonify({"error": "Position is required"}), 400
        
        roadmap = roadmap_manager.generate_personalized_roadmap(
            position, experience_level, specific_interests
        )
        
        return jsonify({
            "roadmap": roadmap,
            "position": position,
            "experience_level": experience_level
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate roadmap: {str(e)}"}), 500

@app.route('/api/roadmap/suggestions', methods=['POST'])
def get_learning_suggestions():
    """Lấy gợi ý học tập tiếp theo"""
    try:
        data = request.json
        position = data.get('position', '')
        completed_items = data.get('completed_items', [])
        
        if not position:
            return jsonify({"error": "Position is required"}), 400
        
        suggestions = roadmap_manager.get_learning_suggestions(position, completed_items)
        
        return jsonify({
            "suggestions": suggestions,
            "position": position
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get suggestions: {str(e)}"}), 500

@app.route('/api/roadmap/position/<position_key>', methods=['GET'])
def get_position_details(position_key):
    """Lấy chi tiết lộ trình cho vị trí cụ thể"""
    try:
        roadmap_data = roadmap_manager.get_roadmap_for_position(position_key)
        if roadmap_data:
            return jsonify(roadmap_data)
        else:
            return jsonify({"error": "Position not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to get position details: {str(e)}"}), 500

# Endpoints cho tạo nội dung tự động
@app.route('/api/content/welcome-email', methods=['POST'])
def generate_welcome_email():
    """Tạo email chào mừng tự động"""
    try:
        data = request.json
        employee_info = data.get('employee_info', {})
        
        email = content_generator.generate_welcome_email(employee_info)
        
        return jsonify({
            "email": email,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate welcome email: {str(e)}"}), 500

@app.route('/api/content/reminder-email', methods=['POST'])
def generate_reminder_email():
    """Tạo email nhắc nhở"""
    try:
        data = request.json
        employee_name = data.get('employee_name', '')
        company_name = data.get('company_name', 'Công ty')
        pending_tasks = data.get('pending_tasks', [])
        deadline = data.get('deadline', '')
        
        if not employee_name:
            return jsonify({"error": "Employee name is required"}), 400
        
        email = content_generator.generate_reminder_email(
            employee_name, company_name, pending_tasks, deadline
        )
        
        return jsonify({
            "email": email,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate reminder email: {str(e)}"}), 500

@app.route('/api/content/summarize', methods=['POST'])
def summarize_document():
    """Tóm tắt tài liệu"""
    try:
        data = request.json
        document_text = data.get('document_text', '')
        summary_type = data.get('summary_type', 'general')  # general, key_points, action_items
        
        if not document_text:
            return jsonify({"error": "Document text is required"}), 400
        
        summary = content_generator.summarize_document(document_text, summary_type)
        
        return jsonify({
            "summary": summary,
            "summary_type": summary_type,
            "original_length": len(document_text),
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to summarize document: {str(e)}"}), 500

@app.route('/api/content/training-questions', methods=['POST'])
def generate_training_questions():
    """Sinh câu hỏi đào tạo"""
    try:
        data = request.json
        content = data.get('content', '')
        question_type = data.get('question_type', 'mixed')  # mixed, multiple_choice, true_false
        num_questions = data.get('num_questions', 5)
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        questions = content_generator.generate_training_questions(
            content, question_type, num_questions
        )
        
        return jsonify({
            "questions": questions,
            "question_type": question_type,
            "num_questions": len(questions),
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate training questions: {str(e)}"}), 500

@app.route('/api/content/onboarding-checklist', methods=['POST'])
def generate_onboarding_checklist():
    """Tạo checklist onboarding"""
    try:
        data = request.json
        position = data.get('position', '')
        department = data.get('department', '')
        
        if not position:
            return jsonify({"error": "Position is required"}), 400
        
        checklist = content_generator.generate_onboarding_checklist(position, department)
        
        return jsonify({
            "checklist": checklist,
            "position": position,
            "department": department,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate checklist: {str(e)}"}), 500

# Endpoints cho trích xuất thông tin tự động
@app.route('/api/extract/upload', methods=['POST'])
def upload_document():
    """Upload và xử lý tài liệu"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type', 'cv')  # cv, id_card, diploma, general
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Lưu file tạm thời
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Xử lý tài liệu
        result = document_extractor.process_document_file(file_path, document_type)
        
        # Xóa file tạm sau khi xử lý
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            "result": result,
            "processed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to process document: {str(e)}"}), 500

@app.route('/api/extract/text', methods=['POST'])
def extract_from_text():
    """Trích xuất thông tin từ text đã có"""
    try:
        data = request.json
        text = data.get('text', '')
        document_type = data.get('document_type', 'cv')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        if document_type == 'cv':
            extracted_data = document_extractor.extract_cv_information(text)
        else:
            extracted_data = document_extractor.extract_document_information(text, document_type)
        
        return jsonify({
            "extracted_data": extracted_data,
            "document_type": document_type,
            "processed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to extract information: {str(e)}"}), 500

@app.route('/api/extract/auto-fill', methods=['POST'])
def auto_fill_form():
    """Tự động điền biểu mẫu từ dữ liệu đã trích xuất"""
    try:
        data = request.json
        extracted_data = data.get('extracted_data', {})
        form_template = data.get('form_template', 'employee_info_form')
        
        if not extracted_data:
            return jsonify({"error": "Extracted data is required"}), 400
        
        filled_form = document_extractor.auto_fill_form(extracted_data, form_template)
        
        return jsonify({
            "filled_form": filled_form,
            "form_template": form_template,
            "processed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to auto-fill form: {str(e)}"}), 500

@app.route('/api/extract/form-templates', methods=['GET'])
def get_form_templates():
    """Lấy danh sách templates biểu mẫu"""
    try:
        templates = document_extractor.get_form_templates()
        return jsonify({"templates": templates})
    except Exception as e:
        return jsonify({"error": f"Failed to get form templates: {str(e)}"}), 500

@app.route('/api/extract/form-templates', methods=['POST'])
def add_form_template():
    """Thêm template biểu mẫu mới"""
    try:
        data = request.json
        template_name = data.get('template_name', '')
        template_data = data.get('template_data', {})
        
        if not template_name or not template_data:
            return jsonify({"error": "Template name and data are required"}), 400
        
        document_extractor.add_form_template(template_name, template_data)
        
        return jsonify({
            "message": "Template added successfully",
            "template_name": template_name
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to add template: {str(e)}"}), 500

@app.route('/api/extract/process-complete', methods=['POST'])
def process_document_complete():
    """Xử lý tài liệu hoàn chỉnh: upload -> extract -> auto-fill"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type', 'cv')
        form_template = request.form.get('form_template', 'employee_info_form')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Lưu file tạm thời
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Bước 1: Xử lý tài liệu
            process_result = document_extractor.process_document_file(file_path, document_type)
            
            if process_result.get("processing_status") != "success":
                return jsonify({
                    "error": "Document processing failed",
                    "details": process_result
                }), 400
            
            # Bước 2: Tự động điền biểu mẫu
            extracted_data = process_result.get("extracted_data", {})
            filled_form = document_extractor.auto_fill_form(extracted_data, form_template)
            
            return jsonify({
                "document_processing": process_result,
                "auto_filled_form": filled_form,
                "processed_at": datetime.now().isoformat()
            })
            
        finally:
            # Xóa file tạm
            try:
                os.remove(file_path)
            except:
                pass
        
    except Exception as e:
        return jsonify({"error": f"Failed to process document completely: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
