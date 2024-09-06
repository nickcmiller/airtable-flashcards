import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional, Callable, Tuple

load_dotenv()

def chat_with_openai_model(
    prompt: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    model: str = "gpt-4o-mini",
    response_format: Optional[Dict[str, str]] = None,
    tools: Optional[List[Dict]] = None,
    tool_choice: Optional[str] = None
) -> dict:
    client = OpenAI()
    
    if prompt and not messages:
        messages = [{"role": "user", "content": prompt}]
    elif prompt and messages:
        messages = messages + [{"role": "user", "content": prompt}]
    elif not messages:
        raise ValueError("Either 'prompt' or 'messages' must be provided")
    
    kwargs = {
        "model": model,
        "messages": messages,
    }
    
    if response_format:
        kwargs["response_format"] = response_format
    if tools:
        kwargs["tools"] = tools
    if tool_choice:
        kwargs["tool_choice"] = tool_choice
    
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message

def format_message(
    message: Union[dict, OpenAIObject]
) -> dict:
    if isinstance(message, dict):
        return message
    
    formatted = {
        "role": message.role,
        "content": message.content
    }
    
    if hasattr(message, 'tool_calls') and message.tool_calls:
        formatted["tool_calls"] = [{
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        } for tool_call in message.tool_calls]
    
    return formatted

def react_agent(
    user_input: str
) -> str:
    conversation = [
        {
            "role": "system", 
            "content": (
                "You are a ReACT agent designed to help users get weather information. "
                "You can think, act, and observe. Use the tools provided to accomplish the task."
            )
        }
    ]
    
    tools = {
        "recognize_weather_request": recognize_weather_request_tool(),
        "get_weather_data": get_weather_data_tool()
    }
    
    while True:
        assistant_message = chat_with_openai_model(
            prompt=user_input,
            messages=conversation,
            tools=[tool_info for tool_info, _ in tools.values()],
            tool_choice="auto"
        )
        formatted_message = format_message(assistant_message)
        conversation.append(formatted_message)
        
        result = _process_tool_calls(
            formatted_message, 
            conversation, 
            tools
        )
        if result:
            print(f"\n\nConversation: {json.dumps(conversation, indent=2)}\n\n")
            return result

def _process_tool_calls(
    assistant_message: dict,
    conversation: List[Dict[str, str]],
    tools: Dict[str, Tuple[Dict, Callable]]
) -> Optional[str]:
    if "tool_calls" in assistant_message:
        for tool_call in assistant_message["tool_calls"]:
            result = _call_tool(tool_call["function"], tools)
            conversation.append(
                {
                    "role": "tool", 
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"], 
                    "content": json.dumps(result)
                }
            )
        return None
    else:
        return assistant_message["content"]

def _call_tool(
    function: dict, 
    tools: dict
) -> dict:
    function_name = function["name"]
    function_args = json.loads(function["arguments"])
    
    if function_name not in tools:
        raise ValueError(f"Unknown tool: {function_name}")
    
    _, tool_func = tools[function_name]
    return tool_func(**function_args)

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
    result = react_agent(user_input)
    print(result)