# AI Agent for Data-Driven Query Processing

A comprehensive data analysis platform combining Streamlit UI with AI-powered query processing capabilities.

## 🚀 Features

- **Data Input**: Upload CSV files or connect to Google Sheets
- **Smart Querying**: Dynamic filtering with natural language support
- **Web Search Integration**: Fallback to Google Custom Search when local data is insufficient  
- **AI Enhancement**: Google Gemini integration for intelligent data analysis
- **Export Options**: Download results as CSV or plain text

## 📁 Project Structure

```text
├── apps/streamlit-app/     # Main Streamlit application
│   ├── main.py            # Entry point
│   ├── google_api.py      # Google Sheets integration
│   ├── gemini_api.py      # AI processing
│   └── requirements.txt   # Dependencies
├── packages/pandas-ai/    # PandasAI backend (optional)
├── scripts/               # Utility scripts
├── docs/                 # Generated documentation  
└── infra/               # Infrastructure configs
```

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Google API credentials (for Sheets and Search)
- Gemini API key

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

3. **Set environment variables**

   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   export GOOGLE_API_KEY="your_google_api_key" 
   export SEARCH_ENGINE_ID="your_search_engine_id"
   ```

4. **Run the application**

   ```bash
   streamlit run apps/streamlit-app/main.py
   ```

## 🔧 Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_API_KEY=your_google_api_key
SEARCH_ENGINE_ID=your_custom_search_engine_id
```

### Google APIs Setup

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
