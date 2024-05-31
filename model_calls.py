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

