import cv2
import time
import os
from cloud.Cloud_Handler import Cloud_Handler 
from camera.camera import Camera
from preprocessing.preprocessing import preprocess_frame

def main():
    uploader = Cloud_Handler()
    save_folder = "frames" 
    os.makedirs(save_folder, exist_ok=True) 
    cam = Camera(0)
    frame_count = 0
    last_save_time = 0

    while True:
        frame = cam.get_frame()
        if frame is None:
            break
            
        processed = preprocess_frame(frame)
        processed_img = (processed * 255).clip(0, 255).astype('uint8')
        cv2.imshow("Processed", processed_img)
        
        current_time = time.time()
        if current_time - last_save_time >= 0.5:
            filename = os.path.join(save_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(filename, processed_img)
            uploader.upload_frame(filename) 
            frame_count += 1
            last_save_time = current_time

        if cv2.waitKey(1) == 27: 
            break

    cam.release()
    cv2.destroyAllWindows()

main()