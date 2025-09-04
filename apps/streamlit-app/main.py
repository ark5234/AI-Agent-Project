import streamlit as st
import pandas as pd
import os
import re
from dotenv import load_dotenv
from google_api import authenticate_google_sheets, read_google_sheet
from googleapiclient.discovery import build
from gemini_api import query_gemini

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("The Gemini API key is not set. Please set the `GEMINI_API_KEY` environment variable.")
    st.stop()

def main():
    st.title("AI Agent for Data-Driven Query Processing")

    input_option = st.radio("Select Data Source", ("Google Sheets URL", "Upload CSV File"))

    if input_option == "Google Sheets URL":
        handle_google_sheets()

    elif input_option == "Upload CSV File":
        handle_csv_upload()

def handle_google_sheets():
    sheet_url = st.text_input("Enter Google Sheets URL")
    if sheet_url:
        if "docs.google.com/spreadsheets" not in sheet_url:
            st.warning("Please enter a valid Google Sheets URL.")
            return

        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        sheet_name = st.text_input("Enter sheet name (e.g., Sheet1)")

        if sheet_name:
            service = authenticate_google_sheets()
            if service:
                try:
                    range_name = f"{sheet_name}!A:Z"
                    values = read_google_sheet(service, sheet_id, range_name)
                    if values:
                        headers = values[0]
                        data = pd.DataFrame(values[1:], columns=headers)
                        st.write("Data from Google Sheets:")
                        st.dataframe(data, height=600)
                        main_column_selection(data)
                    else:
                        st.error("No data found in the specified range.")
                except Exception as e:
                    st.error(f"Error reading data from Google Sheets: {e}")
            else:
                st.error("Failed to authenticate with Google Sheets.")

def handle_csv_upload():
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, encoding="utf-8")
            st.write("Data from uploaded CSV:")
            st.dataframe(data, height=600)
            main_column_selection(data)
        except UnicodeDecodeError:
            try:
                data = pd.read_csv(uploaded_file, encoding="latin1")
                st.write("Data from uploaded CSV:")
                st.dataframe(data, height=600)
                main_column_selection(data)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

def main_column_selection(data):
    if not data.empty:
        st.subheader("Step 1: Select Analysis Focus (Optional)")
        column_names = ["Auto-detect (Recommended)"] + data.columns.tolist()
        main_column = st.selectbox("Choose focus column or let AI auto-detect:", column_names)

        if main_column == "Auto-detect (Recommended)":
            st.success("✨ AI will automatically understand your queries for any column")
            main_column = data.columns[0]
        else:
            st.success(f"Selected focus column: {main_column}")
            
        st.info(f"📊 Dataset: {data.shape[0]} rows, {data.shape[1]} columns")
        with st.expander("📋 Column Overview"):
            for col in data.columns:
                unique_count = data[col].nunique()
                sample_vals = data[col].dropna().unique()[:5]
                st.write(f"**{col}**: {unique_count} unique values. Sample: {list(sample_vals)}")
        
        process_and_download(data, main_column)

def process_and_download(data, main_column):
    # Set adaptive placeholder text
    placeholder_text = f"e.g., Show records where [column] is [value], Count [category], Find [condition]"
    
    query = st.text_input(f"Enter your query (AI will understand automatically):", placeholder=placeholder_text)
    
    # Add optional debug mode
    debug_mode = st.checkbox("🔍 Debug Mode (Show AI analysis process)", value=False)
    
    if query:
        if debug_mode:
            st.expander("🔍 Dataset Info", expanded=True).write(f"""
            **Available Columns:** {list(data.columns)}
            **Dataset Shape:** {data.shape}
            **Column Types:** {dict(data.dtypes)}
            """)
        
        # Process query with fully adaptive AI
        result = process_query(data, query, main_column)
        
        if isinstance(result, pd.DataFrame):
            if not result.empty:
                # If result is a valid DataFrame, show the results
                st.write("Query result:")
                st.dataframe(result)

                csv = result.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )
                return
            # Empty DataFrame: try Gemini first for data analysis, then web search
            st.info("No matching rows found locally. Asking Gemini to analyze the data...")
            response = query_gemini_ai(query, data)
            if response:
                st.subheader("Gemini Analysis:")
                st.write(response)
                st.download_button(
                    label="Download response as TXT",
                    data=response,
                    file_name="gemini_response.txt",
                    mime="text/plain",
                )
                return
            
            # If Gemini fails, try web search as fallback
            st.info("Gemini analysis failed. Searching the web...")
            web_results = web_search(query)
            if web_results:
                st.subheader("Web Search Results:")
                for item in web_results:
                    st.write(f"**{item['title']}**: [Link]({item['link']})")
                    st.write(item['snippet'])
                return
        # If processing failed, still try fallbacks
        st.info("Couldn’t process query locally. Trying web search...")
        web_results = web_search(query)
        if web_results:
            st.subheader("Web Search Results:")
            for item in web_results:
                st.write(f"**{item['title']}**: [Link]({item['link']})")
                st.write(item['snippet'])
            return
        response = query_gemini_ai(query, data)
        if response:
            st.write("Gemini response:")
            st.write(response)
            st.download_button(
                label="Download response as TXT",
                data=response,
                file_name="gemini_response.txt",
                mime="text/plain",
            )



def process_query(data, query, main_column):
    try:
        st.info("🤖 Analyzing your query with AI...")
        
        data_context = get_data_context(data)
        ai_response = query_gemini_ai(query, data)
        
        if ai_response and "no suitable" not in ai_response.lower() and "error" not in ai_response.lower():
            structured_result = extract_structured_data(ai_response, data, query)
            
            if structured_result is not None and not structured_result.empty:
                st.write("🎯 **AI Analysis Result:**")
                st.write(ai_response)
                return structured_result
            else:
                st.write("🤖 **AI Analysis:**")
                st.write(ai_response)
                return pd.DataFrame()
        
        st.info("Trying basic pattern matching as fallback...")
        return basic_fallback_processing(data, query, main_column)
        
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return None

def get_data_context(data):
    context = {
        "columns": list(data.columns),
        "dtypes": {col: str(data[col].dtype) for col in data.columns},
        "shape": data.shape,
        "sample_values": {},
        "numeric_columns": [],
        "categorical_columns": []
    }
    
    for col in data.columns:
        unique_vals = data[col].dropna().unique()
        if len(unique_vals) <= 20:
            context["sample_values"][col] = list(unique_vals)
        else:
            context["sample_values"][col] = list(unique_vals[:10]) + ["...more values"]
        
        if pd.api.types.is_numeric_dtype(data[col]):
            context["numeric_columns"].append(col)
        else:
            context["categorical_columns"].append(col)
    
    return context

def extract_structured_data(ai_response, data, original_query):
    try:
        response_lower = ai_response.lower()
        
        if any(phrase in response_lower for phrase in ['where', 'filter', 'records', 'rows']):
            filter_query = f"""
            Based on this data analysis response: "{ai_response}"
            And the original query: "{original_query}"
            
            Generate Python pandas filtering code that would extract the relevant records.
            Only return the filtering condition(s) as Python code that can be applied to a DataFrame called 'data'.
            
            Examples:
            - data[data['column'] == 'value']
            - data[(data['col1'] > 5) & (data['col2'] == 'text')]
            - data[data['column'].str.contains('pattern', case=False)]
            
            Available columns: {list(data.columns)}
            """
            
            filter_code_response = query_gemini_simple(filter_query)
            
            if filter_code_response and "data[" in filter_code_response:
                import re
                filter_match = re.search(r'data\[(.*?)\]', filter_code_response)
                if filter_match:
                    filter_expr = filter_match.group(1)
                    try:
                        filtered_data = data.query(filter_expr) if '.' not in filter_expr else eval(f"data[{filter_expr}]")
                        return filtered_data
                    except:
                        pass
        
        return None
    except:
        return None

def basic_fallback_processing(data, query, main_column):
    try:
        query_lower = query.lower()
        
        if main_column in data.columns:
            words = query_lower.split()
            for word in words:
                if len(word) > 2:
                    matches = data[data[main_column].astype(str).str.lower().str.contains(word, na=False)]
                    if not matches.empty:
                        st.write(f"Found {len(matches)} records containing '{word}' in {main_column}")
                        return matches
        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Fallback processing error: {e}")
        return pd.DataFrame()

def query_gemini_simple(query):
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY:
            return query_gemini(query, GEMINI_API_KEY)
        return None
    except:
        return None

def web_search(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()
        
        if 'items' in res:
            search_results = []
            for item in res['items']:
                search_results.append({
                    'title': item['title'],
                    'link': item['link'],
                    'snippet': item['snippet']
                })
            return search_results
        return None
    
    except Exception as e:
        st.error(f"Error during web search: {e}")
        return None

def query_gemini_ai(query, data):
    try:
        response = query_gemini(query, GEMINI_API_KEY, data)
        return response
    except Exception as e:
        st.error(f"Error querying Gemini: {e}")
        return None

if __name__ == "__main__":
    main()
