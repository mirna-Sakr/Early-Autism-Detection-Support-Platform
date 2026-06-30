import os
import re
import glob
import json
from typing import Dict, List, Optional
import cv2
import numpy as np
import mediapipe as mp
from scipy.signal import find_peaks

# ─────────────────────────────────────────────────────────────
#  PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────
BASE_DIR   = r"C:\Users\Sroor For Laptop\OneDrive - Faculty of Computer and Information Sciences (Ain Shams University)\Gp_Project\Graduation-Project\DATA_FRAMES"
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "output")
DATA_JSON_DIR = os.path.join(os.path.dirname(BASE_DIR), "DATA_JSON")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATA_JSON_DIR, exist_ok=True)

SESSIONS_ALL_PATH = os.path.join(OUTPUT_DIR, "sessions_all.json")
FINAL_ALL_PATH    = os.path.join(OUTPUT_DIR, "final_all.json")
EVAL_METRICS_PATH = os.path.join(OUTPUT_DIR, "evaluation_metrics.json")

FPS_ASSUMED            = 30.0
BLUR_FILTER            = False
BLUR_THRESHOLD         = 80.0
AUTISM_THRESHOLD_SCORE = 100.0

# ─────────────────────────────────────────────────────────────
#  MEDIAPIPE
# ─────────────────────────────────────────────────────────────
mp_pose  = mp.solutions.pose
mp_hands = mp.solutions.hands
POSE  = mp_pose.Pose(model_complexity=1)
HANDS = mp_hands.Hands(model_complexity=0, max_num_hands=2)

# ─────────────────────────────────────────────────────────────
#  SESSION I/O
# ─────────────────────────────────────────────────────────────
def load_sessions_all() -> List[Dict]:
    if not os.path.exists(SESSIONS_ALL_PATH):
        return []
    with open(SESSIONS_ALL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sessions_all(sessions: List[Dict]) -> None:
    with open(SESSIONS_ALL_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=4, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────
#  FRAME HELPERS
# ─────────────────────────────────────────────────────────────
def frame_index(path: str) -> int:
    m = re.search(r"frame_(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0

def list_frames(folder: str) -> List[str]:
    frames = (glob.glob(os.path.join(folder, "*.jpg")) +
              glob.glob(os.path.join(folder, "*.png")))
    return sorted(frames, key=frame_index)

def preprocess_frame(bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

def is_blurry(bgr: np.ndarray, thr: float = 80.0) -> bool:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < thr

def collect_all_frames(person_dir: str) -> List[str]:
    direct = list_frames(person_dir)
    if direct:
        return direct
    deep = sorted(
        glob.glob(os.path.join(person_dir, "**", "frame_*.jpg"), recursive=True),
        key=frame_index
    )
    if deep:
        return deep
    return sorted(
        glob.glob(os.path.join(person_dir, "**", "*.jpg"), recursive=True),
        key=frame_index
    )

# ─────────────────────────────────────────────────────────────
#  BEHAVIOUR DETECTORS
# ─────────────────────────────────────────────────────────────
def behaviour_eye_contact(nose, left_eye, right_eye) -> int:
    if any(v is None for v in [nose, left_eye, right_eye]):
        return 0
    eye_line = np.linalg.norm(np.array(left_eye) - np.array(right_eye))
    if eye_line == 0:
        return 0
    ratio = np.linalg.norm(np.array(nose) - np.array(left_eye)) / eye_line
    return 1 if 0.8 < ratio < 1.2 else 0

def behaviour_head_turn(prev, curr, thr=0.01) -> Optional[float]:
    if prev is None or curr is None:
        return None
    mv = abs(curr[0] - prev[0])
    return float(mv) if mv > thr else None

def behaviour_body_sway(prev, curr, thr=0.01) -> Optional[float]:
    if prev is None or curr is None:
        return None
    mv = abs(curr[0] - prev[0])
    return float(mv) if mv > thr else None

def behaviour_body_movement(prev_lm, curr_lm, thr=0.01) -> Optional[float]:
    if prev_lm is None or curr_lm is None:
        return None
    curr = np.array([(l.x, l.y) for l in curr_lm], dtype=float)
    prev = np.array([(l.x, l.y) for l in prev_lm], dtype=float)
    mv = float(np.linalg.norm(curr - prev))
    return mv if mv > thr else None

def behaviour_gesture(prev_hand, curr_hand, thr=0.01) -> Optional[float]:
    if prev_hand is None or curr_hand is None:
        return None
    mv = float(np.linalg.norm(curr_hand - prev_hand))
    return mv if mv > thr else None

def count_repetition(signal: List[float], min_prominence: float = 0.01) -> int:
    if len(signal) < 3:
        return 0
    arr = np.array(signal, dtype=float)
    peaks, _ = find_peaks(arr, prominence=min_prominence)
    return int(len(peaks))

# ─────────────────────────────────────────────────────────────
#  SAVE pose.json TO DATA_JSON/<person_id>/
# ─────────────────────────────────────────────────────────────
def save_pose_json(person_id: str, pose_features: Dict) -> str:
    person_json_dir = os.path.join(DATA_JSON_DIR, person_id)
    os.makedirs(person_json_dir, exist_ok=True)
    pose_path = os.path.join(person_json_dir, "pose.json")
    with open(pose_path, "w", encoding="utf-8") as f:
        json.dump(pose_features, f, indent=4, ensure_ascii=False)
    return pose_path

# ─────────────────────────────────────────────────────────────
#  PROCESS ONE PERSON
# ─────────────────────────────────────────────────────────────
def process_session(person_id: str, person_dir: str) -> Dict:
    frames = collect_all_frames(person_dir)
    if not frames:
        raise FileNotFoundError(f"No frames found in: {person_dir}")

    prev_pose = prev_nose = prev_hip = prev_hand = None
    eye_contact_frames = 0
    head_signal, move_signal, sway_signal, gesture_signal = [], [], [], []
    processed_frames = 0

    for img_path in frames:
        bgr = cv2.imread(img_path)
        if bgr is None:
            continue
        if BLUR_FILTER and is_blurry(bgr, BLUR_THRESHOLD):
            continue

        processed_frames += 1
        rgb = preprocess_frame(bgr)
        pose_res  = POSE.process(rgb)
        hands_res = HANDS.process(rgb)

        if pose_res.pose_landmarks:
            lm        = pose_res.pose_landmarks.landmark
            nose      = (lm[0].x,  lm[0].y)
            left_eye  = (lm[1].x,  lm[1].y)
            right_eye = (lm[2].x,  lm[2].y)
            hip       = (lm[23].x, lm[23].y)

            eye_contact_frames += behaviour_eye_contact(nose, left_eye, right_eye)

            ht = behaviour_head_turn(prev_nose, nose)
            if ht is not None:
                head_signal.append(ht)

            mv = behaviour_body_movement(prev_pose, lm)
            if mv is not None:
                move_signal.append(mv)

            sw = behaviour_body_sway(prev_hip, hip)
            if sw is not None:
                sway_signal.append(sw)

            prev_pose, prev_nose, prev_hip = lm, nose, hip

        if hands_res.multi_hand_landmarks:
            for hand_lm in hands_res.multi_hand_landmarks:
                curr_hand = np.array(
                    [(l.x, l.y, l.z) for l in hand_lm.landmark], dtype=float
                )
                gs = behaviour_gesture(prev_hand, curr_hand)
                if gs is not None:
                    gesture_signal.append(gs)
                prev_hand = curr_hand

    rep_head    = count_repetition(head_signal)
    rep_move    = count_repetition(move_signal)
    rep_sway    = count_repetition(sway_signal)
    rep_gesture = count_repetition(gesture_signal)
    total_score = rep_head + rep_move + rep_sway + rep_gesture

    pose_features = {
        "eye_contact_duration": round(eye_contact_frames / FPS_ASSUMED, 6),
        "head_turn_frequency":  round(float(np.mean(head_signal)) if head_signal else 0.0, 6),
        "movement_intensity":   round(float(np.mean(move_signal)) if move_signal else 0.0, 6),
        "body_sway_index":      round(float(np.mean(sway_signal)) if sway_signal else 0.0, 6),
        "gesture_count":        int(rep_gesture)
    }

    save_pose_json(person_id, pose_features)

    return {
        "person_id":           person_id,
        "processed_frames":    processed_frames,
        "eye_contact_frames":  int(eye_contact_frames),
        "eye_contact_seconds": round(eye_contact_frames / FPS_ASSUMED, 3),
        "repetition": {
            "head_turn": int(rep_head),
            "movement":  int(rep_move),
            "body_sway": int(rep_sway),
            "gesture":   int(rep_gesture)
        },
        "total_score":   int(total_score),
        "pose_features": pose_features
    }

# ─────────────────────────────────────────────────────────────
#  COMPUTE FINAL RESULTS
# ─────────────────────────────────────────────────────────────
def compute_final_all(threshold_score: float = AUTISM_THRESHOLD_SCORE) -> Dict:
    sessions = load_sessions_all()

    if not sessions:
        final = {
            "threshold_score": float(threshold_score),
            "persons": [],
            "summary": {"persons_count": 0, "autism_yes": 0, "autism_no": 0},
            "note": "Screening-style heuristic, not a medical diagnosis."
        }
        with open(FINAL_ALL_PATH, "w", encoding="utf-8") as f:
            json.dump(final, f, indent=4, ensure_ascii=False)
        return final

    by_person: Dict[str, List[Dict]] = {}
    for s in sessions:
        by_person.setdefault(s["person_id"], []).append(s)

    persons_out = []
    autism_yes = autism_no = 0

    for person_id, ss in sorted(by_person.items()):
        avg_head    = float(np.mean([x["repetition"]["head_turn"]  for x in ss]))
        avg_move    = float(np.mean([x["repetition"]["movement"]   for x in ss]))
        avg_sway    = float(np.mean([x["repetition"]["body_sway"]  for x in ss]))
        avg_gesture = float(np.mean([x["repetition"]["gesture"]    for x in ss]))
        avg_total   = avg_head + avg_move + avg_sway + avg_gesture

        autism_flag = 1 if avg_total > threshold_score else 0
        autism_yes += autism_flag
        autism_no  += (1 - autism_flag)

        persons_out.append({
            "person_id":      person_id,
            "sessions_count": int(len(ss)),
            "avg_repetition": {
                "head_turn": round(avg_head,    3),
                "movement":  round(avg_move,    3),
                "body_sway": round(avg_sway,    3),
                "gesture":   round(avg_gesture, 3)
            },
            "avg_total_score":   round(float(avg_total), 3),
            "autism_prediction": int(autism_flag)
        })

    final = {
        "threshold_score": float(threshold_score),
        "persons": persons_out,
        "summary": {
            "persons_count": len(persons_out),
            "autism_yes":    int(autism_yes),
            "autism_no":     int(autism_no)
        },
        "note": "Screening-style heuristic, not a medical diagnosis."
    }
    with open(FINAL_ALL_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=4, ensure_ascii=False)
    return final

# ─────────────────────────────────────────────────────────────
#  PRINT HELPERS  (minimal — only what matters)
# ─────────────────────────────────────────────────────────────
def print_person_result(p):
    status = "AUTISM DETECTED" if p["autism_prediction"] else "No Autism"
    print(f"  {p['person_id']:<8} score={p['avg_total_score']:>7.1f}  -> {status}")

def print_summary_box(summary, threshold, scores):
    total = summary["persons_count"]
    yes   = summary["autism_yes"]
    no    = summary["autism_no"]
    pct   = yes / total * 100 if total else 0
    width = 50

    print("\n" + "=" * width)
    print("     AUTISM SCREENING — FINAL REPORT")
    print("=" * width)
    print(f"  Threshold        : {threshold}")
    print(f"  Total persons    : {total}")
    print(f"  Autism detected  : {yes}  ({pct:.1f}%)")
    print(f"  No autism        : {no}  ({100-pct:.1f}%)")
    print(f"  Score mean/std   : {np.mean(scores):.1f} / {np.std(scores):.1f}")
    print(f"  Score min/max    : {np.min(scores):.0f} / {np.max(scores):.0f}")
    print("=" * width)
    print("  NOTE: Screening heuristic — not a medical diagnosis.")
    print("=" * width)

# ─────────────────────────────────────────────────────────────
#  UNSUPERVISED EVALUATION
# ─────────────────────────────────────────────────────────────
def evaluate_unsupervised(final: Dict):
    persons = final.get("persons", [])
    if not persons:
        print("No persons to evaluate.")
        return

    scores      = [p["avg_total_score"]   for p in persons]
    predictions = [p["autism_prediction"] for p in persons]
    threshold   = final.get("threshold_score", AUTISM_THRESHOLD_SCORE)

    print("\n" + "=" * 50)
    print("  RESULTS PER PERSON")
    print("=" * 50)
    for p in persons:
        print_person_result(p)

    print_summary_box(final["summary"], threshold, scores)

    autism_yes = sum(predictions)
    autism_no  = len(predictions) - autism_yes

    metrics = {
        "type":            "unsupervised",
        "total_persons":   len(persons),
        "threshold_score": threshold,
        "autism_yes":      int(autism_yes),
        "autism_no":       int(autism_no),
        "autism_rate":     round(autism_yes / len(persons), 4),
        "score_mean":      round(float(np.mean(scores)), 4),
        "score_std":       round(float(np.std(scores)),  4),
        "score_min":       round(float(np.min(scores)),  4),
        "score_max":       round(float(np.max(scores)),  4),
        "per_person": [
            {"person_id":  p["person_id"],
             "score":      p["avg_total_score"],
             "prediction": p["autism_prediction"]}
            for p in persons
        ]
    }
    with open(EVAL_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)
    print(f"Metrics saved -> {EVAL_METRICS_PATH}")
    return metrics

# ─────────────────────────────────────────────────────────────
#  MAIN PIPELINE
# ─────────────────────────────────────────────────────────────
def run_all_persons_once(base_dir: str):
    patterns = ["P*", "p*", "Person*", "person*"]
    person_dirs = []
    for pat in patterns:
        person_dirs += [p for p in glob.glob(os.path.join(base_dir, pat))
                        if os.path.isdir(p)]
    person_dirs = sorted(set(person_dirs))

    if not person_dirs:
        print("No person folders found in:", base_dir)
        if os.path.exists(base_dir):
            print("Contents:", os.listdir(base_dir))
        return None

    print(f"Found {len(person_dirs)} persons. Processing...")

    sessions_all  = load_sessions_all()
    processed_ids = {s["person_id"] for s in sessions_all}

    for i, pdir in enumerate(person_dirs, 1):
        person_id = os.path.basename(pdir.rstrip("/\\"))
        if person_id in processed_ids:
            continue
        try:
            s = process_session(person_id, pdir)
            sessions_all.append(s)
            save_sessions_all(sessions_all)
            print(f"  [{i}/{len(person_dirs)}] {person_id} done (score={s['total_score']})")
        except Exception as e:
            print(f"  [{i}/{len(person_dirs)}] {person_id} ERROR: {e}")

    final = compute_final_all(threshold_score=AUTISM_THRESHOLD_SCORE)
    return final


if __name__ == "__main__":
    final = run_all_persons_once(BASE_DIR)
    if final:
        evaluate_unsupervised(final)