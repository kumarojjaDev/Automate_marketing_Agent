import os
import logging
import traceback
from dotenv import load_dotenv
from main import process_leads

# Set logging to DEBUG for maximum visibility
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

print("🔍 STARTING DEEP DIAGNOSTIC...")
try:
    process_leads()
    print("✅ Pass complete.")
except Exception as e:
    print(f"❌ CRITICAL ERROR during process_leads:")
    traceback.print_exc()
