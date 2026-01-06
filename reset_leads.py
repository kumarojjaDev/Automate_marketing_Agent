import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def reset_all_leads():
    sid = os.getenv("SPREADSHEET_ID")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)
    
    # Reset status (J) and note (K) for Row 2-10
    print(f"Resetting leads in {sid}...")
    try:
        body = {'values': [["PENDING", "Clean start for personalized campaign"]] * 9}
        service.spreadsheets().values().update(
            spreadsheetId=sid, range="Sheet1!J2:K10", 
            valueInputOption="RAW", body=body
        ).execute()
        print("✅ Sheet1 Reset Successful (Rows 2-10)")
    except Exception as e:
        print(f"❌ Reset Failed: {e}")

if __name__ == "__main__":
    reset_all_leads()
