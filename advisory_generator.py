"""Generate plain-text crop disease advisory reports."""

from typing import Any


# Keep the report layout in one place so every generated advisory is consistent.
_HEADER = "========================================"


def _format_list(items: Any, prefix: str) -> str:
    """Format a list of values, or explain that no values were provided."""
    if not isinstance(items, list) or not items:
        return "None reported."

    return "\n".join(f"{prefix}{item}" for item in items)


def generate_advisory(data: dict) -> str:
    """Return a formatted plain-text advisory from the supplied report data."""
    crop = data.get("crop", "Not provided.")
    possible_problem = data.get("possible_problem", "Not provided.")
    risk_level = data.get("risk_level", "Not provided.")
    detection_stage = data.get("detection_stage", "Not provided.")
    confidence = data.get("confidence", "Not provided.")

    symptoms = _format_list(data.get("observed_symptoms"), "- ")
    actions = _format_list(
        data.get("immediate_actions"),
        "",
    )
    if actions != "None reported.":
        actions = "\n".join(
            f"{number}. {action}"
            for number, action in enumerate(data["immediate_actions"], start=1)
        )

    prevention = _format_list(data.get("prevention"), "- ")

    return f"""{_HEADER}
        SHAMBA ADVISOR
{_HEADER}

CROP: {crop}

POSSIBLE PROBLEM:
{possible_problem}

RISK LEVEL:
{risk_level}

DETECTION STAGE:
{detection_stage}

CONFIDENCE:
{confidence}%

OBSERVED SYMPTOMS:
{symptoms}

IMMEDIATE ACTIONS:
{actions}

PREVENTION:
{prevention}

WARNING:
This is an AI-based early warning and not a laboratory diagnosis.
{_HEADER}"""


if __name__ == "__main__":
    sample_advisory = {
        "crop": "Tomato",
        "possible_problem": "Early blight",
        "risk_level": "MEDIUM",
        "detection_stage": "EARLY",
        "confidence": 86,
        "observed_symptoms": [
            "Small dark spots on older leaves",
            "Yellowing around the spots",
        ],
        "immediate_actions": [
            "Remove and safely dispose of badly affected leaves",
            "Avoid wetting the leaves when watering",
            "Improve airflow between plants",
        ],
        "prevention": [
            "Rotate tomatoes with unrelated crops",
            "Water at the base of each plant",
            "Remove crop debris after harvest",
        ],
    }

    print(generate_advisory(sample_advisory))
