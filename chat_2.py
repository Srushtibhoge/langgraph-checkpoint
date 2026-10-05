from typing_extensions import TypedDict
from dotenv import load_dotenv
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import os

load_dotenv()

# client = OpenAI()
client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


class State(TypedDict):
    user_query:str
    llm_output:Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):#here it will have access to current state
    response = client.chat.completions.create(
        # model="gpt-4.1-mini",
        model="gemini-3.8-flash",
        messages=[
            {"role":"user", "content": state.get("user_query")}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state

def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    if True:
        return "endnode"
    
    return "chatbot_gemini"

def chatbot_gemini(state:State):
    response = client.chat.completions.create(
        # model="gpt-4.1-mini",
        model="gemini-3.8-flash",
        messages=[
                {"role":"user", "content": state.get("user_query")}
        ]
        )
    state["llm_output"] = response.choices[0].message.content
    return state

def endnode(state:State):
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("chatbot_gemini",chatbot_gemini)
graph_builder.add_node("endnode",endnode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)
graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query":"Hey, what is 2+2?"}))
print(updated_state)