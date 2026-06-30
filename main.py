import os
import json
from fusion_model.inference import predict_from_json

DATA_PATH = "DATA_JSON"
results = []

for person in os.listdir(DATA_PATH):

    person_path = os.path.join(DATA_PATH, person)

    emotion_path = os.path.join(person_path, "emotion.json")
    pose_path = os.path.join(person_path, "pose.json")

    if not os.path.exists(emotion_path) or not os.path.exists(pose_path):
        continue

    result = predict_from_json(emotion_path, pose_path)

    result["person_id"] = person

    results.append(result)

    print(person, "->", round(result["risk_score"], 3), result["risk_level"])

with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

print("\nAll results saved to results.json")