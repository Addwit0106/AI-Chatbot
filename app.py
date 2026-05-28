from flask import Flask, render_template, request, Response
import requests
import json

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Conversation memory
conversation_history = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    # Store user message
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Keep only recent messages
    recent_history = conversation_history[-6:]

    # Format conversation properly
    formatted_history = ""

    for msg in recent_history:

        if msg["role"] == "user":
            formatted_history += f"User: {msg['content']}\n"

        else:
            formatted_history += f"Assistant: {msg['content']}\n"

    # System Prompt
    full_prompt = f"""
You are a simple and helpful AI assistant.

Rules:
- Give direct answers only.
- Keep responses short unless user asks for details.
- Do not generate unrelated information.
- Do not continue old topics.
- Respond naturally like a chatbot.
- If user says "hi" or "hello", greet briefly.
- Do not create long explanations unless requested.

Conversation:
{formatted_history}

Assistant:
"""

    data = {
        "model": "phi3",
        "prompt": full_prompt,
        "stream": True,
        "options": {
            "temperature": 0.3,
            "num_predict": 120,
            "top_p": 0.9
        }
    }

    def generate():

        full_response = ""

        response = requests.post(
            OLLAMA_URL,
            json=data,
            stream=True
        )

        for line in response.iter_lines():

            if line:

                json_data = json.loads(line)

                if "response" in json_data:

                    chunk = json_data["response"]

                    full_response += chunk

                    yield chunk

        # Store assistant response
        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })

    return Response(generate(), mimetype='text/plain')


if __name__ == "__main__":
    app.run(debug=True)