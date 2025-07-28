import os
import shutil

# كل الفولدرات اللي نبي ننسخ لها
TARGET_FOLDERS = [
    "endodontics",
    "generalmedicine",
    "generalsurgery",
    "operative",
    "oralpathology",
    "oralsurgery",
    "orthodontics",
    "pedodontics",
    "periodontology",
    "prosthodontics"
]

SOURCE_FOLDER = "endodontics/edit"  # الفولدر اللي فيه lecture_titles.py

for folder in TARGET_FOLDERS:
    target_edit = os.path.join(folder, "edit")
    os.makedirs(target_edit, exist_ok=True)
    shutil.copy(os.path.join(SOURCE_FOLDER, "lecture_titles.py"), target_edit)
    print(f"✅ Copied lecture_titles.py to {target_edit}")
