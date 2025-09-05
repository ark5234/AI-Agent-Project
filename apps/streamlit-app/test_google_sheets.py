#!/usr/bin/env python3
"""
Test script for Google Sheets API integration with API key authentication.
"""

import os
from google_api import read_google_sheet_public, extract_sheet_id_from_url

def test_google_sheets():
    """Test Google Sheets authentication and data reading with API key."""
    
    # Test data provided by user
    api_key = "AIzaSyC6lHAGoWbW_tPg1Vn4SHlDF0zutkcacRA"
    sheet_url = "https://docs.google.com/spreadsheets/d/15puRis-kWLS0eJ53O8t6utoOavH4yTo02IynnTf0w-U/edit?gid=0#gid=0"
    sheet_name = "name"
    
    print(f"🔗 Testing Google Sheets URL: {sheet_url}")
    print(f"📋 Sheet name: {sheet_name}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    # Extract sheet ID
    sheet_id = extract_sheet_id_from_url(sheet_url)
    print(f"📊 Extracted Sheet ID: {sheet_id}")
    
    if not sheet_id:
        print("❌ Failed to extract sheet ID from URL")
        return False
    
    # Test reading data
    range_name = f"{sheet_name}!A:Z"
    print(f"📥 Reading range: {range_name}")
    
    try:
        values = read_google_sheet_public(sheet_id, range_name, api_key)
        
        if values:
            print(f"✅ Successfully read {len(values)} rows from Google Sheets!")
            
            if len(values) > 0:
                print(f"📊 Headers: {values[0]}")
                
            if len(values) > 1:
                print(f"📝 First data row: {values[1]}")
                print(f"📝 Total data rows: {len(values) - 1}")
            else:
                print("⚠️ No data rows found (only headers)")
                
            return True
        else:
            print("❌ No data returned from Google Sheets")
            return False
            
    except Exception as e:
        print(f"❌ Error reading Google Sheets: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Sheets API Integration")
    print("=" * 50)
    
    success = test_google_sheets()
    
    print("=" * 50)
    if success:
        print("✅ Google Sheets integration test PASSED!")
    else:
        print("❌ Google Sheets integration test FAILED!")
        print("💡 Make sure the sheet is publicly accessible and the API key has Sheets API enabled.")
