"""
Shamba Advisor
--------------
A two-stage AI tool that helps a smallholder farmer diagnose a problem on
their shamba (farm/plot) and get a practical, low-cost action plan.

STAGE 1 (Diagnosis call):  Takes the farmer's description of their shamba
                           (location, crop, size, what's going wrong) and
                           returns a structured diagnosis: likely causes,
                           urgency, and recommended practices.
STAGE 2 (Action Plan call): Takes the Stage 1 diagnosis + the original
                           description and turns it into a concrete,
                           affordable, step-by-step plan the farmer can
                           start this week.

Both calls use the Gemini API (Google) and both prompts are written using
the R-T-C-C-O framework (Role, Task, Context, Constraints, Output format).
"""

# ---------------------------------------------------------------------------
# SECTION 1: IMPORTS
# ---------------------------------------------------------------------------
import os
import json
import sys
from datetime import datetime

from dotenv import load_dotenv   # loads variables from a .env file
from google import genai         # official Google Gen AI Python SDK
from google.genai import types   # lets us set response format (e.g. JSON)


# ---------------------------------------------------------------------------
# SECTION 2: CONFIGURATION / API KEY LOADING
# ---------------------------------------------------------------------------
# The API key is NEVER hard-coded. It is loaded from a local .env file which
# is excluded from git via .gitignore. See .env.example for the expected
# format: GEMINI_API_KEY=your_key_here
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash"

if not API_KEY:
    # Fail loudly and early if the key is missing, rather than letting every
    # API call crash later with a confusing error.
    print("ERROR: No API key found. Create a .env file with:")
    print("GEMINI_API_KEY=your_key_here")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------------------------
# SECTION 3: HELPER FUNCTION - SAFE API CALL
# ---------------------------------------------------------------------------
def call_gemini(prompt: str) -> str | None:
    """
    Sends a single prompt to the Gemini API and returns the raw text
    response. Wrapped in try/except so a network error or API failure does
    not crash the whole program.

    We ask Gemini to respond with response_mime_type="application/json" so
    it returns clean JSON without markdown fences around it - but we still
    treat the reply as plain text here and let parse_json_response() do the
    actual parsing/validation, in case that ever changes.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return response.text
    except Exception as api_error:
        # Covers connection errors, rate limits, invalid key, timeouts, etc.
        print(f"\n[API CALL FAILED] Something went wrong talking to Gemini: {api_error}")
        return None


def parse_json_response(raw_text: str | None) -> dict | None:
    """
    Tries to parse a JSON object out of the model's raw text reply.
    Even though we ask Gemini for pure JSON, models occasionally still wrap
    it in ```json fences, so we strip those first just in case.
    Returns None (instead of crashing) if parsing fails.
    """
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as parse_error:
        print(f"\n[JSON PARSE FAILED] The model's reply wasn't valid JSON: {parse_error}")
        print("Raw reply was:\n", raw_text)
        return None


# ---------------------------------------------------------------------------
# SECTION 4: STAGE 1 - DIAGNOSE THE SHAMBA ISSUE (R-T-C-C-O PROMPT)
# ---------------------------------------------------------------------------
def diagnose_issue(farm_description: str) -> dict | None:
    """
    First API call. Sends the farmer's description to Gemini and asks for a
    structured diagnosis in JSON format. This call also acts as a topic
    guardrail: if the input isn't actually about farming, is_farming_related
    will be false and a polite decline_message is returned instead of a
    diagnosis.
    """
    prompt = f"""
ROLE: You are a pragmatic agricultural extension officer who advises
smallholder farmers in East Africa on crops, soil, pests, and weather-related
issues, using low-cost, locally available solutions.

TASK: First, check whether the text below is actually about a farming,
crop, livestock, soil, or agricultural topic. If it is not, politely
decline and do not attempt a diagnosis. If it IS a farming topic, analyse
it and identify what is most likely going on, how urgent it is, and what
general approach the farmer should take.

CONTEXT: The user wrote:
\"\"\"{farm_description}\"\"\"

CONSTRAINTS:
- This tool only handles farming/agriculture topics (crops, livestock,
  soil, pests, weather affecting a shamba, etc). Anything else - general
  knowledge, entertainment, other unrelated requests - must be declined.
- If is_farming_related is false: set summary, likely_causes,
  recommended_approach to empty values, and write a short, polite,
  one-sentence decline_message explaining that this tool only helps with
  farming/shamba questions, and inviting the user to ask a farming question
  instead. Do not lecture or over-explain - keep it brief and friendly.
- If is_farming_related is true: set decline_message to an empty string,
  and fill in the diagnosis fields as normal.
- Assume the farmer has limited cash to spend on inputs; prefer low-cost and
  locally available solutions over expensive imported products.
- Give exactly 3 likely_causes, ordered from most to least likely (only
  when is_farming_related is true).
- urgency must be exactly one of: "low", "medium", "high" (or "unknown" if
  is_farming_related is false).
- Keep every point to one short, plain-language sentence (no jargon).

OUTPUT: Respond with ONLY valid JSON, no extra text, no markdown fences,
using exactly this structure:
{{
  "is_farming_related": true,
  "decline_message": "",
  "summary": "one sentence restating the problem in your own words",
  "likely_causes": ["...", "...", "..."],
  "urgency": "low|medium|high",
  "recommended_approach": "one or two sentences on the general direction to take"
}}
"""
    raw_reply = call_gemini(prompt)
    return parse_json_response(raw_reply)


# ---------------------------------------------------------------------------
# SECTION 5: STAGE 2 - BUILD AN ACTION PLAN (R-T-C-C-O PROMPT)
# ---------------------------------------------------------------------------
def build_action_plan(farm_description: str, diagnosis: dict) -> dict | None:
    """
    Second API call. Uses the Stage 1 diagnosis as context to generate a
    concrete, affordable action plan.
    """
    prompt = f"""
ROLE: You are a hands-on farm advisor who turns a diagnosis into a simple
plan a farmer can follow without needing to consult anyone else.

TASK: Using the shamba description and diagnosis provided below, create a
short, practical action plan the farmer can start this week.

CONTEXT:
Original description: \"\"\"{farm_description}\"\"\"
Prior diagnosis (JSON): {json.dumps(diagnosis)}

CONSTRAINTS:
- Give exactly 4 this_week_actions, ordered by what to do first.
- Give exactly 3 materials_needed (things the farmer must buy, borrow, or
  find locally). Prefer cheap, locally available options.
- Give exactly 2 warning_signs that mean the farmer should seek in-person
  help from an agricultural officer.
- Keep every item to one short, concrete sentence (no vague advice).

OUTPUT: Respond with ONLY valid JSON, no extra text, no markdown fences,
using exactly this structure:
{{
  "this_week_actions": ["...", "...", "...", "..."],
  "materials_needed": ["...", "...", "..."],
  "warning_signs": ["...", "..."],
  "expected_outcome": "one sentence describing what improvement to expect and by when"
}}
"""
    raw_reply = call_gemini(prompt)
    return parse_json_response(raw_reply)


# ---------------------------------------------------------------------------
# SECTION 6: SAVE OUTPUT TO FILE
# ---------------------------------------------------------------------------
def save_result(farm_description: str, diagnosis: dict, plan: dict) -> str:
    """
    Combines both stages into one JSON file and saves it with a timestamped
    filename so previous runs are never overwritten.
    """
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/shamba_report_{timestamp}.json"

    result = {
        "farm_description": farm_description,
        "diagnosis": diagnosis,
        "action_plan": plan,
        "generated_at": timestamp,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return filename


# ---------------------------------------------------------------------------
# SECTION 7: DISPLAY RESULTS NICELY IN THE TERMINAL
# ---------------------------------------------------------------------------
def display_result(diagnosis: dict, plan: dict) -> None:
    print("\n===== DIAGNOSIS =====")
    print(f"Summary: {diagnosis['summary']}")
    print(f"Urgency: {diagnosis['urgency'].upper()}")
    print("Likely causes:")
    for c in diagnosis["likely_causes"]:
        print(f"  - {c}")
    print(f"Recommended approach: {diagnosis['recommended_approach']}")

    print("\n===== ACTION PLAN =====")
    print("This week's actions:")
    for i, step in enumerate(plan["this_week_actions"], start=1):
        print(f"  {i}. {step}")
    print("Materials needed:")
    for m in plan["materials_needed"]:
        print(f"  - {m}")
    print("Seek help if you see:")
    for w in plan["warning_signs"]:
        print(f"  ! {w}")
    print(f"Expected outcome: {plan['expected_outcome']}")


# ---------------------------------------------------------------------------
# SECTION 8: MAIN MENU / PROGRAM ENTRY POINT
# ---------------------------------------------------------------------------
def run_full_pipeline():
    """Handles menu option 1: get a shamba description and run both stages."""
    farm_description = input(
        "\nDescribe your shamba and the problem (crop, location, what you're "
        "seeing): "
    ).strip()

    # Handle empty input explicitly rather than letting the API reject it.
    if not farm_description:
        print("No description entered - nothing to diagnose. Returning to menu.")
        return

    print("\nDiagnosing the issue...")
    diagnosis = diagnose_issue(farm_description)
    if diagnosis is None:
        print("Could not complete the diagnosis stage. Please try again.")
        return

    # --- GUARDRAIL: politely decline anything that isn't about farming ---
    if not diagnosis.get("is_farming_related", True):
        print(f"\n{diagnosis.get('decline_message', 'Sorry, this tool only helps with farming/shamba questions.')}")
        return

    print("Building your action plan...")
    plan = build_action_plan(farm_description, diagnosis)
    if plan is None:
        print("Could not complete the planning stage. Please try again.")
        return

    display_result(diagnosis, plan)
    saved_path = save_result(farm_description, diagnosis, plan)
    print(f"\nFull report saved to: {saved_path}")


def view_past_reports():
    """Handles menu option 2: list previously saved reports in outputs/."""
    if not os.path.isdir("outputs") or not os.listdir("outputs"):
        print("\nNo saved reports yet. Run option 1 first.")
        return

    files = sorted(os.listdir("outputs"))
    print("\nSaved reports:")
    for f in files:
        print(f"  - outputs/{f}")


def main_menu():
    """Main program loop with a menu offering the user multiple choices."""
    while True:
        print("\n================ SHAMBA ADVISOR ================")
        print("1. Diagnose a shamba problem and get an action plan")
        print("2. View previously saved reports")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            run_full_pipeline()
        elif choice == "2":
            view_past_reports()
        elif choice == "3":
            print("Kwaheri! Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_menu()