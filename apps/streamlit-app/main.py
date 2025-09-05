import streamlit as st
import pandas as pd
import os
import re
import hashlib
import json
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from google_api import authenticate_google_sheets, read_google_sheet
from googleapiclient.discovery import build
from gemini_api import query_gemini

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("The Gemini API key is not set. Please set the `GEMINI_API_KEY` environment variable.")
    st.stop()

@st.cache_data(ttl=3600)
def cached_dataset_analysis(data_hash, columns_str, shape_str):
    """Cache dataset analysis for 1 hour to improve performance"""
    return None

@st.cache_data(ttl=1800)
def cached_ai_response(query_hash, data_context_hash):
    """Cache AI responses for 30 minutes to avoid redundant API calls"""
    return None

def generate_data_hash(data):
    """Generate a hash for the dataset to enable caching"""
    try:
        data_str = data.to_string()
        return hashlib.md5(data_str.encode()).hexdigest()[:16]
    except:
        return hashlib.md5(str(data.shape).encode()).hexdigest()[:16]

def generate_query_hash(query, data_context):
    """Generate a hash for query + context combination"""
    combined = f"{query}_{str(data_context)}"
    return hashlib.md5(combined.encode()).hexdigest()[:16]

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
            data = pd.read_csv(file, encoding="utf-8", errors="ignore")
            st.warning("⚠️ Some characters were ignored due to encoding issues.")
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
    st.title("AI Agent for Data-Driven Query Processing")

    input_option = st.radio("Select Data Source", ("Google Sheets URL", "Upload CSV File"))

    if input_option == "Google Sheets URL":
        handle_google_sheets()

    elif input_option == "Upload CSV File":
        handle_csv_upload()
    st.title("AI Agent for Data-Driven Query Processing")

    input_option = st.radio("Select Data Source", ("Google Sheets URL", "Upload CSV File"))

    if input_option == "Google Sheets URL":
        handle_google_sheets()

    elif input_option == "Upload CSV File":
        handle_csv_upload()

def handle_google_sheets():
    sheet_url = st.text_input("Enter Google Sheets URL")
    if sheet_url:
        if "docs.google.com/spreadsheets" not in sheet_url:
            st.warning("Please enter a valid Google Sheets URL.")
            return

        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        sheet_name = st.text_input("Enter sheet name (e.g., Sheet1)")

        if sheet_name:
            service = authenticate_google_sheets()
            if service:
                try:
                    range_name = f"{sheet_name}!A:Z"
                    values = read_google_sheet(service, sheet_id, range_name)
                    if values:
                        headers = values[0]
                        data = pd.DataFrame(values[1:], columns=headers)
                        st.write("Data from Google Sheets:")
                        st.dataframe(data, height=600)
                        main_column_selection(data)
                    else:
                        st.error("No data found in the specified range.")
                except Exception as e:
                    st.error(f"Error reading data from Google Sheets: {e}")
            else:
                st.error("Failed to authenticate with Google Sheets.")

def handle_csv_upload():
    uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx", "xls", "json"])
    if uploaded_file is not None:
        # Validate file first
        is_valid, message = validate_csv_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        st.success(f"✅ {message}")
        
        # Determine file type and read accordingly
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        with st.spinner(f"📖 Reading {file_extension} file..."):
            if file_extension == '.csv':
                data = secure_read_csv(uploaded_file)
            elif file_extension in ['.xlsx', '.xls']:
                data = secure_read_excel(uploaded_file)
            elif file_extension == '.json':
                data = secure_read_json(uploaded_file)
            else:
                st.error("Unsupported file format")
                return
        
        if data is not None:
            st.success(f"📊 Successfully loaded {len(data)} rows and {len(data.columns)} columns")
            st.write("Data preview:")
            st.dataframe(data.head(), height=300)
            main_column_selection(data)
        else:
            st.error("Failed to read the file. Please check the format and try again.")

def main_column_selection(data):
    if not data.empty:
        st.subheader("Step 1: Select Analysis Focus (Optional)")
        column_names = ["Auto-detect (Recommended)"] + data.columns.tolist()
        main_column = st.selectbox("Choose focus column or let AI auto-detect:", column_names)

        if main_column == "Auto-detect (Recommended)":
            st.success("✨ AI will automatically understand your queries for any column")
            main_column = data.columns[0]
        else:
            st.success(f"Selected focus column: {main_column}")
            
        st.info(f"📊 Dataset: {data.shape[0]} rows, {data.shape[1]} columns")
        with st.expander("📋 Column Overview"):
            for col in data.columns:
                unique_count = data[col].nunique()
                sample_vals = data[col].dropna().unique()[:5]
                st.write(f"**{col}**: {unique_count} unique values. Sample: {list(sample_vals)}")
        
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



def process_query(data, query, main_column):
    try:
        st.info("🤖 Analyzing your query with AI...")
        
        data_context = get_data_context(data)
        ai_response = query_gemini_ai(query, data)
        
        if ai_response and "no suitable" not in ai_response.lower() and "error" not in ai_response.lower():
            structured_result = extract_structured_data(ai_response, data, query)
            
            if structured_result is not None and not structured_result.empty:
                st.write("🎯 **AI Analysis Result:**")
                st.write(ai_response)
                return structured_result
            else:
                st.write("🤖 **AI Analysis:**")
                st.write(ai_response)
                return pd.DataFrame()
        
        st.info("Trying basic pattern matching as fallback...")
        return basic_fallback_processing(data, query, main_column)
        
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return None

def get_data_context(data):
    context = {
        "columns": list(data.columns),
        "dtypes": {col: str(data[col].dtype) for col in data.columns},
        "shape": data.shape,
        "sample_values": {},
        "numeric_columns": [],
        "categorical_columns": []
    }
    
    for col in data.columns:
        unique_vals = data[col].dropna().unique()
        if len(unique_vals) <= 20:
            context["sample_values"][col] = list(unique_vals)
        else:
            context["sample_values"][col] = list(unique_vals[:10]) + ["...more values"]
        
        if pd.api.types.is_numeric_dtype(data[col]):
            context["numeric_columns"].append(col)
        else:
            context["categorical_columns"].append(col)
    
    return context

def extract_structured_data(ai_response, data, original_query):
    try:
        response_lower = ai_response.lower()
        
        if any(phrase in response_lower for phrase in ['where', 'filter', 'records', 'rows']):
            filter_query = f"""
            Based on this data analysis response: "{ai_response}"
            And the original query: "{original_query}"
            
            Generate Python pandas filtering code that would extract the relevant records.
            Only return the filtering condition(s) as Python code that can be applied to a DataFrame called 'data'.
            
            Examples:
            - data[data['column'] == 'value']
            - data[(data['col1'] > 5) & (data['col2'] == 'text')]
            - data[data['column'].str.contains('pattern', case=False)]
            
            Available columns: {list(data.columns)}
            """
            
            filter_code_response = query_gemini_simple(filter_query)
            
            if filter_code_response and "data[" in filter_code_response:
                import re
                filter_match = re.search(r'data\[(.*?)\]', filter_code_response)
                if filter_match:
                    filter_expr = filter_match.group(1)
                    try:
                        filtered_data = data.query(filter_expr) if '.' not in filter_expr else eval(f"data[{filter_expr}]")
                        return filtered_data
                    except:
                        pass
        
        return None
    except:
        return None

def basic_fallback_processing(data, query, main_column):
    try:
        query_lower = query.lower()
        
        if main_column in data.columns:
            words = query_lower.split()
            for word in words:
                if len(word) > 2:
                    matches = data[data[main_column].astype(str).str.lower().str.contains(word, na=False)]
                    if not matches.empty:
                        st.write(f"Found {len(matches)} records containing '{word}' in {main_column}")
                        return matches
        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Fallback processing error: {e}")
        return pd.DataFrame()

def query_gemini_simple(query):
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY:
            return query_gemini(query, GEMINI_API_KEY)
        return None
    except:
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

def query_gemini_ai(query, data):
    try:
        # Generate hashes for caching
        data_hash = generate_data_hash(data)
        data_context = get_data_context(data)
        query_hash = generate_query_hash(query, data_context)
        
        # Check cache first
        cached_result = cached_ai_response(query_hash, data_hash)
        if cached_result:
            st.success("⚡ Retrieved from cache (faster response)")
            return cached_result
        
        # If not in cache, make API call
        response = query_gemini(query, GEMINI_API_KEY, data)
        
        # Store in cache for future use
        if response:
            cached_ai_response(query_hash, data_hash)
            
        return response
    except Exception as e:
        st.error(f"Error querying Gemini: {e}")
        return None
    try:
        # Generate hashes for caching
        data_hash = generate_data_hash(data)
        data_context = get_data_context(data)
        query_hash = generate_query_hash(query, data_context)
        
        # Check cache first
        cached_result = cached_ai_response(query_hash, data_hash)
        if cached_result:
            st.success("⚡ Retrieved from cache (faster response)")
            return cached_result
        
        # If not in cache, make API call
        response = query_gemini(query, GEMINI_API_KEY, data)
        
        # Store in cache for future use
        if response:
            cached_ai_response(query_hash, data_hash)
            
        return response
    except Exception as e:
        st.error(f"Error querying Gemini: {e}")
        return None

if __name__ == "__main__":
    try:
        # Set page configuration for better UX
        st.set_page_config(
            page_title="AI Data Agent",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Add custom CSS for better styling
        st.markdown("""
        <style>
        .main > div {
            padding-top: 1rem;
        }
        .stAlert > div {
            border-radius: 10px;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        main()
        
    except Exception as e:
        st.error("🚨 Critical Application Error")
        st.error(f"The application encountered an unexpected error: {str(e)}")
        st.info("Please refresh the page and try again. If the problem persists, contact support.")
        
        if st.checkbox("🔍 Show technical details"):
            st.code(str(e), language="python")
