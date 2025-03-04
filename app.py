from flask import Flask, request, jsonify,render_template,send_file
from chat_gpt_handler import ChatGPTHandle
from dotenv import load_dotenv
import os
import json
import boto3
from weather_handler import Weather_Handler
from google_search_handler import google_custom_search
from schedule_handler import add_event, get_schedule, get_current_datetime ,remove_event
import uuid
import traceback

load_dotenv('.env')


app = Flask(__name__)
gpt_key = os.getenv('GPT_KEY')
weather_api_key=os.getenv('WEATHER_API_KEY')

polly = boto3.client(
    "polly",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name="eu-north-1",
)

chat_gpt = ChatGPTHandle(api_key=gpt_key, weather_api_key=weather_api_key)

messages = [
    {
        "role": "system", 
        "content": "You are a helpful Virtual Assistant. You have been integrated with a speech system, so now you can listen and speak. keep eye on function calling"
    }
]

functions = {
    "googleCustomSearch": google_custom_search,
    "weatherCheck": lambda city: Weather_Handler().get_weather(city,weather_api_key),
    "addEvent": add_event,
    "getSchedule": get_schedule,
    "getCurrentDateTime": get_current_datetime,
    "removeEvent": remove_event,
}


app.config["SESSION_TYPE"] = "filesystem"

DATA_DIR = "user_data"  # Directory to store user files
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure directory exists

@app.route('/')
def start():
    """ Show the user consent form. """
    return render_template("start.html")

@app.route('/start_chat', methods=['POST'])
def start_chat():
    """ Store user details and create a file for storing interactions. """
    name = request.form.get("name", "").replace(" ", "")
    occupation = request.form.get("occupation", "").replace(" ", "")
    consent = request.form.get("consent")

    if not (name and occupation and consent):
        return "Consent is required to proceed.", 400

    user_id = str(uuid.uuid4())[:8]  # Short unique ID
    filename = f"{name}-{occupation}_{user_id}.txt"
    filepath = os.path.join(DATA_DIR, filename)

    # Create file and save user details
    with open(filepath, "w") as f:
        f.write(f"User: {name}\nOccupation: {occupation}\n--- Conversations ---\n")

    # Pass filename to index.html
    return render_template('index.html', filename=filename)

@app.route('/chat', methods=['POST'])
def chat():
    """ Process user message and store chat in a file instead of session """
    try:
    # Get filename from request
        filename = request.args.get("filename", "").strip()
        if not filename:
            return jsonify({"error": "Filename is required"}), 400

        filepath = os.path.join(DATA_DIR, filename)

        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Store user message in file
        with open(filepath, "a") as f:
            f.write(f"User: {user_message}\n")

        # Prepare chat history for ChatGPT
        chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
        
        # Read existing messages from file (excluding headers)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines[3:]:  # Skip headers
                    if line.startswith("User: "):
                        chat_history.append({"role": "user", "content": line.replace("User: ", "").strip()})
                    elif line.startswith("Assistant: "):
                        chat_history.append({"role": "assistant", "content": line.replace("Assistant: ", "").strip()})

        # Get response from ChatGPT
        response = chat_gpt.get_chatgpt_response(chat_history)

        if response:
            while True:
                choice = response.choices[0]
                finish_reason = choice.finish_reason

                if finish_reason == "function_call":
                    fn_name = choice.message.function_call.name
                    args = json.loads(choice.message.function_call.arguments)

                    # Call the appropriate function
                    fn = functions.get(fn_name)
                    if fn:
                        if fn_name == "googleCustomSearch":
                            result = fn(args['query'])
                        elif fn_name == "weatherCheck":
                            city = args.get("city", "Islamabad")  # Default city
                            result = fn(city)
                        elif fn_name == "addEvent":
                            result = fn(args['event_name'], args['event_date'], args['event_time'])
                        elif fn_name == "getSchedule":
                            result = fn()
                        elif fn_name == 'getCurrentDateTime':
                            result = fn()
                        elif fn_name == "removeEvent":
                            result = fn(args['event_name'], args['event_date'], args['event_time'])

                        chat_history.append({
                            "role": "function",
                            "name": fn_name,
                            "content": json.dumps({"result": result}),
                        })
                        response = chat_gpt.get_chatgpt_response(chat_history)
                else:
                    assistant_response = choice.message.content
                    break

            # Store assistant response in file
            with open(filepath, "a") as f:
                f.write(f"Assistant: {assistant_response}\n")

            return jsonify({"reply": assistant_response})
        else:
            return jsonify({"error": "Failed to fetch response from ChatGPT"}), 500
    except Exception as e:
        print(f"Error message: {e}")
        # Print the full traceback
        print("Stack trace:")
        traceback.print_exc()  # Prints the complete traceback to the console

@app.route("/synthesize", methods=["POST"])
def synthesize_speech():
    data = request.json
    text = data.get("text", "Hello, this is Amazon Polly.")

    response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")

    # Save the audio file
    audio_file = "output.mp3"
    with open(audio_file, "wb") as file:
        file.write(response["AudioStream"].read())

    return send_file(audio_file, mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
