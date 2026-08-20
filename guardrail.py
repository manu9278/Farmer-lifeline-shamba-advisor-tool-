

import json
import os
import sys
from typing import List, Optional

from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; env vars can be set another way

from guardrails import Guard 

# ---------------------------------------------------------------------------
# Stage 1 schema
# ---------------------------------------------------------------------------m
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


SYSTEM_PROMPT = """You are an input-validation and intent-extraction specialist for an
agricultural crop-health advisory system (Shamba Advisor).

TASK:
Given a farmer's raw message, determine whether it describes a crop/plant health
problem, and if so, extract structured details.

RULES:
- If the message is NOT about a crop, plant, or farm health issue (e.g. sports, weather
  chit-chat, general questions unrelated to farming), set validity=false, intent="unrelated",
  and give a short rejection_reason. Leave other fields empty/default.
- If it IS agriculture-related but not about a specific crop symptom (e.g. "how do I
  improve soil pH"), set validity=true, intent="general_farming".
- If it's a crop/plant symptom report, set validity=true, intent="crop_health", and
  extract crop, symptoms, plant_part, growth_stage, urgency as best you can.
- Do NOT diagnose the disease or suggest treatment — that is out of scope for this stage.
- If a field cannot be determined from the message, use "unknown" (or empty list for symptoms).
- Never invent crops or symptoms the farmer didn't mention or imply.
"""
# ---------------------------------------------------------------------------
# Gemini client (lazy-initialized so this file still imports/tests without
# the SDK installed or an API key set)
# ---------------------------------------------------------------------------

_client = None

def get_client():
    global _client
    if _client is None:
        from google import genai  # imported here so a missing SDK doesn't break local tests
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set. Add it to a .env file or export it in your shell."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def stage_1(user_message: str) -> Stage1Output:
    from google.genai import types

    client = get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=Stage1Output,
            temperature=0.1,
        ),
    )
    return response.parsed
# ---------------------------------------------------------------------------
# Combined guardrail check
# ---------------------------------------------------------------------------
def check_message(user_message: str, pipeline: Guard) -> dict:
    """
    Runs local guardrails first (free), then the Gemini Stage 1 guardrail.
    Returns a plain dict — this is the guardrail's final verdict on the
    message, nothing further downstream is called from here.
    """
    local_result = pipeline.parse(user_message)
    if not local_result.validation_passed:
        return {
            "validity": False,
            "intent": "blocked_locally",
            "rejection_reason": local_result.reason,
        }

    try:
        stage1_result = stage_1(local_result.sanitized_text)
    except Exception as exc:
        return {
            "validity": False,
            "intent": "error",
            "rejection_reason": f"Could not reach Gemini: {exc}",
        }

    return stage1_result.model_dump()


def print_result(result: dict) -> None:
    print(json.dumps(result, indent=2))
    if result.get("validity"):
        print("\n[PASS] Message accepted by guardrail.")
    else:
        reason = result.get("rejection_reason") or "Message was not accepted."
        print(f"\n[BLOCKED] {reason}")


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------

def main() -> None:
    pipeline = Guard.for_pydantic(output_class=Stage1Output)
    print("Shamba Advisor Guardrail — type a message to test it (type 'quit' to exit)\n")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            sys.exit(0)

        if user_message.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        if not user_message:
            continue

        result = check_message(user_message, pipeline)
        print_result(result)
        print()


if __name__ == "__main__":
    main()