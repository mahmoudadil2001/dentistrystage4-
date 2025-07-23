import streamlit as st
import requests
from orders import main as orders_main  # ملف عرض الأسئلة والمحاضرات

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbycx6K2dBkAytd7QQQkrGkVnGkQUc0Aqs2No55dUDVeUmx8ERwaLqClhF9zhofyzPmY/exec"

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def authenticate_user(username, password):
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user['username'] == username and user['password'] == password:
                    return True, user['name'], user['group']
        return False, None, None
    except Exception as e:
        print("خطأ في التحقق من تسجيل الدخول:", e)
        return False, None, None

def register_user(username, password, name, group):
    data = {
        'action': 'register',
        'username': username,
        'password': password,
        'name': name,
        'group': group
    }
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        if response.status_code == 200:
            return response.text == "Success"
    except Exception as e:
        print("فشل في إنشاء الحساب:", e)
    return False

def update_password(username, full_name, new_password):
    data = {
        'action': 'update_password',
        'username': username,
        'full_name': full_name,
        'new_password': new_password
    }
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, data=data)
        if response.status_code == 200:
            return response.text == "Password updated"
    except Exception as e:
        print("خطأ في تحديث كلمة المرور:", e)
    return False

# تحميل CSS الخارجي
load_css("style.css")

st.markdown("<h1 class='main-title'>تسجيل الدخول إلى منصة التدريب</h1>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

if "show_forgot" not in st.session_state:
    st.session_state["show_forgot"] = False

if "name" not in st.session_state:
    st.session_state["name"] = ""

if "group" not in st.session_state:
    st.session_state["group"] = ""

if "username" not in st.session_state:
    st.session_state["username"] = ""

if "password_updated" not in st.session_state:
    st.session_state["password_updated"] = False

if st.session_state["logged_in"]:
    st.sidebar.success(f"مرحبًا {st.session_state['name']} 👋")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()
    orders_main(st.session_state['name'], st.session_state['group'])

elif st.session_state["show_register"]:
    st.subheader("إنشاء حساب جديد")
    new_username = st.text_input("اسم المستخدم", key="reg_username")
    new_password = st.text_input("كلمة المرور", type="password", key="reg_password")
    full_name = st.text_input("الاسم الكامل", key="reg_name")
    group = st.text_input("المجموعة", key="reg_group")
    if st.button("تسجيل"):
        if register_user(new_username, new_password, full_name, group):
            st.success("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
            st.session_state["show_register"] = False
        else:
            st.error("فشل في إنشاء الحساب. ربما اسم المستخدم مستخدم بالفعل.")
    if st.button("عودة إلى تسجيل الدخول"):
        st.session_state["show_register"] = False

elif st.session_state["show_forgot"]:
    st.subheader("استعادة كلمة المرور")
    username = st.text_input("اسم المستخدم", key="forgot_username")
    full_name = st.text_input("الاسم الكامل", key="forgot_name")
    new_password = st.text_input("كلمة المرور الجديدة", type="password", key="new_password")
    confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="confirm_password")

    if st.button("تحديث كلمة المرور"):
        if new_password != confirm_password:
            st.error("كلمتا المرور غير متطابقتين")
        elif not new_password:
            st.error("كلمة المرور لا يمكن أن تكون فارغة")
        else:
            if update_password(username, full_name, new_password):
                st.session_state['password_updated'] = True
                st.session_state['password_reset_message'] = "✅ تم تحديث كلمة المرور بنجاح"
                st.session_state['show_forgot'] = False
                st.rerun()
            else:
                st.error("حدث خطأ أثناء تحديث كلمة المرور")

    if st.button("عودة إلى تسجيل الدخول"):
        st.session_state["show_forgot"] = False

else:
    st.subheader("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        success, name, group = authenticate_user(username, password)
        if success:
            st.session_state["logged_in"] = True
            st.session_state["name"] = name
            st.session_state["group"] = group
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
    if st.button("إنشاء حساب جديد"):
        st.session_state["show_register"] = True
    if st.button("نسيت كلمة المرور؟"):
        st.session_state["show_forgot"] = True

    if st.session_state.get('password_updated') and st.session_state.get('password_reset_message'):
        st.success(st.session_state['password_reset_message'])
        st.session_state['password_updated'] = False
