from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

MODEL_NAME = "deepseek/deepseek-r1"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/evaluate", methods=["POST"])
def evaluate_summary():
    try:
        data = request.json
        student_summary = data.get("content", "").strip()

        if not student_summary:
            return jsonify({"error": "No summary provided"}), 400

        prompt = (
            f"Evaluate the student's summary based on grammar, clarity, coherence, completeness, and overall quality. "
            f"Provide feedback in exactly five lines as a single paragraph. Ensure that the last sentence explicitly states 'Overall Score: X/10'. "
            f"Do not omit the score under any circumstances.\n\n"
            f"Student's Summary: \"{student_summary}\"\n\n"
            f"Feedback:"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 250
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        # Check if response is successful
        if response.status_code != 200:
            return jsonify({"error": "API request failed", "details": response.text}), 500

        response_json = response.json()

        # Validate AI response structure
        if "choices" not in response_json or not response_json["choices"]:
            return jsonify({"error": "Invalid AI response format", "details": response_json}), 500

        ai_feedback = response_json["choices"][0].get("message", {}).get("content", "").strip()

        if ai_feedback:
            match = re.search(r'Overall Score:\s*(\d+)/10', ai_feedback)
            score = int(match.group(1)) if match else None  # Allow None instead of forcing 0

            cleaned_feedback = re.sub(r'Overall Score:\s*\d+/10', '', ai_feedback).strip()

            return jsonify({
                "feedback": cleaned_feedback,
                "score": score if score is not None else "Not Provided"
            })

        return jsonify({"error": "Empty response from AI", "details": response_json}), 500

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # Ensure debug is off in production
