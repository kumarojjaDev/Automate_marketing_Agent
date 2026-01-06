# AI Lead Enrichment & Email Automation System

This system automates the process of lead research and personalized outreach.

## System Architecture
The system uses a **Service-Oriented Architecture** (SOA) built in Python:
- **Orchestrator (`main.py`)**: Manages the 10-minute polling loop and coordinate service interactions.
- **Google Sheets Service**: Handles row locking, reading pending leads, and updating statuses.
- **Website Analyzer**: Extracts mission and product data from company sites.
- **LinkedIn Enricher**: Uses safe methods (APIs/Search) to infer activity themes and roles.
- **Email Generator**: Integrates Gemini 1.5 Flash to create personalized, high-quality emails.
- **Mail Sender**: SMTP-based delivery with exponential backoff retry logic.

## Setup Instructions
1. **Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate
   pip install requests beautifulsoup4 google-api-python-client google-auth-oauthlib google-auth-httplib2 google-generativeai pydantic python-dotenv
   ```
2. **Configuration**:
   - Copy `.env.example` to `.env`.
   - Fill in your `SPREADSHEET_ID`, `GEMINI_API_KEY`, and `SMTP` credentials.
   - Place your Google Service Account credentials JSON and set the path in `GOOGLE_CREDENTIALS_PATH`.

3. **Google Sheet Headers**:
   Ensures your sheet has columns in this exact order:
   `Full Name | Email | Company Name | Company Website | LinkedIn Profile URL | Status | Updated At | Email Subject | Email Body | LinkedIn Level | Verification Notes`

4. **Running**:
   You can start all three components (Backend, API, and Dashboard) simultaneously using the provided script:
   ```powershell
   ./start-all.ps1
   ```
   Alternatively, run them in separate terminals:
   - **Backend**: `python main.py`
   - **API Bridge**: `cd dashboard-api && node server.js`
   - **Frontend**: `cd dashboard-ui && npm run dev`

## Compliance & Safety
- **No Scraping**: The LinkedIn module is designed to use official enrichment APIs or public search snippets.
- **Non-Generic Outreach**: AI is prompted to prioritize professional tone and specific activity hooks over generic templates.
- **Locking**: Row-level status updates prevent duplicate processing.
