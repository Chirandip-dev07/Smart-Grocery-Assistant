# Smart Grocery Assistant

A small Streamlit app that helps manage pantry items and generate meal suggestions and shopping lists.

## Deployment-ready changes made
- Removed embedded API key from `.streamlit/secrets.toml` (now empty). Use environment variables or Streamlit secrets for production.
- Added `.gitignore` with `.streamlit/secrets.toml` excluded.
- Added a `Procfile` for simple PaaS deployment (e.g., Heroku).

## Run locally
1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Provide your Google API key either via environment variable or Streamlit secrets.

- Environment variable (PowerShell):

```powershell
$env:GOOGLE_API_KEY = "your_api_key_here"
```

- Or add to `.streamlit/secrets.toml` (local only — do NOT commit your real key):

```toml
GOOGLE_API_KEY = "your_api_key_here"
```

4. Run the app:

```powershell
streamlit run app.py
```

## Deploy (example with Heroku)
1. Ensure `Procfile` exists (provided).
2. Set the `GOOGLE_API_KEY` as a config var on the platform.
3. Push the repo and deploy.

## Notes
- No code behavior in `app.py` was changed.
- Secrets are intentionally left out of the repository. Add keys via environment variables or your host's secrets manager before deploying.
