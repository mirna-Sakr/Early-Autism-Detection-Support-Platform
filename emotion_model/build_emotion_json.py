import json
import os
from emotion_model.person_aggregation import process_person
from emotion_model.emotion_features import extract_emotion_features

DATASET_PATH = "DATA_FRAMES"
OUTPUT_PATH = "OUTPUT_JSON"

os.makedirs(OUTPUT_PATH, exist_ok=True)

def generate_emotion_json(person_path, output_path):
    emotions, conf = process_person(person_path)
    features = extract_emotion_features(emotions, conf)

    with open(output_path, "w") as f:
        json.dump(features, f, indent=4)

    print(f"emotion.json created for {person_path}!")


# 🔥 هنا بقى المهم: loop على كل الأشخاص
for person_folder in os.listdir(DATASET_PATH):
    person_path = os.path.join(DATASET_PATH, person_folder)

    if os.path.isdir(person_path):   # يتأكد إنه فولدر
        output_file = os.path.join(OUTPUT_PATH, f"{person_folder}.json")
        generate_emotion_json(person_path, output_file)