from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def query_groq_api(messages):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    response = client.chat.completions.create(
      model="llama3-70b-8192",
      messages=messages
    )

    return response

def format_groq_query(user_and_assistant_messages: str, system_message: str=None):
    formatted_messages = []

    if system_message:
        formatted_messages.append({"role": "system", "content": system_message})

    for message in user_and_assistant_messages:
        for key, value in message.items():
            role = key
            content = value
        formatted_messages.append({
            "role": role,
            "content": content
        })

    return formatted_messages

def get_groq_response(messages, system_message=None):
    formatted_query = format_groq_query(messages, system_message)
    response = query_groq_api(formatted_query)
    return response.choices[0].message.content

from langchain import LangChain

def langchain_groq_call(messages, system_message=None):
    """
    Function to call the Groq API using the Langchain framework.
    
    Args:
    messages (list): A list of dictionaries containing user and assistant messages.
    system_message (str, optional): A system message to be included in the query. Defaults to None.
    
    Returns:
    str: The content of the response message from the Groq API.
    """
    # Initialize LangChain
    lc = LangChain()

    # Format the messages for the Groq API
    formatted_query = format_groq_query(messages, system_message)

    # Use LangChain to call the Groq API
    response = lc.call("groq", model="llama3-70b-8192", messages=formatted_query)
    
    # Extract the response content
    return response.choices[0].message.content





if __name__ == "__main__":
    messages = [
        {"assistant": "How can I help you?"},
        {"user": "Hello, can you help me understand the OpenAI API better?"}
    ]
    

    print(get_groq_response(messages, "I will always respond with yes"))

