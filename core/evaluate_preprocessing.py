import os
import cv2
from core.preprocessing import is_blurry

DATA_PATH = "DATA_FRAMES"

total_frames = 0
kept_frames = 0
blurry_frames = 0


def process_folder(folder_path):
    global total_frames, kept_frames, blurry_frames

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isdir(item_path):
            process_folder(item_path)

        elif item_path.lower().endswith((".jpg", ".png", ".jpeg")):
            image = cv2.imread(item_path)

            if image is None:
                continue

            total_frames += 1

            if is_blurry(image):
                blurry_frames += 1
            else:
                kept_frames += 1


process_folder(DATA_PATH)

print("\n=== Preprocessing Evaluation ===")
print("Total Frames:", total_frames)
print("Kept Frames:", kept_frames)
print("Blurry Frames Removed:", blurry_frames)

if total_frames > 0:
    print("Retention Rate:", round(kept_frames / total_frames, 3))
    print("Noise Removed:", round(blurry_frames / total_frames, 3))