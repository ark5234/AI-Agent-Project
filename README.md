# AI Agent for Data-Driven Query Processing

This project is a versatile AI-powered dashboard designed for efficient information retrieval from CSV files and Google Sheets. It combines web search capabilities with AI-driven query processing to extract specific information based on user-defined prompts.

Project Description
The AI Agent for Data-Driven Query Processing empowers users to:

Upload a CSV file or connect to a Google Sheet for data processing.
Dynamically query data using customizable placeholders.
Perform automated web searches to fetch missing information.
Leverage Grok (xAI) for natural language query processing and parsing.
Export results in a user-friendly format, such as CSV or directly update Google Sheets.

Features
CSV/Google Sheets Integration: Seamless data upload and preview.
Dynamic Querying: Use placeholders to tailor queries for your data.
Automated Web Search: Fetch relevant data using Google Custom Search API.
LLM Integration: Enhance results with AI-based processing.
Export Options: Download extracted results or update Google Sheets.

Repository Structure
```
├── main.py                # Main application file
├── google_api.py          # Google Sheets API utilities
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .env                   # (optional) Store API keys and environment variables
└── static/                # Static assets (if any)
```


Setup Instructions

1️⃣ Clone the Repository
```
git clone https://github.com/ark5234/AI-Agent-Project.git
cd AI-Agent-Project
```
2️⃣ Install Dependencies
Ensure you have Python 3.8+ installed. Then, install the required libraries:
```
pip install -r requirements.txt
```
3️⃣ Set Up API Keys
Create a .env file in the project directory and add the following keys:
```
GROK_API_KEY=<Your_Grok_API_Key>
GOOGLE_API_KEY=<Your_Google_API_Key>
SEARCH_ENGINE_ID=<Your_Custom_Search_Engine_ID>
```
Alternatively, export these variables in your terminal:
```
export GROK_API_KEY=<Your_Grok_API_Key>
export GOOGLE_API_KEY=<Your_Google_API_Key>
export SEARCH_ENGINE_ID=<Your_Custom_Search_Engine_ID>
```
4️⃣ Run the Application
Start the Streamlit dashboard:
```
streamlit run main.py
Access the application in your browser at http://localhost:8501.
```



Usage Guide

Step 1: Data Input
Upload CSV: Use the Upload CSV File option to browse and upload your data.
Google Sheets: Enter the Google Sheets URL and the desired sheet name to fetch data.

Step 2: Select Main Column
After uploading or fetching data, choose the column you want to process (e.g., company names).

Step 3: Define Queries
Input your query using placeholders like {entity}, which will dynamically reference rows in your selected column.
Example:
Get the contact email for {entity}

Step 4: Retrieve Results
If data exists locally, it will filter and display relevant rows.
If missing, it will perform a web search and query Grok for advanced AI-driven processing.

Step 5: Export Data
Download the results as a CSV.
Update Google Sheets directly.




APIs and Tools Used

1️⃣ Grok (xAI)
For AI-based natural language query processing.
Integrated via openai Python library with the grok-beta model.

2️⃣ Google Sheets API
For reading and updating Google Sheets.
Integrated using googleapiclient library.

3️⃣ Google Custom Search API
For automated web searches to fetch missing data.



Environment Variables
```
Variable Name	Purpose
GROK_API_KEY	API key for Grok (xAI).
GOOGLE_API_KEY	API key for Google APIs.
SEARCH_ENGINE_ID	Custom Search Engine ID for CSE.
```
Ensure all environment variables are set before running the application.



Contributors
```
Vikrant Kawadkar (@ark5234)
```
Feel free to raise an issue or submit a pull request for contributions!




Contact
If you have any questions, feedback, or suggestions, feel free to reach out:
```
Author: Vikrant Kawadkar
Email: vikrantkawadkar2099@gmail.com
```



License
This project is licensed under the MIT License.
