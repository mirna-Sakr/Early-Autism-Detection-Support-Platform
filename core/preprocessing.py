import cv2

# =========================
# 1. Blur Detection
# =========================
def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold


# =========================
# 2. Face Validation
# =========================
def is_valid_face(box, min_size=40):
    if box is None:
        return False

    x, y, w, h = box
    return w >= min_size and h >= min_size


# =========================
# 3. Crop Face
# =========================
def crop_face(image, box, size=(224, 224)):
    x, y, w, h = box

    face = image[y:y+h, x:x+w]

    if face.size == 0:
        return None

    face = cv2.resize(face, size)
    return face