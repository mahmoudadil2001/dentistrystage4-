import streamlit_authenticator as stauth

def hash_password(password_plain):
    hashed = stauth.Hasher([password_plain]).generate()[0]
    return hashed
