from openai import OpenAI


class ChatGPTHandle:
    def __init__(self, api_key, weather_api_key):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")
        self.weather_api_key=weather_api_key
        self.client = OpenAI(api_key=api_key)
        self.functions_schema = [
            {
                "name": "googleCustomSearch",
                "description": "Searches Google for a query and returns the top result snippet.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
            },
            {
                "name": "weatherCheck",
                "description": "Retrieves the weather for a specified city.",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}
            },
            {
                "name": "addEvent",
                "description": "Adds an event to the schedule.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_name": {"type": "string", "description": "Name of the event to be scheduled."},
                        "event_date": {"type": "string", "format": "date", "description": "Date of the event in YYYY-MM-DD format."},
                        "event_time": {"type": "string", "format": "time", "description": "Time of the event in HH:MM format."}
                    },
                    "required": ["event_name", "event_date", "event_time"]
                }
            },
            {
                "name": "getSchedule",
                "description": "Retrieves the list of all scheduled events.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "removeEvent",
                "description": "Removes an event from the schedule based on name, date, and time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_name": {"type": "string", "description": "Name of the event to be removed."},
                        "event_date": {"type": "string", "format": "date", "description": "Date of the event in YYYY-MM-DD format."},
                        "event_time": {"type": "string", "format": "time", "description": "Time of the event in HH:MM format."}
                    },
                    "required": ["event_name", "event_date", "event_time"]
                }
            },
            {
                "name": "getCurrentDateTime",
                "description": "Returns the current date and time.",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "getPlainText",
                "description": "Automatically process text containing URLs or numbers into plain text for speech synthesis. Call this function whenever such text appears.Converts text containing URLs or large numerical values into plain text by removing URLs and converting numbers to words, making it suitable for speech synthesis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The input text that needs to be cleaned and formatted."
                        }
                    },
                    "required": ["text"]
                }
            },
        ]

    def get_chatgpt_response(self, messages,f_schema=None):
        try:
            if f_schema=="0":
                f_schema = None
            else:
                f_schema=self.functions_schema
            print("message:",messages)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                functions=f_schema,
                temperature=0,
            )
            # return response.choices[0].message.content  # Updated for new API
            return response
        except Exception as e:
            print("Error fetching response:", e)
            return None
