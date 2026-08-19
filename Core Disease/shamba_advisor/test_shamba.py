import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import CropDiseaseDatabase
from stage_2_disease_advisor import stage_2
from advisory_generator import generate_advisory_text, generate_advisory_json
from main import stage_1, detect_crop, extract_symptoms


def test_database_initialization():
    db = CropDiseaseDatabase(":memory:")
    crops = db.get_all_crops()
    assert len(crops) == 8
    assert "tomato" in crops
    assert "maize" in crops


def test_detect_crop():
    assert detect_crop("My tomato plants are sick") == "tomato"
    assert detect_crop("Maize leaves turning yellow") == "maize"
    assert detect_crop("Unknown crop xyz") is None


def test_extract_symptoms():
    symptoms = extract_symptoms("Leaves have brown spots and yellow halos")
    assert "brown" in symptoms
    assert "spots" in symptoms
    assert "yellow" in symptoms
    assert "halo" in symptoms


def test_stage1_valid_input():
    result = stage_1("My tomato leaves have brown spots with yellow halos")
    assert result["validity"] is True
    assert result["crop"] == "tomato"
    assert len(result["symptoms"]) > 0


def test_stage1_invalid_input():
    result = stage_1("Who won the football match?")
    assert result["validity"] is False
    assert result["intent"] == "non_agricultural"


def test_stage1_empty_input():
    result = stage_1("")
    assert result["validity"] is False
    assert result["intent"] == "empty_input"


def test_rag_retrieval():
    db = CropDiseaseDatabase(":memory:")
    results = db.read_rag("tomato", ["brown spots", "yellow leaves"])
    assert len(results) > 0
    assert any(r["name"] == "Early Blight" for r in results)


def test_stage2_analysis():
    stage1_result = {
        "crop": "tomato",
        "symptoms": ["brown spots", "yellow leaves"],
        "plant_part": "leaves",
        "confidence": 0.8
    }
    db = CropDiseaseDatabase(":memory:")
    rag_results = db.read_rag("tomato", ["brown spots", "yellow leaves"])
    result = stage_2(stage1_result, rag_results)
    assert result["crop"] == "tomato"
    assert "most_likely_problem" in result
    assert 0 <= result["confidence"] <= 1
    assert result["risk_level"] in ["HIGH", "MEDIUM", "LOW"]


def test_advisory_text_generation():
    result = {
        "crop": "tomato",
        "most_likely_problem": "Early Blight",
        "alternative_possibilities": ["Bacterial Leaf Spot"],
        "confidence": 0.82,
        "risk_level": "MEDIUM",
        "stage": "EARLY",
        "evidence": ["Observed brown spots match symptoms"],
        "immediate_actions": ["Remove affected leaves", "Improve airflow"],
        "prevention": ["Crop rotation", "Proper spacing"],
        "monitoring": ["Check daily", "Monitor neighbors"],
        "escalation_required": False,
        "rag_matches": []
    }
    text = generate_advisory_text(result)
    assert "TOMATO" in text
    assert "Early Blight" in text
    assert "MEDIUM" in text
    assert "82%" in text


def test_advisory_json_generation():
    result = {
        "crop": "tomato",
        "most_likely_problem": "Early Blight",
        "alternative_possibilities": [],
        "confidence": 0.82,
        "risk_level": "MEDIUM",
        "stage": "EARLY",
        "evidence": [],
        "immediate_actions": [],
        "prevention": [],
        "monitoring": [],
        "escalation_required": False,
        "rag_matches": []
    }
    json_str = generate_advisory_json(result)
    import json
    data = json.loads(json_str)
    assert data["crop"] == "tomato"
    assert data["diagnosis"]["most_likely"] == "Early Blight"
    assert data["diagnosis"]["confidence"] == 0.82


def test_non_agricultural_rejection():
    cases = [
        "What's the weather today?",
        "Who won the football game?",
        "Best restaurant in town",
    ]
    for case in cases:
        result = stage_1(case)
        assert result["validity"] is False
        assert result["intent"] == "non_agricultural"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])