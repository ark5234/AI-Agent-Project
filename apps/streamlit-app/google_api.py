import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

# If modifying or querying data, you may want to specify the following scope.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Authenticate and build the Google Sheets service
def authenticate_google_sheets():
    """Authenticate the Google Sheets API."""
    creds = None
    # The token.pickle file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    # Support token in app folder or project root
    token_paths = [
        os.path.join(os.path.dirname(__file__), 'token.pickle'),
        os.path.join(os.getcwd(), 'token.pickle'),
    ]
    token_path = next((p for p in token_paths if os.path.exists(p)), None)
    if token_path:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Support credentials in app folder or project root
            cred_paths = [
                os.path.join(os.path.dirname(__file__), 'credentials.json'),
                os.path.join(os.getcwd(), 'credentials.json'),
            ]
            cred_path = next((p for p in cred_paths if os.path.exists(p)), None)
            if not cred_path:
                print("Please add 'credentials.json' to the project root or app folder.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        # Prefer saving alongside credentials.json
        save_token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')
        with open(save_token_path, 'wb') as token:
            pickle.dump(creds, token)

    try:
        # Build the Sheets API service
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def read_google_sheet(service, spreadsheet_id, range_name):
    """Read data from Google Sheets."""
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            return values
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None
