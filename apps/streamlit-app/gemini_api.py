import google.generativeai as genai
import pandas as pd

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def query_gemini(query, api_key, data=None):
    try:
        configure_gemini(api_key)
        
        model_names = [
            'gemini-1.5-flash',
            'gemini-1.5-pro', 
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro'
        ]
        
        model = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception:
                continue
        
        if model is None:
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if available_models:
                    model = genai.GenerativeModel(available_models[0])
                else:
                    return "Error: No suitable Gemini models available for content generation."
            except Exception as e:
                return f"Error: Could not access Gemini models. {str(e)}"
        
        if data is not None:
            data_analysis = analyze_dataset_automatically(data)
            
            prompt = f"""You are an expert data analyst with advanced natural language understanding. 
Your task is to understand user queries about any dataset and provide accurate, actionable responses.

DATASET ANALYSIS:
{data_analysis}

USER QUERY: "{query}"

INSTRUCTIONS:
1. Analyze the user's query to understand their intent (filtering, counting, analysis, etc.)
2. Automatically map the query terms to the most relevant columns in the dataset
3. Handle variations in terminology (e.g., "credit policy" could mean a binary approval column)
4. For filtering queries, identify the exact records that match the criteria
5. For counting queries, provide the exact count
6. For analysis queries, provide insights based on the data

IMPORTANT: 
- Do not assume column names - work with what's available in the dataset
- Be flexible with value matching (handle case sensitivity, partial matches)
- If the query asks to "show" or "display" records, specify exactly which rows match
- Provide both the answer AND the reasoning behind it
- If filtering is needed, describe the exact conditions applied

RESPONSE FORMAT:
- Start with a clear answer to the user's question
- Explain your analysis process
- If applicable, mention the number of matching records
- Be specific about which columns and values you used"""
        else:
            prompt = f"""You are a helpful AI assistant. Please respond to this query: {query}"""
        
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "No response generated from Gemini."
            
    except Exception as e:
        return f"Error querying Gemini: {str(e)}"

def analyze_dataset_automatically(data):
    analysis = []
    
    analysis.append(f"Dataset Shape: {data.shape[0]} rows, {data.shape[1]} columns")
    analysis.append(f"Column Names: {', '.join(data.columns)}")
    
    analysis.append("\nCOLUMN DETAILS:")
    for col in data.columns:
        col_info = []
        
        dtype = str(data[col].dtype)
        col_info.append(f"Type: {dtype}")
        
        unique_vals = data[col].dropna().unique()
        unique_count = len(unique_vals)
        col_info.append(f"Unique values: {unique_count}")
        
        if unique_count <= 10:
            col_info.append(f"Values: {list(unique_vals)}")
        elif unique_count <= 50:
            col_info.append(f"Sample values: {list(unique_vals[:10])}...")
        else:
            if pd.api.types.is_numeric_dtype(data[col]):
                col_info.append(f"Range: {data[col].min()} to {data[col].max()}")
            else:
                col_info.append(f"Sample values: {list(unique_vals[:5])}...")
        
        null_count = data[col].isnull().sum()
        if null_count > 0:
            col_info.append(f"Missing: {null_count}")
        
        analysis.append(f"- {col}: {', '.join(col_info)}")
    
    analysis.append(f"\nSAMPLE DATA (first 3 rows):")
    sample_data = data.head(3).to_string()
    analysis.append(sample_data)
    
    return "\n".join(analysis)