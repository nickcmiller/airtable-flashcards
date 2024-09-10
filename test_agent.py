import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional
from agent_functions import *

load_dotenv()

def recognize_weather_request_tool():
    def _recognize_weather_request(
        user_input: str
    ) -> dict:
        prompt = f"""
        Analyze the following message and determine if the intent is to get weather information. If so, extract the location and date if mentioned.

        Message: "{user_input}"

        Return a JSON object with keys: "intent", "location", and "date".
        {{
            "intent": "get_weather",
            "location": "",
            "date": ""
        }}

        Only return the JSON object. Do not include any other text.
        """
        
        response = chat_with_openai_model(
            prompt=prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.content)

    return {
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
    }, _recognize_weather_request

def get_weather_data_tool():
    def _get_weather_data(
        city: str
    ) -> Optional[dict]:
        api_key = os.getenv("WEATHERAPI_KEY")
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    return {
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
    }, _get_weather_data


if __name__ == "__main__":
    user_input = input("Enter a message: ")
    tools = {
        "recognize_weather_request": recognize_weather_request_tool(),
        "get_weather_data": get_weather_data_tool()
    }
    result = react_agent(
        user_input=user_input,
        tools=tools
    )
    
    print(result)