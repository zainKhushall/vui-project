from flask import Flask, request, jsonify,render_template,session
from chat_gpt_handler import ChatGPTHandle
from dotenv import load_dotenv
import os
import json
from weather_handler import Weather_Handler
from google_search_handler import google_custom_search
from schedule_handler import add_event, get_schedule, get_current_datetime ,remove_event
from flask_session import Session


load_dotenv('.env')


app = Flask(__name__)
gpt_key = os.getenv('GPT_KEY')
weather_api_key=os.getenv('WEATHER_API_KEY')

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
    "getPlainText": lambda text: chat_gpt.get_chatgpt_response(text, f_schema="0")
}


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
        # gpt_message = response.choices[0].message.content
        no_plain_text = "-1"
        while True:
            choice = response.choices[0]
            finish_reason = choice.finish_reason
            print("choice:",choice)
            print("reason:",finish_reason)
            if response and finish_reason == "function_call":
                fn_name = choice.message.function_call.name
                args = json.loads(choice.message.function_call.arguments)

                # Call the appropriate function
                fn = functions.get(fn_name)
                if fn:
                    if fn_name == "googleCustomSearch":
                        result = fn(args['query'])
                        # search_snippet = result["items"][0]["snippet"] if result.get("items") else "No results found."
                        
                    elif fn_name == "weatherCheck":
                        city = args.get("city", "Islamabad")  # Default city
                        result = fn(city)
                    elif fn_name == "getPlainText":
                        text = args.get("text", '')
                        result = fn(text)
                        no_plain_text = text
                    elif fn_name == "addEvent":
                        result = fn(args['event_name'], args['event_date'], args['event_time'])
                    elif fn_name == "getSchedule":
                        result = fn()
                    elif fn_name == 'getCurrentDateTime':
                        result = fn()
                    elif fn_name == "removeEvent":
                        result = fn(args['event_name'], args['event_date'], args['event_time'])
                        
                    session['messages'].append({
                        "role": "function",
                        "name": fn_name,
                        "content": json.dumps({"result": result}),
                    })
                    response = chat_gpt.get_chatgpt_response(session['messages'])
                    
            else:
                response = response.choices[0].message.content
                break

        session['messages'].append({"role": "assistant", "content": response})
        return jsonify({"reply": response, "write":no_plain_text})
    else:
        return jsonify({"error": "Failed to fetch response from ChatGPT"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
