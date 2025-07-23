import streamlit_authenticator as stauth

def hash_password(password_plain):
    # يحمّل قائمة كلمة سر واحدة فقط ويُرجع الهاش كقيمة نصية
    hashed = stauth.Hasher([password_plain]).generate()[0]
    return hashed
