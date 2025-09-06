import os
from typing import Optional, List, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests library not available")
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    print("Warning: Google API client libraries not available")
    GOOGLE_API_AVAILABLE = False
    # Create dummy functions to prevent import errors
    def build(*args, **kwargs):
        return None

def authenticate_google_sheets() -> Optional[Any]:
    """
    Authenticate with Google Sheets using API key instead of OAuth2.
    This is simpler and works better for public sheets.
    """
    if not GOOGLE_API_AVAILABLE:
        print("Google API client libraries not available")
        return None
        
    try:
        # Get API key from environment or Streamlit secrets
        import streamlit as st
        
        # Try to get from Streamlit secrets first, then environment
        try:
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
            else:
                api_key = os.getenv("GOOGLE_API_KEY")
        except Exception:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("Google API Key not found. Please set GOOGLE_API_KEY in environment variables or Streamlit secrets.")
            return None
        
        # Build the service with API key authentication
        service = build('sheets', 'v4', developerKey=api_key)
        return service
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return None

def read_google_sheet_public(spreadsheet_id: str, range_name: str, api_key: str) -> Optional[List[List[str]]]:
    """
    Read Google Sheet data using direct API calls for public sheets.
    This method works without OAuth2 authentication.
    """
    if not REQUESTS_AVAILABLE:
        print("Requests library not available")
        return None
        
    try:
        # Construct the URL for the Google Sheets API
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"
        params = {
            'key': api_key,
            'majorDimension': 'ROWS',
            'valueRenderOption': 'FORMATTED_VALUE'
        }
        
        # Double-check requests availability before using it
        if not REQUESTS_AVAILABLE or requests is None:
            print("Requests library not available for API call")
            return None
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('values', [])
        
    except Exception as e:
        # Simple error handling that works regardless of requests availability
        print(f"An error occurred: {e}")
        return None

def read_google_sheet(service: Any, spreadsheet_id: str, range_name: str) -> Optional[List[List[str]]]:
    """
    Read data from Google Sheets.
    Now supports both service-based and direct API approaches.
    
    Returns:
        list: List of rows from the sheet, or None if error
    """
    try:
        # Try service-based approach first
        if service:
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            
            if not values:
                print('No data found.')
                return []
            else:
                return values
        
        # Fallback to direct API approach
        import streamlit as st
        
        # Get API key
        try:
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
            else:
                api_key = os.getenv("GOOGLE_API_KEY")
        except Exception:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("Google API Key not found for fallback method.")
            return None
        
        return read_google_sheet_public(spreadsheet_id, range_name, api_key)
        
    except Exception as e:
        # Handle both HttpError and other exceptions
        if GOOGLE_API_AVAILABLE and 'HttpError' in str(type(e).__name__):
            print(f"Google Sheets API error: {e}")
        else:
            print(f"An error occurred: {e}")
        return None

def extract_sheet_id_from_url(url: str) -> Optional[str]:
    """
    Extract the spreadsheet ID from a Google Sheets URL.
    """
    try:
        # Handle different URL formats
        if '/spreadsheets/d/' in url:
            # Standard Google Sheets URL format
            start = url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
            end = url.find('/', start)
            if end == -1:
                end = url.find('?', start)
            if end == -1:
                end = url.find('#', start)
            if end == -1:
                end = len(url)
            return url[start:end]
        else:
            # If it's already just the ID
            return url
    except Exception as e:
        print(f"Error extracting sheet ID: {e}")
        return None

def fetch_google_search_results(query, num_results=10):
    """
    Fetch Google search results using Custom Search API.
    """
    if not REQUESTS_AVAILABLE:
        print("Requests library not available")
        return []
        
    try:
        import streamlit as st
        
        # Get API key and search engine ID
        try:
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
                search_engine_id = st.secrets.get("GOOGLE_SEARCH_ENGINE_ID")
            else:
                api_key = os.getenv("GOOGLE_API_KEY")
                search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        except Exception:
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            print("Google API Key or Search Engine ID not found in environment variables.")
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': min(num_results, 10)  # API limit is 10 per request
        }
        
        # Double-check requests availability before using it
        if not REQUESTS_AVAILABLE or requests is None:
            print("Requests library not available for API call")
            return []
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        
        return results
        
    except Exception as e:
        # Simple error handling that works regardless of requests availability
        print(f"An error occurred during search: {e}")
        return []
