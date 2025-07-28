import os
import shutil

SOURCE_FOLDER = "endodontics/edit"  # الفولدر الأساسي اللي فيه الملف الأصلي
SUBJECTS = [
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

for subject in SUBJECTS:
    target_edit = os.path.join(subject, "edit")
    os.makedirs(target_edit, exist_ok=True)

    # لو كان الفولدر نفسه هو endodontics، نتجاهله
    if os.path.abspath(SOURCE_FOLDER) == os.path.abspath(target_edit):
        continue

    shutil.copy(os.path.join(SOURCE_FOLDER, "lecture_titles.py"), target_edit)
    print(f"✅ Copied to {target_edit}")
