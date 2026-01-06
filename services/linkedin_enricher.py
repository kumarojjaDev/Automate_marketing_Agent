import os
import logging
from .models import LinkedInInfo
from duckduckgo_search import DDGS
import time

class LinkedInEnricher:
    def __init__(self, api_key: str = None, provider: str = "search"):
        self.api_key = api_key
        self.provider = provider 

    def enrich(self, linkedin_url: str, name: str = "", company: str = "") -> LinkedInInfo:
        """
        Enriches LinkedIn data using DuckDuckGo Search to find dynamic snippets.
        """
        try:
            logging.info(f"🔍 Searching DDG for: {name} {company}")
            
            role = "Professional"
            recent_post = None # Initialize as None, not string
            themes = []
            
            # Query strings - Relaxed to improve hit rate
            queries = [
                f"{name} {company} LinkedIn",
                f"{name} {company} site:linkedin.com/in/"
            ]
            
            profile_results = []
            for q in queries:
                print(f"   SEARCHING: '{q}'")
                try:
                    results = list(ddgs.text(q, max_results=2))
                    if results:
                        profile_results = results
                        break
                except Exception as ex:
                    print(f"   Search failed for '{q}': {ex}")
                    time.sleep(2)
            
            if profile_results:
                # Snippet often contains: "Name - Role - Company..."
                snippet = profile_results[0].get('body', '') or profile_results[0].get('title', '')
                try:
                    with open("search_proof.txt", "a", encoding="utf-8") as f:
                        f.write(f"SNIPPET FOUND: {snippet}\n")
                except: pass
                    
                    # Robust Parsing
                    detected_role = "Unknown"
                    if "-" in snippet:
                        parts = snippet.split("-")
                        if len(parts) > 1:
                            role_candidate = parts[1].strip()
                            # Clean up common garbage
                            role_candidate = role_candidate.split("|")[0].split(" at ")[0].strip()
                            if len(role_candidate) > 2 and len(role_candidate) < 60:
                                detected_role = role_candidate
                                print(f"   EXTRACTED ROLE: {detected_role}")
                    
                    if detected_role == "Unknown" or detected_role == "Professional":
                        # Attempt to parse from the start if it looks like a title
                        if " at " in snippet:
                             potential = snippet.split(" at ")[0].strip()
                             if len(potential) < 50:
                                 detected_role = potential

                    # Fallback Search: Experience
                    if detected_role == "Unknown" or detected_role == "Professional":
                         print(f"   ⚠️ Role unclear. Searching 'Experience' specifically...")
                         q_exp = f"{name} {company} LinkedIn experience role title"
                         exp_results = list(ddgs.text(q_exp, max_results=1))
                         if exp_results:
                             exp_snippet = exp_results[0].get('body', '')
                             if " at " in exp_snippet:
                                 detected_role = exp_snippet.split(" at ")[0].split(" - ")[-1].strip()
                                 print(f"   ✅ FOUND ROLE VIA EXPERIENCE: {detected_role}")

                    role = detected_role
                
                # 2. Search for Recent Activity phrases
                logging.info(f"   - searching activity...")
                activity_results = list(ddgs.text(q_activity, max_results=3))
                if activity_results:
                    # Combine unique snippets to form "recent activity" context
                    posts = [r.get('body', '') for r in activity_results]
                    # Filter for relevant keywords to verify it's a post
                    valid_posts = [p for p in posts if any(x in p.lower() for x in ['posted', 'shared', 'announced', 'excited', 'thinking'])]
                    
                    if valid_posts:
                        recent_post = valid_posts[0][:300] + "..."
                        themes = ["Industry Trend", "Recent Update"]
                    else:
                        recent_post = None
            
            # 3. Search for 'About' section if no recent post
            about_section = None
            if not recent_post:
                logging.info(f"   - searching about section...")
                q_about = f"{name} {company} LinkedIn about summary bio"
                about_results = list(ddgs.text(q_about, max_results=2))
                if about_results:
                     candidate = (about_results[0].get('body', '') or about_results[0].get('title', ''))
                     # Validation: Check for English-like text and length
                     # Heuristic: If > 20% chars are non-ascii (like Japanese/Chinese), reject it.
                     non_ascii = sum(1 for c in candidate if ord(c) > 127)
                     if non_ascii / len(candidate) > 0.2:
                         print(f"   ⚠️ REJECTED ABOUT SNIPPET (Detected non-English/Garbage): {candidate[:50]}...")
                         about_section = None
                     elif len(candidate) < 40:
                         print("   ⚠️ REJECTED ABOUT SNIPPET (Too short)")
                         about_section = None
                     else:
                         about_section = candidate[:300] + "..."

            return LinkedInInfo(
                role=role[:50], 
                seniority="Unknown",
                activity_themes=themes or ["General Business"],
                recent_post=recent_post,
                about_section=about_section,
                tone="Professional",
                verification_level="web_search"
            )

        except Exception as e:
            logging.error(f"Error enriching LinkedIn profile {linkedin_url}: {e}")
            return LinkedInInfo(verification_level="failed")
