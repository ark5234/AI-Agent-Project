from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
import streamlit as st
from gemini_api import gemini_tool, create_gemini_llm

# Initialize LangChain with your Gemini API Key
def create_gemini_agent(gemini_api_key):
    gemini_query_tool = gemini_tool(gemini_api_key)
    gemini_llm = create_gemini_llm(gemini_api_key)
    
    # Create an agent that uses the Gemini query tool
    tools = [gemini_query_tool]
    agent = initialize_agent(tools, gemini_llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    return agent

# Run the agent and get a response
def run_agent(query, gemini_api_key):
    agent = create_gemini_agent(gemini_api_key)
    response = agent.run(query)
    return response
