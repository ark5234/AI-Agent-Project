# AI-Powered Data Analysis Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0-red.svg)](https://streamlit.io)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-green.svg)](https://ai.google.dev)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen.svg)](https://ai-data-agent.streamlit.app/)

## 🚀 Live Demo

**Try it now:** [https://ai-data-agent.streamlit.app/](https://ai-data-agent.streamlit.app/)

Upload your data and start asking questions in natural language instantly!

## Overview

A comprehensive artificial intelligence platform for automated data analysis, query processing, and visualization. Built with Streamlit and powered by Google's Gemini AI, this application provides intelligent insights from CSV, Excel, and JSON datasets with natural language queries.

## Features

### Core Functionality
- **Multi-format Data Support**: Process CSV, Excel (xlsx/xls), and JSON files seamlessly
- **Natural Language Queries**: Ask questions about your data in plain English
- **AI-Powered Analysis**: Leverages Google Gemini AI for intelligent data interpretation
- **Smart Visualizations**: Automatically generates appropriate charts based on query context
- **Performance Optimization**: Implements intelligent caching for faster response times
- **Google Sheets Integration**: Direct connection to Google Sheets for live data analysis

### Advanced Features
- **Security Framework**: Comprehensive input validation and file size limitations
- **Error Boundaries**: Robust error handling with graceful degradation
- **Multi-source Fallback**: Web search integration when local analysis is insufficient
- **Cloud Deployment Ready**: Pre-configured for Streamlit Cloud with secrets management
- **Interactive Visualizations**: Plotly-powered charts with hover details and zoom capabilities

### Supported Visualizations
- Line charts for time series analysis
- Bar charts for categorical comparisons
- Scatter plots for correlation analysis
- Histograms for distribution analysis
- Pie charts for summary data
- Automatic chart type selection based on data characteristics

## Technical Architecture

### Technology Stack
- **Frontend**: Streamlit 1.40.0 for interactive web interface
- **Data Processing**: Pandas 2.2.3 with NumPy 2.1.3 for data manipulation
- **AI Integration**: Google Generative AI 0.8.5 with Gemini 1.5-flash/pro models
- **Visualizations**: Plotly 5.24.1 for interactive charts
- **Cloud Services**: Google APIs for Sheets integration and web search
- **File Processing**: OpenPyXL for Excel support, native JSON parsing

### Performance Features
- **Response Caching**: 30-minute TTL for AI responses to reduce API calls
- **Dataset Caching**: 1-hour TTL for dataset analysis results
- **Lazy Loading**: On-demand chart generation to optimize performance
- **Memory Management**: Safe processing decorators to handle large datasets

### Security Implementation
- **File Validation**: 50MB size limit with extension verification
- **Query Sanitization**: SQL injection prevention and content filtering
- **Input Validation**: Comprehensive user input checking
- **Error Isolation**: Safe execution boundaries to prevent crashes

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Google AI Studio API key

### Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ark5234/AI-Agent-Project.git
   cd AI-Agent-Project
   ```

2. **Install Dependencies**
   ```bash
   pip install -r apps/streamlit-app/requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   SEARCH_ENGINE_ID=your_search_engine_id_here
   ```

4. **Obtain API Keys**
   - **Gemini API**: Visit [Google AI Studio](https://aistudio.google.com/) to get your API key
   - **Google API**: Create credentials in [Google Cloud Console](https://console.cloud.google.com/)
   - **Search Engine**: Set up Custom Search Engine in Google

5. **Run the Application**
   ```bash
   streamlit run apps/streamlit-app/main.py
   ```

### Streamlit Cloud Deployment

1. **Push to GitHub**
   Ensure your code is in a GitHub repository

2. **Deploy to Streamlit Cloud**
   - Visit [Streamlit Cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - Select `apps/streamlit-app/main.py` as the main file

3. **Configure Secrets**
   In your Streamlit Cloud app settings, add secrets in TOML format:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   GOOGLE_API_KEY = "your_google_api_key_here"
   SEARCH_ENGINE_ID = "your_search_engine_id_here"
   ```

## Usage Guide

### Basic Data Analysis

1. **Upload Your Data**
   - Select "Upload CSV File" option
   - Choose from supported formats: CSV, Excel, JSON
   - Review the automatic data preview

2. **Ask Natural Language Questions**
   ```
   Example queries:
   - "Show me records where sales > 1000"
   - "What is the average price by category?"
   - "Count customers by region"
   - "Find products with low inventory"
   ```

3. **Review Results**
   - View filtered data tables
   - Examine automatically generated visualizations
   - Download results in CSV format

### Google Sheets Integration

1. **Select Google Sheets Option**
2. **Provide Sheet URL**
   ```
   https://docs.google.com/spreadsheets/d/your-sheet-id/edit
   ```
3. **Specify Sheet Name** (e.g., "Sheet1")
4. **Analyze Live Data** with the same query interface

### Advanced Query Examples

- **Trend Analysis**: "Show sales trend over time"
- **Comparison**: "Compare revenue by product category"
- **Distribution**: "Show age distribution of customers"
- **Correlation**: "Relationship between price and sales"
- **Filtering**: "Products launched in 2023 with rating > 4"

## Project Structure

```
AI-Agent-Project/
├── apps/
│   └── streamlit-app/
│       ├── main.py              # Primary application logic
│       ├── gemini_api.py        # AI integration module
│       ├── google_api.py        # Google services integration
│       ├── requirements.txt     # Python dependencies
│       └── credentials.json     # Google API credentials
├── .streamlit/
│   └── secrets.toml            # Cloud deployment secrets template
├── .env                        # Local environment variables
├── .gitignore                  # Git ignore patterns
├── LICENSE                     # MIT license
└── README.md                   # This documentation
```

## API Reference

### Core Functions

#### `validate_csv_file(file)`
Validates uploaded files for security and format compliance.
- **Parameters**: file object from Streamlit file uploader
- **Returns**: tuple (is_valid: bool, message: str)
- **Security**: Size limits, extension validation, content checking

#### `process_query(data, query, main_column)`
Processes natural language queries against dataset.
- **Parameters**: 
  - data: pandas DataFrame
  - query: string query in natural language
  - main_column: primary column for analysis focus
- **Returns**: processed DataFrame or analysis results

#### `generate_smart_visualizations(data, query, result_data)`
Creates appropriate visualizations based on query intent.
- **Parameters**: 
  - data: original dataset
  - query: user query for context
  - result_data: filtered/processed results
- **Returns**: Plotly figure object

### Configuration Options

#### Caching Settings
```python
@st.cache_data(ttl=1800)  # 30 minutes for AI responses
@st.cache_data(ttl=3600)  # 1 hour for dataset analysis
```

#### Security Parameters
- Maximum file size: 50MB
- Supported formats: CSV, XLSX, XLS, JSON
- Query length limit: 1000 characters
- SQL injection prevention: Active

## Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 Python style guidelines
2. **Documentation**: Include docstrings for all functions
3. **Testing**: Test all features before submitting pull requests
4. **Security**: Maintain input validation and error handling

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add comprehensive feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request with detailed description

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version compatibility (3.8+)

**API Key Issues**
- Confirm API keys are correctly set in environment variables or Streamlit secrets
- Verify API key permissions and quotas in respective consoles

**File Upload Problems**
- Check file size (must be under 50MB)
- Ensure supported file format (CSV, Excel, JSON)
- Verify file encoding (UTF-8 recommended)

**Performance Issues**
- Large datasets may require increased memory allocation
- Consider data sampling for very large files
- Monitor API usage to avoid rate limiting

### Support

For technical support and bug reports:
- Create an issue in the GitHub repository
- Provide detailed error messages and reproduction steps
- Include system information and Python version

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete details.

## Acknowledgments

- Google AI Studio for Gemini API access
- Streamlit team for the excellent web framework
- Plotly for interactive visualization capabilities
- Open source community for various Python libraries

## Author

**Vikrant Kawadkar** (@ark5234)
- Email: vikrantkawadkar2099@gmail.com
- GitHub: https://github.com/ark5234

---

**Version**: 2.0.0  
**Last Updated**: September 2025  
**Compatibility**: Python 3.8+, Streamlit 1.40.0+
