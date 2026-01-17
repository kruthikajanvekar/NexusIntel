
import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any

def perform_research_sync(url: str) -> Dict[str, Any]:
    """
    Synchronous research function using the modern Google GenAI SDK.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable is missing.")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Perform a deep-dive research into the company at: {url}
    Extract contact details, summary, and locations.
    Return a JSON object following the required enterprise schema.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text)
        
        # Grounding sources extraction
        if response.candidates and response.candidates[0].grounding_metadata:
            chunks = response.candidates[0].grounding_metadata.grounding_chunks
            if chunks:
                grounding_sources = [c.web.uri for c in chunks if c.web]
                data['sources'] = list(set(data.get('sources', []) + grounding_sources))
            
        return data
        
    except Exception as e:
        return {
            "company_name": "Discovery Failed",
            "website": url,
            "summary": f"Extraction Error: {str(e)}",
            "emails": [], "phone_numbers": [], "socials": [], "addresses": [], "notes": "", "sources": []
        }

async def perform_research(url: str) -> Dict[str, Any]:
    return perform_research_sync(url)
