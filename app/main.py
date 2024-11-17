import streamlit as st
import pandas as pd
import os
from google_api import authenticate_google_sheets, read_google_sheet
from googleapiclient.discovery import build
from openai import OpenAI

# Set up your Google CSE API key and search engine ID
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Initialize Grok (xAI) client
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    st.error("The Grok API key is not set. Please set the `GROK_API_KEY` environment variable.")
    st.stop()

client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"  # xAI API base URL
)

def main():
    st.title("AI Agent for Data-Driven Query Processing")

    input_option = st.radio("Select Data Source", ("Google Sheets URL", "Upload CSV File"))

    if input_option == "Google Sheets URL":
        handle_google_sheets()

    elif input_option == "Upload CSV File":
        handle_csv_upload()

def handle_google_sheets():
    """Handles Google Sheets URL input, authentication, and data retrieval."""
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
    """Handles CSV file upload, reading, and data display."""
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
    """Prompts the user to select the main column for query processing."""
    if not data.empty:
        st.subheader("Step 1: Select Main Column")
        column_names = data.columns.tolist()
        main_column = st.selectbox("Choose the main column for analysis:", column_names)

        if main_column:
            st.success(f"Selected main column: {main_column}")
            process_and_download(data, main_column)

def process_and_download(data, main_column):
    # Set the placeholder text based on the main column
    placeholder_text = f"e.g., Show all companies in the {main_column} industry"
    
    query = st.text_input(f"Enter your query using the main column '{main_column}':", placeholder=placeholder_text)
    
    if query:
        # Process query on the data
        result = process_query(data, query, main_column)
        
        if isinstance(result, pd.DataFrame) and not result.empty:
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
        elif result is None:
            # If no data found, perform a web search
            st.write("No matching data found. Searching the web for more information...")
            web_results = web_search(query)
            
            if web_results:
                st.subheader("Web Search Results:")
                for result in web_results:
                    st.write(f"**{result['title']}**: [Link]({result['link']})")
                    st.write(result['snippet'])
            else:
                st.write("No relevant web search results found.")
        else:
            # If Grok's response is triggered
            response = query_grok(query, data)
            if response:
                st.write("Grok response:")
                st.write(response)
                st.download_button(
                    label="Download response as TXT",
                    data=response,
                    file_name="grok_response.txt",
                    mime="text/plain",
                )



def process_query(data, query, main_column):
    """Filters data based on the query and the main column."""
    try:
        # Example of filtering data based on the query (adjust logic as needed)
        filtered_data = data[data[main_column].str.contains(query, case=False, na=False)]
        return filtered_data
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return None

def web_search(query):
    try:
        # Initialize Google Custom Search API
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        # Perform the web search with the user's query
        res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()
        
        # Check if we have search results
        if 'items' in res:
            search_results = []
            for item in res['items']:
                search_results.append({
                    'title': item['title'],
                    'link': item['link'],
                    'snippet': item['snippet']
                })
            return search_results
        
        # If no results, return None
        return None
    
    except Exception as e:
        st.error(f"Error during web search: {e}")
        return None


def query_grok(query, data):
    """Queries Grok (xAI) for processing and returns a response."""
    data_subset = data.head(50)  # Limit data to first 50 rows for efficiency
    data_dict = data_subset.to_dict(orient="records")
    
    try:
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{
                "role": "system", 
                "content": "You are Grok, an intelligent assistant that can analyze data."
            }, {
                "role": "user", 
                "content": f"The following data is from a CSV file:\n{data_dict}\n\n{query}"
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error querying Grok: {e}")
        return None

if __name__ == "__main__":
    main()
