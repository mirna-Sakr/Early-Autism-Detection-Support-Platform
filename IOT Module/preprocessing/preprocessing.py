import cv2
def preprocess_frame(frame, size=(224, 224)):
    resized = cv2.resize(frame, size) 
    normalized = resized / 255.0   
    return normalized
