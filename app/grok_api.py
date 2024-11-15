import requests
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import OpenAI

# Function to call Grok API
def query_grok(query, grok_api_key):
    url = "https://api.xai.com/v1/engines/grok-beta/completions"  # Replace with the actual endpoint
    headers = {"Authorization": f"Bearer {grok_api_key}"}
    data = {
        "prompt": query,
        "max_tokens": 150  # You can adjust this as needed
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('text', 'No response from Grok.')
    else:
        return f"Error: {response.status_code}, {response.text}"

# Define a LangChain tool to query Grok
def grok_tool(grok_api_key):
    return Tool(
        name="Grok API",
        func=lambda query: query_grok(query, grok_api_key),
        description="Query Grok for a response"
    )
