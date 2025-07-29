import requests

# ضع هنا رابط سكربت Google Apps Script
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxGxzNfgsJhN8x_W-IgtaL98KTUGIulaYHgr9SQHgFPoIz3PSSMmX5PZin_J_-iKqRV/exec"

def save_version_to_sheet(username, sheet_name, selected_version):
    """
    يحفظ النسخة المحددة للمستخدم في شيت Google
    """
    data = {
        "action": "save_version",
        "username": username,
        "sheet_name": sheet_name,
        "selected_version": selected_version
    }
    try:
        r = requests.post(GOOGLE_SCRIPT_URL, data=data)
        return r.text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def get_user_versions(username):
    """
    يجلب جميع النسخ التي حددها المستخدم سابقًا
    """
    data = {
        "action": "get_user_versions",
        "username": username
    }
    try:
        r = requests.post(GOOGLE_SCRIPT_URL, data=data)
        if r.text.strip() == "":
            return {}
        
        result = {}
        rows = r.text.strip().split("\n")
        for row in rows:
            parts = row.split(",")
            if len(parts) == 2:
                sheet_name, version = parts
                result[sheet_name] = version
        return result
    except Exception as e:
        return {}
