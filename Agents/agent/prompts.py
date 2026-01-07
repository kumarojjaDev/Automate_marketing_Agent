from langchain_core.prompts import PromptTemplate

# 1) RESEARCH_PROMPT
# Analyzes raw scraped text to extract structured insights.
RESEARCH_PROMPT_TEMPLATE = """
You are an expert researcher for "Project Pigeon", an autonomous marketing system.
Your task is to analyze the provided raw text from a LinkedIn profile or company website.

RAW TEXT:
{raw_text}

INSTRUCTIONS:
Extract the following information in strict JSON format:
1. "bio": A 1-2 line professional summary of the person/company.
2. "recent_news": One concrete, recent signal or update found in the text (e.g., a new role, a post, a company update). If none found, state "No specific recent news found."
3. "writing_style": Analyze the tone of their profile text. Must be exactly one of: "Formal" or "Casual".

OUTPUT SCHEMA (JSON ONLY):
{{
  "bio": "string",
  "recent_news": "string",
  "writing_style": "string"
}}
"""

RESEARCH_PROMPT = PromptTemplate(
    template=RESEARCH_PROMPT_TEMPLATE,
    input_variables=["raw_text"]
)


# 2) EMAIL_PROMPT
# Generates a calm, human-like cold email draft.
EMAIL_PROMPT_TEMPLATE = """
You are a senior consultant at Project Pigeon. Write a cold outreach email based on the research provided.

CONTEXT:
- Bio: {bio}
- Recent News: {recent_news}
- Writing Style: {writing_style}

RULES:
- Use the "recent_news" as the opening hook.
- Tone: Consultant, calm, human, and conversational.
- NO marketing hype, NO buzzwords (like 'unlock', 'scale', 'game-changer'), NO emojis.
- Maximum 50 words total.
- The email must feel like it was typed by a human to a peer.

OUTPUT SCHEMA (JSON ONLY):
{{
  "subject": "string",
  "body": "string"
}}
"""

EMAIL_PROMPT = PromptTemplate(
    template=EMAIL_PROMPT_TEMPLATE,
    input_variables=["bio", "recent_news", "writing_style"]  
)
