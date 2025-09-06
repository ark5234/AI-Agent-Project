#!/usr/bin/env python3
"""
Final integration test for Google Sheets with the specific user data.
"""

import os
import sys
import pandas as pd

# Add the app directory to Python path
sys.path.append(os.path.dirname(__file__))

from google_api import read_google_sheet_public, extract_sheet_id_from_url

def test_user_sheet():
    """Test with the specific user's Google Sheet data."""
    
    # User's specific data
    api_key = "AIzaSyC6lHAGoWbW_tPg1Vn4SHlDF0zutkcacRA"
    sheet_url = "https://docs.google.com/spreadsheets/d/15puRis-kWLS0eJ53O8t6utoOavH4yTo02IynnTf0w-U/edit?gid=0#gid=0"
    correct_sheet_name = "Sheet1"  # From our discovery
    
    print("🎯 Testing User's Specific Google Sheet")
    print("=" * 50)
    print(f"📄 Sheet: RAS Finance and reg")
    print(f"📋 Sheet Name: {correct_sheet_name}")
    print(f"🔗 URL: {sheet_url}")
    
    # Extract sheet ID
    sheet_id = extract_sheet_id_from_url(sheet_url)
    print(f"🆔 Sheet ID: {sheet_id}")
    
    # Check if sheet_id was extracted successfully
    if not sheet_id:
        print("❌ Failed to extract sheet ID from URL")
        return False
    
    # Read data
    range_name = f"{correct_sheet_name}!A:Z"
    print(f"📥 Reading range: {range_name}")
    
    try:
        values = read_google_sheet_public(sheet_id, range_name, api_key)
        
        
        if values and len(values) > 0:
            print(f"✅ Successfully loaded {len(values)} rows!")
            
            # Create DataFrame
            headers = values[0]
            data_rows = values[1:] if len(values) > 1 else []
            
            if data_rows:
                df = pd.DataFrame(data_rows, columns=headers)
                
                print(f"\n📊 Data Summary:")
                print(f"   Columns: {len(df.columns)}")
                print(f"   Rows: {len(df)}")
                print(f"   Headers: {list(df.columns)}")
                
                print(f"\n📝 Sample Data (first 3 rows):")
                print(df.head(3).to_string(index=False))
                
                print(f"\n🔍 Data Quality Check:")
                print(f"   Missing values: {df.isnull().sum().sum()}")
                print(f"   Duplicate rows: {df.duplicated().sum()}")
                
                # Check specific columns that were mentioned
                if 'Name ' in df.columns:
                    print(f"   Students with names: {df['Name '].notna().sum()}")
                
                if 'Mobile No' in df.columns:
                    print(f"   Students with mobile numbers: {df['Mobile No'].notna().sum()}")
                
                return True
            else:
                print("⚠️ No data rows found (only headers)")
                return False
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_user_sheet()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Integration test PASSED!")
        print("🎉 Your Google Sheets is now ready for AI analysis!")
        print("\n💡 Next steps:")
        print("   1. Use 'Sheet1' as the sheet name in the app")
        print("   2. The app will automatically load your student data")
        print("   3. You can now ask AI questions about the data")
    else:
        print("❌ Integration test FAILED!")
        print("🛠️ Please check your configuration.")
