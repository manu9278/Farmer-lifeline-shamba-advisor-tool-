# Shamba Advisor - Crop Disease Early Warning System

A Python-based agricultural advisory system that helps farmers identify potential crop diseases from symptom descriptions and provides actionable recommendations.

## Architecture

```
Farmer Input
     ↓
Stage 1 — Guardrail & Intent Extraction
     ↓
Crop/Disease RAG Database (SQLite)
     ↓
Stage 2 — Disease Analysis & Risk Assessment
     ↓
Advisory Generator (Text + JSON Output)
```

## Project Structure

```
shamba_advisor/
├── main.py                    # System integration & CLI
├── database_manager.py        # SQLite RAG database (Emmanuel)
├── stage_1_guardrail.py       # Input validation & intent extraction (Cecilia)
├── stage_2_disease_advisor.py # Disease analysis & risk assessment (David)
├── advisory_generator.py      # Farmer-friendly output generation (Malik)
├── crop_disease.db            # SQLite database (auto-generated)
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Team Members

| Member | Module | Responsibility |
|--------|--------|----------------|
| Emmanuel | database_manager.py | RAG crop/disease knowledge base |
| Cecilia | stage_1_guardrail.py | Guardrail & farmer-intent extraction |
| David | stage_2_disease_advisor.py | Disease detection, risk & severity |
| Malik | advisory_generator.py | Generate farmer-friendly Python output |
| Baba Yega | main.py | Integrate and run the entire system |

## Features

- **Two-Stage AI Pipeline**: Clean separation of input understanding (Stage 1) and disease reasoning (Stage 2)
- **RAG Knowledge Base**: SQLite database with 18 diseases across 8 major crops
- **Symptom Matching**: Intelligent matching of farmer-described symptoms to disease profiles
- **Risk Assessment**: Automatic risk level (HIGH/MEDIUM/LOW) and disease stage (EARLY/ADVANCED) determination
- **Farmer-Friendly Output**: Plain text advisories with immediate actions, prevention, and monitoring
- **Dual Output Format**: Human-readable `.txt` and machine-readable `.json`
- **Interactive CLI**: Continuous conversation loop for multiple queries

## Supported Crops & Diseases

| Crop | Diseases |
|------|----------|
| Tomato | Early Blight, Late Blight, Bacterial Leaf Spot |
| Maize | Gray Leaf Spot, Northern Corn Leaf Blight, Maize Streak Virus |
| Potato | Late Blight, Early Blight |
| Wheat | Stripe Rust, Fusarium Head Blight |
| Rice | Bacterial Leaf Blight, Rice Blast |
| Beans | Angular Leaf Spot, Bean Common Mosaic Virus |
| Cassava | Cassava Mosaic Disease, Cassava Brown Streak Disease |
| Banana | Black Sigatoka, Banana Bunchy Top Virus |

## Installation

```bash
# Clone/navigate to project
cd shamba_advisor

# Install dependencies
pip install -r requirements.txt

# Run the system (database auto-initializes on first run)
python main.py
```

## Usage

### Interactive Mode
```bash
python main.py
```

### Command Line Arguments
```bash
# Single query
python main.py "My tomato leaves have brown spots with yellow halos"

# Run batch tests
python main.py --test

# Show help
python main.py --help

# List available crops
python main.py --crops
```

### Example Session
```
🌿 Describe your crop problem: My maize leaves have rectangular gray spots with yellow edges

🔍 Stage 1: Guardrail & Intent Extraction...
   ✓ Crop identified: maize
   ✓ Symptoms: ['gray', 'spots', 'yellow', 'rectangular', 'lesions', 'margins']

📚 Stage 1b: Retrieving knowledge from RAG database...
   ✓ Found 2 potential disease(s):
      - Gray Leaf Spot (match score: 8)
      - Northern Corn Leaf Blight (match score: 3)

🧠 Stage 2: Disease Analysis & Risk Assessment...
   ✓ Most likely: Gray Leaf Spot
   ✓ Confidence: 82%
   ✓ Risk Level: MEDIUM
   ✓ Stage: EARLY

📋 Stage 3: Generating Advisory...

==================================================
          SHAMBA ADVISOR
==================================================

  CROP                    : MAIZE

  POSSIBLE PROBLEM
  Gray Leaf Spot

  RISK ASSESSMENT
  RISK LEVEL              : 🟡 MEDIUM
  DETECTION STAGE         : 🌱 EARLY STAGE
  CONFIDENCE              : 82%

  OBSERVED SYMPTOMS & EVIDENCE
  • Observed 'gray spots' matches typical symptom: Rectangular gray lesions on leaves, yellow halos, premature leaf death...
  • 'yellow margins' is an early sign of this disease

  IMMEDIATE ACTIONS
  1. Remove affected leaves
  2. Improve airflow
  3. Avoid prolonged leaf wetness
  4. Apply fungicide at tasseling
  5. Rotate with non-host crops

  PREVENTION MEASURES
  • Crop rotation
  • Resistant hybrids
  • Residue management
  • Balanced fertility

  MONITORING RECOMMENDATIONS
  • Check plants daily for symptom progression
  • Monitor neighboring plants for spread
  • Track weather conditions favorable to disease
  • Scout field every 3-4 days
  • Watch for new lesions on upper leaves

  IMPORTANT WARNING
  This is an AI-based early warning advisory
  based on symptom pattern matching.
  It is NOT a laboratory diagnosis.

==================================================

[Saved to: advisory.txt and advisory.json]
```

## Output Files

Each advisory generates two files:

- **advisory.txt** - Human-readable formatted advisory
- **advisory.json** - Structured data for integration

## Development

### Running Tests
```bash
# Test individual modules
python database_manager.py
python stage_1_guardrail.py
python stage_2_disease_advisor.py
python advisory_generator.py

# Run full pipeline test
python main.py --test
```

### Adding New Diseases
Edit `database_manager.py` and add entries to the `diseases_data` list in `_populate_initial_data()`.

### Extending with LLMs
The system is designed for future LLM integration:
- Stage 1: Can use LLM for better intent extraction
- Stage 2: Can use LLM for more sophisticated reasoning
- Set `OPENAI_API_KEY` in `.env` when ready

## Design Principles

1. **No Hallucination**: Only uses verified knowledge from the RAG database
2. **Early Warning Focus**: Prioritizes early detection and prevention
3. **Uncertainty Acknowledged**: Confidence scores, alternatives, escalation flags
4. **Farmer-Centric**: Simple language, actionable steps, clear warnings
5. **Offline-Capable**: Core functionality works without internet/LLMs

## Disclaimer

> This system provides AI-based early warning advisories based on symptom pattern matching against a curated knowledge base. It is NOT a substitute for laboratory diagnosis or professional agricultural advice. Always consult your local agricultural extension officer or plant clinic for definitive diagnosis and treatment recommendations.

## License

Educational/Research Project - Shamba Advisor Team