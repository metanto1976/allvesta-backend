from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app, resources={
    r"/chat": {"origins": "*", "methods": ["POST", "OPTIONS"]},
    r"/health": {"origins": "*"}
})

def init_gemini(api_key):
    genai.configure(api_key=api_key)

@app.route('/chat', methods=['POST', 'OPTIONS'])
@cross_origin()
def chat():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        conversation = data.get('conversation', [])
        user_message = data.get('user_message', '')

        messages = []
        for msg in conversation:
            if msg['role'] == 'user':
                messages.append({"role": "user", "parts": [msg['text']]})
            else:
                messages.append({"role": "model", "parts": [msg['text']]})

        messages.append({"role": "user", "parts": [user_message]})

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            contents=messages,
            system_instruction="You are AllVesta''s Customer Agent. Have a warm, natural conversation about investing. Understand their experience, knowledge, confidence, risk tolerance, readiness. Ask follow-up questions. Never give financial advice. Keep responses conversational (1-2 sentences).",
            generation_config={"temperature": 0.7, "max_output_tokens": 150}
        )

        return jsonify({"success": True, "response": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Backend is running"})

if __name__ == "__main__":
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        exit(1)
    init_gemini(api_key)
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
