import streamlit as st
from google_api import fetch_google_sheet_data
from data_processing import process_data_from_csv
from grok_api import query_grok

# Set up the main function
def main():
    st.title("AI Agent for Data-Driven Query Processing")

    # User option for uploading a CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    # User option for providing a Google Sheets URL
    google_sheets_url = st.text_input("Or, enter Google Sheets URL")

    # Process based on user input
    if uploaded_file is not None:
        # Process CSV file
        csv_data = process_data_from_csv(uploaded_file)
        st.write("CSV Data:", csv_data)
    elif google_sheets_url:
        # Extract the Google Sheet ID from the URL
        sheet_id = google_sheets_url.split("/d/")[1].split("/")[0]
        sheet_name = st.text_input("Enter the sheet name (e.g., Sheet1)")

        if sheet_name:
            # Fetch data from Google Sheets
            try:
                google_api_key = st.secrets["GOOGLE_API_KEY"]  # Use the API key stored in the secrets
                sheet_data = fetch_google_sheet_data(sheet_id, sheet_name, google_api_key)
                st.write("Google Sheets Data:", sheet_data)
            except Exception as e:
                st.error(f"Failed to retrieve data from Google Sheets: {e}")
        else:
            st.warning("Please enter the sheet name.")
    
    # Additional processing if data is available
    if uploaded_file or google_sheets_url:
        query = st.text_input("Enter your query for Grok")
        if query:
            grok_api_key = st.secrets["GROK_API_KEY"]
            response = query_grok(query, grok_api_key)
            st.write("Grok Response:", response)

# Run the main function
if __name__ == "__main__":
    main()
