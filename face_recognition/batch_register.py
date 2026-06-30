import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2, glob
from face_recognition.face_recognizer import register_face, predict_for_child

DATA_FRAMES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATA_FRAMES")
DATA_JSON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATA_JSON")


def register_all_children():
    if not os.path.exists(DATA_FRAMES_DIR):
        print(f"DATA_FRAMES not found at {DATA_FRAMES_DIR}")
        return

    person_dirs = sorted(glob.glob(os.path.join(DATA_FRAMES_DIR, "P*")))
    if not person_dirs:
        print(f"No P* folders found in {DATA_FRAMES_DIR}")
        return

    success = 0
    failed = 0
    for pdir in person_dirs:
        person_id = os.path.basename(pdir)
        frames = sorted(glob.glob(os.path.join(pdir, "**", "*.jpg"), recursive=True))
        if not frames:
            print(f"  SKIP  {person_id}: no frames")
            continue

        registered = False
        for f in frames:
            img = cv2.imread(f)
            if img is None:
                continue
            result = register_face(person_id, person_id, img)
            if result["success"]:
                prediction = predict_for_child(person_id)
                risk = f" | risk: {prediction['risk_level']} ({prediction['risk_score']:.3f})" if prediction else ""
                print(f"  DONE  {person_id} from {os.path.basename(f)}{risk}")
                success += 1
                registered = True
                break
        if not registered:
            print(f"  FAIL  {person_id}: no face detected")
            failed += 1

    print(f"\nDone. Registered: {success}, Failed: {failed}")


if __name__ == "__main__":
    register_all_children()
