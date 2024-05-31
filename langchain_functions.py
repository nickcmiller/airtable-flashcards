from groq import Groq
import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq

load_dotenv()

def groq_chain_with_response(human_input, chat_history=[]):
    chat = ChatGroq(temperature=0.0, model="llama3-70b-8192")
    
    system = AIMessage(content="You are an excited and extremely upbeat assistant. You respond to everything with great enthusiasm and energy.")
    human = HumanMessage(content=human_input)
    prompt = ChatPromptTemplate.from_messages([
        system, 
        MessagesPlaceholder(variable_name="chat_history"),
        human
    ])
    print(f"\n\nprompt: {prompt}\n\n")
    chain = prompt | chat
    return chain.invoke({
        "input": human_input,
        "chat_history": chat_history
    })

if __name__ == "__main__":
    prompt = "What is a Maine Coon? What color should it be?"
    # chat_history = [HumanMessage(content="Always bring up the color blue, especially in the context of a cat.")]
    print(get_groq_response_with_prompt(prompt))