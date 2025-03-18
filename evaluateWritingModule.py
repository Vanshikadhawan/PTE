from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re  # Import regex to extract the score

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = "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"
MODEL_NAME = "deepseek/deepseek-r1"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/evaluate", methods=["POST"])
def evaluate_summary():
    try:
        data = request.json
        student_summary = data.get("content", "").strip()

        if not student_summary:
            return jsonify({"error": "No summary provided"}), 400

        # Stronger prompt to enforce scoring in every response
        prompt = (
            f"Evaluate the student's summary based on grammar, clarity, coherence, completeness, and overall quality. "
            f"Provide feedback in exactly five lines as a single paragraph. Ensure that the last sentence explicitly states 'Overall Score: X/10'. "
            f"Do not omit the score under any circumstances.\n\n"
            f"Student's Summary: \"{student_summary}\"\n\n"
            f"Feedback:"
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,  
            "max_tokens": 250  
        }

        response = requests.post(API_URL, json=payload, headers=headers)
        response_json = response.json()

        print("Response JSON:", response_json)  # Debugging print

        if response.status_code == 200 and "choices" in response_json:
            if response_json["choices"]:
                ai_feedback = response_json["choices"][0].get("message", {}).get("content", "").strip()

                if ai_feedback:
                    # Extract numeric score using regex
                    match = re.search(r'Overall Score:\s*(\d+)/10', ai_feedback)
                    score = int(match.group(1)) if match else 0  # Default to 0 if not found

                    # Remove "Overall Score: X/10" from feedback
                    cleaned_feedback = re.sub(r'Overall Score:\s*\d+/10', '', ai_feedback).strip()

                    return jsonify({
                        "feedback": cleaned_feedback,
                        "score": score
                    })
        
        return jsonify({"error": "Received empty response from AI", "details": response_json}), 500

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
