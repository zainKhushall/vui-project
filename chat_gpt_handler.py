api_key = "sk-proj-DSZfHRrRS7Ltl8ltaqm3T3BlbkFJLa545ew9czx9oOkhpE4n"
from openai import OpenAI
import os

class ChatGPTHandle:
    def __init__(self):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")
        self.client = OpenAI(api_key=api_key)

    def get_chatgpt_response(self, messages, functions_schema=None):
        print("messages:",messages)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                #functions=functions_schema,
                temperature=0,
            )
            print("resp= ",response)
            # return response.choices[0].message.content  # Updated for new API
            return response
        except Exception as e:
            print("Error fetching response:", e)
            return None

# a=ChatGPTHandle()
# r=a.get_chatgpt_response([{"role": "user", "content": "hi, how are you.", }] )
# print("r:",r)
# m=r.choices[0].message.content
# print("m:",m)