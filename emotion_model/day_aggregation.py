import os
from emotion_model.extract_sequence import extract_sequence_from_video

def process_day(day_path):

    day_emotions = []
    day_conf = []

    for video in sorted(os.listdir(day_path)):  # ✅ ترتيب

        video_path = os.path.join(day_path, video)

        if not os.path.isdir(video_path):
            continue

        seq, conf = extract_sequence_from_video(video_path)

        day_emotions.extend(seq)
        day_conf.extend(conf)

    return day_emotions, day_conf