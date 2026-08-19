import sqlite3
import json
from typing import List, Dict, Optional
import os
import threading


class CropDiseaseDatabase:
    def __init__(self, db_path: str = "crop_disease.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_memory_db = (db_path == ":memory:")
        if self._init_memory_db:
            self._create_memory_schema()
        else:
            self.init_database()

    def _get_connection(self):
        if self._init_memory_db:
            if not hasattr(self._local, 'conn'):
                self._local.conn = sqlite3.connect(":memory:", check_same_thread=False)
                cursor = self._local.conn.cursor()
                self._create_schema(cursor)
                self._populate_initial_data(cursor)
                self._local.conn.commit()
            return self._local.conn
        return sqlite3.connect(self.db_path)

    def _create_memory_schema(self):
        """Create schema in memory database (called once per thread)."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        cursor = conn.cursor()
        self._create_schema(cursor)
        self._populate_initial_data(cursor)
        conn.commit()
        conn.close()

    def _create_schema(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                early_symptoms TEXT NOT NULL,
                advanced_symptoms TEXT NOT NULL,
                causes TEXT NOT NULL,
                risk_factors TEXT NOT NULL,
                prevention TEXT NOT NULL,
                management TEXT NOT NULL,
                warning_signs TEXT NOT NULL,
                FOREIGN KEY (crop_id) REFERENCES crops (id),
                UNIQUE(crop_id, name)
            )
        """)

    def init_database(self):
        """Create the crop disease database schema and populate initial data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        self._create_schema(cursor)
        conn.commit()
        self._populate_initial_data(cursor)
        conn.commit()
        conn.close()

    def _populate_initial_data(self, cursor):
        """Populate the database with initial crop disease knowledge."""
        crops_data = [
            ("tomato",),
            ("maize",),
            ("potato",),
            ("wheat",),
            ("rice",),
            ("beans",),
            ("cassava",),
            ("banana",),
        ]

        for crop in crops_data:
            cursor.execute("INSERT OR IGNORE INTO crops (name) VALUES (?)", crop)

        diseases_data = [
            {
                "crop": "tomato",
                "name": "Early Blight",
                "symptoms": "Small dark spots on leaves, yellowing leaves, concentric rings on spots",
                "early_symptoms": "Small brown spots on lower leaves, yellowing around spots",
                "advanced_symptoms": "Large lesions with concentric rings, leaf drop, fruit rot",
                "causes": "Fungus Alternaria solani, spreads via wind and rain splash",
                "risk_factors": "High humidity, warm temperatures (24-29°C), poor airflow, wet foliage",
                "prevention": "Crop rotation, proper spacing, avoid overhead watering, mulching",
                "management": "Remove affected leaves, apply copper-based fungicides, improve air circulation",
                "warning_signs": "Rapid spread in humid conditions, defoliation, reduced yield"
            },
            {
                "crop": "tomato",
                "name": "Late Blight",
                "symptoms": "Water-soaked lesions on leaves, white fuzzy growth, brown lesions on stems",
                "early_symptoms": "Pale green water-soaked spots, white mold on leaf undersides",
                "advanced_symptoms": "Large brown lesions, stem cankers, fruit rot with firm brown lesions",
                "causes": "Oomycete Phytophthora infestans, spreads rapidly in cool wet conditions",
                "risk_factors": "Cool temperatures (10-20°C), high humidity >90%, rain or fog",
                "prevention": "Resistant varieties, proper spacing, avoid overhead irrigation, remove volunteers",
                "management": "Remove infected plants, apply fungicides preventively, destroy crop residue",
                "warning_signs": "Explosive epidemic potential, complete crop loss in days"
            },
            {
                "crop": "tomato",
                "name": "Bacterial Leaf Spot",
                "symptoms": "Small water-soaked spots, yellow halos, scabby lesions on fruit",
                "early_symptoms": "Tiny water-soaked spots on leaves, yellow margins",
                "advanced_symptoms": "Spots merge, leaves yellow and drop, raised scabby fruit spots",
                "causes": "Bacteria Xanthomonas campestris, seed-borne, spreads by water splash",
                "risk_factors": "Warm wet weather (25-30°C), high humidity, overhead irrigation",
                "prevention": "Disease-free seed, crop rotation, avoid working in wet fields",
                "management": "Copper sprays, remove infected debris, avoid overhead watering",
                "warning_signs": "Rapid spread during rain, seed transmission to next season"
            },
            {
                "crop": "maize",
                "name": "Gray Leaf Spot",
                "symptoms": "Rectangular gray lesions on leaves, yellow halos, premature leaf death",
                "early_symptoms": "Small tan rectangular spots with yellow margins",
                "advanced_symptoms": "Large gray lesions merging, extensive leaf blighting, stalk rot",
                "causes": "Fungus Cercospora zeae-maydis, overwinters in residue",
                "risk_factors": "High humidity, warm temps (25-30°C), continuous maize, minimum tillage",
                "prevention": "Crop rotation, resistant hybrids, residue management, balanced fertility",
                "management": "Fungicide at tasseling, rotate with non-host crops, bury residue",
                "warning_signs": "Yield loss up to 50%, stalk lodging, ear rot"
            },
            {
                "crop": "maize",
                "name": "Northern Corn Leaf Blight",
                "symptoms": "Long elliptical gray-green lesions, fuzzy spores in humid conditions",
                "early_symptoms": "Small gray-green elliptical spots on lower leaves",
                "advanced_symptoms": "Large lesions merging, leaf death, reduced photosynthesis",
                "causes": "Fungus Exserohilum turcicum, survives in crop residue",
                "risk_factors": "Cool wet weather (18-27°C), high humidity, susceptible hybrids",
                "prevention": "Resistant hybrids, crop rotation, tillage to bury residue",
                "management": "Foliar fungicides at early onset, rotate crops, manage residue",
                "warning_signs": "Significant yield loss if before silking, stalk weakening"
            },
            {
                "crop": "maize",
                "name": "Maize Streak Virus",
                "symptoms": "Yellow-white streaks on leaves, stunted growth, poor ear formation",
                "early_symptoms": "Fine yellow streaks on young leaves, transmitted by leafhoppers",
                "advanced_symptoms": "Broad yellow stripes, severe stunting, no ear development",
                "causes": "Mastrevirus transmitted by Cicadulina leafhoppers",
                "risk_factors": "Early planting, leafhopper populations, susceptible varieties",
                "prevention": "Resistant varieties, early planting, insecticide seed treatment",
                "management": "Control leafhoppers, remove infected plants, use certified seed",
                "warning_signs": "Total crop failure in severe infections, vector-borne spread"
            },
            {
                "crop": "potato",
                "name": "Late Blight",
                "symptoms": "Water-soaked lesions, white sporulation, brown rot on tubers",
                "early_symptoms": "Pale green water-soaked spots, white mold on leaf undersides",
                "advanced_symptoms": "Rapid leaf blighting, stem lesions, firm brown tuber rot",
                "causes": "Phytophthora infestans, same pathogen as tomato late blight",
                "risk_factors": "Cool wet conditions (10-20°C), high humidity, dense canopy",
                "prevention": "Certified seed, resistant varieties, proper hilling, avoid overhead irrigation",
                "management": "Fungicide program, destroy cull piles, vine killing before harvest",
                "warning_signs": "Explosive epidemic, complete crop loss, tuber rot in storage"
            },
            {
                "crop": "potato",
                "name": "Early Blight",
                "symptoms": "Dark brown lesions with concentric rings, target spot appearance",
                "early_symptoms": "Small dark spots on older leaves, yellow halos",
                "advanced_symptoms": "Large target lesions, leaf yellowing and drop, tuber lesions",
                "causes": "Alternaria solani, overwinters in soil and debris",
                "risk_factors": "Warm temps (20-30°C), alternating wet/dry, stressed plants",
                "prevention": "Crop rotation, balanced nutrition, avoid stress, resistant varieties",
                "management": "Foliar fungicides, proper irrigation, remove crop residue",
                "warning_signs": "Premature defoliation, reduced tuber size, secondary infections"
            },
            {
                "crop": "wheat",
                "name": "Stripe Rust",
                "symptoms": "Yellow-orange pustules in stripes on leaves, stunted growth",
                "early_symptoms": "Small yellow pustules forming stripes on leaves",
                "advanced_symptoms": "Extensive pustules, leaf death, shriveled grain",
                "causes": "Puccinia striiformis, wind-dispersed spores",
                "risk_factors": "Cool moist conditions (10-15°C), susceptible varieties, early planting",
                "prevention": "Resistant varieties, timely planting, fungicide seed treatment",
                "management": "Foliar fungicides at flag leaf, resistant varieties, crop rotation",
                "warning_signs": "Rapid spread by wind, up to 100% yield loss in susceptible varieties"
            },
            {
                "crop": "wheat",
                "name": "Fusarium Head Blight",
                "symptoms": "Bleached spikelets, pink/orange spores, shriveled tombstone kernels",
                "early_symptoms": "Water-soaked appearance on spikelets, premature bleaching",
                "advanced_symptoms": "Pink spore masses, mycotoxin contamination, light shriveled kernels",
                "causes": "Fusarium graminearum, overwinters in residue",
                "risk_factors": "Warm humid flowering (20-30°C), corn/wheat rotation, no-till",
                "prevention": "Resistant varieties, crop rotation, fungicide at flowering",
                "management": "Triazole fungicides at anthesis, avoid corn rotation, clean seed",
                "warning_signs": "Mycotoxin (DON) contamination, market rejection, health hazard"
            },
            {
                "crop": "rice",
                "name": "Bacterial Leaf Blight",
                "symptoms": "Yellow-white lesions with wavy margins, leaf drying, wilting",
                "early_symptoms": "Water-soaked lesions near leaf tip, yellow halos",
                "advanced_symptoms": "Large lesions merging, leaf blight, seedling wilting (kresek)",
                "causes": "Xanthomonas oryzae, seed-borne, water-borne, insect vectors",
                "risk_factors": "High nitrogen, wet conditions, susceptible varieties, typhoons",
                "prevention": "Resistant varieties, balanced fertilizer, clean seed, water management",
                "management": "Copper compounds, reduce nitrogen, drain fields, resistant varieties",
                "warning_signs": "Kresek phase kills seedlings, epidemic in wet seasons"
            },
            {
                "crop": "rice",
                "name": "Rice Blast",
                "symptoms": "Diamond-shaped lesions with gray centers, brown margins, neck rot",
                "early_symptoms": "Small white to gray spots with dark brown borders",
                "advanced_symptoms": "Large diamond lesions, neck rot, panicle blast, whiteheads",
                "causes": "Magnaporthe oryzae, airborne spores, survives in residue",
                "risk_factors": "High humidity, cool nights (15-25°C), excess nitrogen, drought stress",
                "prevention": "Resistant varieties, balanced N, water management, seed treatment",
                "management": "Fungicides (tricyclazole), resistant genes, silicon fertilizer",
                "warning_signs": "Neck rot causes total grain loss, explosive epidemics"
            },
            {
                "crop": "beans",
                "name": "Angular Leaf Spot",
                "symptoms": "Angular brown lesions on leaves, pods, stems, limited by veins",
                "early_symptoms": "Small angular brown spots on lower leaves",
                "advanced_symptoms": "Lesions merge, defoliation, pod lesions, seed discoloration",
                "causes": "Pseudocercospora griseola, seed-borne, residue-borne",
                "risk_factors": "Warm humid (20-28°C), dense canopy, susceptible varieties",
                "prevention": "Certified seed, crop rotation, resistant varieties, residue management",
                "management": "Fungicides, remove debris, rotate with cereals, clean seed",
                "warning_signs": "Seed transmission, yield loss 30-80%"
            },
            {
                "crop": "beans",
                "name": "Bean Common Mosaic Virus",
                "symptoms": "Mosaic patterns, leaf curling, stunting, necrotic lesions",
                "early_symptoms": "Light/dark green mosaic on young leaves, slight curling",
                "advanced_symptoms": "Severe mosaic, necrosis, plant death (black root), yield loss",
                "causes": "BCMV, aphid-transmitted, seed-borne",
                "risk_factors": "Aphid flights, susceptible varieties, infected seed",
                "prevention": "Virus-free seed, resistant varieties, aphid control, rogue infected plants",
                "management": "Remove infected plants, control aphids, use certified seed",
                "warning_signs": "Necrotic strain kills plants, seed transmission"
            },
            {
                "crop": "cassava",
                "name": "Cassava Mosaic Disease",
                "symptoms": "Yellow mosaic, leaf distortion, stunting, reduced root yield",
                "early_symptoms": "Mild mosaic on young leaves, slight distortion",
                "advanced_symptoms": "Severe mosaic, severe stunting, small roots, plant death",
                "causes": "Cassava mosaic begomoviruses, whitefly-transmitted",
                "risk_factors": "Whitefly populations, susceptible varieties, infected cuttings",
                "prevention": "Clean cuttings, resistant varieties, whitefly control, rogueing",
                "management": "Use healthy planting material, resistant varieties, vector control",
                "warning_signs": "Total crop loss in susceptible varieties, whitefly spread"
            },
            {
                "crop": "cassava",
                "name": "Cassava Brown Streak Disease",
                "symptoms": "Yellow leaf veins, brown streaks on stems, root necrosis",
                "early_symptoms": "Feathery yellowing along veins, mild stem streaking",
                "advanced_symptoms": "Severe root necrosis, constrictions, post-harvest rot",
                "causes": "Cassava brown streak ipomoviruses, whitefly-transmitted",
                "risk_factors": "Whitefly pressure, infected cuttings, susceptible varieties",
                "prevention": "Virus-free cuttings, resistant varieties, whitefly management",
                "management": "Rogue infected plants, clean planting material, resistant varieties",
                "warning_signs": "Root necrosis makes roots unmarketable, silent spread"
            },
            {
                "crop": "banana",
                "name": "Black Sigatoka",
                "symptoms": "Dark streaks on leaves, yellow halos, leaf death, reduced bunch weight",
                "early_symptoms": "Small yellow streaks on older leaves, darkening to brown",
                "advanced_symptoms": "Large necrotic areas, premature leaf death, small bunches",
                "causes": "Pseudocercospora fijiensis, wind-borne spores",
                "risk_factors": "High rainfall, humidity >90%, warm temps (25-28°C), dense planting",
                "prevention": "Resistant varieties, proper spacing, drainage, deleafing",
                "management": "Fungicide rotation, deleafing, improved drainage, forecasting",
                "warning_signs": "50% yield loss, premature ripening, high control costs"
            },
            {
                "crop": "banana",
                "name": "Banana Bunchy Top Virus",
                "symptoms": "Dark green streaks on petioles, bunched leaves, stunted plants",
                "early_symptoms": "Morse code streaks on petioles, leaf margins curled",
                "advanced_symptoms": "Rosette appearance, no fruit production, plant death",
                "causes": "Banana bunchy top virus, aphid-transmitted (Pentalonia nigronervosa)",
                "risk_factors": "Infected suckers, aphid vectors, no resistant varieties",
                "prevention": "Virus-free planting material, aphid control, rogue infected mats",
                "management": "Destroy infected mats, control aphids, use tissue culture plants",
                "warning_signs": "No cure, complete yield loss, spreads via planting material"
            },
        ]

        for disease in diseases_data:
            cursor.execute("SELECT id FROM crops WHERE name = ?", (disease["crop"],))
            crop_id = cursor.fetchone()
            if crop_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO diseases 
                    (crop_id, name, symptoms, early_symptoms, advanced_symptoms, causes, risk_factors, prevention, management, warning_signs)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    crop_id[0], disease["name"], disease["symptoms"], disease["early_symptoms"],
                    disease["advanced_symptoms"], disease["causes"], disease["risk_factors"],
                    disease["prevention"], disease["management"], disease["warning_signs"]
                ))

    def read_rag(self, crop: str, symptoms: List[str]) -> List[Dict]:
        """Retrieve relevant disease knowledge from the database based on crop and symptoms."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM crops WHERE name = ?", (crop.lower(),))
        crop_row = cursor.fetchone()

        if not crop_row:
            if not self._init_memory_db:
                conn.close()
            return []

        crop_id = crop_row[0]

        cursor.execute("""
            SELECT * FROM diseases WHERE crop_id = ?
        """, (crop_id,))

        diseases = cursor.fetchall()
        if not self._init_memory_db:
            conn.close()

        results = []
        for disease in diseases:
            disease_dict = dict(disease)
            match_score = self._calculate_match_score(symptoms, disease_dict)
            if match_score > 0:
                disease_dict["match_score"] = match_score
                results.append(disease_dict)

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

    def _calculate_match_score(self, symptoms: List[str], disease: Dict) -> int:
        """Calculate how well the symptoms match the disease."""
        score = 0
        symptom_text = " ".join(symptoms).lower()
        
        disease_symptoms = disease["symptoms"].lower()
        disease_early = disease["early_symptoms"].lower()
        disease_advanced = disease["advanced_symptoms"].lower()

        for symptom in symptoms:
            symptom_lower = symptom.lower()
            if symptom_lower in disease_symptoms:
                score += 3
            if symptom_lower in disease_early:
                score += 2
            if symptom_lower in disease_advanced:
                score += 1

        return score

    def get_all_crops(self) -> List[str]:
        """Get list of all crops in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM crops")
        crops = [row[0] for row in cursor.fetchall()]
        if not self._init_memory_db:
            conn.close()
        return crops

    def get_diseases_for_crop(self, crop: str) -> List[Dict]:
        """Get all diseases for a specific crop."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM crops WHERE name = ?", (crop.lower(),))
        crop_row = cursor.fetchone()

        if not crop_row:
            if not self._init_memory_db:
                conn.close()
            return []

        crop_id = crop_row[0]
        cursor.execute("SELECT * FROM diseases WHERE crop_id = ?", (crop_id,))
        diseases = [dict(row) for row in cursor.fetchall()]
        if not self._init_memory_db:
            conn.close()
        return diseases


if __name__ == "__main__":
    db = CropDiseaseDatabase()
    print("Database initialized successfully!")
    print(f"Crops available: {db.get_all_crops()}")
    
    test_results = db.read_rag("tomato", ["yellow leaves", "brown spots"])
    print(f"\nTest RAG for tomato with symptoms ['yellow leaves', 'brown spots']:")
    for disease in test_results:
        print(f"  - {disease['name']} (score: {disease['match_score']})")