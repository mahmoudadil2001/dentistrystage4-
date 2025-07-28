import os
import shutil

# المجلد المصدر الذي يحتوي على ملف lecture_titles.py
SOURCE_EDIT_FOLDER = "endodontics/edit"

# قائمة كل المواد التي تريد نسخ مجلد edit إليها
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

def copy_edit_folder_to_all_subjects():
    for subject in SUBJECTS:
        target_edit_folder = os.path.join(subject, "edit")
        os.makedirs(target_edit_folder, exist_ok=True)  # إذا ما موجود ينشئ

        # نسخ كل ملفات مجلد edit من المصدر إلى المجلد الهدف
        for filename in os.listdir(SOURCE_EDIT_FOLDER):
            source_file = os.path.join(SOURCE_EDIT_FOLDER, filename)
            target_file = os.path.join(target_edit_folder, filename)

            # إذا نفس الملف، تخطي (لتجنب خطأ النسخ على نفس المسار)
            if os.path.abspath(source_file) == os.path.abspath(target_file):
                continue

            shutil.copy2(source_file, target_file)
            print(f"Copied {source_file} to {target_file}")

if __name__ == "__main__":
    copy_edit_folder_to_all_subjects()
    print("✅ Finished copying edit folders to all subjects.")
