
from flask import Flask, render_template, request
import requests
import os
from PyPDF2 import PdfReader

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Memory
conversation_history = []
pdf_text = ""
pdf_chunks = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    global pdf_text
    global pdf_chunks

    user_message = request.json["message"]

    conversation_history.append(
        f"User: {user_message}"
    )

    recent_history = conversation_history[-4:]

    # Find relevant PDF chunk
    relevant_text = ""

    for chunk in pdf_chunks:

        if any(
            word.lower() in chunk.lower()
            for word in user_message.split()
        ):
            relevant_text = chunk[:1000]
            break

    full_prompt = f"""
You are a helpful AI assistant.

Rules:
- Answer greetings normally.
- If the question is about the uploaded PDF, use the PDF content.
- Keep answers short and clear.
- Be conversational.

Relevant PDF Content:
{relevant_text}

Conversation:
{chr(10).join(recent_history)}

Assistant:
"""

    data = {
        "model": "gemma:2b",
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "num_predict": 150
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

        ai_response = f"Error: {str(e)}"

    conversation_history.append(
        f"Assistant: {ai_response}"
    )

    return ai_response


@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():

    global pdf_text
    global pdf_chunks

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

    total_pages = len(reader.pages)

    pdf_text = ""
    pdf_chunks = []

    for page in reader.pages:

        text = page.extract_text()

        if text:

            pdf_text += text + "\n"

            pdf_chunks.append(text)

    return f"PDF uploaded successfully! Pages: {total_pages}"


if __name__ == "__main__":
    app.run(debug=True)

