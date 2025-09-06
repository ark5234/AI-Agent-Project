# Streamlit Cloud Deployment Instructions

## � IMPORTANT: Updated File Path

**After project restructure, the main file path has changed:**
- ❌ Old path: `apps/streamlit-app/main.py`
- ✅ New path: `main.py`

**If your deployment is failing, update the main file path in Streamlit Cloud settings!**

## 🚀 Setting Up Your Streamlit Cloud App

### Step 1: Deploy New App or Update Existing
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. **For New Deployment:**
   - Click "New app"
   - Repository: `ark5234/AI-Agent-Project`
   - Branch: `master`
   - **Main file path**: `main.py` (NOT `apps/streamlit-app/main.py`)
3. **For Existing App:**
   - Find your app in the dashboard
   - Click "⚙️ Settings"
   - Update main file path to `main.py`
   - Save and redeploy

### Step 2: Add Your API Keys
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Find your deployed app: `AI-Agent-Project`
3. Click the "⚙️" (Settings) button
4. Navigate to the "Secrets" tab

### Step 2: Add Your API Keys
Copy and paste the following into the secrets text area:

```toml
GEMINI_API_KEY = "AIzaSyCQp3Wb6e1wmgylk4nuH8lC1g5R1euqAks"
GOOGLE_API_KEY = "AIzaSyC6lHAGoWbW_tPg1Vn4SHlDF0zutkcacRA"
GOOGLE_SEARCH_ENGINE_ID = "f3bd297a2efdf4270"
```

### Step 3: Save and Deploy
1. Click "Save" in the secrets section
2. Your app will automatically restart with the new secrets
3. Test the Google Sheets functionality

## 🔧 Troubleshooting

### Common Issues:
- **Invalid TOML Format**: Make sure there are no extra spaces or special characters
- **API Key Errors**: Verify your keys are correctly copied
- **Google Sheets Access**: Ensure your sheet is publicly accessible

### Testing Your Setup:
1. Go to your live app: https://ai-data-agent.streamlit.app/
2. Try the Google Sheets URL feature
3. Use the test URL: `https://docs.google.com/spreadsheets/d/15puRis-kWLS0eJ53O8t6utoOavH4yTo02IynnTf0w-U/edit`
4. Select "Sheet1" when prompted

## 📊 Your Test Data
- **Sheet**: RAS Finance and reg
- **Records**: 82 students
- **Columns**: NO, Name, Reg No, BRANCH, Mobile No, DSW FORM, CC Member, need to call

## ✅ Success Indicators
- No "API Key Missing" errors
- Google Sheets data loads successfully
- AI analysis works with your data
- All features functional in production
