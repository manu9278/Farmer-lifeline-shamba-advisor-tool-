
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
# Load environment variables from a local .env file

load_dotenv()


class CropHealth(BaseModel):
    validity: bool
    intent: str
    crop: Optional[str] = None
    symptoms: list[str] = Field(default_factory=list)
    urgency: str = "unknown"


PROMPT = """
You are a crop-health input validator.

Decide if the farmer's message is about crop/plant health.

If yes:
- validity=true
- intent="crop_health"
- extract crop, symptoms and urgency

If it is farming-related but not a health problem:
- validity=true
- intent="general_farming"

Otherwise:
- validity=false
- intent="unrelated"

Do not diagnose or give treatment advice.
"""


EXIT_WORDS = {"exit", "quit", "q"}



api_key = os.getenv("GEMINI_API_KEY_MINE")

print("API key exists:", api_key is not None)
print("API key length:", len(api_key) if api_key else 0)
print("API key prefix:", api_key[:8] if api_key else None)

client = genai.Client(api_key=api_key)

def check_message(message: str):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=message,
        config={
            "system_instruction": PROMPT,
            "response_mime_type": "application/json",
            "response_schema": CropHealth,
            "temperature": 0.1,
        },
    )

    return response.parsed.model_dump()


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
            result = check_message(message)
        except Exception as e:
            print(f"ERROR: Gemini request failed: {e}\n")
            continue

        if not result["validity"] or result["intent"] == "unrelated":
            print(
                "BLOCKED: That doesn't look like a crop/plant health "
                "question.\n"
            )
            continue

        print(result)
        print()


if __name__ == "__main__":
    main()

"""
If the idea or question is harmful to life decline the request but suggest a related topic to discuss

"""