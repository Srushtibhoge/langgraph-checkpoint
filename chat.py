from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()
# llm = init_chat_model(
#     model = "gpt-4o",
#     model_provider="openai" 
# )

llm = init_chat_model(
    model="gemini-3.8-flash",
    model_provider="google_genai"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
def chatbot(state: State):#here it will have access to current state
    print("\n\nInside chatbot node", state)
    response = llm.invoke(state.get("messages"))
    # return { "message" : ["Hi, This is a message from ChatBot Node"] }
    return { "messages" : [response] }

def samplenode(state:State):
    print("\n\nInside samplenode node", state)
    return { "messages" : ["Sample message appended"]}

graph_builder = StateGraph(State)

#to tell graph builder as this is a node, it will register this as node
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("samplenode",samplenode)

#START -> chatbot -> samplenode -> (END)
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"messages": ["Hi, my name is Srushti Bhoge"]}))
print('\n\nupdated_state',updated_state)

#state= {messages: ["Hey there"]} #when we pass initial state as messagess as hey there
# when we do graph invocation, then this node runs , this node returns list then after invcation new state will be
# node runs: chatbot(state: ["Hey There"]) -> ["Hi, This is a message from ChatBot Node"]
# state = {"mesages": ["Hey there", "Hi, This is a message from ChatBot Node"]}
