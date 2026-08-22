"""
Shamba Advisor - a friendly AI helper that diagnoses shamba (farm) problems
and gives a short, practical action plan. One Gemini call handles both
diagnosis and plan to keep things fast and simple.
"""

import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"

if not API_KEY:
    print("ERROR: No API key found. Add this to your .env file:")
    print("GEMINI_API_KEY=your_key_here")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------------------------
# API CALL
# ---------------------------------------------------------------------------
def ask_gemini(farm_description: str) -> dict | None:
    """Sends the farmer's problem to Gemini and gets back a diagnosis +
    action plan in one shot, as JSON."""
    prompt = f"""
ROLE: You are a friendly, practical agricultural extension officer helping
smallholder farmers in East Africa.

TASK: First check if this is actually about farming (crops, livestock,
soil, pests, weather). If not, politely decline. If it is, diagnose the
likely problem and give a short action plan.

FARMER SAID: \"\"\"{farm_description}\"\"\"

CONSTRAINTS:
- Assume the farmer has little money; prefer cheap, local solutions.
- Keep every point short, plain, and jargon-free (one sentence each).
- Exactly 3 causes, 3 action steps, 2 prevention tips.
- If not farming-related, leave other fields empty and just fill decline_message.

OUTPUT: Respond with ONLY valid JSON, no markdown fences:
{{
  "is_farming_related": true,
  "decline_message": "",
  "issue_name": "short name of the likely disease/problem",
  "causes": ["...", "...", "..."],
  "urgency": "low|medium|high",
  "action_plan": ["...", "...", "..."],
  "prevention_tips": ["...", "..."]
}}
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.strip("`").replace("json", "", 1).strip()
        return json.loads(text)
    except Exception as e:
        print(f"\n⚠️  Something went wrong talking to Gemini: {e}")
        return None


# ---------------------------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------------------------
def show_result(result: dict) -> None:
    if not result.get("is_farming_related", True):
        print(f"\n🙂 {result.get('decline_message', 'I can only help with farming questions!')}")
        return

    urgency_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(result.get("urgency", ""), "")

    print(f"\n🔍 Likely issue: {result['issue_name']}  {urgency_icon} ({result['urgency']} urgency)")

    print("\n📋 Likely causes:")
    for c in result["causes"]:
        print(f"  - {c}")

    print("\n✅ What to do this week:")
    for i, step in enumerate(result["action_plan"], start=1):
        print(f"  {i}. {step}")

    print("\n🛡️  To avoid this next time:")
    for t in result["prevention_tips"]:
        print(f"  - {t}")


def save_result(farm_description: str, result: dict) -> str:
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/shamba_report_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"farm_description": farm_description, **result, "generated_at": timestamp}, f, indent=2)
    return filename


# ---------------------------------------------------------------------------
# MAIN CONVERSATION LOOP
# ---------------------------------------------------------------------------
def diagnose_flow():
    farm_description = input(
        "\nTell me what's going on (crop, location, what you're seeing): "
    ).strip()

    if not farm_description:
        print("Hmm, I didn't catch that. Let's try again.")
        return

    print("\n🌱 Let me take a look...")
    result = ask_gemini(farm_description)

    if result is None:
        print("Sorry, I couldn't process that right now. Please try again.")
        return

    show_result(result)

    if result.get("is_farming_related", True):
        path = save_result(farm_description, result)
        print(f"\n💾 Saved to: {path}")


def view_past_reports():
    if not os.path.isdir("outputs") or not os.listdir("outputs"):
        print("\nNo saved reports yet.")
        return
    print("\n📁 Saved reports:")
    for f in sorted(os.listdir("outputs")):
        print(f"  - outputs/{f}")


def main():
    print("\nHello Farmer! 👋 I'm here to help with your shamba.\n")
    print("=" * 45)
    print("   🌾 SHAMBA ADVISOR — your farm helper")
    print("=" * 45)

    while True:
        print("\n1. Diagnose a shamba problem")
        print("2. View past reports")
        print("3. Exit")
        choice = input("What would you like to do? (1-3): ").strip()

        if choice == "1":
            diagnose_flow()
        elif choice == "2":
            view_past_reports()
        elif choice == "3":
            print("\nKwaheri! 🌾 Take care of that shamba!")
            break
        else:
            print("Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
