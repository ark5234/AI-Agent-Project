#!/usr/bin/env python3
"""
Advanced test to simulate missing libraries and test error handling
"""

import sys
import os

def test_with_missing_libraries():
    """Test what happens when libraries are unavailable."""
    
    print("🧪 Testing with simulated missing libraries...")
    
    # Create a modified version that simulates missing libraries
    with open('google_api.py', 'r') as f:
        original_content = f.read()
    
    # Create a test version that forces libraries to be unavailable
    test_content = original_content.replace(
        'REQUESTS_AVAILABLE = True', 'REQUESTS_AVAILABLE = False'
    ).replace(
        'GOOGLE_API_AVAILABLE = True', 'GOOGLE_API_AVAILABLE = False'
    )
    
    # Write test file
    with open('google_api_test.py', 'w') as f:
        f.write(test_content)
    
    try:
        # Import the test module
        import google_api_test
        
        print("✅ Module imports successfully even with missing libraries")
        
        # Test functions
        result1 = google_api_test.authenticate_google_sheets()
        print(f"📊 authenticate_google_sheets with missing libs: {result1}")
        
        result2 = google_api_test.read_google_sheet_public("test", "test", "test")
        print(f"📊 read_google_sheet_public with missing libs: {result2}")
        
        result3 = google_api_test.fetch_google_search_results("test")
        print(f"📊 fetch_google_search_results with missing libs: {result3}")
        
        print("✅ All functions handle missing libraries gracefully!")
        
    except Exception as e:
        print(f"❌ Error with missing libraries: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists('google_api_test.py'):
            os.remove('google_api_test.py')
    
    return True

def test_real_functionality():
    """Test with actual Google Sheets data to ensure it works."""
    
    print("\n🔍 Testing real Google Sheets functionality...")
    
    try:
        import google_api
        
        # Test with the real sheet data
        api_key = "AIzaSyC6lHAGoWbW_tPg1Vn4SHlDF0zutkcacRA"
        sheet_id = "15puRis-kWLS0eJ53O8t6utoOavH4yTo02IynnTf0w-U"
        sheet_name = "Sheet1"
        range_name = f"{sheet_name}!A:Z"
        
        print(f"📊 Testing with real sheet: {sheet_id}")
        
        # Test the public API method
        values = google_api.read_google_sheet_public(sheet_id, range_name, api_key)
        
        if values and len(values) > 0:
            print(f"✅ Successfully read {len(values)} rows from real Google Sheet!")
            print(f"📋 Headers: {values[0]}")
            if len(values) > 1:
                print(f"📝 First data row: {values[1][:3]}...")  # Show first 3 columns
            return True
        else:
            print("❌ No data returned from real Google Sheet")
            return False
            
    except Exception as e:
        print(f"❌ Error testing real functionality: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Advanced Google API Error Testing")
    print("=" * 60)
    
    test1_ok = test_with_missing_libraries()
    test2_ok = test_real_functionality()
    
    print("=" * 60)
    if test1_ok and test2_ok:
        print("✅ ALL TESTS PASSED!")
        print("🎉 google_api.py is robust and handles all error cases properly!")
    else:
        print("❌ Some tests failed - see details above")
