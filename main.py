import os
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from a local .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY_MINE")



client = genai.Client(api_key=api_key)
EXIT_WORDS = {"exit", "quit", "q"}


# ---- 1. Define the output schema with Pydantic ----
class Stage1Output(BaseModel):
    validity: bool = Field(description="True if the message is a crop/plant health issue")
    intent: str = Field(description="e.g. 'crop_health', 'general_farming', 'unrelated'")
    crop: Optional[str] = Field(default=None, description="Crop mentioned, if any")
    symptoms: List[str] = Field(default_factory=list)
    plant_part: Optional[str] = Field(default=None, description="leaves, stem, roots, fruit, unknown")
    growth_stage: str = Field(default="unknown")
    urgency: str = Field(default="unknown", description="low, medium, high, unknown")
    rejection_reason: Optional[str] = Field(
        default=None, description="Only set if validity is false"
    )


SYSTEM_PROMPT = """
You are an input-validation and intent-extraction specialist for the Shamba Advisor agricultural advisory system.

TASKS:
1. Determine agricultural relevance.
2. Detect crop-health concerns.
3. Extract structured data for valid messages.
4. Block harmful requests while suggesting safe agricultural topics.

SAFETY (PROTECT LIFE):
- Reject requests asking for methods, quantities, or procedures intended to kill, poison, or seriously harm humans, animals, or non-target life.
- Set: validity=false, intent="unsafe", rejection_reason=[brief explanation + alternative safe topic, e.g., safe pest management or crop protection].
- Do NOT provide operational details for harmful requests.
- Allow routine agricultural pest/disease management and safe-handling questions intended to protect crops.

RELEVANCE & INTENT CLASSIFICATION:
- Non-agricultural (sports, casual chat, etc.): validity=false, intent="unrelated", rejection_reason=[short statement].
- General agriculture (no specific symptoms): validity=true, intent="general_farming".
- Crop-health problem: validity=true, intent="crop_health". Extract explicitly stated details: `crop`, `symptoms`, `plant_part`, `growth_stage`, `urgency`. Use "unknown" (or empty list) for unmentioned fields.

EXTRACTION CONSTRAINTS:
- DO NOT offer diagnoses, treatments, chemical dosages, or interventions.
- Extract ONLY explicitly stated or clearly implied facts. Never invent details.

OUTPUT: Return strictly structured data matching the schema.
"""


def stage_1(user_message: str) -> dict:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=Stage1Output,
            temperature=0.1,  # low temp: this is classification, not creative work
        ),
    )

    # response.parsed gives you a validated Stage1Output instance directly
    result: Stage1Output = response.parsed
    return result.model_dump()


def main():
    print(
        "Shamba Advisor — ask a crop/plant health question, "
        "or type 'exit' to quit.\n"
    )

    while True:
        message = input("Farmer: ").strip()

        if message.lower() in EXIT_WORDS:
            print("Goodbye.")
            break

        if not message:
            print("BLOCKED: Message was empty.\n")
            continue

        try:
            result = stage_1(message)
        except Exception as e:
            print(f"ERROR: Gemini request failed: {e}\n")
            continue

        if not result["validity"] or result["intent"] == "unrelated":
            print(result["rejection_reason"])
            continue

        print(json.dumps(result, indent=2))
        print("-" * 40)


if __name__ == "__main__":
    main()
