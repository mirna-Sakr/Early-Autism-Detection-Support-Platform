import json
import pandas as pd
import joblib

model = joblib.load("saved_model/mlp_model.pkl")
scaler = joblib.load("saved_model/scaler.pkl")
feature_columns = joblib.load("saved_model/feature_columns.pkl")


def generate_insights(emotion, pose):

    insights = {}

    if emotion.get("neutral_dominance", 0) > 0.7:
        insights["social_engagement"] = "Low social engagement detected"

    if emotion.get("confidence_variability", 0) < 0.2:
        insights["emotional_pattern"] = "Limited emotional variability"

    if emotion.get("repetition", 0) > 0.6:
        insights["repetition"] = "Repetitive emotional pattern"

    if pose.get("eye_contact_duration", 1) < 0.3:
        insights["eye_contact"] = "Reduced eye contact"

    if pose.get("movement_intensity", 0) > 0.6:
        insights["motor_behavior"] = "High repetitive movement"

    if pose.get("gesture_count", 0) > 8:
        insights["gesture_behavior"] = "Frequent gestures observed"

    return insights


def predict_from_json(emotion_path, pose_path):

    try:
        with open(emotion_path) as f:
            emotion = json.load(f)
    except:
        raise ValueError("Invalid emotion.json")

    try:
        with open(pose_path) as f:
            pose = json.load(f)
    except:
        raise ValueError("Invalid pose.json")

    row = {}

    # emotion features
    for k, v in emotion.items():
        row["emotion_" + k] = v

    # pose features
    for k, v in pose.items():
        row["pose_" + k] = v

    # ensure same feature order
    for col in feature_columns:
        row[col] = row.get(col, 0)

    features_df = pd.DataFrame(
        [[row[col] for col in feature_columns]],
        columns=feature_columns
    )

    features_scaled = scaler.transform(features_df)

    prob = float(model.predict_proba(features_scaled)[0][1])

    if prob >= 0.75:
        level = "High"
    elif prob >= 0.5:
        level = "Medium"
    else:
        level = "Low"

    insights = generate_insights(emotion, pose)

    return {
        "risk_score": prob,
        "risk_level": level,
        "key_insights": insights
    }