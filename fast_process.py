import os
import logging
import traceback
from dotenv import load_dotenv
from services.google_sheets import GoogleSheetsService
from services.website_analyzer import WebsiteAnalyzer
from services.linkedin_enricher import LinkedInEnricher
from services.email_generator import EmailGenerator
from services.mail_sender import MailSender
from datetime import datetime

# Configure concise logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
load_dotenv()

def fast_process_one_lead():
    print("STARTING FAST PROCESS (Skipping Safety Delays)...")
    
    # Initialize services
    gs = GoogleSheetsService(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"),
        credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH")
    )
    wa = WebsiteAnalyzer()
    le = LinkedInEnricher(api_key=os.getenv("LINKEDIN_API_KEY")) # Will fallback to DDG search
    eg = EmailGenerator(api_key=os.getenv("GEMINI_API_KEY"))
    # FORCE OVERRIDE model for fast process to avoid rate limits
    eg.primary_model = "models/gemini-2.0-flash-exp" 
    eg.fallback_model = "models/gemini-1.5-flash"
    
    ms_user = os.getenv("SMTP_USERNAME")
    ms = MailSender(
        smtp_server=os.getenv("SMTP_SERVER"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=ms_user,
        password=os.getenv("SMTP_PASSWORD")
    )

    leads = gs.get_pending_leads()
    print(f"Found {len(leads)} pending leads.")

    if not leads:
        print("No leads found. Please reset or add leads.")
        return

    # Process ONLY the first lead
    lead = leads[0]
    try:
        name = f"{lead.first_name} {lead.last_name}"
        print(f"Processing: {name} ({lead.email})")
        
        # 1. Lock Row
        gs.lock_row(lead.row_index)
        
        # 2. Analyze Website
        print(f"   Analyzing website: {lead.company_website}...")
        try:
            company_info = wa.analyze(lead.company_website)
            lead.company_summary = (company_info.mission or "")[:200]
        except Exception as e:
             print(f"   Website analysis partial fail: {e}")
             lead.company_summary = "Company analysis pending."

        # 3. Enrich LinkedIn (Agent 2)
        print(f"   Enriching LinkedIn: {lead.linkedin_url}...")
        full_name = f"{lead.first_name} {lead.last_name}"
        linkedin_info = le.enrich(lead.linkedin_url, name=full_name, company=lead.company_name)
        
        # Override with Sheet Data if available
        if lead.linkedin_post:
            print(f"   Using LinkedIn Post from Sheet: {lead.linkedin_post[:50]}...")
            linkedin_info.recent_post = lead.linkedin_post
        
        lead.role = lead.role or linkedin_info.role
        
        # 4. Generate Email
        print(f"   Generating personalized email via Gemini (Rush Mode)...")
        # Retry delay = 1 second to trigger fallback immediately if quota hits
        subject, body = eg.generate(lead, company_info, linkedin_info, retry_delay=1)
        
        lead.email_subject = subject
        lead.email_body = body
        
        print(f"\nGENERATED EMAIL:\nSubject: {subject}\nBody: {body[:100]}...\n")

        # 5. Send Email
        print(f"   Sending email to {lead.email}...")
        success = ms.send_email(lead.email, subject, body)
        
        if success:
            lead.status = "SENT"
            lead.email_sent_at = datetime.now().isoformat()
            lead.status_note = "Fast Process Success"
            print("EMAIL SENT SUCCESSFULLY!")
        else:
            lead.status = "FAILED"
            print("EMAIL SEND FAILED.")
            
        # 6. Update Sheet
        gs.update_lead_status(lead)

    except Exception as e:
        print(f"💥 Error processing {name}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    fast_process_one_lead()
