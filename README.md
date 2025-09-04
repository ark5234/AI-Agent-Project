# 🤖 AI Agent for Data-Driven Query Processing

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0-red.svg)](https://streamlit.io)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-green.svg)](https://ai.google.dev)

## 🌟 Overview

A powerful, adaptive AI-powered data analysis platform that uses Google's Gemini AI to understand and process natural language queries on any dataset. This system automatically adapts to different data structures without requiring hardcoded patterns or manual configuration.

### ✨ Key Features

- **🧠 Zero-Hardcoding Architecture**: Automatically understands any dataset structure without manual configuration
- **🗣️ Natural Language Processing**: Ask questions in plain English - AI understands complex queries automatically
- **📊 Universal Data Support**: Works with any CSV dataset or Google Sheets
- **🚀 Adaptive Intelligence**: AI-first approach that learns your data structure on the fly
- **⚡ Fast & Intuitive**: Clean, modern Streamlit interface with instant results
- **🔍 Smart Fallbacks**: Multi-layered processing with web search integration
- **Export Options**: Download results as CSV or plain text
## �️ Technology Stack

- **Backend**: Python 3.13, pandas 2.2.3, numpy 2.1.3
- **AI Engine**: Google Gemini 1.5-Flash/Pro with automatic model fallback
- **Frontend**: Streamlit 1.40.0 with interactive data visualization
- **APIs**: Google Sheets API, Google Custom Search API
- **Environment**: python-dotenv for secure configuration management

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ installed
- Google Cloud Project with enabled APIs
- Gemini API key from Google AI Studio

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ark5234/AI-Agent-Project.git
   cd AI-Agent-Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r apps/streamlit-app/requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Required: Gemini AI API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional: For Google Sheets and web search
   GOOGLE_API_KEY=your_google_api_key_here
   SEARCH_ENGINE_ID=your_search_engine_id_here
   ```

4. **Run the application**
   ```bash
   python -m streamlit run apps/streamlit-app/main.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🎯 Usage Examples

### Natural Language Queries

The AI understands various query patterns automatically:

```
✅ "Show me all records where status is approved"
✅ "Count how many customers have income above 50000"
✅ "Find all entries with credit card as loan purpose"
✅ "Display records where age is between 25 and 35"
✅ "What percentage of applicants were rejected?"
```

### Data Sources

- **CSV Upload**: Drag and drop any CSV file
- **Google Sheets**: Paste your Google Sheets URL
- **Auto-Detection**: AI automatically understands column types and relationships

## 🏗️ Project Structure

```
AI-Agent-Project/
├── apps/
│   └── streamlit-app/           # Main application
│       ├── main.py              # Streamlit interface & core logic
│       ├── gemini_api.py        # Gemini AI integration
│       ├── google_api.py        # Google Sheets API
│       └── requirements.txt     # Dependencies
├── .env                         # Environment variables
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## 🔧 Configuration

### API Keys Setup

1. **Gemini API Key** (Required)
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Add to `.env` as `GEMINI_API_KEY`

2. **Google APIs** (Optional)
   - Enable Google Sheets API and Custom Search API
   - Create service account credentials
   - Add keys to `.env`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Your Gemini AI API key |
| `GOOGLE_API_KEY` | ❌ Optional | For Google services |
| `SEARCH_ENGINE_ID` | ❌ Optional | For web search fallback |

## 🧠 How It Works

### Adaptive Processing Pipeline

1. **Data Ingestion**: Upload CSV or connect Google Sheets
2. **AI Analysis**: Gemini automatically analyzes dataset structure
3. **Query Understanding**: Natural language processing interprets user intent
4. **Smart Execution**: AI generates appropriate pandas operations
5. **Result Delivery**: Structured data with download options

### Key Innovations

- **Zero-Hardcoding**: No predefined patterns or column assumptions
- **Adaptive Schema Detection**: Automatically understands any data structure
- **Intelligent Query Mapping**: Maps natural language to precise data operations
- **Multi-Model Fallback**: Automatic model switching for optimal performance

## � Recent Improvements

### v2.0 - Adaptive AI Architecture
- ✅ Eliminated all hardcoded patterns and assumptions
- ✅ Implemented AI-first query processing
- ✅ Added automatic dataset structure detection
- ✅ Enhanced natural language understanding
- ✅ Streamlined codebase and dependencies

### Performance Optimizations
- ⚡ Reduced dependencies from 20+ to 9 core packages
- ⚡ Improved query processing speed with smart caching
- ⚡ Enhanced UI responsiveness with async operations

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ark5234/AI-Agent-Project/issues)
- **Email**: Support available through GitHub

---

<div align="center">
<strong>Built with ❤️ using Google Gemini AI</strong>
<br>
<em>Making data analysis accessible through natural language</em>
</div>

1. **Google Sheets API**:
   - Enable Google Sheets API in Google Cloud Console
   - Download `credentials.json` and place in `apps/streamlit-app/`

2. **Google Custom Search**:
   - Create a Custom Search Engine at <https://cse.google.com>
   - Note the Search Engine ID

3. **Google Gemini**:
   - Get API key from Google AI Studio

## 🎯 Usage

1. **Select Data Source**: Choose between CSV upload or Google Sheets URL
2. **Data Preview**: View your data in an interactive table
3. **Choose Main Column**: Select the primary column for analysis
4. **Enter Query**: Use natural language or specific filters
5. **Get Results**: View filtered data, web search results, or AI analysis
6. **Export**: Download results as CSV or text file

## 🏗️ Backend (Optional)

The project includes a PandasAI backend server:

- **Location**: `packages/pandas-ai/`
- **Setup**: See `packages/pandas-ai/server/README.md`
- **Stack**: FastAPI + PostgreSQL + Next.js client

## 📚 Documentation

- **Architecture**: See `ARCHITECTURE.md`
- **API Routes**: `docs/fastapi_routes.json`
- **Security**: Don't commit secrets or virtual environments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see `LICENSE` file for details.

## 👨‍💻 Author

**Vikrant Kawadkar** (@ark5234)

- Email: <vikrantkawadkar2099@gmail.com>
