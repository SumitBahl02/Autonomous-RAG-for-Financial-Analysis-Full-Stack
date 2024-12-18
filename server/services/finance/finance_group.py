from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
# from typing import TypedDict, Annotated
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
import json
from langchain_core.messages import (
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"


# ================================= HELPER FUNCTIONS =================================
# Load the JSON file
def load_personas(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

# Access the persona data for a specific category
def get_personas_for_category(data, category):
    if category in data:
        supervisor = data[category]["supervisor_persona"]
        agent_1 = data[category]["agent_1_persona"]
        agent_2 = data[category]["agent_2_persona"]
        return {
            "supervisor": supervisor,
            "agent_1": agent_1,
            "agent_2": agent_2
        }
    else:
        raise ValueError(f"Category '{category}' not found in the data.")


json_file = r"/home/nakul/Pathway/server/services/finance/personas.json"
personas_data = load_personas(json_file)

# ================================= MAIN CODE =================================

llm_mini = ChatOpenAI(model="gpt-4o-mini")

llm = ChatOpenAI(model="gpt-4o-mini")
class AgentReply(BaseModel):
    """A response from an agent."""
    content: str = Field(description="The content of the response.")
    fallback: str = Field(description="A fallback flag when the conversation ends. Can be only YES or NO")
    
class SupervisorReply(BaseModel):
    """A response from the supervisor agent."""
    content: str = Field(description="The content of the response.")
    return_summary: str = Field(description="A flag to end the conversation and return the summary. Can be only YES or NO")

structured_llm_mini = llm_mini.with_structured_output(AgentReply)

structured_llm = llm.with_structured_output(SupervisorReply)

# Here we are developing a group of agents with variable personas that will discuss financial topics, among two agents and return the conversation to their supervisor agent which will analyze the conversation and provide a summary of the conversation with additional insights if required.

class State(TypedDict):
    """A state object to keep track of the conversation."""

    topic: str = Field(description="The topic of the conversation with additional context.")
    context: str = Field(description="Additional context or data that needs to be passed to the agents for conversation.")
    conversation: Annotated[list, add_messages]
    supervisor_: str = Field(description="The persona of the supervisor agent.")
    agent1: str = Field(description="The persona of agent 1.")
    agent2: str = Field(description="The persona of agent 2.")
    summary: str = Field(description="A summary of the conversation.")
    fallback: str = Field(description="A fallback message when the conversation ends. Can be only YES or NO")
    return_summary: str = Field(description="A return summary message when the summary is generated. Can be only YES or NO")
    count: int = Field(description="The count of the conversation messages.")


def agent_node_1(state: State) -> State:
    """A node that represents an agent in the conversation."""
    prompt = ChatPromptTemplate.from_messages(
        [   
            ("system", state["agent1"] + "You can set the fallback to YES or NO based on wether you need to return the conversation to the supervisor or not. YES to return to supervisor, NO to continue the conversation.  Set the fallback to YES if the conversation is becoming too long and you need the supervisor to summarize the conversation."),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    # messages = state['conversation']
    # agent_1_llm = prompt | llm_mini 
    agent_1 = prompt | structured_llm_mini
    if state["count"] == 0:
        messages = [HumanMessage(f"Your task is to simulate an agent in a financial conversation. You need to play your part in a conversation on the topic: \n{state['topic']}  and additional context: \n{state['context']}. \nInitiate the conversation as the given persona.")]
        # state["conversation"].append(messages[0] +  and additional context: \n{state['context']})
        response = agent_1.invoke({"messages": messages})
        # state["conversation"].append(response.content)
        state["count"] += 1
        # fallback = 'YES' if 'YES' in response.content else 'NO' #instruct llm for YES or NO
        state["fallback"] = response.fallback
        print(f"Agent 1: {response.fallback}")
        state["conversation"].append(response.content)
    else:
        state["conversation"][-1] = HumanMessage(content = state["conversation"][-1].content)
        response = agent_1.invoke({"messages": state["conversation"]})
        # state["conversation"].append(response.content)
        state["count"] += 1
        # fallback = 'YES' if 'YES' in response.content else 'NO' #instruct llm for YES or NO
        state["fallback"] = response.fallback
        print(f"Agent 1: {response.fallback}")
        state["conversation"].append(response.content)
    return state


def agent_node_2(state: State) -> State:
    """A node that represents an agent in the conversation."""
    prompt = ChatPromptTemplate.from_messages(
        [   
            ("system", state["agent2"]  + "You can set the fallback to YES or NO based on wether you need to return the conversation to the supervisor or not. YES to return to supervisor, NO to continue the conversation. Set the fallback to YES if the conversation is becoming too long and you need the supervisor to summarize the conversation."),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    messages = state['conversation']
    agent_2 = prompt | structured_llm_mini
    print(state)
    response = agent_2.invoke({"messages": state["conversation"]})
    # state["conversation"].append(response.content)
    state["count"] += 1
    # fallback = 'YES' if 'YES' in response.content else 'NO' #instruct llm for YES or NO
    state["fallback"] = response.fallback
    print(f"Agent 2: {response.fallback}")
    state["conversation"].append(response.content)
    return state

# def passthrough_node_1(state: State) -> State:
#     """A node that passes the state through without any changes."""
#     if state["fallback"] == "YES":
#         return state

# def passthrough_node_2(state: State) -> State:
#     """A node that passes the state through without any changes."""
#     if state["fallback"] == "YES":
#         return state


def supervisor_node(state: State) -> State:
    """A node that represents the supervisor agent in the conversation."""
    messages = state['conversation']
    print('Supervisor Analyst Node\n')
    if state["count"] == 0:
        return state
    else:
        prompt = ChatPromptTemplate.from_messages(
            [   
                ("system", state["supervisor_"] + " Summarize the given conversation between two agents, include all the details and insights from the conversation in the summary."  + "You can set the return_summary to YES or NO based on wether you need to return the summar to the user or not. YES to return to user, NO to continue the conversation.  Set the fallback to YES if the conversation is becoming too long and you need the supervisor to summarize the conversation."),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        supervisor_llm = prompt | structured_llm 
        # state["conversation"][-1] = HumanMessage(content = state["conversation"][-1].content)
        response = supervisor_llm.invoke({"messages": messages})
        # state["conversation"].append(response.content)
        state["summary"] = response.content
        state["count"] += 1
        # return_summary = 'YES' if 'YES' in response.content else 'NO'
        state["return_summary"] = response.return_summary
        print(f"Supervisor: {response.return_summary}")
        state["conversation"].append(response.content)
        return state

#==================================== GRAPH ====================================
graph = StateGraph(State)
graph.add_node("agent_1",agent_node_1)
# graph.add_node("passthrough_1",passthrough_node_1)
# graph.add_node("passthrough_2",passthrough_node_2)
graph.add_node("agent_2",agent_node_2)
graph.add_node("supervisor",supervisor_node)
graph.add_edge(START, "supervisor")
# graph.add_edge("supervisor", "agent_1")
# graph.add_edge("agent_1", "passthrough_1")
# graph.add_edge(passthrough_node_1, agent_node_2)
# graph.add_edge("agent_2", "passthrough_2")
# graph.add_edge(passthrough_node_2, agent_node_1)
def return_1(state):
    fallback = state["fallback"]
    if fallback == "YES" or state["count"] > 40:
        print('Returning Supervisor\n')
        return "supervisor"
    else:
        print('Returning Agent 2\n')
        return "agent_2"

def return_2(state):
    fallback = state["fallback"]
    if fallback == "YES" or state['count'] > 40:
        print("Returning Supervisor\n")
        return "supervisor"
    else:
        print('Returning Agent 1\n')
        return "agent_1"

graph.add_conditional_edges(
    "agent_1",
    return_1,
)
graph.add_conditional_edges(
    "agent_2",
    return_2,
)


def returnsummary(state):
    return_ = state["return_summary"]
    if return_ == "YES":
        print('Returning Summary\n')
        return END
    else:
        print('Returning Agent 1\n')
        return "agent_1"

graph.add_conditional_edges(
    "supervisor",
    returnsummary,
)

app = graph.compile()


#==================================== MAIN FUNCTION ====================================

def finance_group(category,context,topic) -> str:
    """A function that imitates conversation between two agents and a supervisor agent on a financial topic.

    Args:
        category (str): The category of the financial topic, possible categories: Market Sentiment Analysts, Risk Assessment Analysts, Fundamental Analysts 
        context (str): Additional context or data that needs to be passed to the agents for conversation.
        topic (str): The financial topic for the conversation.
    Returns:
        str: A summary of the conversation along with additional insights.
    """

    # Initialize the state object
    # Category to fetch personas for
    try:
        personas = get_personas_for_category(personas_data, category)
        print(f"Supervisor Persona: {personas['supervisor']}\n")
        print(f"Agent 1 Persona: {personas['agent_1']}\n")
        print(f"Agent 2 Persona: {personas['agent_2']}\n")
    except ValueError as e:
        print(e)
    state = State(
        topic=topic,
        context = context,
        supervisor_=personas['supervisor'],
        agent1=personas['agent_1'],
        agent2=personas['agent_2'],
        conversation=[],
        summary="",
        count = 0,
        return_summary = "NO",
        # messages = [],
    )
    # Start the conversation
    print('Starting the conversation...')
    result =  app.invoke(state)
    print('Conversation ended.')
    return result["summary"]

class FinanceGroupInput(BaseModel):
    category: str = Field(description="The category of the financial topic, possible categories: Market Sentiment Analysts, Risk Assessment Analysts, Fundamental Analysts.")
    context: str = Field(description="ADditional context or data that needs to be passed to the agents for conversation.")
    topic: str = Field(description="The topic of the conversation with additional context.")

finance_group_tool = StructuredTool.from_function(
    finance_group,
    name="finance_group",
    description='''finance_group(category: str, context: str, topic: str) -> str:
    Use this tool to gain insights on financial topics from multiple perspectives, useful for good decision making in financial domain.
    ALWAYS USE THIS TOOL WHENEVER THE QUERY INVOLVES FINANCIAL TOPICS.
    This simulates a conversation between two agents and a supervisor agent on a financial topic.
    The agents will discuss the topic based on the given context and provide a summary of the conversation.
    The supervisor agent will analyze the conversation and provide additional insights if required.
    Try to provide a detailed topic and context for a more insightful conversation.
    Example usage:
    finance_group("Market Sentiment Analysts", "context", "Apple just released iphone 15 with new features but people are not happy. Discuss the market sentiment and the impact on the stock price."),"
    category: The category of the financial topic, possible categories: Market Sentiment Analysts, Risk Assessment Analysts, Fundamental Analysts
    context: Additional context or data that needs to be passed to the agents for conversation.
    ALWAYS USE THIS TOOL WHENEVER THE QUERY INVOLVES FINANCIAL TOPICS.
    ''',
    args_schema=FinanceGroupInput,
    )


#==================================== EXAMPLE USAGE ====================================
if __name__ == "__main__":
    print('==========================')
    print(finance_group_tool.run({"category":"Market Sentiment Analysts", "context" : "Apple just released iphone 15 with new features but people are not happy. Discuss the market sentiment and the impact on the stock price.", "topic":"Qualitative analysis of Apple's new product release"}))

