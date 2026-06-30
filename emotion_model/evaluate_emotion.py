import json
import os
from collections import Counter
import matplotlib.pyplot as plt

DATA_PATH = "DATA_JSON"

all_emotions = []

for person in os.listdir(DATA_PATH):

    emotion_path = os.path.join(DATA_PATH, person, "emotion.json")

    if not os.path.exists(emotion_path):
        continue

    with open(emotion_path) as f:
        data = json.load(f)

    if "dominant_emotion" in data:
        all_emotions.append(data["dominant_emotion"])

counter = Counter(all_emotions)

print("\nEmotion Distribution:")
for k, v in counter.items():
    print(k, ":", v)

plt.bar(counter.keys(), counter.values())
plt.title("Emotion Distribution")
plt.xticks(rotation=45)
plt.show()