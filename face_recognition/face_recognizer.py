import cv2
import numpy as np
import os
import json
import base64
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "lbph_model.yml")
LABEL_MAP_PATH = os.path.join(BASE_DIR, "label_map.json")
IMAGES_DIR = os.path.join(BASE_DIR, "registered_images")
DETECTED_DIR = os.path.join(BASE_DIR, "detected_faces")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DETECTED_DIR, exist_ok=True)

CONFIDENCE_THRESHOLD = 120

_MODEL_FILE = os.path.expanduser("~/.mediapipe/models/blaze_face_short_range.tflite")
_face_detector = None


def _get_detector():
    global _face_detector
    if _face_detector is None:
        if not os.path.exists(_MODEL_FILE):
            import urllib.request
            os.makedirs(os.path.dirname(_MODEL_FILE), exist_ok=True)
            url = ("https://storage.googleapis.com/mediapipe-models/"
                   "face_detector/blaze_face_short_range/float16/latest/"
                   "blaze_face_short_range.tflite")
            urllib.request.urlretrieve(url, _MODEL_FILE)
        options = vision.FaceDetectorOptions(
            base_options=python.BaseOptions(model_asset_path=_MODEL_FILE),
            running_mode=vision.RunningMode.IMAGE,
            min_detection_confidence=0.5
        )
        _face_detector = vision.FaceDetector.create_from_options(options)
    return _face_detector


def _load_label_map():
    if os.path.exists(LABEL_MAP_PATH):
        with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ids": []}


def _save_label_map(data):
    with open(LABEL_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _get_model():
    model = cv2.face.LBPHFaceRecognizer_create()
    if os.path.exists(MODEL_PATH):
        model.read(MODEL_PATH)
    return model


def _save_model(model):
    model.write(MODEL_PATH)


def detect_faces(image_bgr):
    detector = _get_detector()
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = detector.detect(mp_img)
    faces = []
    if results.detections:
        for det in results.detections:
            bbox = det.bounding_box
            faces.append((bbox.origin_x, bbox.origin_y, bbox.width, bbox.height))
    return faces


def _preprocess_face(face_bgr):
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (200, 200))
    return cv2.equalizeHist(resized)


def register_face(child_id: str, name: str, image_bgr):
    faces = detect_faces(image_bgr)
    if len(faces) == 0:
        return {"success": False, "error": "No face detected"}

    x, y, w, h = faces[0]
    face_roi = image_bgr[y:y+h, x:x+w]
    if face_roi.size == 0:
        return {"success": False, "error": "Invalid face region"}

    processed = _preprocess_face(face_roi)
    label_map = _load_label_map()

    if child_id in label_map["ids"]:
        idx = label_map["ids"].index(child_id)
        model = _get_model()
        model.update([processed], np.array([idx], dtype=np.int32))
        _save_model(model)
    else:
        idx = len(label_map["ids"])
        label_map["ids"].append(child_id)
        label_map.setdefault("names", {})[child_id] = name
        _save_label_map(label_map)
        model = _get_model()
        model.update([processed], np.array([idx], dtype=np.int32))
        _save_model(model)

    cv2.imwrite(os.path.join(IMAGES_DIR, f"{child_id}.jpg"), image_bgr)

    child_dir = os.path.join(DETECTED_DIR, child_id)
    os.makedirs(child_dir, exist_ok=True)
    count = len(os.listdir(child_dir))
    cv2.imwrite(os.path.join(child_dir, f"face_{count+1}.jpg"), face_roi)

    return {"success": True, "child_id": child_id, "name": name}


def recognize_face(image_bgr, source_name=None):
    faces = detect_faces(image_bgr)
    if len(faces) == 0:
        return {"faces_detected": 0, "matches": []}

    if not os.path.exists(MODEL_PATH):
        return {"faces_detected": len(faces), "matches": [],
                "error": "No registered faces. Please register first."}

    model = _get_model()
    label_map = _load_label_map()
    results = []

    for (x, y, w, h) in faces:
        face_roi = image_bgr[y:y+h, x:x+w]
        if face_roi.size == 0:
            continue

        processed = _preprocess_face(face_roi)
        label_id, confidence = model.predict(processed)

        match = None
        if label_id < len(label_map["ids"]):
            child_id = label_map["ids"][label_id]
            name = label_map.get("names", {}).get(child_id, "")
            if confidence < CONFIDENCE_THRESHOLD:
                child_dir = os.path.join(DETECTED_DIR, child_id)
                os.makedirs(child_dir, exist_ok=True)
                count = len(os.listdir(child_dir))
                save_name = source_name or f"frame_{count+1}"
                cv2.imwrite(os.path.join(child_dir, f"{save_name}.jpg"), face_roi)

                registered_img = os.path.join(IMAGES_DIR, f"{child_id}.jpg")
                img_b64 = None
                if os.path.exists(registered_img):
                    with open(registered_img, "rb") as f:
                        img_b64 = base64.b64encode(f.read()).decode("utf-8")

                match = {
                    "child_id": child_id,
                    "name": name,
                    "confidence": round(float(confidence), 2),
                    "image_base64": img_b64
                }

        results.append({
            "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
            "match": match
        })

    return {"faces_detected": len(faces), "matches": results}


def test_recognize_all():
    DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "DATA_FRAMES")
    if not os.path.exists(DATA_DIR):
        print(f"DATA_FRAMES not found at {DATA_DIR}")
        return

    person_dirs = sorted([
        p for p in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, p)) and p.startswith("P")
    ])

    import glob
    for pid in person_dirs:
        frames = sorted(glob.glob(os.path.join(DATA_DIR, pid, "**", "*.jpg"), recursive=True))
        if not frames:
            continue
        last_frame = frames[-1]
        img = cv2.imread(last_frame)
        if img is None:
            continue
        result = recognize_face(img, source_name=f"{pid}_last")
        if result["faces_detected"] > 0 and result["matches"][0]["match"]:
            m = result["matches"][0]["match"]
            print(f"  {pid} -> matched {m['child_id']} (conf={m['confidence']})")
        else:
            print(f"  {pid} -> NO MATCH")


def predict_for_child(child_id):
    DATA_JSON = os.path.join(os.path.dirname(BASE_DIR), "DATA_JSON")
    person_dir = os.path.join(DATA_JSON, child_id)
    emotion_path = os.path.join(person_dir, "emotion.json")
    pose_path = os.path.join(person_dir, "pose.json")
    label_path = os.path.join(person_dir, "label.txt")

    if not os.path.exists(emotion_path) or not os.path.exists(pose_path):
        return None

    try:
        from fusion_model.inference import predict_from_json
        result = predict_from_json(emotion_path, pose_path)
        result["person_id"] = child_id
        if os.path.exists(label_path):
            with open(label_path) as f:
                result["actual_label"] = int(f.read().strip())
        return result
    except:
        return None


def recognize_and_predict(image_bgr):
    rec_result = recognize_face(image_bgr)
    for m in rec_result["matches"]:
        if m["match"]:
            child_id = m["match"]["child_id"]
            prediction = predict_for_child(child_id)
            m["match"]["prediction"] = prediction
    return rec_result


def process_camera_frame(image_bgr, child_id, save_to_data_frames=True):
    DATA_FRAMES = os.path.join(os.path.dirname(BASE_DIR), "DATA_FRAMES")
    result = recognize_face(image_bgr)

    for m in result["matches"]:
        if m["match"] and m["match"]["child_id"] == child_id:
            if save_to_data_frames:
                child_dir = os.path.join(DATA_FRAMES, child_id, "detected_faces")
                os.makedirs(child_dir, exist_ok=True)
                count = len([f for f in os.listdir(child_dir) if f.endswith(".jpg")])
                cv2.imwrite(os.path.join(child_dir, f"cam_{count+1}.jpg"), image_bgr)
            return result

    return result


def process_camera_frames(frames_folder, save_to_data_frames=True):
    DATA_FRAMES = os.path.join(os.path.dirname(BASE_DIR), "DATA_FRAMES")
    import glob

    frames = sorted(glob.glob(os.path.join(frames_folder, "*.jpg")) +
                    glob.glob(os.path.join(frames_folder, "*.png")))
    if not frames:
        return {"processed": 0, "matches": []}

    results_summary = []
    for f in frames:
        img = cv2.imread(f)
        if img is None:
            continue

        rec_result = recognize_face(img, source_name=os.path.basename(f))

        for m in rec_result["matches"]:
            if m["match"]:
                child_id = m["match"]["child_id"]
                if save_to_data_frames:
                    child_dir = os.path.join(DATA_FRAMES, child_id, "detected_faces")
                    os.makedirs(child_dir, exist_ok=True)
                    count = len([x for x in os.listdir(child_dir) if x.endswith(".jpg")])
                    cv2.imwrite(os.path.join(child_dir, f"cam_{count+1}.jpg"), img)

                results_summary.append({
                    "frame": os.path.basename(f),
                    "child_id": child_id,
                    "confidence": m["match"]["confidence"],
                    "saved_to": os.path.join(DATA_FRAMES, child_id, "detected_faces") if save_to_data_frames else None
                })

    return {
        "processed": len(frames),
        "matched": len(results_summary),
        "results": results_summary
    }


def get_registered_children():
    label_map = _load_label_map()
    return [
        {
            "child_id": cid,
            "name": label_map.get("names", {}).get(cid, ""),
            "has_image": os.path.exists(os.path.join(IMAGES_DIR, f"{cid}.jpg")),
            "detected_count": len(os.listdir(os.path.join(DETECTED_DIR, cid))) if os.path.exists(os.path.join(DETECTED_DIR, cid)) else 0
        }
        for cid in label_map["ids"]
    ]


def get_child_info(child_id: str):
    label_map = _load_label_map()
    if child_id not in label_map["ids"]:
        return None
    name = label_map.get("names", {}).get(child_id, "")
    img_path = os.path.join(IMAGES_DIR, f"{child_id}.jpg")
    img_b64 = None
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    detected_count = 0
    child_dir = os.path.join(DETECTED_DIR, child_id)
    if os.path.exists(child_dir):
        detected_count = len(os.listdir(child_dir))
    return {
        "child_id": child_id,
        "name": name,
        "image_base64": img_b64,
        "detected_images_count": detected_count,
        "detected_folder": child_dir
    }


def delete_child(child_id: str):
    label_map = _load_label_map()
    if child_id not in label_map["ids"]:
        return False

    label_map["ids"].remove(child_id)
    label_map.get("names", {}).pop(child_id, None)
    _save_label_map(label_map)

    all_faces = []
    all_labels = []
    for i, cid in enumerate(label_map["ids"]):
        img_path = os.path.join(IMAGES_DIR, f"{cid}.jpg")
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            faces = detect_faces(img)
            if len(faces) > 0:
                fx, fy, fw, fh = faces[0]
                face_roi = img[fy:fy+fh, fx:fx+fw]
                if face_roi.size > 0:
                    all_faces.append(_preprocess_face(face_roi))
                    all_labels.append(i)
    if all_faces:
        model = cv2.face.LBPHFaceRecognizer_create()
        model.train(all_faces, np.array(all_labels))
        _save_model(model)
    else:
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)

    for p in [os.path.join(IMAGES_DIR, f"{child_id}.jpg"),
              os.path.join(DETECTED_DIR, child_id)]:
        if os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            import shutil
            shutil.rmtree(p)

    return True
