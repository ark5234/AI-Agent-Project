# AI-Agent-Project (Monorepo)

## Layout

- apps/
  - streamlit-app/ (Streamlit UI)
- packages/
  - pandas-ai/ (Backend server + web client)
- infra/ (infra-as-code)
- scripts/ (utilities)
- docs/ (generated docs)

## Quickstart

- Streamlit app
  1. Create/activate a Python 3.11 venv
  2. `pip install -r apps/streamlit-app/requirements.txt`
  3. Set env: GEMINI_API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID
  4. `streamlit run apps/streamlit-app/main.py`

- Backend server
  - Use Docker Compose in `packages/pandas-ai` (requires Postgres)
  - Or run `packages/pandas-ai/server/main.py` with a Python 3.11 venv and a live Postgres set in `.env`

## Security notes

- Don’t commit venvs or secrets. Ensure `.env`, any `token.pickle`, and `env/` are ignored.
- If a secret was pushed, rotate it and remove from history. Example (requires git-filter-repo):
  1. `pip install git-filter-repo`
  2. `git filter-repo --invert-paths --path app/token.pickle --path env --path ai_agent_env`
