
from flask import Flask, render_template, request
import requests
import os
from PyPDF2 import PdfReader

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Chat Memory
conversation_history = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    # Save user message
    conversation_history.append(
        f"User: {user_message}"
    )

    # Keep last few messages
    recent_history = conversation_history[-4:]

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
        "model": "gemma:2b",
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

    except Exception:

        ai_response = "AI is busy or not responding."

    # Save AI response
    conversation_history.append(
        f"Assistant: {ai_response}"
    )

    return ai_response


@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():

    if "pdf" not in request.files:
        return "No PDF uploaded."

    pdf_file = request.files["pdf"]

    if pdf_file.filename == "":
        return "No file selected."

    upload_folder = "uploads"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filepath = os.path.join(
        upload_folder,
        pdf_file.filename
    )

    pdf_file.save(filepath)

    reader = PdfReader(filepath)

    total_pages = len(
        reader.pages
    )

    return f"PDF uploaded successfully! Pages: {total_pages}"


if __name__ == "__main__":
    app.run(debug=True)

