import streamlit as st
import pandas as pd
import os
import re
from io import StringIO
from google_api import authenticate_google_sheets, read_google_sheet
from openai import OpenAI

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

    # Add a radio button to choose between Google Sheets URL or CSV upload
    input_option = st.radio("Select Data Source", ("Google Sheets URL", "Upload CSV File"))

    if input_option == "Google Sheets URL":
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
                            process_and_download(data)
                        else:
                            st.error("No data found in the specified range.")
                    except Exception as e:
                        st.error(f"Error reading data from Google Sheets: {e}")
                else:
                    st.error("Failed to authenticate with Google Sheets.")

    elif input_option == "Upload CSV File":
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file is not None:
            try:
                data = pd.read_csv(uploaded_file, encoding="utf-8")
                st.write("Data from uploaded CSV:")
                st.dataframe(data, height=600)
                process_and_download(data)
            except UnicodeDecodeError:
                try:
                    data = pd.read_csv(uploaded_file, encoding="latin1")
                    st.write("Data from uploaded CSV:")
                    st.dataframe(data, height=600)
                    process_and_download(data)
                except Exception as e:
                    st.error(f"Error reading CSV file: {e}")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

def process_and_download(data):
    query = st.text_input("Enter your query (e.g., Show all companies with rating greater than 4)")
    if query:
        result = process_query(data, query)
        if isinstance(result, pd.DataFrame) and not result.empty:
            st.write("Query result:")
            st.dataframe(result)

            # Provide download option for DataFrame
            csv = result.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv",
            )
        elif result is None:
            st.warning("No valid result found. Please check your query or data.")
        else:
            response = query_grok(query, data)
            if response:
                st.write("Grok response:")
                st.write(response)

                # Provide download option for text response
                st.download_button(
                    label="Download response as TXT",
                    data=response,
                    file_name="grok_response.txt",
                    mime="text/plain",
                )

def process_query(df, query):
    query = query.lower()

    # Match query with available column names dynamically
    for column in df.columns:
        if column.lower() in query:
            match = re.search(rf'{column.lower()} greater than (\d+(\.\d+)?)', query)
            if match:
                threshold = float(match.group(1))
                try:
                    result = df[df[column].astype(float) > threshold]
                    return result
                except ValueError:
                    st.warning(f"The column '{column}' contains non-numeric values and cannot be compared numerically.")
                    return None

    st.warning(f"No matching column found for the query. Available columns: {', '.join(df.columns)}. Please rephrase your query.")
    return query_grok(query, df)

def query_grok(query, data):
    data_subset = data.head(50)  # Limit to first 50 rows
    data_dict = data_subset.to_dict(orient="records")
    
    try:
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are Grok, an intelligent assistant that can analyze data."},
                {"role": "user", "content": f"The following data is from a CSV file:\n{data_dict}\n\n{query}"},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error querying Grok: {e}")
        return None

if __name__ == "__main__":
    main()
