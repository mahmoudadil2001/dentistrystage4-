import streamlit_authenticator as stauth

def hash_password(password_plain: str) -> str:
    # دالة تستقبل كلمة سر نصية وتعيد هاش مشفر
    hashed_list = stauth.Hasher([password_plain]).generate()
    hashed = hashed_list[0]  # نأخذ أول عنصر من القائمة لأننا مررنا كلمة واحدة فقط
    return hashed
