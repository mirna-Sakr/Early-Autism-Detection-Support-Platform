import os
import cv2
from deepface import DeepFace
from core.preprocessing import is_blurry

def extract_sequence_from_video(video_path):

    emotion_sequence = []
    confidence_sequence = []

    for img in sorted(os.listdir(video_path)):  # ✅ ترتيب الصور

        img_path = os.path.join(video_path, img)

        if not img_path.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        try:
            image = cv2.imread(img_path)

            if image is None or is_blurry(image):  # ✅ فلترة
                continue

            result = DeepFace.analyze(
                img_path,
                actions=['emotion'],
                enforce_detection=False
            )

            # ✅ حل مشكلة list/dict
            if isinstance(result, list):
                result = result[0]

            emotions = result["emotion"]

            dominant = max(emotions, key=emotions.get)

            emotion_sequence.append(dominant)
            confidence_sequence.append(max(emotions.values()) / 100)

        except Exception as e:
            print(f"Error in {img_path}: {e}")
            continue

    return emotion_sequence, confidence_sequence