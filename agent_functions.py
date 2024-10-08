import os
import json

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from typing import List, Dict, Optional, Callable, Tuple, Union

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def chat_with_openai_model(
    prompt: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    model: str = "gpt-4o-mini",
    response_format: Optional[Dict[str, str]] = None,
    tools: Optional[List[Dict]] = None,
    tool_choice: Optional[str] = None
) -> Dict[str, str]:
    """
        Use OpenAI format to generate a text response using OpenAI.
        Supports both streaming and non-streaming responses.

        Args:
            prompt (str): The user's input prompt.
            messages (List[Dict[str, str]]): Previous conversation history.
            model (str): The model to use for generation.
            response_format (Dict[str, str]): Response format.
            tools (List[Dict]): Tools to use.
            tool_choice (str): The tool to use.

        Returns:
            dict: The generated text response.
    """
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
    message: Union[dict, ChatCompletionMessage]
) -> Dict[str, str]:
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
    user_input: str,
    tools: List[Dict[str, Callable]],
    tool_choice: Optional[str] = "auto",
    system_instructions: Optional[str] = None
) -> str:
    conversation = [
        {
            "role": "system", 
            "content": (
                "You are a ReACT agent designed to help users. "
                "You can think, act, and observe. Use the tools provided to accomplish the task."
            )
        }
    ]

    if system_instructions:
        conversation[0]["content"] += f"\n{system_instructions}"
    
    while True:
        try:
            assistant_message = chat_with_openai_model(
                prompt=user_input,
                messages=conversation,
                tools=[tool_info for tool_info, _ in tools.values()],
                tool_choice=tool_choice
            )
            formatted_message = format_message(assistant_message)
            conversation.append(formatted_message)
            
            result = _process_tool_calls(
                formatted_message, 
                conversation, 
                tools
            )
            if result:
                logger.info(f"\n\nConversation: {json.dumps(conversation, indent=2)}\n\n")
                return result
        except Exception as e:
            logger.error(f"\n\nConversation: {json.dumps(conversation, indent=2)}\n\n")
            logger.error(f"Error occurred: {e}")
            return None

def _process_tool_calls(
    assistant_message: dict,
    conversation: List[Dict[str, str]],
    tools: Dict[str, Tuple[Dict, Callable]]
) -> Optional[str]:
    if "tool_calls" in assistant_message:
        for tool_call in assistant_message["tool_calls"]:
            result = _call_tool(tool_call["function"], tools)
            try:
                if type(result) == str:
                    content = result
                else:
                    content = json.dumps(result)
            except Exception as e:
                content = f"Error: {e}"

            conversation.append(
                {
                    "role": "tool", 
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"], 
                    "content": content
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