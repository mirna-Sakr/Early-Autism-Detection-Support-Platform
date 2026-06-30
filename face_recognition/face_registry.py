import json
import os
import base64
from datetime import datetime

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "face_registry.json")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "registered_images")

os.makedirs(IMAGES_DIR, exist_ok=True)


def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(registry):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def register_child(child_id: str, name: str, embedding: list, image_base64: str) -> dict:
    registry = load_registry()

    img_filename = f"{child_id}.jpg"
    img_path = os.path.join(IMAGES_DIR, img_filename)
    with open(img_path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    registry[child_id] = {
        "child_id": child_id,
        "name": name,
        "embedding": embedding,
        "image_path": img_path,
        "created_at": datetime.now().isoformat()
    }
    save_registry(registry)
    return registry[child_id]


def get_child(child_id: str):
    registry = load_registry()
    return registry.get(child_id)


def get_all_children() -> list:
    registry = load_registry()
    return [
        {
            "child_id": v["child_id"],
            "name": v["name"],
            "created_at": v["created_at"]
        }
        for v in registry.values()
    ]


def get_child_image_base64(child_id: str):
    child = get_child(child_id)
    if not child:
        return None
    img_path = child["image_path"]
    if not os.path.exists(img_path):
        return None
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def delete_child(child_id: str) -> bool:
    registry = load_registry()
    if child_id not in registry:
        return False
    img_path = registry[child_id].get("image_path")
    if img_path and os.path.exists(img_path):
        os.remove(img_path)
    del registry[child_id]
    save_registry(registry)
    return True
