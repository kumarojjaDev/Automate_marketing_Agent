import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from services.google_sheets import GoogleSheetsService
from services.website_analyzer import WebsiteAnalyzer
from services.linkedin_enricher import LinkedInEnricher
from services.email_generator import EmailGenerator
from services.mail_sender import MailSender

# Setup logging with File Trace
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("activity.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

load_dotenv()

def process_leads():
    logging.info("🚀 Starting high-speed lead processing cycle...")
    
    # Initialize services
    gs = GoogleSheetsService(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"),
        credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH")
    )
    wa = WebsiteAnalyzer()
    le = LinkedInEnricher(api_key=os.getenv("LINKEDIN_API_KEY"))
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    eg = EmailGenerator(api_key=gemini_key) if gemini_key else None
    
    ms_user = os.getenv("SMTP_USERNAME")
    ms = MailSender(
        smtp_server=os.getenv("SMTP_SERVER"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=ms_user,
        password=os.getenv("SMTP_PASSWORD")
    ) if ms_user else None

    # Limit batch size to 5 to allow frequent re-checks
    leads = gs.get_pending_leads()[:5] 
    
    if leads:
        msg = f"⏳ Found {len(leads)} leads. Starting Batch Processing (One-by-One)..."
        print(msg)
        logging.info(msg)
        # 3 minute cooling ONLY if we actually have work
        time.sleep(180) 

    for lead in leads:
        try:
            name = f"{lead.first_name} {lead.last_name}"
            logging.info(f"👉 Processing: {name} ({lead.email})")
            
            # 1. Lock Row (Status -> RESEARCHING)
            gs.lock_row(lead.row_index)
            
            # 2. Analyze Website (Agent 1)
            print(f"   🌐 Analyzing website: {lead.company_website}...")
            company_info = wa.analyze(lead.company_website)
            lead.company_summary = (company_info.mission or "")[:200]
            
            # 3. Enrich LinkedIn (Agent 2)
            print(f"   👤 Enriching LinkedIn (Live Search): {lead.linkedin_url}...")
            # Use name and company for search query
            full_name = f"{lead.first_name} {lead.last_name}"
            linkedin_info = le.enrich(lead.linkedin_url, name=full_name, company=lead.company_name)
            
            # OVERRIDE with Sheet Data if available (User Request)
            if lead.linkedin_post:
                print(f"   📝 Using LinkedIn Post from Sheet: {lead.linkedin_post[:50]}...")
                linkedin_info.recent_post = lead.linkedin_post
                linkedin_info.verification_level = "user_provided"
            
            lead.role = lead.role or linkedin_info.role
            lead.personal_hook = f"Interested in your work on {', '.join(linkedin_info.activity_themes[:2])}"
            
            # 4. Generate Email (Agent 3)
            print(f"   ✍️ Generating personalized email via Gemini...")
            if eg:
                subject, body = eg.generate(lead, company_info, linkedin_info)
            else:
                subject, body = f"Draft for {lead.last_name}", f"Simulation Mode: No Gemini Key provided."
            
            lead.email_subject = subject
            lead.email_body = body
            lead.status_note = f"Personalized via AI. Target: {linkedin_info.role}"

            # 5. Send Email (Execution)
            if ms:
                print(f"   📧 Sending real email to {lead.email}...")
                success = ms.send_email(lead.email, subject, body)
            else:
                print(f"   📧 [SIMULATION] Skipping send for {lead.email}")
                success = True
            
            if success:
                lead.status = "SENT"
                lead.email_sent_at = datetime.now().isoformat()
                logging.info(f"✅ Email SENT successfully to {name}")
            else:
                lead.status = "FAILED"
                logging.error(f"❌ Failed to send email to {name}")
                
            # 6. Final Update to Google Sheet
            gs.update_lead_status(lead)
            
            logging.info(f"✅ [SUCCESS] Outreach complete for {name}. Waiting 120s for safe quota reset...")
            time.sleep(120)

        except Exception as e:
            name = f"{lead.first_name} {lead.last_name}"
            logging.error(f"💥 Error processing {name}: {e}")
            # Log the full error to the sheet so the user can see it
            lead.status = "ERROR"
            error_msg = str(e)
            if "429" in error_msg:
                lead.status_note = "Rate limit hit. Retrying later."
            elif "404" in error_msg:
                lead.status_note = "AI Model not found. Check settings."
            else:
                lead.status_note = error_msg[:100]
            gs.update_lead_status(lead)
            time.sleep(5) # Small sleep after error

    to_process = len(leads)
    logging.info(f"Cycle complete. Processed {to_process} leads.")

def main():
    # 10-minute cycle as requested
    interval = 600 
    while True:
        try:
            process_leads()
        except Exception as e:
            logging.error(f"🛑 Critical error in main loop: {e}")
        
        logging.info(f"💤 Cycle complete. Waiting {interval}s (10 min) for new leads...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
