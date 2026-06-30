import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from face_recognition.face_recognizer import get_registered_children, get_child_info
import glob

print("========================================")
print("  Face Recognition - Status Report")
print("========================================")

children = get_registered_children()
print(f"\nRegistered children: {len(children)}")
for c in children:
    info = get_child_info(c["child_id"])
    print(f"  {c['child_id']}:")
    print(f"    Name: {c['name']}")
    print(f"    Registered image: {'Yes' if c['has_image'] else 'No'}")
    print(f"    Detected faces saved: {info['detected_images_count']}")
    print(f"    Folder: face_recognition/detected_faces/{c['child_id']}/")

print(f"\nFolders in detected_faces/:")
det_dir = "face_recognition/detected_faces"
if os.path.exists(det_dir):
    for d in sorted(os.listdir(det_dir)):
        files = os.listdir(os.path.join(det_dir, d))
        print(f"  {d}/: {len(files)} images")

print("\n========================================")
print("  How to use:")
print("  1. Register: python -m face_recognition.batch_register")
print("  2. Test: python -m face_recognition.test_terminal")
print("  3. Run API: uvicorn main_api:app --reload")
print("========================================")
