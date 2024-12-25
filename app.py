from flask import Flask, request, jsonify,render_template,session
from chat_gpt_handler import ChatGPTHandle

app = Flask(__name__)
chat_gpt = ChatGPTHandle()

# Initial messages for the assistant
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

from flask_session import Session

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]
    
    user_message = request.json.get("message", "")
    session['messages'].append({"role": "user", "content": user_message})
    
    response = chat_gpt.get_chatgpt_response(session['messages'])
    if response:
        gpt_message = response.choices[0].message.content
        session['messages'].append({"role": "assistant", "content": gpt_message})
        return jsonify({"reply": gpt_message})
    else:
        return jsonify({"error": "Failed to fetch response from ChatGPT"}), 500

if __name__ == '__main__':
    app.run(debug=True)
