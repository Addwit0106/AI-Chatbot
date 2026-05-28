from flask import Flask, render_template, request, Response
import requests
import json

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    data = {
        "model": "phi3",
        "prompt": user_message,
        "stream": True
    }

    def generate():

        response = requests.post(
            OLLAMA_URL,
            json=data,
            stream=True
        )

        for line in response.iter_lines():

            if line:

                json_data = json.loads(line)

                if "response" in json_data:
                    yield json_data["response"]

    return Response(generate(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)