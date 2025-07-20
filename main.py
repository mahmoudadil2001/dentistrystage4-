import streamlit as st
import os
import uuid
from datetime import datetime, timedelta
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# إعداد المسارات وقاعدة البيانات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'chat.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    profile_picture = Column(String(255), nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, default=True)
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    image_filename = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="messages")

Base.metadata.create_all(bind=engine)

def save_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((800, 800))
    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join(UPLOAD_DIR, filename)
    img.save(path, "JPEG", quality=85)
    return filename

def get_user_by_username(db, username):
    return db.query(User).filter(User.username == username).first()

def add_or_update_user(db, username, profile_picture_file=None):
    user = get_user_by_username(db, username)
    if not user:
        user = User(username=username)
        if profile_picture_file:
            user.profile_picture = save_image(profile_picture_file)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_seen = datetime.utcnow()
        user.is_online = True
        if profile_picture_file:
            user.profile_picture = save_image(profile_picture_file)
        db.commit()
    return user

def mark_user_offline(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_online = False
        db.commit()

def add_message(db, user_id, content, image_file=None):
    msg = Message(user_id=user_id, content=content)
    if image_file:
        msg.image_filename = save_image(image_file)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_recent_messages(db, limit=50):
    return db.query(Message).order_by(Message.timestamp.desc()).limit(limit).all()[::-1]

def show_login_page():
    db = SessionLocal()
    st.title("مرحباً بك في غرفة الدردشة")
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("اسم المستخدم", max_chars=50, placeholder="أدخل اسمك هنا")
        profile_picture = st.file_uploader("صورة الملف الشخصي (اختياري)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("دخول")
        if submitted:
            if username.strip() == "":
                st.warning("يرجى إدخال اسم المستخدم.")
            else:
                user = add_or_update_user(db, username.strip(), profile_picture)
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.profile_picture = user.profile_picture
                st.experimental_rerun()

def show_chat_page():
    db = SessionLocal()
    st.title("غرفة الدردشة")

    if st.button("⬅️ العودة إلى الصفحة الرئيسية"):
        st.session_state.page = "orders"
        st.experimental_rerun()

    # عرض الرسائل
    messages = get_recent_messages(db)
    for msg in messages:
        user_display = f"**{msg.user.username}**"
        if msg.user.profile_picture:
            st.image(os.path.join(UPLOAD_DIR, msg.user.profile_picture), width=40)
        st.markdown(f"{user_display} ({msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}):")
        if msg.content:
            st.write(msg.content)
        if msg.image_filename:
            st.image(os.path.join(UPLOAD_DIR, msg.image_filename))

    # إرسال رسالة جديدة
    with st.form("send_message_form", clear_on_submit=True):
        message_text = st.text_area("اكتب رسالتك هنا:")
        image_file = st.file_uploader("ارفق صورة (اختياري)", type=["png", "jpg", "jpeg"])
        send_btn = st.form_submit_button("إرسال")

        if send_btn:
            if (message_text.strip() == "") and (image_file is None):
                st.warning("يرجى كتابة رسالة أو إرفاق صورة.")
            else:
                add_message(db, st.session_state.user_id, message_text.strip(), image_file)
                st.experimental_rerun()
