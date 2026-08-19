#!/usr/bin/env python3
"""
Shamba Advisor - Crop Disease Early Warning System
Main entry point integrating all stages of the advisory pipeline.
"""

import sys
import os
import re
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import CropDiseaseDatabase
from stage_2_disease_advisor import stage_2
from advisory_generator import generate_advisory, save_advisory


CROP_KEYWORDS = {
    "maize": ["maize", "corn", "mealie"],
    "tomato": ["tomato", "tomatoes"],
    "potato": ["potato", "potatoes", "irish potato"],
    "wheat": ["wheat"],
    "rice": ["rice", "paddy"],
    "beans": ["beans", "bean", "green beans", "french beans"],
    "cassava": ["cassava", "manioc", "yuca"],
    "banana": ["banana", "plantain", "matoke"],
}

SYMPTOM_KEYWORDS = [
    "yellow", "brown", "black", "white", "spots", "lesions", "wilting", "wilts",
    "dying", "dead", "dry", "curling", "curled", "distorted", "mosaic", "streaks",
    "streak", "stunted", "stunting", "small", "rot", "rotting", "mold", "mould",
    "fungus", "fungal", "blight", "rust", "powdery", "downy", "water-soaked",
    "water soaked", "halo", "halos", "concentric", "rings", "ring", "target",
    "angular", "veins", "vein", "necrosis", "necrotic", "chlorosis", "chlorotic",
    "pale", "discolor", "discolour", "bleach", "bleached", "shrivel", "shriveled",
    "shrivelled", "drop", "dropping", "falling", "premature", "defoliation",
    "whiteflies", "whitefly", "aphid", "aphids", "leafhopper", "leafhoppers",
    "insect", "pest", "pests", "holes", "chewed", "eaten", "damage"
]

PLANT_PARTS = [
    "leaf", "leaves", "stem", "stalks", "stalk", "root", "roots", "fruit",
    "fruits", "pod", "pods", "ear", "ears", "tassel", "tassels", "flower",
    "flowers", "panicle", "panicles", "bunch", "bunches", "sucker", "suckers",
    "corm", "corms", "tuber", "tubers", "grain", "grains", "kernel", "kernels",
    "spike", "spikes", "spikelet", "spikelets", "sheath", "sheaths", "blade",
    "blades", "midrib", "midribs"
]

GROWTH_STAGES = [
    "seedling", "germination", "emergence", "vegetative", "flowering", "bloom",
    "fruit set", "fruiting", "grain fill", "grain filling", "maturity", "harvest",
    "early", "late", "young", "mature", "established", "newly planted"
]

URGENCY_KEYWORDS = {
    "high": ["urgent", "emergency", "critical", "severe", "rapid", "spreading fast", "dying fast", "quickly", "immediate"],
    "medium": ["worried", "concerned", "spreading", "getting worse", "expanding", "increasing"],
    "low": ["notice", "noticed", "seeing", "observed", "wondering", "curious"]
}

NON_AGRICULTURAL_PATTERNS = [
    r"football|soccer|match|game|score|won|lost|play",
    r"weather|rain|sun|temperature|forecast",
    r"politics|election|government|president|minister",
    r"movie|film|actor|actress|cinema",
    r"music|song|artist|album|concert",
    r"cooking|recipe|food|meal|restaurant",
    r"shopping|buy|sell|price|cost|market",
    r"travel|trip|flight|hotel|vacation",
    r"health|doctor|hospital|medicine|sick|illness",
    r"school|university|exam|test|study|homework",
    r"job|work|career|salary|interview",
    r"technology|computer|phone|app|software|internet"
]


def detect_crop(text: str) -> Optional[str]:
    text_lower = text.lower()
    for crop, keywords in CROP_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return crop
    return None


def extract_symptoms(text: str) -> List[str]:
    text_lower = text.lower()
    found_symptoms = []
    for symptom in SYMPTOM_KEYWORDS:
        if symptom in text_lower:
            found_symptoms.append(symptom)
    symptom_phrases = re.findall(r'(yellow|brown|black|white|dark|pale)\s+(leaves?|spots?|patches?|streaks?|lesions?)', text_lower)
    for adj, noun in symptom_phrases:
        phrase = f"{adj} {noun}"
        if phrase not in found_symptoms:
            found_symptoms.append(phrase)
    return list(set(found_symptoms))


def detect_plant_part(text: str) -> Optional[str]:
    text_lower = text.lower()
    for part in PLANT_PARTS:
        if part in text_lower:
            return part
    return None


def detect_growth_stage(text: str) -> Optional[str]:
    text_lower = text.lower()
    for stage in GROWTH_STAGES:
        if stage in text_lower:
            return stage
    return None


def detect_urgency(text: str) -> Optional[str]:
    text_lower = text.lower()
    for level, keywords in URGENCY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return level
    return None


def is_agricultural_query(text: str) -> bool:
    text_lower = text.lower()
    has_crop = detect_crop(text) is not None
    has_symptom = len(extract_symptoms(text)) > 0
    has_plant_part = detect_plant_part(text) is not None
    for pattern in NON_AGRICULTURAL_PATTERNS:
        if re.search(pattern, text_lower):
            if not (has_crop or has_symptom or has_plant_part):
                return False
    return has_crop or has_symptom or has_plant_part


def stage_1(user_input: str) -> Dict:
    raw_input = user_input.strip()
    if not raw_input:
        return {"validity": False, "intent": "empty_input", "crop": None, "symptoms": [], "plant_part": None, "growth_stage": None, "urgency": None, "confidence": 0.0, "raw_input": raw_input}
    if not is_agricultural_query(raw_input):
        return {"validity": False, "intent": "non_agricultural", "crop": None, "symptoms": [], "plant_part": None, "growth_stage": None, "urgency": None, "confidence": 0.9, "raw_input": raw_input}
    crop = detect_crop(raw_input)
    symptoms = extract_symptoms(raw_input)
    plant_part = detect_plant_part(raw_input)
    growth_stage = detect_growth_stage(raw_input)
    urgency = detect_urgency(raw_input)
    has_crop = crop is not None
    has_symptoms = len(symptoms) > 0
    has_plant_part = plant_part is not None
    confidence = 0.0
    if has_crop:
        confidence += 0.4
    if has_symptoms:
        confidence += 0.4
    if has_plant_part:
        confidence += 0.2
    validity = has_crop and has_symptoms
    if not validity and (has_crop or has_symptoms):
        validity = True
    return {"validity": validity, "intent": "crop_health" if validity else "insufficient_info", "crop": crop, "symptoms": symptoms, "plant_part": plant_part, "growth_stage": growth_stage, "urgency": urgency, "confidence": confidence, "raw_input": raw_input}


def print_welcome():
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("        SHAMBA ADVISOR - Crop Disease Early Warning")
    print("=" * 60)
    print("  Describe your crop problem in simple language.")
    print("  Example: 'My tomato leaves have brown spots with yellow halos'")
    print("  Type 'quit', 'exit', or 'q' to exit.")
    print("  Type 'help' for more examples.")
    print("=" * 60 + "\n")


def print_help():
    """Print help with example inputs."""
    print("\n" + "-" * 60)
    print("  EXAMPLE INPUTS:")
    print("  - My maize leaves are turning yellow")
    print("  - Tomato plants have brown spots on leaves")
    print("  - Potato leaves show water-soaked lesions with white mold")
    print("  - Wheat stems have yellow-orange stripes")
    print("  - Rice leaves have diamond-shaped gray lesions")
    print("  - Cassava leaves show yellow mosaic pattern")
    print("  - Banana leaves have dark streaks and are dying")
    print("  - Beans have angular brown spots on leaves")
    print("-" * 60 + "\n")


def print_available_crops(db: CropDiseaseDatabase):
    """Print available crops in the database."""
    crops = db.get_all_crops()
    print("\n  Available crops in database:")
    for crop in crops:
        diseases = db.get_diseases_for_crop(crop)
        disease_names = [d["name"] for d in diseases]
        print(f"    - {crop.capitalize()}: {', '.join(disease_names)}")
    print()


def run_pipeline(user_input: str, db: CropDiseaseDatabase, save_output: bool = True) -> Dict:
    """
    Run the complete Shamba Advisor pipeline.
    Returns the final analysis result.
    """
    print(f"\n[INPUT]: {user_input}")
    print("-" * 60)
    
    print("[STAGE 1] Guardrail & Intent Extraction...")
    stage1_result = stage_1(user_input)
    
    if not stage1_result["validity"]:
        intent = stage1_result["intent"]
        if intent == "non_agricultural":
            print("[ERROR] This doesn't appear to be a crop-related question.")
            print("   Please describe a crop health problem (e.g., symptoms, affected plants).")
        elif intent == "empty_input":
            print("[ERROR] Empty input. Please describe your crop problem.")
        else:
            print("[ERROR] Could not identify crop and symptoms clearly.")
            print("   Please mention the crop name and describe the symptoms.")
        
        if stage1_result["crop"]:
            print(f"   Detected crop: {stage1_result['crop']}")
        if stage1_result["symptoms"]:
            print(f"   Detected symptoms: {', '.join(stage1_result['symptoms'])}")
        return {"error": "Invalid input", "stage1": stage1_result}
    
    print(f"   [OK] Crop identified: {stage1_result['crop']}")
    print(f"   [OK] Symptoms: {', '.join(stage1_result['symptoms']) if stage1_result['symptoms'] else 'None specified'}")
    if stage1_result["plant_part"]:
        print(f"   [OK] Plant part: {stage1_result['plant_part']}")
    if stage1_result["growth_stage"]:
        print(f"   [OK] Growth stage: {stage1_result['growth_stage']}")
    if stage1_result["urgency"]:
        print(f"   [OK] Urgency: {stage1_result['urgency']}")
    
    print("\n[STAGE 1b] Retrieving knowledge from RAG database...")
    rag_results = db.read_rag(stage1_result["crop"], stage1_result["symptoms"])
    
    if not rag_results:
        print(f"   [WARN] No matching diseases found for {stage1_result['crop']} with these symptoms.")
        print("   Try describing symptoms differently or check crop name.")
        return {"error": "No RAG matches", "stage1": stage1_result, "rag_results": []}
    
    print(f"   [OK] Found {len(rag_results)} potential disease(s):")
    for r in rag_results[:3]:
        print(f"      - {r['name']} (match score: {r['match_score']})")
    
    print("\n[STAGE 2] Disease Analysis & Risk Assessment...")
    stage2_result = stage_2(stage1_result, rag_results)
    
    print(f"   [OK] Most likely: {stage2_result['most_likely_problem']}")
    print(f"   [OK] Confidence: {stage2_result['confidence']*100:.0f}%")
    print(f"   [OK] Risk Level: {stage2_result['risk_level']}")
    print(f"   [OK] Stage: {stage2_result['stage']}")
    if stage2_result["alternative_possibilities"]:
        print(f"   [OK] Alternatives: {', '.join(stage2_result['alternative_possibilities'])}")
    
    print("\n[STAGE 3] Generating Advisory...")
    generate_advisory(stage2_result, save_files=save_output)
    
    return {
        "stage1": stage1_result,
        "rag_results": rag_results,
        "stage2": stage2_result
    }


def run_batch_test(db: CropDiseaseDatabase):
    """Run a batch of test cases."""
    test_cases = [
        "My tomato leaves have small brown spots with yellow halos and they're turning yellow",
        "Maize plants show rectangular gray lesions on leaves with yellow margins",
        "Potato leaves have water-soaked spots with white mold on the underside",
        "Wheat has yellow-orange pustules forming stripes on the leaves",
        "Rice leaves have diamond-shaped lesions with gray centers and brown margins",
        "Cassava cuttings are showing yellow mosaic patterns on leaves",
        "Banana leaves have dark streaks with yellow halos, leaves dying",
        "Beans have angular brown spots limited by leaf veins",
    ]
    
    print("\n" + "=" * 60)
    print("  RUNNING BATCH TESTS")
    print("=" * 60)
    
    results = []
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"  TEST {i}/{len(test_cases)}")
        print(f"{'='*60}")
        result = run_pipeline(test_input, db, save_output=False)
        results.append({"input": test_input, "result": result})
    
    print("\n" + "=" * 60)
    print("  BATCH TEST SUMMARY")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        if "error" not in r["result"]:
            s2 = r["result"]["stage2"]
            print(f"  {i}. {r['input'][:50]}...")
            print(f"     -> {s2['most_likely_problem']} ({s2['confidence']*100:.0f}%, {s2['risk_level']})")
        else:
            print(f"  {i}. {r['input'][:50]}...")
            print(f"     -> ERROR: {r['result']['error']}")
    
    return results


def main():
    """Main entry point."""
    db = CropDiseaseDatabase()
    print_welcome()
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--test", "-t"]:
            run_batch_test(db)
            return
        elif sys.argv[1] in ["--help", "-h"]:
            print_help()
            print_available_crops(db)
            return
        elif sys.argv[1] in ["--crops", "-c"]:
            print_available_crops(db)
            return
        else:
            user_input = " ".join(sys.argv[1:])
            run_pipeline(user_input, db)
            return
    
    while True:
        try:
            user_input = input("\n[INPUT] Describe your crop problem: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n[EXIT] Thank you for using Shamba Advisor. Stay safe!")
                break
            
            if user_input.lower() in ["help", "h"]:
                print_help()
                continue
            
            if user_input.lower() in ["crops", "list"]:
                print_available_crops(db)
                continue
            
            run_pipeline(user_input, db)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()