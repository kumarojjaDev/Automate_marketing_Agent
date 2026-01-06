import os
from dotenv import load_dotenv
from services.google_sheets import GoogleSheetsService

load_dotenv()

sid = os.getenv("SPREADSHEET_ID")
cred = os.getenv("GOOGLE_CREDENTIALS_PATH")

print(f"Testing ID: {sid}")
print(f"Testing Cred Path: {cred}")

gs = GoogleSheetsService(sid, cred)
try:
    leads = gs.get_pending_leads()
    print(f"✅ Success! Found {len(leads)} leads in your REAL Google Sheet.")
    for l in leads:
        print(f"- {l.first_name} {l.last_name}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Tip: Make sure you shared the sheet with email-bot@leads-481712.iam.gserviceaccount.com as an 'Editor'.")
