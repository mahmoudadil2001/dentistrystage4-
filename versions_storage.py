import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby0Y1Iq0incLLHdMAQUDWOp2qRXivZthdfLYEusIXZUEgCltNvxjuIRSaK4M2WUlfwK/exec"

def save_user_version(username, sheet_name, selected_version):
    payload = {
        "action": "save_version",
        "username": username,
        "sheet_name": sheet_name,
        "selected_version": selected_version
    }
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, data=payload)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"

def get_user_versions(username):
    payload = {
        "action": "get_user_versions",
        "username": username
    }
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, data=payload)
        text = response.text.strip()
        if not text:
            return {}
        lines = text.split("\n")
        versions = {}
        for line in lines:
            parts = line.split(",")
            if len(parts) == 2:
                sheet_name, version = parts
                versions[sheet_name] = version
        return versions
    except requests.exceptions.RequestException as e:
        return {}
