from flask import Flask, request, jsonify, make_response
import google.generativeai as genai
import os

app = Flask(__name__)

# Add CORS headers manually to all responses
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

def init_gemini(api_key):
    genai.configure(api_key=api_key)

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return make_response("", 204)
    
    try:
        data = request.get_json()
        conversation = data.get("conversation", [])
        user_message = data.get("user_message", "")

        messages = []
        for msg in conversation:
            if msg["role"] == "user":
                messages.append({"role": "user", "parts": [msg["text"]]})
            else:
                messages.append({"role": "model", "parts": [msg["text"]]})

        messages.append({"role": "user", "parts": [user_message]})

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            contents=messages,
            system_instruction="You are AllVesta''s Customer Agent. Have a warm conversation about investing. Ask about experience, knowledge, confidence, risk, readiness. Never give advice. Keep it 1-2 sentences.",
            generation_config={"temperature": 0.7, "max_output_tokens": 150}
        )

        return jsonify({"success": True, "response": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        exit(1)
    init_gemini(api_key)
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
