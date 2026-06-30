import os
import json
import pandas as pd

DATA_PATH = "DATA_JSON"
rows = []

for person in os.listdir(DATA_PATH):

    person_path = os.path.join(DATA_PATH, person)

    if not os.path.isdir(person_path):
        continue

    try:
        with open(os.path.join(person_path, "emotion.json")) as f:
            emotion = json.load(f)

        with open(os.path.join(person_path, "pose.json")) as f:
            pose = json.load(f)

        with open(os.path.join(person_path, "label.txt")) as f:
            label = int(f.read().strip())

    except Exception as e:
        print("Skipping:", person, e)
        continue

    row = {}

    # emotion features
    for k, v in sorted(emotion.items()):
        row["emotion_" + k] = v

    # pose features
    for k, v in sorted(pose.items()):
        row["pose_" + k] = v

    row["label"] = label

    rows.append(row)

df = pd.DataFrame(rows)

df = df.sort_index(axis=1)  # تثبيت ترتيب الأعمدة

df.to_csv("features.csv", index=False)

print("Dataset saved -> features.csv")