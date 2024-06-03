
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

def groq_chain_with_chat_history(human_input, chat_history=[]):
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
        
def groq_query_agent(human_input, memory):
    llm = ChatGroq(temperature=0.0, model="llama3-70b-8192")

    # Define your tools
    def search_tool(query: str) -> str:
        # Implement your search logic here
        result = "Maine Coon cats are blue"
        return result
    search_tool_obj = Tool(
        name="Search",
        func=search_tool,
        description="Tells you the color of a Maine Coon cat"
    )

    tools = [search_tool_obj]

    # Define the prompt
    prompt = '''
        Answer the following questions as best you can. You have access to the following tools: {tools}.
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, it will usually be one of [{tool_names}] but not always
        Action Input: the input to the action
        Observation: your memory is in {chat_history}
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        Begin!
        Question: {input}
        Thought:{agent_scratchpad}
    '''
    prompt_template = PromptTemplate.from_template(prompt)

    # Create the ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt_template,
    )

    # Initialize the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

    result = agent_executor.invoke({
        "input": human_input
    })

    return result

if __name__ == "__main__":
    prompt = "What color is a Maine Coon?"
    chat_history = [
        AIMessage(content="How should I behave around you?"),
        HumanMessage(content="Always thank me for my question."),
        AIMessage(content="I will do that. Thank you :)")
    ]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Add the initial chat history to the memory
    for message in chat_history:
        if isinstance(message, HumanMessage):
            memory.chat_memory.add_user_message(message.content)
        elif isinstance(message, AIMessage):
            memory.chat_memory.add_ai_message(message.content)

    groq_query_agent(prompt, memory)
    result = groq_query_agent("Did you thank me?", memory)
    print(f"result: {result}\n\n")
    print(f"memory:\n\n{memory.chat_memory}\n\n")