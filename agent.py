import os
import requests

import openai
from dotenv import load_dotenv
load_dotenv()

from genai_toolbox.text_prompting.model_calls import openai_text_response
from genai_toolbox.helper_functions.string_helpers import evaluate_and_clean_valid_response


def get_weather_data(
    city: str,
    date: str
):
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
    
    response = openai_text_response(
        model_choice="4o-mini",
        prompt=prompt
    )
    result = evaluate_and_clean_valid_response(response, dict)
    
    return result

if __name__ == "__main__":
    prompt = input("Enter a message: ")
    response = recognize_weather_request(prompt)
    print(response)
    location = response['location']
    date = response['date']
    weather = get_weather_data(location, date)
    print(weather)