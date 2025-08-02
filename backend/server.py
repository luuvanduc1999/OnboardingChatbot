from flask import Flask, request, jsonify, Response
import chatbot
import tts

app = Flask(__name__)


@app.route('/api/chatbot', methods=['POST'])
def chatbot_search():
    data = request.json
    query = data.get('question', '')
    #return sample mock message
    if not query:
        return jsonify({"error": "No query provided"}), 400
    get_answer = chatbot.get_answer(query, top_k=5, threshold=0.2)
    
    response = {"response": get_answer  }
    return jsonify(response)

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
