import os
from emotion_model.day_aggregation import process_day

def process_person(person_path):

    all_emotions = []
    all_conf = []

    for day in sorted(os.listdir(person_path)):  # ✅ ترتيب

        day_path = os.path.join(person_path, day)

        if not os.path.isdir(day_path):
            continue

        emotions, conf = process_day(day_path)

        all_emotions.extend(emotions)
        all_conf.extend(conf)

    return all_emotions, all_conf