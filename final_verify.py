import os
import smtplib
from dotenv import load_dotenv
import google.generativeai as genai
from services.google_sheets import GoogleSheetsService

load_dotenv()

def verify_all():
    print("🎬 Starting Final Verification...")
    
    # 1. Google Sheets
    print("\n📊 Checking Google Sheets...")
    try:
        sid = os.getenv("SPREADSHEET_ID")
        cred = os.getenv("GOOGLE_CREDENTIALS_PATH")
        gs = GoogleSheetsService(sid, cred)
        leads = gs.get_pending_leads()
        print(f"✅ Google Sheets Connected! Found {len(leads)} pending leads in 'Leads' tab.")
    except Exception as e:
        print(f"❌ Google Sheets Failed: {e}")
        return False

    # 2. AI (Gemini)
    print("\n🧠 Checking AI (Gemini)...")
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, reply with 'AI Verified'")
        print(f"✅ Gemini Response: {response.text.strip()}")
    except Exception as e:
        print(f"❌ Gemini Failed: {e}")
        return False

    # 3. SMTP
    print("\n📧 Checking SMTP Authentication...")
    try:
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
        server.starttls()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD").replace(" ", ""))
        server.quit()
        print("✅ SMTP Authentication Successful!")
    except Exception as e:
        print(f"❌ SMTP Failed: {e}")
        return False

    print("\n🎉 ALL SYSTEMS READY! Launching project...")
    return True

if __name__ == "__main__":
    verify_all()
