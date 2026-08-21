import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
import google.generativeai as genai


# Define structured output schema for Gemini
class CropGuardrailResponse(BaseModel):
    is_agricultural: bool = Field(
        description="True ONLY if the query is strictly about crop health, crop diseases, plant farming, or crop pests. False for livestock, general chit-chat, weather, or non-crop topics."
    )
    extracted_crop: Optional[str] = Field(
        default=None,
        description="The plant/crop named in the input (e.g., 'maize', 'cassava', 'sukuma wiki', 'tomato'). Return None if no crop is identified."
    )
    extracted_symptoms: List[str] = Field(
        default_factory=list,
        description="List of observed plant disease symptoms or pest damage (e.g., ['yellow leaves', 'wilting', 'leaf spots'])."
    )
    decline_message: Optional[str] = Field(
        default=None,
        description="Polite rejection message if is_agricultural is False. Clearly state that Shamba Advisor strictly handles crop health issues. Set to None if valid."
    )


SYSTEM_PROMPT = """
You are Stage 1 Guardrail for 'Shamba Advisor', an AI assistant strictly dedicated to crop health, plant diseases, and agricultural pests.

STRICT CLASSIFICATION RULES:
1. ACCEPT (is_agricultural = True):
   - Queries about crop health, plant diseases, crop pests, soil issues for crops, or specific farming crops (e.g., maize, beans, potatoes, cassava, tomatoes).
   - If a crop symptom is mentioned without naming a specific crop, accept it as True and extract the symptoms.

2. REJECT (is_agricultural = False):
   - Animal / Livestock queries (cows, goats, chickens, pigs, veterinary questions) -> REJECT.
   - General chit-chat, greetings without farming context -> REJECT.
   - Non-agricultural topics (tech, math, general knowledge, sports) -> REJECT.
   - Standalone general weather queries with no crop context -> REJECT.

When rejecting, populate `decline_message` politely guiding the user back to crop disease topics.
"""


def process_stage_1_guardrail(user_prompt: str) -> dict:
    """
    Evaluates farmer query against crop guardrails and extracts key symptoms.
    Returns a dictionary structured for main.py, RAG lookup, and Stage 2 analysis.
    """
    # Ensure API Key is set in your environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "is_agricultural": False,
            "extracted_crop": None,
            "extracted_symptoms": [],
            "decline_message": "System Error: Gemini API key is missing. Please check configuration."
        }

    genai.configure(api_key=api_key)

    # Gemini model with structured JSON enforcement
    model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": CropGuardrailResponse,
            "temperature": 0.1  # Low randomness for consistent classification
        }
    )

    try:
        response = model.generate_content(user_prompt)
        # Parse output directly into dictionary
        return json.loads(response.text)
    except Exception as e:
        return {
            "is_agricultural": False,
            "extracted_crop": None,
            "extracted_symptoms": [],
            "decline_message": f"Error validating input query: {str(e)}"
        }


# =====================================================================
# VERIFICATION TESTS (Matches commit: test: add valid and invalid inputs)
# =====================================================================
if __name__ == "__main__":
    test_cases = [
        # Valid Crop Inputs
        "My maize crop has yellow streaks on the leaves and stunted growth.",
        "What insecticide works best for stem borer in sorghum?",
        "Why are my tomato leaves curling and dying?",

        # Invalid Inputs (Livestock / Non-crop / Chit-chat)
        "My cow has a high fever and stopped giving milk.",
        "What is the capital city of Kenya?",
        "Will it rain in Nairobi tomorrow afternoon?",
        "Hello Shamba Advisor, hope you are having a nice day."
    ]

    print("=== STAGE 1 GUARDRAIL TEST SUITE ===\n")
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: '{test}'")
        result = process_stage_1_guardrail(test)
        print("Guardrail Output:", json.dumps(result, indent=2))
        print("-" * 50)