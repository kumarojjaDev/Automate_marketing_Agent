import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from .models import Lead
from datetime import datetime
import json

class GoogleSheetsService:
    def __init__(self, spreadsheet_id: str, credentials_path: str):
        self.spreadsheet_id = spreadsheet_id
        # Strict check for credentials presence
        if spreadsheet_id and credentials_path and os.path.exists(credentials_path):
            try:
                self.local_mode = False
                self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
                self.creds = Credentials.from_service_account_file(credentials_path, scopes=self.scopes)
                self.service = build('sheets', 'v4', credentials=self.creds)
                print(f"✅ REMOTE MODE: Connected to {spreadsheet_id}")
            except Exception as e:
                print(f"❌ AUTH ERROR: {e}. Falling back to local.")
                self.local_mode = True
        else:
            self.local_mode = True
            print("⚠️ LOCAL MODE: Using local_leads.json")

    def get_pending_leads(self, sheet_name: str = "Sheet1") -> list[Lead]:
        if self.local_mode:
            if not os.path.exists("local_leads.json"): return []
            with open("local_leads.json", "r") as f:
                data = json.load(f)
            return [Lead(**l) for l in data if l.get("status") in ["NEW", "PENDING", None]]

        try:
            sheet = self.service.spreadsheets()
            # Extended range to include Column V
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!A2:V").execute()
            values = result.get('values', [])
            
            leads = []
            for i, row in enumerate(values):
                while len(row) < 22: row.append("") # Ensure we have up to Col V (21)
                status = row[9]
                print(f"DEBUG: Row {i+2} status is '{status}'")
                if not status or status.strip().upper() in ["NEW", "PENDING"]:
                    leads.append(Lead(
                        lead_id=row[0], first_name=row[1], last_name=row[2],
                        email=row[3], linkedin_url=row[4], company_name=row[5],
                        company_website=row[6], role=row[7],
                        intent_score=float(row[8]) if row[8] and row[8].strip().replace('.','').isnumeric() else 0.0,
                        status=status, status_note=row[10], row_index=i + 2,
                        linkedin_post=row[21] # New field for user provided post
                    ))
            return leads
        except Exception as e:
            print(f"❌ Error fetching leads: {e}")
            return []

    def update_lead_status(self, lead: Lead, sheet_name: str = "Sheet1"):
        if self.local_mode:
            with open("local_leads.json", "r") as f:
                data = json.load(f)
            for i, l in enumerate(data):
                if str(l.get("lead_id")) == str(lead.lead_id):
                    data[i] = lead.dict()
            with open("local_leads.json", "w") as f:
                json.dump(data, f, indent=2)
            return

        try:
            update_range = f"{sheet_name}!J{lead.row_index}:U{lead.row_index}"
            values = [[
                lead.status, lead.status_note or "", datetime.now().isoformat(),
                lead.next_action_at or "", lead.company_summary or "",
                lead.personal_hook or "", lead.angle or "", lead.cta or "",
                lead.email_subject or "", lead.email_body or "",
                lead.email_sent_at or "", lead.email_message_id or ""
            ]]
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=update_range,
                valueInputOption="RAW", body={'values': values}
            ).execute()
        except Exception as e:
            print(f"❌ Error updating status: {e}")

    def lock_row(self, row_index: int, sheet_name: str = "Sheet1"):
        if self.local_mode:
            with open("local_leads.json", "r") as f:
                data = json.load(f)
            for l in data:
                if l.get("row_index") == row_index:
                    l["status"] = "RESEARCHING"
                    l["status_note"] = "research_started"
            with open("local_leads.json", "w") as f:
                json.dump(data, f, indent=2)
            return

        try:
            update_range = f"{sheet_name}!J{row_index}:K{row_index}"
            body = {'values': [["RESEARCHING", "research_started"]]}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=update_range,
                valueInputOption="RAW", body=body
            ).execute()
        except Exception as e:
            print(f"❌ Error locking row: {e}")
