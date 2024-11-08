import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to authenticate and return a Google Sheets client
def authenticate_google_sheets():
    # Define the scope for Google Sheets and Google Drive
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    # Load credentials from the JSON file
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

# Set up the title and description of the dashboard
st.title("AI Agent Dashboard")
st.write("Upload a CSV file, define a query, and get AI-driven insights for each entity.")

# app.py

# Add a section for file upload or Google Sheets connection
st.write("## Data Input")

# Option to select either CSV or Google Sheets
data_source = st.radio("Choose data source:", ("Upload CSV", "Connect Google Sheet"))

data = None  # Initialize data variable

if data_source == "Upload CSV":
    # CSV file upload
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        # Load the uploaded file into a DataFrame
        data = pd.read_csv(uploaded_file)
        st.write("### Data Preview")
        st.dataframe(data.head())

        # Select the main column for entities
        column_option = st.selectbox("Choose the main column with entities", data.columns)
        st.write(f"Selected Column: `{column_option}`")

elif data_source == "Connect Google Sheet":
    st.write("### Google Sheets Connection")
    sheet_url = st.text_input("Enter the Google Sheet URL")

    if sheet_url:
        try:
            # Authenticate and fetch data
            client = authenticate_google_sheets()
            sheet = client.open_by_url(sheet_url)
            worksheet = sheet.get_worksheet(0)  # Load the first sheet

            # Convert worksheet to DataFrame
            data = pd.DataFrame(worksheet.get_all_records())
            st.write("### Data Preview")
            st.dataframe(data.head())

            # Select the main column for entities
            column_option = st.selectbox("Choose the main column with entities", data.columns)
            st.write(f"Selected Column: `{column_option}`")

        except Exception as e:
            st.error("Could not connect to the Google Sheet. Please check the URL and permissions.")
            st.write(e)

# Step 2: Add a Prompt Input Section
st.write("### Define Your Query")
prompt_template = st.text_input("Enter your prompt (e.g., 'Get the email address of {company}')")

# Display the selected prompt for clarity
if prompt_template:
    st.write(f"Your query template: `{prompt_template}`")

# Check if both data and prompt are available before fetching
if data is not None and prompt_template:
    if st.button("Fetch Information"):
        st.write("Processing your request...")  # Placeholder for actual functionality

# Placeholder section for displaying results (future step)
st.write("### Results")
st.write("Results will appear here after fetching and processing data.")
