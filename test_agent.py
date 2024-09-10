import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional
from agent_functions import *

load_dotenv()

import os
import requests
import json
import logging
import traceback

def get_weather_tool():
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

    def _get_weather(
        user_input: str
    ) -> Optional[dict]:
        weather_request = _recognize_weather_request(user_input)
        if weather_request["intent"] == "get_weather":
            city = weather_request["location"]
            return _get_weather_data(city)
        else:
            return None

    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather data for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "The user's input message"}
                },
                "required": ["user_input"]
            }
        }
    }, _get_weather

def get_currency_converter_tool():
    def _recognize_currency_conversion_request(user_input: str) -> Dict[str, str]:
        prompt = f"""
        Analyze the following message and determine if the intent is to convert currency. If so, extract the amount, source currency, and target currency if mentioned.
        Use standard 3-letter currency codes (USD, EUR, GBP, JPY, etc.) when possible.

        Message: "{user_input}"

        Return a JSON object with keys: "intent", "amount", "from_currency", and "to_currency".
        {{
            "intent": "convert_currency",
            "amount": 0,
            "from_currency": "",
            "to_currency": ""
        }}

        Only return the JSON object. Do not include any other text.
        """
        
        response = chat_with_openai_model(
            prompt=prompt,
            response_format={"type": "json_object"}
        )

        print:(f"Response: {response.content}")
        
        return json.loads(response.content)

    def _get_exchange_rate(from_currency: str, to_currency: str, amount: Optional[float] = None) -> Optional[Dict]:
        api_key = os.getenv("EXCHANGERATE_API_KEY")
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
        if amount is not None:
            url += f"/{amount}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data["result"] == "success":
                result = {
                    "conversion_rate": data["conversion_rate"],
                    "base_code": data["base_code"],
                    "target_code": data["target_code"]
                }
                if "conversion_result" in data:
                    result["conversion_result"] = data["conversion_result"]
                return result
            else:
                logging.error(f"API Error: {data.get('error-type', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def _convert_currency(user_input: str) -> Optional[Dict[str, float]]:
        conversion_request = _recognize_currency_conversion_request(user_input)
        if conversion_request["intent"] == "convert_currency":
            amount = conversion_request["amount"]
            from_currency = conversion_request["from_currency"]
            to_currency = conversion_request["to_currency"]
            
            result = _get_exchange_rate(from_currency, to_currency, amount)
            if result is not None:
                return {
                    "from_amount": amount,
                    "from_currency": result["base_code"],
                    "to_amount": result.get("conversion_result", amount * result["conversion_rate"]),
                    "to_currency": result["target_code"],
                    "exchange_rate": result["conversion_rate"]
                }
        return None

    return {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "The user's input message"}
                },
                "required": ["user_input"]
            }
        }
    }, _convert_currency

if __name__ == "__main__":
    user_input = input("Enter a message: ")
    tools = {
        "get_weather": get_weather_tool(),
        "convert_currency": get_currency_converter_tool()
    }
    result = react_agent(
        user_input=user_input,
        tools=tools
    )
    
    print(result)