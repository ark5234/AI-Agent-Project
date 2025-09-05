#!/usr/bin/env python3
"""
Test script to identify errors in google_api.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_google_api_functions():
    """Test all functions in google_api.py for potential errors."""
    
    print("🧪 Testing google_api.py functions...")
    
    try:
        import google_api
        print("✅ google_api module imported successfully")
        
        # Test 1: Check availability flags
        print(f"📊 REQUESTS_AVAILABLE: {google_api.REQUESTS_AVAILABLE}")
        print(f"📊 GOOGLE_API_AVAILABLE: {google_api.GOOGLE_API_AVAILABLE}")
        
        # Test 2: Test authenticate_google_sheets
        print("\n🔐 Testing authenticate_google_sheets()...")
        try:
            service = google_api.authenticate_google_sheets()
            print(f"✅ authenticate_google_sheets returned: {type(service)}")
        except Exception as e:
            print(f"❌ authenticate_google_sheets error: {e}")
        
        # Test 3: Test extract_sheet_id_from_url
        print("\n🔗 Testing extract_sheet_id_from_url()...")
        test_url = "https://docs.google.com/spreadsheets/d/1ABC123/edit"
        try:
            sheet_id = google_api.extract_sheet_id_from_url(test_url)
            print(f"✅ extract_sheet_id_from_url returned: {sheet_id}")
        except Exception as e:
            print(f"❌ extract_sheet_id_from_url error: {e}")
        
        # Test 4: Test read_google_sheet_public (with dummy data)
        print("\n📥 Testing read_google_sheet_public()...")
        try:
            result = google_api.read_google_sheet_public("dummy_id", "Sheet1!A:Z", "dummy_key")
            print(f"✅ read_google_sheet_public returned: {type(result)}")
        except Exception as e:
            print(f"❌ read_google_sheet_public error: {e}")
        
        # Test 5: Test read_google_sheet
        print("\n📊 Testing read_google_sheet()...")
        try:
            result = google_api.read_google_sheet(None, "dummy_id", "Sheet1!A:Z")
            print(f"✅ read_google_sheet returned: {type(result)}")
        except Exception as e:
            print(f"❌ read_google_sheet error: {e}")
        
        # Test 6: Test fetch_google_search_results
        print("\n🔍 Testing fetch_google_search_results()...")
        try:
            result = google_api.fetch_google_search_results("test query", 5)
            print(f"✅ fetch_google_search_results returned: {type(result)}")
        except Exception as e:
            print(f"❌ fetch_google_search_results error: {e}")
        
        print("\n✅ All function tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def check_code_issues():
    """Check for specific code issues."""
    
    print("\n🔍 Checking for code issues...")
    
    issues = []
    
    # Check 1: requests usage when requests is None
    with open('google_api.py', 'r') as f:
        content = f.read()
        
        if 'requests.get(' in content and 'if not REQUESTS_AVAILABLE:' not in content.split('requests.get(')[0].split('\n')[-5:]:
            issues.append("❌ requests.get() used without checking REQUESTS_AVAILABLE")
        
        if 'requests.exceptions' in content:
            issues.append("❌ requests.exceptions used - may fail when requests is None")
        
        if 'build(' in content and 'if not GOOGLE_API_AVAILABLE:' not in content.split('build(')[0].split('\n')[-5:]:
            issues.append("❌ build() used without checking GOOGLE_API_AVAILABLE")
    
    if issues:
        print("🚨 Found issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No obvious code issues found")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("🔍 Google API Code Analysis")
    print("=" * 50)
    
    functions_ok = test_google_api_functions()
    code_ok = check_code_issues()
    
    print("=" * 50)
    if functions_ok and code_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Issues found - see details above")
