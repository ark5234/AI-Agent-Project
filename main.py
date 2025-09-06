import streamlit as st
import pandas as pd
import io
import os
import sys
import re
import hashlib
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Any, Union
from dotenv import load_dotenv

# Import Google API functions with proper type handling
try:
    from google_api import (  # type: ignore
        authenticate_google_sheets,  # type: ignore
        read_google_sheet,  # type: ignore
        extract_sheet_id_from_url,  # type: ignore
        read_google_sheet_public  # type: ignore
    )
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    def authenticate_google_sheets() -> None:
        return None
    def read_google_sheet(service: Any, spreadsheet_id: str, range_name: str) -> Optional[List[List[str]]]:
        return None
    def extract_sheet_id_from_url(url: str) -> Optional[str]:
        return None
    def read_google_sheet_public(spreadsheet_id: str, range_name: str, api_key: str) -> Optional[List[List[str]]]:
        return None

import requests
from googleapiclient.discovery import build
from gemini_api import query_gemini

APP_DIR = os.path.dirname(__file__)
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

load_dotenv()

def get_sheet_names(sheet_id, api_key):
    """Get available sheet names from a Google Spreadsheet."""
    try:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
        params = {'key': api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        sheets = data.get('sheets', [])
        
        sheet_names = []
        for sheet in sheets:
            properties = sheet.get('properties', {})
            sheet_name = properties.get('title', 'Unknown')
            sheet_names.append(sheet_name)
        
        return sheet_names
        
    except Exception as e:
        return None

def get_secret(key: str, default: str | None = None) -> str | None:
    """Return a config value, preferring Streamlit Cloud secrets then env vars.
    - Uses membership test to avoid KeyError and avoid depending on Mapping.get implementation.
    - Works both locally and on Cloud.
    """
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    # Local env var or .env
    val = os.getenv(key, default)
    if val:
        return val
    # Optional local secrets file support for development only
    try:
        local_secrets_path = os.path.join(os.path.dirname(APP_DIR), ".streamlit", "secrets.toml")
        if os.path.exists(local_secrets_path):
            import tomllib  # py311+
            with open(local_secrets_path, "rb") as f:
                data = tomllib.load(f)
            return data.get(key, default)
    except Exception:
        pass
    return default

# Resolve API keys
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = get_secret("SEARCH_ENGINE_ID")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

if not GEMINI_API_KEY:
        st.error("🔑 Gemini API Key Missing")
        st.markdown("""
        For Streamlit Cloud deployment, set the secret in your app settings and restart:
        - Settings → Secrets → add this line exactly (without brackets):
            GEMINI_API_KEY = "your_api_key_here"

        Notes:
        - The secrets file in your repository (.streamlit/secrets.toml) is ignored by Streamlit Cloud.
        - After saving secrets in the UI, click 'Restart' on the app for changes to take effect.

        For local development, either set an environment variable or add it to a .env file at the repo root.
        """)
        # Minimal diagnostics (no secret values shown)
        try:
            has_secrets = hasattr(st, "secrets")
            in_st_secrets = False
            if has_secrets:
                try:
                    in_st_secrets = ("GEMINI_API_KEY" in st.secrets)
                except Exception:
                    in_st_secrets = False
            has_env = bool(os.getenv("GEMINI_API_KEY"))
            local_secrets_path = os.path.join(os.path.dirname(APP_DIR), ".streamlit", "secrets.toml")
            has_local_secrets = os.path.exists(local_secrets_path)
            st.info(
                f"Diagnostics — st.secrets available: {has_secrets}; key in secrets: {in_st_secrets}; env var present: {has_env}; local secrets file: {has_local_secrets}"
            )
        except Exception:
            pass
        st.stop()

@st.cache_data(ttl=3600)
def cached_dataset_analysis(data_hash, columns_str, shape_str):
    """Cache dataset analysis for 1 hour to improve performance"""
    return None

def validate_csv_file(file):
    """Comprehensive file validation for security and performance"""
    if file is None:
        return False, "No file provided"
    
    # Size validation (50MB limit)
    max_size = 50 * 1024 * 1024
    if file.size > max_size:
        return False, f"File too large ({file.size / 1024 / 1024:.1f}MB). Maximum allowed: 50MB"
    
    # Extension validation
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in allowed_extensions:
        return False, f"Unsupported file format: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
    
    return True, "File validation passed"

def validate_query_input(query):
    """Validate user query for security and quality"""
    if not query or len(query.strip()) == 0:
        return False, "Query cannot be empty"
    
    if len(query) > 1000:
        return False, "Query too long (max 1000 characters)"
    
    # Basic SQL injection prevention
    dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    query_upper = query.upper()
    for pattern in dangerous_patterns:
        if pattern in query_upper:
            return False, f"Query contains potentially dangerous keyword: {pattern}"
    
    return True, "Query validation passed"

def safe_data_processing(func):
    """Decorator for safe data processing with error boundaries"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MemoryError:
            st.error("⚠️ Dataset too large for processing. Please try with a smaller file.")
            return None
        except pd.errors.EmptyDataError:
            st.error("📊 The uploaded file appears to be empty.")
            return None
        except pd.errors.ParserError as e:
            st.error(f"📝 File parsing error: {str(e)}")
            return None
        except UnicodeDecodeError:
            st.error("🔤 Text encoding error. Please ensure your file is properly encoded.")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None
    return wrapper

@safe_data_processing
def secure_read_csv(file):
    """Safely read CSV with comprehensive error handling"""
    try:
        # Try UTF-8 first
        data = pd.read_csv(file, encoding="utf-8")
        return data
    except UnicodeDecodeError:
        try:
            # Fallback to latin1
            file.seek(0)  # Reset file pointer
            data = pd.read_csv(file, encoding="latin1")
            st.warning("⚠️ File encoding detected as Latin1. Some characters may not display correctly.")
            return data
        except Exception:
            # Final fallback
            file.seek(0)
            data = pd.read_csv(file, encoding="utf-8", on_bad_lines='skip')
            st.warning("⚠️ Some problematic lines were skipped due to encoding issues.")
            return data

@safe_data_processing
def secure_read_excel(file):
    """Safely read Excel files with error handling"""
    return pd.read_excel(file, engine='openpyxl')

@safe_data_processing
def secure_read_json(file):
    """Safely read JSON files with error handling"""
    return pd.read_json(file)

def main():
    # Hero section with improved branding
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f77b4; margin-bottom: 0.5rem;'>🤖 AI Data Analytics Platform</h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 1rem;'>
            Transform your data into insights with natural language queries
        </p>
        <p style='color: #888; font-size: 0.9rem;'>
            🚀 <a href='https://ai-data-analytics-agent.streamlit.app/' target='_blank' style='text-decoration: none;'>
                Live Demo Available
            </a> | 
            📊 Support CSV, Excel, JSON & Google Sheets | 
            🧠 Powered by Google Gemini AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🔍 Smart Analysis**
        - Natural language queries
        - AI-powered insights
        - Automatic visualizations
        """)
    with col2:
        st.markdown("""
        **📈 Multiple Formats**
        - CSV, Excel, JSON files
        - Google Sheets integration
        - Real-time data processing
        """)
    with col3:
        st.markdown("""
        **⚡ Fast & Secure**
        - Intelligent caching
        - File validation
        - Privacy-focused design
        """)

    st.markdown("---")

    # Data source selection with better styling
    st.subheader("📂 Choose Your Data Source")
    
    # Conditionally include Google Sheets option based on availability
    if GOOGLE_SHEETS_AVAILABLE:
        options = ("📄 Upload File (CSV, Excel, JSON)", "📊 Google Sheets URL")
    else:
        options = ("📄 Upload File (CSV, Excel, JSON)",)
        st.info("ℹ️ Google Sheets integration is temporarily unavailable. Please use file upload.")
    
    input_option = st.radio(
        "Select how you want to provide data:",
        options,
        help="Choose your preferred method to upload or connect your data"
    )

    if input_option == "📊 Google Sheets URL" and GOOGLE_SHEETS_AVAILABLE:
        handle_google_sheets()
    elif input_option == "📄 Upload File (CSV, Excel, JSON)":
        handle_csv_upload()

def handle_google_sheets():
    st.markdown("### 🔗 Connect to Google Sheets")
    st.info("💡 **Tip**: Make sure your Google Sheet is publicly accessible or shared with the service account.")
    
    sheet_url = st.text_input(
        "📝 Enter Google Sheets URL:",
        placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
        help="Paste the full URL of your Google Sheet"
    )
    
    if sheet_url:
        if "docs.google.com/spreadsheets" not in sheet_url:
            st.warning("⚠️ Please enter a valid Google Sheets URL.")
            return

        # Extract sheet ID from URL using helper function
        sheet_id = extract_sheet_id_from_url(sheet_url)
        
        if not sheet_id:
            st.error("❌ Invalid Google Sheets URL. Please check the URL format.")
            return
        
        # Check if we have a Google API key
        api_key = get_secret("GOOGLE_API_KEY")
        
        if not api_key:
            st.error("❌ Google API Key not found. Please configure GOOGLE_API_KEY in your secrets.")
            return
        
        # Try to get available sheet names
        with st.spinner("🔍 Discovering available sheets..."):
            available_sheets = get_sheet_names(sheet_id, api_key)
        
        if available_sheets:
            st.success(f"✅ Found {len(available_sheets)} sheets: {', '.join(available_sheets)}")
            
            # Let user select from available sheets
            sheet_name = st.selectbox(
                "📋 Select sheet:",
                options=available_sheets,
                help="Choose the sheet tab you want to analyze"
            )
        else:
            # Fallback to manual input
            st.warning("⚠️ Could not auto-detect sheets. Please enter the sheet name manually.")
            sheet_name = st.text_input(
                "📋 Enter sheet name:",
                value="Sheet1",
                help="The name of the specific sheet tab (e.g., 'Sheet1', 'name', etc.)"
            )

        if sheet_name:
            try:
                with st.spinner("📥 Loading data from Google Sheets..."):
                    range_name = f"{sheet_name}!A:Z"
                    
                    # Try direct API method first for public sheets
                    values = read_google_sheet_public(sheet_id, range_name, api_key)
                    
                    # If direct method fails, try service-based method as fallback
                    if not values:
                        service = authenticate_google_sheets()
                        if service:
                            values = read_google_sheet(service, sheet_id, range_name)
                
                if values and len(values) > 0:
                    headers = values[0]
                    data_rows = values[1:] if len(values) > 1 else []
                    
                    if data_rows:
                        data = pd.DataFrame(data_rows, columns=headers)
                        
                        st.success(f"✅ Successfully loaded {len(data)} rows from Google Sheets!")
                        st.markdown("### 📊 Data Preview")
                        st.dataframe(data, height=400)
                        main_column_selection(data)
                    else:
                        st.warning("⚠️ Sheet contains headers but no data rows.")
                else:
                    st.error("❌ No data found in the specified sheet. Please check the sheet name.")
                    
            except Exception as e:
                st.error(f"❌ Error reading data from Google Sheets: {str(e)}")
                st.info("💡 Make sure the sheet is publicly accessible or you have the correct permissions.")

def handle_csv_upload():
    st.markdown("### 📁 Upload Your Data File")
    st.info("💡 **Supported formats**: CSV, Excel (.xlsx, .xls), JSON | **Max size**: 50MB")
    
    uploaded_file = st.file_uploader(
        "🔺 Choose your data file:",
        type=["csv", "xlsx", "xls", "json"],
        help="Drag and drop your file here, or click to browse"
    )
    
    if uploaded_file is not None:
        # File info display
        file_details = {
            "📄 Filename": uploaded_file.name,
            "📏 File size": f"{uploaded_file.size / 1024 / 1024:.2f} MB",
            "🏷️ File type": uploaded_file.type
        }
        
        with st.expander("📋 File Details", expanded=False):
            for key, value in file_details.items():
                st.write(f"**{key}**: {value}")
        
        # Validate file first
        is_valid, message = validate_csv_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        st.success(f"✅ {message}")
        
        # Determine file type and read accordingly
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        with st.spinner(f"📖 Processing {file_extension} file..."):
            if file_extension == '.csv':
                data = secure_read_csv(uploaded_file)
            elif file_extension in ['.xlsx', '.xls']:
                data = secure_read_excel(uploaded_file)
            elif file_extension == '.json':
                data = secure_read_json(uploaded_file)
            else:
                st.error("❌ Unsupported file format")
                return
        
        if data is not None:
            # Display success metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Rows", f"{len(data):,}")
            with col2:
                st.metric("📋 Columns", len(data.columns))
            with col3:
                st.metric("💾 Memory", f"{data.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
            
            st.markdown("### 👀 Data Preview")
            st.dataframe(data.head(10), height=300)
            
            # Data quality indicators
            with st.expander("🔍 Data Quality Summary", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Missing Values:**")
                    missing_data = data.isnull().sum()
                    for col, missing in missing_data.items():
                        if missing > 0:
                            st.write(f"- {col}: {missing} ({missing/len(data)*100:.1f}%)")
                with col2:
                    st.write("**Data Types:**")
                    for col, dtype in data.dtypes.items():
                        st.write(f"- {col}: {dtype}")
            
            main_column_selection(data)
        else:
            st.error("❌ Failed to read the file. Please check the format and try again.")

def main_column_selection(data):
    if not data.empty:
        st.markdown("---")
        st.markdown("### 🎯 Analysis Configuration")
        
        # Column focus selection
        st.markdown("#### 📍 Analysis Focus")
        column_names = ["🤖 Auto-detect (Recommended)"] + data.columns.tolist()
        main_column = st.selectbox(
            "Choose a primary column for analysis or let AI auto-detect:",
            column_names,
            help="Select a specific column to focus analysis on, or let the AI automatically understand your queries"
        )

        if main_column == "🤖 Auto-detect (Recommended)":
            st.success("✨ AI will automatically understand your queries for any column")
            main_column = data.columns[0]
        else:
            main_column = main_column  # Remove emoji prefix if user selected specific column
            st.success(f"🎯 Selected focus column: **{main_column}**")
        
        # Dataset overview in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📊 **Dataset Size**\n{data.shape[0]:,} rows × {data.shape[1]} columns")
        with col2:
            numeric_cols = len(data.select_dtypes(include=['number']).columns)
            st.info(f"� **Numeric Columns**\n{numeric_cols} available")
        with col3:
            text_cols = len(data.select_dtypes(include=['object']).columns)
            st.info(f"📝 **Text Columns**\n{text_cols} available")
        
        # Column details in expandable section
        with st.expander("📋 Detailed Column Information", expanded=False):
            for col in data.columns:
                unique_count = data[col].nunique()
                sample_vals = data[col].dropna().unique()[:5]
                missing_count = data[col].isnull().sum()
                
                col_info = f"**{col}**"
                col_info += f" • Type: {data[col].dtype}"
                col_info += f" • Unique: {unique_count:,}"
                if missing_count > 0:
                    col_info += f" • Missing: {missing_count:,}"
                col_info += f" • Sample: {list(sample_vals)}"
                
                st.write(col_info)
        
        process_and_download(data, main_column)

def process_and_download(data, main_column):
    placeholder_text = f"e.g., Show records where [column] is [value], Count [category], Find [condition]"
    query = st.text_input(f"Enter your query (AI will understand automatically):", placeholder=placeholder_text)
    debug_mode = st.checkbox("🔍 Debug Mode (Show AI analysis process)", value=False)
    
    if query:
        # Validate query first
        is_valid_query, validation_message = validate_query_input(query)
        if not is_valid_query:
            st.error(f"❌ Query validation failed: {validation_message}")
            return
        
        if debug_mode:
            st.expander("🔍 Dataset Info", expanded=True).write(f"""
            **Available Columns:** {list(data.columns)}
            **Dataset Shape:** {data.shape}
            **Column Types:** {dict(data.dtypes)}
            """)
        
        result = process_query(data, query, main_column)
        
        if isinstance(result, pd.DataFrame):
            if not result.empty:
                # If result is a valid DataFrame, show the results
                st.write("Query result:")
                st.dataframe(result)

                # Generate smart visualizations
                with st.expander("📊 Data Visualization", expanded=True):
                    chart = generate_smart_visualizations(data, query, result)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    else:
                        st.info("💡 Tip: Try queries like 'show trend', 'compare categories', or 'distribution' for automatic charts")

                csv = result.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )
                return
            # Empty DataFrame: try Gemini first for data analysis, then web search
            st.info("No matching rows found locally. Asking Gemini to analyze the data...")
            response = query_gemini_ai(query, data)
            if response:
                st.subheader("Gemini Analysis:")
                st.write(response)
                st.download_button(
                    label="Download response as TXT",
                    data=response,
                    file_name="gemini_response.txt",
                    mime="text/plain",
                )
                return
            
            # If Gemini fails, try web search as fallback
            st.info("Gemini analysis failed. Searching the web...")
            web_results = web_search(query)
            if web_results:
                st.subheader("Web Search Results:")
                for item in web_results:
                    st.write(f"**{item['title']}**: [Link]({item['link']})")
                    st.write(item['snippet'])
                return
        # If processing failed, still try fallbacks
        st.info("Couldn’t process query locally. Trying web search...")
        web_results = web_search(query)
        if web_results:
            st.subheader("Web Search Results:")
            for item in web_results:
                st.write(f"**{item['title']}**: [Link]({item['link']})")
                st.write(item['snippet'])
            return
        response = query_gemini_ai(query, data)
        if response:
            st.write("Gemini response:")
            st.write(response)
            st.download_button(
                label="Download response as TXT",
                data=response,
                file_name="gemini_response.txt",
                mime="text/plain",
            )



def process_query(data: pd.DataFrame, query: str, main_column: str) -> Optional[pd.DataFrame]:
    """Optimized query processing with fast pattern matching first, then AI fallback."""
    try:
        # Fast pattern matching first (much faster than AI)
        fast_result = optimized_pattern_matching(data, query)
        if fast_result is not None and not fast_result.empty:
            return fast_result
        
        # AI processing only if pattern matching fails
        st.info("🤖 Using AI for complex analysis...")
        ai_response = query_gemini_ai(query, data)
        
        if ai_response and "error" not in ai_response.lower():
            st.write("🤖 **AI Analysis:**")
            st.write(ai_response)
            return pd.DataFrame()  # Return empty for AI text responses
        
        return None
        
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def optimized_pattern_matching(data: pd.DataFrame, query: str) -> Optional[pd.DataFrame]:
    """Fast pattern matching for common queries - much faster than AI."""
    query_lower = query.lower()
    
    # Fast numeric filtering
    if any(op in query_lower for op in ['>', '<', '>=', '<=', '==', '!=']):
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]) or col.lower() in query_lower:
                # Extract numeric comparisons
                import re
                patterns = [
                    (r'(\w+)\s*>\s*(\d+\.?\d*)', lambda m: data[data[m.group(1)] > float(m.group(2))]),
                    (r'(\w+)\s*<\s*(\d+\.?\d*)', lambda m: data[data[m.group(1)] < float(m.group(2))]),
                    (r'(\w+)\s*>=\s*(\d+\.?\d*)', lambda m: data[data[m.group(1)] >= float(m.group(2))]),
                    (r'(\w+)\s*<=\s*(\d+\.?\d*)', lambda m: data[data[m.group(1)] <= float(m.group(2))]),
                ]
                
                for pattern, func in patterns:
                    match = re.search(pattern, query_lower)
                    if match and match.group(1) in [c.lower() for c in data.columns]:
                        col_name = next(c for c in data.columns if c.lower() == match.group(1))
                        try:
                            # Convert to numeric if needed
                            if data[col_name].dtype == 'object':
                                data[col_name] = pd.to_numeric(data[col_name], errors='coerce')
                            
                            if '>' in query_lower:
                                return data[data[col_name] > float(match.group(2))]
                            elif '<' in query_lower:
                                return data[data[col_name] < float(match.group(2))]
                            elif '>=' in query_lower:
                                return data[data[col_name] >= float(match.group(2))]
                            elif '<=' in query_lower:
                                return data[data[col_name] <= float(match.group(2))]
                        except:
                            continue
    
    # Fast text filtering
    if any(word in query_lower for word in ['contains', 'like', 'has', 'with']):
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    words = query_lower.split()
                    for word in words:
                        if len(word) > 3:  # Skip short words
                            matches = data[data[col].astype(str).str.contains(word, case=False, na=False)]
                            if not matches.empty:
                                return matches
                except:
                    continue
    
    # Fast counting
    if any(word in query_lower for word in ['count', 'how many']):
        return pd.DataFrame({'count': [len(data)]})
    
    return None

def get_data_context(data: pd.DataFrame) -> dict:
    """Minimal context for faster processing."""
    return {
        "columns": list(data.columns),
        "shape": data.shape,
        "dtypes": {col: str(data[col].dtype) for col in data.columns[:10]}  # Limit to first 10 columns
    }

def query_gemini_simple(query: str) -> Optional[str]:
    """Simple Gemini query for filter generation."""
    try:
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if api_key:
            return query_gemini(query, api_key)
        return None
    except:
        return None
        return None

def web_search(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()
        
        if 'items' in res:
            search_results = []
            for item in res['items']:
                search_results.append({
                    'title': item['title'],
                    'link': item['link'],
                    'snippet': item['snippet']
                })
            return search_results
        return None
    
    except Exception as e:
        st.error(f"Error during web search: {e}")
        return None

def generate_smart_visualizations(data, query, result_data):
    """Generate intelligent visualizations based on query intent and data"""
    query_lower = query.lower()
    
    try:
        # Determine visualization type based on query keywords
        if any(word in query_lower for word in ['trend', 'over time', 'timeline', 'time series']):
            return create_time_series_chart(result_data)
        elif any(word in query_lower for word in ['distribution', 'histogram', 'frequency']):
            return create_distribution_chart(result_data)
        elif any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus']):
            return create_comparison_chart(result_data)
        elif any(word in query_lower for word in ['correlation', 'relationship', 'scatter']):
            return create_correlation_chart(result_data)
        elif any(word in query_lower for word in ['count', 'total', 'sum', 'aggregate']):
            return create_summary_chart(result_data)
        else:
            # Default: smart auto-detection based on data types
            return create_auto_chart(result_data)
    except Exception as e:
        st.warning(f"Could not generate visualization: {e}")
        return None

def create_time_series_chart(data):
    """Create time series visualization"""
    date_cols = data.select_dtypes(include=['datetime64']).columns
    numeric_cols = data.select_dtypes(include=['number']).columns
    
    if len(date_cols) > 0 and len(numeric_cols) > 0:
        fig = px.line(data, x=date_cols[0], y=numeric_cols[0], 
                     title=f"Time Series: {numeric_cols[0]} over {date_cols[0]}")
        return fig
    return None

def create_distribution_chart(data):
    """Create distribution histogram"""
    numeric_cols = data.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) > 0:
        fig = px.histogram(data, x=numeric_cols[0], 
                          title=f"Distribution of {numeric_cols[0]}")
        return fig
    return None

def create_comparison_chart(data):
    """Create comparison bar chart"""
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns
    numeric_cols = data.select_dtypes(include=['number']).columns
    
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        fig = px.bar(data, x=categorical_cols[0], y=numeric_cols[0],
                    title=f"{numeric_cols[0]} by {categorical_cols[0]}")
        return fig
    return None

def create_correlation_chart(data):
    """Create scatter plot for correlation"""
    numeric_cols = data.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) >= 2:
        fig = px.scatter(data, x=numeric_cols[0], y=numeric_cols[1],
                        title=f"Correlation: {numeric_cols[0]} vs {numeric_cols[1]}")
        return fig
    return None

def create_summary_chart(data):
    """Create summary chart for aggregated data"""
    if len(data) <= 20:  # Small dataset - show all values
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        numeric_cols = data.select_dtypes(include=['number']).columns
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            fig = px.pie(data, names=categorical_cols[0], values=numeric_cols[0],
                        title=f"Summary: {numeric_cols[0]} by {categorical_cols[0]}")
            return fig
    return None

def create_auto_chart(data):
    """Automatically choose best chart type based on data"""
    numeric_cols = data.select_dtypes(include=['number']).columns
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns
    
    # Priority: scatter for 2+ numeric, bar for 1 categorical + 1 numeric
    if len(numeric_cols) >= 2:
        return create_correlation_chart(data)
    elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
        return create_comparison_chart(data)
    elif len(numeric_cols) > 0:
        return create_distribution_chart(data)
    
    return None

def query_gemini_ai(query: str, data: pd.DataFrame) -> Optional[str]:
    """Streamlined AI query processing."""
    try:
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Gemini API key not configured"
            
        # Create focused prompt for faster processing
        context = f"""Analyze this query for a dataset with {len(data)} rows and columns: {', '.join(data.columns[:10])}.
Query: {query}

Provide a concise analysis or filtering suggestion."""
        
        response = query_gemini(context, api_key)
        return response
        
    except Exception as e:
        return f"AI Error: {str(e)}"

if __name__ == "__main__":
    try:
        st.set_page_config(
            page_title="AI Data Analytics Platform",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Minimal clean styling
        st.markdown("""
        <style>
        .main > div { padding-top: 1rem; }
        .stAlert > div { border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)
        
        main()
        
        # Simple footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 1rem; color: #666;'>
            🤖 AI Data Analytics Platform | 
            <a href='https://github.com/ark5234/AI-Agent-Project' target='_blank'>GitHub</a> | 
            <a href='https://ai-data-analytics-agent.streamlit.app/' target='_blank'>Live Demo</a>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        if st.checkbox("Show details"):
            st.code(str(e))
