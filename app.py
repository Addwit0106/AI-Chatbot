
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Memory
conversation_history = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    # Save user message
    conversation_history.append(f"User: {user_message}")

    # Small memory
    recent_history = conversation_history[-4:]

    # Prompt
    full_prompt = f"""
You are a helpful AI assistant.

Rules:
- Keep answers short and clear
- Be conversational
- Avoid unrelated information

Conversation:
{chr(10).join(recent_history)}

Assistant:
"""

    data = {
        "model": "phi3",
        "prompt": full_prompt,
        "stream": False,
        
        "options": {
        "num_predict": 200
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=data,
            timeout=180
        )

        response_json = response.json()

        ai_response = response_json.get(
            "response",
            "No response from AI."
        )

    except Exception as e:

        ai_response = "AI is busy or not responding."

    # Save AI response
    conversation_history.append(f"Assistant: {ai_response}")

    return ai_response


if __name__ == "__main__":
    app.run(debug=True)
