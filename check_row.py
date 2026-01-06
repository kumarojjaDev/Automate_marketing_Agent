import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def inspect_row_2():
    sid = os.getenv("SPREADSHEET_ID")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    
    # Read Row 2 widely to include Column V (Index 21)
    result = service.spreadsheets().values().get(spreadsheetId=sid, range="Sheet1!A2:V2").execute()
    values = result.get('values', [])
    
    if values:
        row = values[0]
        print("Row 2 Data:")
        for i, cell in enumerate(row):
            val = cell[:50] + "..." if isinstance(cell, str) and len(cell)>50 else cell
            print(f"Col {i}: {val}")
        
        if len(row) > 21:
            print(f"\n✅ FOUND DATA IN COL 21 (V): {row[21]}")
        else:
            print(f"\n⚠️ COL 21 (V) IS EMPTY or MISSING.")
    else:
        print("No data in Row 2.")

if __name__ == "__main__":
    inspect_row_2()
