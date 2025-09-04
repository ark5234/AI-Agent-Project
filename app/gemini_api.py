import google.generativeai as genai
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import GoogleGenerativeAI

def configure_gemini(api_key):
    """Configure Google Gemini API with the provided API key."""
    genai.configure(api_key=api_key)

def query_gemini(query, api_key, data=None):
    """Query Google Gemini API and return a response."""
    try:
        configure_gemini(api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt
        if data:
            # If data is provided, include it in the context
            prompt = f"""You are an intelligent AI assistant that can analyze data.

Data from CSV file:
{data}

User Query: {query}

Please provide a helpful response based on the data and query."""
        else:
            prompt = f"User Query: {query}"
        
        # Generate response
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "No response generated from Gemini."
            
    except Exception as e:
        return f"Error querying Gemini: {str(e)}"

def gemini_tool(api_key):
    """Create a LangChain tool for Gemini API."""
    return Tool(
        name="Gemini API",
        func=lambda query: query_gemini(query, api_key),
        description="Query Google Gemini for intelligent responses and data analysis"
    )

def create_gemini_llm(api_key):
    """Create a LangChain LLM wrapper for Gemini."""
    configure_gemini(api_key)
    return GoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.7
    ) 