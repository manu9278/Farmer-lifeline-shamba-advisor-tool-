from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class Stage2Output:
    crop: str
    problem_type: str
    most_likely_problem: str
    alternative_possibilities: List[str]
    confidence: float
    risk_level: str
    stage: str
    evidence: List[str]
    immediate_actions: List[str]
    prevention: List[str]
    monitoring: List[str]
    escalation_required: bool
    rag_matches: List[Dict]


DISEASE_STAGE_KEYWORDS = {
    "EARLY": ["early", "initial", "starting", "beginning", "small", "few", "minor", "first signs"],
    "ADVANCED": ["advanced", "severe", "extensive", "widespread", "major", "large", "many", "spreading rapidly", "dying"]
}

RISK_FACTORS = {
    "HIGH": ["explosive", "epidemic", "rapid spread", "complete loss", "total crop failure", "highly contagious", "wind-borne", "seed-borne"],
    "MEDIUM": ["significant yield loss", "spreads in", "favorable conditions", "can cause", "up to 50%", "moderate"],
    "LOW": ["minor", "limited", "localized", "manageable", "usually minor", "rarely severe"]
}


def assess_disease_stage(symptoms: List[str], disease_info: Dict) -> str:
    """Assess whether disease is in early or advanced stage based on symptoms."""
    symptom_text = " ".join(symptoms).lower()
    early_text = disease_info.get("early_symptoms", "").lower()
    advanced_text = disease_info.get("advanced_symptoms", "").lower()
    
    early_matches = sum(1 for kw in DISEASE_STAGE_KEYWORDS["EARLY"] if kw in symptom_text)
    advanced_matches = sum(1 for kw in DISEASE_STAGE_KEYWORDS["ADVANCED"] if kw in symptom_text)
    
    early_symptom_matches = sum(1 for s in symptoms if s.lower() in early_text)
    advanced_symptom_matches = sum(1 for s in symptoms if s.lower() in advanced_text)
    
    total_early = early_matches + early_symptom_matches
    total_advanced = advanced_matches + advanced_symptom_matches
    
    if total_advanced > total_early:
        return "ADVANCED"
    return "EARLY"


def assess_risk_level(disease_info: Dict, stage: str, confidence: float) -> str:
    """Assess risk level based on disease info, stage, and confidence."""
    warning_signs = disease_info.get("warning_signs", "").lower()
    risk_factors = disease_info.get("risk_factors", "").lower()
    
    high_score = sum(1 for kw in RISK_FACTORS["HIGH"] if kw in warning_signs or kw in risk_factors)
    medium_score = sum(1 for kw in RISK_FACTORS["MEDIUM"] if kw in warning_signs or kw in risk_factors)
    low_score = sum(1 for kw in RISK_FACTORS["LOW"] if kw in warning_signs or kw in risk_factors)
    
    if stage == "ADVANCED":
        high_score += 1
    elif stage == "EARLY":
        low_score += 1
    
    if confidence > 0.8:
        high_score += 1
    elif confidence < 0.5:
        low_score += 1
    
    if high_score >= medium_score and high_score >= low_score:
        return "HIGH"
    elif medium_score >= low_score:
        return "MEDIUM"
    return "LOW"


def determine_confidence(rag_matches: List[Dict], stage1_output: Dict) -> float:
    """Determine confidence based on RAG match scores and input quality."""
    if not rag_matches:
        return 0.1
    
    top_match = rag_matches[0]
    match_score = top_match.get("match_score", 0)
    
    base_confidence = min(match_score / 10.0, 0.9)
    
    stage1_conf = stage1_output.get("confidence", 0)
    symptom_count = len(stage1_output.get("symptoms", []))
    
    confidence = base_confidence * 0.7 + stage1_conf * 0.2 + min(symptom_count * 0.05, 0.1)
    
    return min(max(confidence, 0.1), 0.95)


def extract_evidence(symptoms: List[str], disease_info: Dict) -> List[str]:
    """Extract evidence linking symptoms to disease."""
    evidence = []
    symptom_text = " ".join(symptoms).lower()
    
    for symptom in symptoms:
        s_lower = symptom.lower()
        if s_lower in disease_info.get("symptoms", "").lower():
            evidence.append(f"Observed '{symptom}' matches typical symptom: {disease_info['symptoms'][:100]}...")
        if s_lower in disease_info.get("early_symptoms", "").lower():
            evidence.append(f"'{symptom}' is an early sign of this disease")
        if s_lower in disease_info.get("advanced_symptoms", "").lower():
            evidence.append(f"'{symptom}' indicates advanced progression")
    
    if not evidence:
        evidence.append("Symptoms partially match disease profile")
    
    return evidence


def get_immediate_actions(disease_info: Dict, stage: str) -> List[str]:
    """Get immediate actions based on disease management and stage."""
    management = disease_info.get("management", "")
    actions = []
    
    mgmt_parts = [p.strip() for p in management.split(",") if p.strip()]
    for part in mgmt_parts[:3]:
        if part:
            actions.append(part.capitalize())
    
    if stage == "EARLY":
        prevention = disease_info.get("prevention", "")
        prev_parts = [p.strip() for p in prevention.split(",") if p.strip()]
        for part in prev_parts[:2]:
            if part and part not in actions:
                actions.append(f"Preventive: {part.capitalize()}")
    
    if not actions:
        actions = ["Monitor crop closely", "Consult local extension officer", "Avoid spreading to healthy plants"]
    
    return actions[:5]


def get_prevention(disease_info: Dict) -> List[str]:
    """Get prevention measures from disease info."""
    prevention = disease_info.get("prevention", "")
    measures = [p.strip().capitalize() for p in prevention.split(",") if p.strip()]
    return measures[:5]


def get_monitoring(disease_info: Dict, risk_level: str) -> List[str]:
    """Get monitoring recommendations based on risk level."""
    base_monitoring = [
        "Check plants daily for symptom progression",
        "Monitor neighboring plants for spread",
        "Track weather conditions favorable to disease"
    ]
    
    if risk_level == "HIGH":
        base_monitoring.extend([
            "Scout field every 1-2 days",
            "Prepare for rapid intervention if spreading",
            "Consider preventive treatment of nearby healthy plants"
        ])
    elif risk_level == "MEDIUM":
        base_monitoring.extend([
            "Scout field every 3-4 days",
            "Watch for new lesions on upper leaves"
        ])
    
    return base_monitoring[:5]


def check_escalation_required(risk_level: str, stage: str, confidence: float) -> bool:
    """Determine if professional help is required."""
    if risk_level == "HIGH" and confidence > 0.7:
        return True
    if stage == "ADVANCED" and risk_level in ["HIGH", "MEDIUM"]:
        return True
    if confidence > 0.85 and risk_level == "HIGH":
        return True
    return False


def analyze_alternatives(rag_matches: List[Dict], top_disease: Dict) -> List[str]:
    """Get alternative disease possibilities from RAG matches."""
    alternatives = []
    top_name = top_disease.get("name", "")
    
    for match in rag_matches[1:4]:
        name = match.get("name", "")
        if name and name != top_name:
            alternatives.append(name)
    
    return alternatives


def stage_2(stage1_output: Dict, rag_knowledge: List[Dict]) -> Dict:
    """
    Main function for Stage 2 - Disease Analysis & Risk Assessment.
    Takes Stage 1 output and RAG knowledge, returns structured analysis.
    """
    crop = stage1_output.get("crop", "unknown")
    symptoms = stage1_output.get("symptoms", [])
    
    if not rag_knowledge:
        return asdict(Stage2Output(
            crop=crop,
            problem_type="UNKNOWN",
            most_likely_problem="Unable to identify - no matching diseases in database",
            alternative_possibilities=[],
            confidence=0.1,
            risk_level="UNKNOWN",
            stage="UNKNOWN",
            evidence=["No matching diseases found in knowledge base"],
            immediate_actions=["Consult local agricultural extension officer", "Take clear photos of symptoms", "Submit samples to plant clinic"],
            prevention=["Practice crop rotation", "Use certified disease-free seeds", "Maintain field hygiene"],
            monitoring=["Observe crop daily", "Record symptom progression"],
            escalation_required=True,
            rag_matches=[]
        ))
    
    top_disease = rag_knowledge[0]
    
    confidence = determine_confidence(rag_knowledge, stage1_output)
    disease_stage = assess_disease_stage(symptoms, top_disease)
    risk_level = assess_risk_level(top_disease, disease_stage, confidence)
    evidence = extract_evidence(symptoms, top_disease)
    immediate_actions = get_immediate_actions(top_disease, disease_stage)
    prevention = get_prevention(top_disease)
    monitoring = get_monitoring(top_disease, risk_level)
    escalation_required = check_escalation_required(risk_level, disease_stage, confidence)
    alternatives = analyze_alternatives(rag_knowledge, top_disease)
    
    result = Stage2Output(
        crop=crop,
        problem_type="DISEASE",
        most_likely_problem=top_disease.get("name", "Unknown"),
        alternative_possibilities=alternatives,
        confidence=round(confidence, 2),
        risk_level=risk_level,
        stage=disease_stage,
        evidence=evidence,
        immediate_actions=immediate_actions,
        prevention=prevention,
        monitoring=monitoring,
        escalation_required=escalation_required,
        rag_matches=[{"name": m["name"], "score": m["match_score"]} for m in rag_knowledge[:3]]
    )
    
    return asdict(result)


if __name__ == "__main__":
    from database_manager import CropDiseaseDatabase
    from stage_1_guardrail import stage_1
    
    db = CropDiseaseDatabase()
    
    test_cases = [
        "My tomato leaves have small brown spots with yellow halos and they're turning yellow",
        "Maize plants show rectangular gray lesions on leaves with yellow margins",
        "Potato leaves have water-soaked spots with white mold on the underside",
        "Wheat has yellow-orange pustules forming stripes on the leaves",
    ]
    
    print("=" * 60)
    print("STAGE 2 DISEASE ADVISOR - TEST RESULTS")
    print("=" * 60)
    
    for test_input in test_cases:
        print(f"\n{'='*60}")
        print(f"INPUT: {test_input}")
        print(f"{'='*60}")
        
        stage1_result = stage_1(test_input)
        print(f"\nStage 1 Output: {json.dumps(stage1_result, indent=2)}")
        
        if stage1_result["validity"]:
            rag_results = db.read_rag(stage1_result["crop"], stage1_result["symptoms"])
            print(f"\nRAG Matches: {len(rag_results)} diseases found")
            for r in rag_results[:3]:
                print(f"  - {r['name']} (score: {r['match_score']})")
            
            stage2_result = stage_2(stage1_result, rag_results)
            print(f"\nStage 2 Output:")
            print(json.dumps(stage2_result, indent=2))