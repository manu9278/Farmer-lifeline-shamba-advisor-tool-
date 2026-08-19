import json
from typing import Dict, List, Optional
from datetime import datetime


def format_confidence(confidence: float) -> str:
    """Format confidence as percentage."""
    return f"{int(confidence * 100)}%"


def format_risk_level(risk: str) -> str:
    """Format risk level with indicator."""
    indicators = {
        "HIGH": "[HIGH]",
        "MEDIUM": "[MEDIUM]",
        "LOW": "[LOW]",
        "UNKNOWN": "[UNKNOWN]"
    }
    return indicators.get(risk, risk)


def format_stage(stage: str) -> str:
    """Format disease stage."""
    indicators = {
        "EARLY": "[EARLY STAGE]",
        "ADVANCED": "[ADVANCED STAGE]",
        "UNKNOWN": "[UNKNOWN STAGE]"
    }
    return indicators.get(stage, stage)


def generate_advisory_text(result: Dict) -> str:
    """
    Generate a farmer-friendly advisory text from the analysis result.
    """
    lines = []
    width = 50
    
    def add_line(text: str = ""):
        lines.append(text)
    
    def add_header(title: str):
        add_line("=" * width)
        add_line(f"          {title}")
        add_line("=" * width)
    
    def add_section(title: str):
        add_line("-" * width)
        add_line(f"  {title}")
        add_line("-" * width)
    
    def add_field(label: str, value: str):
        add_line(f"  {label:<25}: {value}")
    
    def add_list(items: List[str], prefix: str = "  - "):
        for item in items:
            if item and item.strip():
                add_line(f"{prefix}{item.strip()}")
    
    add_header("SHAMBA ADVISOR")
    add_line("")
    
    crop = result.get("crop", "UNKNOWN").upper()
    add_field("CROP", crop)
    add_line("")
    
    problem = result.get("most_likely_problem", "Unknown")
    add_section("POSSIBLE PROBLEM")
    add_line(f"  {problem}")
    add_line("")
    
    if result.get("alternative_possibilities"):
        add_line("  Other possibilities:")
        for alt in result["alternative_possibilities"]:
            add_line(f"    - {alt}")
        add_line("")
    
    add_section("RISK ASSESSMENT")
    add_field("RISK LEVEL", format_risk_level(result.get("risk_level", "UNKNOWN")))
    add_field("DETECTION STAGE", format_stage(result.get("stage", "UNKNOWN")))
    add_field("CONFIDENCE", format_confidence(result.get("confidence", 0)))
    add_line("")
    
    symptoms = result.get("evidence", [])
    if symptoms:
        add_section("OBSERVED SYMPTOMS & EVIDENCE")
        add_list(symptoms)
        add_line("")
    
    actions = result.get("immediate_actions", [])
    if actions:
        add_section("IMMEDIATE ACTIONS")
        for i, action in enumerate(actions, 1):
            add_line(f"  {i}. {action}")
        add_line("")
    
    prevention = result.get("prevention", [])
    if prevention:
        add_section("PREVENTION MEASURES")
        add_list(prevention)
        add_line("")
    
    monitoring = result.get("monitoring", [])
    if monitoring:
        add_section("MONITORING RECOMMENDATIONS")
        add_list(monitoring)
        add_line("")
    
    add_section("IMPORTANT WARNING")
    add_line("  This is an AI-based early warning advisory")
    add_line("  based on symptom pattern matching.")
    add_line("  It is NOT a laboratory diagnosis.")
    add_line("")
    add_line("  For definitive diagnosis and treatment,")
    add_line("  please consult your local agricultural")
    add_line("  extension officer or plant clinic.")
    add_line("")
    
    if result.get("escalation_required", False):
        add_section("[ESCALATION RECOMMENDED]")
        add_line("  This case shows HIGH RISK indicators.")
        add_line("  Professional diagnosis is strongly")
        add_line("  recommended as soon as possible.")
        add_line("")
    
    add_line("=" * width)
    add_line(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add_line(f"  Shamba Advisor v1.0")
    add_line("=" * width)
    
    return "\n".join(lines)


def generate_advisory_json(result: Dict) -> str:
    """Generate JSON output for programmatic use."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "crop": result.get("crop"),
        "diagnosis": {
            "most_likely": result.get("most_likely_problem"),
            "alternatives": result.get("alternative_possibilities", []),
            "confidence": result.get("confidence"),
            "problem_type": result.get("problem_type")
        },
        "risk_assessment": {
            "level": result.get("risk_level"),
            "stage": result.get("stage"),
            "escalation_required": result.get("escalation_required")
        },
        "evidence": result.get("evidence", []),
        "recommendations": {
            "immediate_actions": result.get("immediate_actions", []),
            "prevention": result.get("prevention", []),
            "monitoring": result.get("monitoring", [])
        },
        "disclaimer": "This is an AI-based early warning advisory based on symptom pattern matching. It is NOT a laboratory diagnosis. Consult your local agricultural extension officer for definitive diagnosis."
    }
    return json.dumps(output, indent=2)


def save_advisory(result: Dict, txt_path: str = "advisory.txt", json_path: str = "advisory.json") -> Dict[str, str]:
    """
    Save advisory to both text and JSON files.
    Returns paths of saved files.
    """
    txt_content = generate_advisory_text(result)
    json_content = generate_advisory_json(result)
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)
    
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_content)
    
    return {
        "txt": txt_path,
        "json": json_path
    }


def generate_advisory(result: Dict, save_files: bool = True) -> str:
    """
    Main function to generate advisory output.
    Prints to console and optionally saves to files.
    """
    advisory_text = generate_advisory_text(result)
    print(advisory_text)
    
    if save_files:
        paths = save_advisory(result)
        print(f"\n[Saved to: {paths['txt']} and {paths['json']}]")
    
    return advisory_text


if __name__ == "__main__":
    test_result = {
        "crop": "tomato",
        "problem_type": "DISEASE",
        "most_likely_problem": "Early Blight",
        "alternative_possibilities": ["Bacterial Leaf Spot", "Late Blight"],
        "confidence": 0.82,
        "risk_level": "MEDIUM",
        "stage": "EARLY",
        "evidence": [
            "Observed 'brown spots' matches typical symptom: Small dark spots on leaves, yellowing leaves, concentric rings on spots...",
            "'yellow leaves' is an early sign of this disease"
        ],
        "immediate_actions": [
            "Remove affected leaves",
            "Improve airflow",
            "Avoid prolonged leaf wetness",
            "Apply copper-based fungicides",
            "Monitor neighbouring plants"
        ],
        "prevention": [
            "Crop rotation",
            "Proper spacing",
            "Avoid overhead watering",
            "Mulching"
        ],
        "monitoring": [
            "Check plants daily for symptom progression",
            "Monitor neighboring plants for spread",
            "Track weather conditions favorable to disease",
            "Scout field every 3-4 days",
            "Watch for new lesions on upper leaves"
        ],
        "escalation_required": False,
        "rag_matches": [
            {"name": "Early Blight", "score": 8},
            {"name": "Bacterial Leaf Spot", "score": 3},
            {"name": "Late Blight", "score": 2}
        ]
    }
    
    print("=" * 60)
    print("ADVISORY GENERATOR - TEST OUTPUT")
    print("=" * 60)
    print()
    
    generate_advisory(test_result, save_files=False)