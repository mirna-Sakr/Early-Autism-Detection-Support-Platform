import numpy as np
from collections import Counter

def safe_div(x, y):
    return x / y if y != 0 else 0
# ================================
# 1. Emotional Stability
# ================================
def emotional_stability(sequence):
    if len(sequence) == 0:
        return 0

    changes = sum(1 for i in range(1, len(sequence)) if sequence[i] != sequence[i-1])
    return 1 - safe_div(changes, len(sequence))


# ================================
# 2. Repetitive Pattern
# ================================
def repetitive_pattern(sequence):
    if len(sequence) == 0:
        return 0

    counts = Counter(sequence)
    dominant = max(counts.values())
    return safe_div(dominant, len(sequence))


# ================================
# 3. Transition Rate
# ================================
def transition_rate(sequence):
    if len(sequence) == 0:
        return 0

    changes = sum(1 for i in range(1, len(sequence)) if sequence[i] != sequence[i-1])
    return safe_div(changes, len(sequence))


# ================================
# 4. Neutral Dominance
# ================================
def neutral_dominance(sequence):
    if len(sequence) == 0:
        return 0

    return safe_div(sequence.count("neutral"), len(sequence))


# ================================
# 5. Emotional Variability (based on confidence)
# ================================
def emotional_variability(conf_seq):
    if len(conf_seq) == 0:
        return 0

    return float(np.var(conf_seq))



# ================================
# 6. Emotion Diversity (عدد المشاعر المختلفة)
# ================================
def emotion_diversity(sequence):
    if len(sequence) == 0:
        return 0

    return safe_div(len(set(sequence)), len(sequence))


# ================================
# 7. Entropy (غنى المشاعر)
# ================================
def emotion_entropy(sequence):
    if len(sequence) == 0:
        return 0

    counts = Counter(sequence)
    probs = np.array(list(counts.values())) / len(sequence)
    return float(-np.sum(probs * np.log2(probs + 1e-8)))  # ✅ log2


# ================================
# 🔥 MAIN FUNCTION
# ================================
def extract_emotion_features(emotion_sequence, confidence_sequence):

    # ✅ مفيش None خلاص
    if len(emotion_sequence) == 0:
        return {
            "stability": 0,
            "repetition": 0,
            "transition_rate": 0,
            "neutral_dominance": 0,
            "confidence_variability": 0,
            "emotion_diversity": 0,
            "emotion_entropy": 0
        }

    features = {
        "stability": float(emotional_stability(emotion_sequence)),
        "repetition": float(repetitive_pattern(emotion_sequence)),
        "transition_rate": float(transition_rate(emotion_sequence)),
        "neutral_dominance": float(neutral_dominance(emotion_sequence)),
        "confidence_variability": float(emotional_variability(confidence_sequence)),
        "emotion_diversity": float(emotion_diversity(emotion_sequence)),
        "emotion_entropy": float(emotion_entropy(emotion_sequence))
    }

    return features