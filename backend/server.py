from flask import Flask, request, jsonify
import chatbot

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
