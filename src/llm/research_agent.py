
import os
import json
import time
from google import genai
from google.genai import types
from typing import Dict, Any

class ResearchAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY is required.")
        self.client = genai.Client(api_key=self.api_key)

    def perform_discovery(self, url: str) -> Dict[str, Any]:
        target_model = 'gemini-3-flash-preview'
        print(f"\n[AI-ENGINE-V3] Discovery Hub: {url}")
        
        prompt = f"""
        Research Target: {url}
        TASK: Extract high-confidence business intelligence.
        REQUIRED JSON SCHEMA:
        {{
            "company_name": "string",
            "website": "{url}",
            "summary": "2 sentences describing core business",
            "emails": ["list"],
            "phone_numbers": ["list"],
            "socials": [{{"platform": "name", "url": "link"}}],
            "addresses": ["physical office locations if found"],
            "notes": "Any additional intelligence notes",
            "sources": ["URLs used for verification"]
        }}
        """

        try:
            print("[AI-ENGINE-V3] Attempting Deep Scan...")
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            data = json.loads(response.text)
            
            if response.candidates and response.candidates[0].grounding_metadata:
                chunks = response.candidates[0].grounding_metadata.grounding_chunks
                if chunks:
                    grounding_sources = [c.web.uri for c in chunks if c.web]
                    data['sources'] = list(set(data.get('sources', []) + grounding_sources))
            
            return data

        except Exception as e:
            if "429" in str(e):
                print("[AI-ENGINE-V3] Quota Hit. Safe Mode engaged.")
                time.sleep(2)
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=prompt + "\nNOTE: Search disabled. Use internal knowledge.",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                data = json.loads(response.text)
                data['notes'] = (data.get('notes', '') + " | [SAFE-MODE]").strip(" | ")
                return data
            
            return {
                "company_name": "Discovery Limited",
                "website": url,
                "summary": f"Connection Error: {str(e)}",
                "emails": [], "phone_numbers": [], "socials": [], "addresses": [], "notes": "Error", "sources": []
            }
