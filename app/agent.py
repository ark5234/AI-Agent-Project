from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
import streamlit as st
from grok_api import grok_tool

# Initialize LangChain with your Grok API Key
def create_grok_agent(grok_api_key):
    grok_query_tool = grok_tool(grok_api_key)
    
    # Create an agent that uses the Grok query tool
    tools = [grok_query_tool]
    agent = initialize_agent(tools, AgentType.ZERO_SHOT_REACT_DESCRIPTION, llm=None)
    
    return agent

# Run the agent and get a response
def run_agent(query, grok_api_key):
    agent = create_grok_agent(grok_api_key)
    response = agent.run(query)
    return response
