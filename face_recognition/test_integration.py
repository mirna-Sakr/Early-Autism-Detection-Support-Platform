import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
from face_recognition.face_recognizer import recognize_and_predict

img = cv2.imread("DATA_FRAMES/P001/day1/vid1/frame_1.jpg")
r = recognize_and_predict(img)
print("Faces:", r["faces_detected"])
for m in r["matches"]:
    if m["match"]:
        print("Child:", m["match"]["child_id"])
        pred = m["match"].get("prediction")
        if pred:
            print("  Risk:", pred["risk_level"], "(", round(pred["risk_score"], 3), ")")
            print("  Insights:", pred["key_insights"])
            print("  Label:", pred.get("actual_label", "?"))
    else:
        print("  No match at", m["bbox"])
