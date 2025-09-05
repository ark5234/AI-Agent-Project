#!/usr/bin/env python3
"""
Enhanced test script for Google Sheets API with better error handling and sheet discovery.
"""

import os
import requests
from google_api import extract_sheet_id_from_url

def get_sheet_metadata(sheet_id, api_key):
    """Get metadata about the spreadsheet including available sheets."""
    try:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
        params = {'key': api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP error getting metadata: {e}")
        return None
    except Exception as e:
        print(f"Error getting metadata: {e}")
        return None

def test_sheet_access(sheet_id, sheet_name, api_key):
    """Test reading from a specific sheet."""
    try:
        range_name = f"{sheet_name}!A:Z"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}"
        params = {
            'key': api_key,
            'majorDimension': 'ROWS',
            'valueRenderOption': 'FORMATTED_VALUE'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            values = data.get('values', [])
            return values, None
        else:
            return None, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return None, str(e)

def main():
    print("🧪 Enhanced Google Sheets API Test")
    print("=" * 60)
    
    # Test data
    api_key = "AIzaSyC6lHAGoWbW_tPg1Vn4SHlDF0zutkcacRA"
    sheet_url = "https://docs.google.com/spreadsheets/d/15puRis-kWLS0eJ53O8t6utoOavH4yTo02IynnTf0w-U/edit?gid=0#gid=0"
    
    # Extract sheet ID
    sheet_id = extract_sheet_id_from_url(sheet_url)
    print(f"📊 Sheet ID: {sheet_id}")
    
    # First, try to get spreadsheet metadata
    print("\n🔍 Getting spreadsheet metadata...")
    metadata = get_sheet_metadata(sheet_id, api_key)
    
    if metadata:
        print("✅ Successfully accessed spreadsheet metadata!")
        print(f"📄 Title: {metadata.get('properties', {}).get('title', 'Unknown')}")
        
        sheets = metadata.get('sheets', [])
        print(f"📋 Available sheets ({len(sheets)}):")
        
        available_sheet_names = []
        for i, sheet in enumerate(sheets):
            properties = sheet.get('properties', {})
            sheet_name = properties.get('title', f'Sheet{i+1}')
            sheet_id_num = properties.get('sheetId', 'Unknown')
            available_sheet_names.append(sheet_name)
            print(f"  - {sheet_name} (ID: {sheet_id_num})")
        
        # Test reading from each available sheet
        print("\n📥 Testing data access for each sheet...")
        for sheet_name in available_sheet_names:
            print(f"\n🧪 Testing sheet: '{sheet_name}'")
            values, error = test_sheet_access(sheet_id, sheet_name, api_key)
            
            if values is not None:
                print(f"✅ Success! Found {len(values)} rows")
                if len(values) > 0:
                    print(f"📊 Headers: {values[0]}")
                if len(values) > 1:
                    print(f"📝 First data row: {values[1]}")
                    print(f"📝 Total data rows: {len(values) - 1}")
            else:
                print(f"❌ Failed: {error}")
        
    else:
        print("❌ Failed to get spreadsheet metadata")
        print("💡 Possible issues:")
        print("   - Sheet is not publicly accessible")
        print("   - API key doesn't have Sheets API enabled")
        print("   - Invalid sheet URL")
        
        # Try testing with common sheet names anyway
        common_names = ["Sheet1", "name", "data", "main"]
        print(f"\n🔄 Trying common sheet names: {common_names}")
        
        for sheet_name in common_names:
            print(f"\n🧪 Testing sheet: '{sheet_name}'")
            values, error = test_sheet_access(sheet_id, sheet_name, api_key)
            
            if values is not None:
                print(f"✅ Success! Found {len(values)} rows")
                if len(values) > 0:
                    print(f"📊 Headers: {values[0]}")
                break
            else:
                print(f"❌ Failed: {error}")

if __name__ == "__main__":
    main()
