import requests
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import OpenAI

# Function to call Grok API
def query_grok(query, grok_api_key):
    """Query Grok API using the correct endpoint."""
    url = "https://api.x.ai/v1/chat/completions"  # Updated endpoint
    headers = {
        "Authorization": f"Bearer {grok_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-beta",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 150
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', 'No response from Grok.')
    else:
        return f"Error: {response.status_code}, {response.text}"

# Define a LangChain tool to query Grok
def grok_tool(grok_api_key):
    return Tool(
        name="Grok API",
        func=lambda query: query_grok(query, grok_api_key),
        description="Query Grok for a response"
    )
