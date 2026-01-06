import requests
from bs4 import BeautifulSoup
from .models import CompanyInfo
import logging

class WebsiteAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def analyze(self, url: str) -> CompanyInfo:
        if not url:
            return CompanyInfo(name="Invalid URL", highlights="No website provided")
            
        if not url.startswith('http'):
            url = 'https://' + url
            
        try:
            print(f"🔍 Analyzing website: {url}...")
            response = requests.get(url, headers=self.headers, timeout=12)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string if soup.title else ""
            
            # Find meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc['content'] if meta_desc and meta_desc.has_attr('content') else ""
            
            # Extract more text for the AI to "read"
            # Get headings and top paragraphs
            headings = [h.text.strip() for h in soup.find_all(['h1', 'h2'])[:5]]
            paragraphs = [p.text.strip() for p in soup.find_all('p')[:8] if len(p.text.strip()) > 30]
            
            combined_text = " | ".join(headings) + " -- " + " ".join(paragraphs)
            
            return CompanyInfo(
                name=title.split('|')[0].strip() if title else url,
                industry="Analyzed from Content", 
                products_services=description[:300] if description else "Check content for services",
                mission=combined_text[:1000] if combined_text else "", 
                highlights="Website live and content extracted."
            )
        except Exception as e:
            logging.error(f"Error analyzing website {url}: {e}")
            return CompanyInfo(name=url, highlights=f"Failed to reach website: {str(e)}", mission="", products_services="", industry="")
