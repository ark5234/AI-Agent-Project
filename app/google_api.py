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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Please make sure the 'credentials.json' file is in the correct path.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
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
