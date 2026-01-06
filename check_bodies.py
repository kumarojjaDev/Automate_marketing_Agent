import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def print_bodies():
    sid = os.getenv("SPREADSHEET_ID")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    
    result = service.spreadsheets().values().get(spreadsheetId=sid, range="Sheet1!A1:S6").execute()
    values = result.get('values', [])
    
    for i, row in enumerate(values):
        if i == 0: continue
        name = f"{row[1]} {row[2]}" if len(row) > 2 else "Unknown"
        status = row[9] if len(row) > 9 else "EMPTY"
        subject = row[17] if len(row) > 17 else "NO SUBJECT"
        body = row[18] if len(row) > 18 else "NO BODY"
        print(f"--- Lead: {name} | Status: {status} ---")
        print(f"Subject: {subject}")
        print(f"Body snippet: {body[:200]}...")
        print("\n")

if __name__ == "__main__":
    print_bodies()
