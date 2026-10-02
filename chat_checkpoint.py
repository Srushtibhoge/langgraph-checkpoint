from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver
from dotenv import load_dotenv

load_dotenv()
# llm = init_chat_model(
#     model = "gpt-4.1-mini",
#     model_provider="openai" 
# )

llm = init_chat_model(
    model="gemini-3.8-flash",
    model_provider="google_genai"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
def chatbot(state: State):#here it will have access to current state
    response = llm.invoke(state.get("messages"))
    return { "messages" : [response] }

graph_builder = StateGraph(State)

#to tell graph builder as this is a node, it will register this as node
graph_builder.add_node("chatbot",chatbot)

#START -> chatbot -> samplenode -> (END)
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot", END)

# graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

DB_URI = "mongodb://localhost:27017/langraph"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)
    
    config = {
        "configurable": {
            "thread_id":"srushti" #user_id give always user id here so that it will be specific to particular user
        }
    }
    
    # updated_state = graph_with_checkpointer.invoke(
    #     State({"mesaages": ["Hi, my name is Srushti bhoge"]}),
    #     config,    
    #     )
    # print('\n\nupdated_state',updated_state)
    
    for chunk in graph_with_checkpointer.stream(
            State({"messages": ["what is my name?"]}),
            config,
            stream_mode="values"  
            ):
        chunk["messages"][-1].pretty_print()

#state= {messages: ["Hey there"]} #when we pass initial state as messagess as hey there
# state = {"mesages": ["Hey there", "Hi, This is a message from ChatBot Node"]}
