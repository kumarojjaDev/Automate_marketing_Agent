import google.generativeai as genai
from .models import Lead, CompanyInfo, LinkedInInfo
import os
import logging
import time

class EmailGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.primary_model = "models/gemini-2.0-flash" 
        self.fallback_model = "models/gemini-flash-latest"

    def generate(self, lead: Lead, company: CompanyInfo, linkedin: LinkedInInfo, retry_delay: int = 180) -> tuple[str, str]:
        # Prepare research context
        if linkedin.recent_post:
            context_label = "LINKEDIN POST"
            context_data = f'"{linkedin.recent_post}"'
        elif linkedin.about_section:
            context_label = "LINKEDIN BIO"
            context_data = f'"{linkedin.about_section}"'
        else:
            context_label = "LINKEDIN CONTEXT"
            context_data = "NOT FOUND"
        
        prompt = f"""
        PERSONALIZED OUTREACH AGENT
        Write an email as Anitha Vakamalla (Technical Lead at Pigeon-Tech) on behalf of CEO Vijay Anthony.
        
        LEAD: {lead.first_name} {lead.last_name} | {lead.role or linkedin.role} at {lead.company_name}
        RESEARCH: {company.mission[:300]}
        {context_label}: {context_data}
        
        LOGIC:
        1. **If LINKEDIN POST is found**: Reference it specifically as the hook.
        2. **If LINKEDIN Bio is found**: Reference their background/experience (e.g., "Reading about your experience with...").
        3. **If NO LinkedIn data**: Do NOT mention LinkedIn. Start by referencing their company's specific mission from RESEARCH.
        4. Identify a specific digital improvement area for {lead.company_name} based on their role.
        5. Connect Pigeon Suite (AI tours, AR/VR, Interactive Quizzes) as the solution.
        4. Tone: Peer-to-peer developer/consultant, professional, helpful.
        
        STRUCTURE:
        Subject: ...
        ---
        Dear {lead.first_name},
        
        ...Body...
        
        Explore Pigeon-Tech @ https://shorturl.at/qsIm6
        Get started with Pigeon Suite for only $175/month*.
        
        Regards,
        Anitha Vakamalla
        """
        
        max_retries = 3
        # Use passed retry_delay
        
        for attempt in range(max_retries):
            try:
                model_name = self.primary_model if attempt == 0 else self.fallback_model
                logging.info(f"AI Generation Request: {lead.first_name} ({model_name})")
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                content = response.text.strip()
                
                if "---" in content:
                    parts = content.split("---", 1)
                    return parts[0].replace("Subject:", "").strip(), parts[1].strip()
                else:
                    lines = content.split('\n')
                    return lines[0].replace("Subject:", "").strip(), '\n'.join(lines[1:]).strip()
                    
            except Exception as e:
                if "429" in str(e):
                    logging.warning(f"Rate limit hit. Quota cool-down for {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    logging.error(f"Generation error: {e}")
                    if attempt == max_retries - 1: 
                        logging.warning("Quota exhausted. Switching to FAIL-SAFE TEMPLATE.")
                        return self.generate_fallback(lead, company, linkedin)
                    time.sleep(20)
        
        logging.warning("All AI retries failed. Using FAIL-SAFE TEMPLATE.")
        return self.generate_fallback(lead, company, linkedin)

    def generate_fallback(self, lead: Lead, company: CompanyInfo, linkedin: LinkedInInfo) -> tuple[str, str]:
        """Non-AI fallback that adapts to available data."""
        
        # Determine the strongest hook
        if linkedin.recent_post:
            topic = "your recent updates on LinkedIn"
            hook_detail = f'("{linkedin.recent_post[:100]}...")'
            subject = f"Question about your post on LinkedIn"
        elif linkedin.about_section:
            topic = "your background on LinkedIn"
            hook_detail = f'(Specifically your experience: "{linkedin.about_section[:100]}...")'
            subject = f"Question about your experience at {lead.company_name}"
        else:
            # Fallback to Company Mission/Website
            topic = f"{lead.company_name}'s digital experience"
            mission_snippet = (company.mission or company.products_services or "your platform")[:100]
            hook_detail = f'(Specifically your focus on: "{mission_snippet}...")'
            subject = f"Idea for {lead.company_name}'s visitor strategy"
        
        # Improve phrasing for generic roles
        role_phrasing = lead.role or linkedin.role
        if role_phrasing.lower() in ["professional", "unknown", "none"]:
            role_phrasing = f"work at {lead.company_name}"
        else:
            role_phrasing = f"role as {role_phrasing}"

        body = f"""Dear {lead.first_name},

I was researching {lead.company_name} and saw {topic}.
{hook_detail}

Given your {role_phrasing}, I noticed a potential opportunity to improve the visitor experience at {lead.company_name} using interactive technology.

Pigeon-Tech helps venues like yours deploy AI-powered recognition and AR tours without heavy custom development.

I'd love to share a few ideas on how this could work for you. Assuming you are the right person, would you be open to a brief chat next week?

Regards,
Anitha Vakamalla
Technical Lead | Pigeon-Tech
"""
        return subject, body
