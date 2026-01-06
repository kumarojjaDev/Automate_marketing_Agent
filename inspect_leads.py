import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def inspect_leads():
    sid = os.getenv("SPREADSHEET_ID")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    
    creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    
    result = service.spreadsheets().values().get(spreadsheetId=sid, range="Sheet1!A1:K10").execute()
    values = result.get('values', [])
    
    print(f"{'Row':<5} | {'Name':<20} | {'Status':<15}")
    print("-" * 45)
    for i, row in enumerate(values):
        if i == 0: continue # Skip header
        name = f"{row[1]} {row[2]}" if len(row) > 2 else "Unknown"
        status = row[9] if len(row) > 9 else "EMPTY"
        print(f"{i+1:<5} | {name:<20} | {status:<15}")

if __name__ == "__main__":
    inspect_leads()
