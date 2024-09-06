import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_weather_data(city: str):
    api_key = os.getenv("WEATHERAPI_KEY")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def recognize_weather_request(user_input):
    prompt = f"""
    Analyze the following message and determine if the intent is to get weather information. If so, extract the location and date if mentioned.

    Message: "{user_input}"

    Return a JSON object with keys: "intent", "location", and "date".
    {{
        "intent": "get_weather",
        "location": "",
        "date": ""
    }}'

    Only return the JSON object. Do not include any other text.
    """
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def react_agent(user_input):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    conversation = [
        {"role": "system", "content": "You are a ReACT agent designed to help users get weather information. You can think, act, and observe. Use the tools provided to accomplish the task."},
        {"role": "user", "content": user_input}
    ]
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=conversation,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "recognize_weather_request",
                        "description": "Analyze user input to determine if it's a weather request and extract location and date",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_input": {"type": "string"}
                            },
                            "required": ["user_input"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather_data",
                        "description": "Get weather data for a specific city",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string"}
                            },
                            "required": ["city"]
                        }
                    }
                }
            ],
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        conversation.append(assistant_message)
        
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "recognize_weather_request":
                    result = recognize_weather_request(function_args["user_input"])
                elif function_name == "get_weather_data":
                    result = get_weather_data(function_args["city"])
                
                conversation.append({"role": "tool", "tool_call_id": tool_call.id, "name": function_name, "content": json.dumps(result)})
        else:
            return assistant_message.content

if __name__ == "__main__":
    user_input = input("Enter a message: ")
    result = react_agent(user_input)
    print(result)