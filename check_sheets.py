import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def test_connection():
    sid = os.getenv("SPREADSHEET_ID")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    
    if not os.path.exists(cred_path):
        print(f"❌ File not found: {cred_path}")
        return

    try:
        creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata to see sheet names
        spreadsheet = service.spreadsheets().get(spreadsheetId=sid).execute()
        sheets = spreadsheet.get('sheets', [])
        
        print(f"✅ Connection Successful!")
        print("Available Tabs (Sheets):")
        for s in sheets:
            print(f"- {s.get('properties', {}).get('title')}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_connection()
