import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def list_headers():
    sid = os.getenv("SPREADSHEET_ID")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    
    result = service.spreadsheets().values().get(spreadsheetId=sid, range="Sheet1!A1:Z1").execute()
    values = result.get('values', [])
    
    if values:
        headers = values[0]
        print("Sheet Headers:")
        for i, h in enumerate(headers):
            print(f"{i}: {h}")
    else:
        print("No headers found.")

if __name__ == "__main__":
    list_headers()
