import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Persistent key (should be securely stored in real apps)
if "KEY" not in st.session_state:
    st.session_state["KEY"] = Fernet.generate_key()
cipher = Fernet(st.session_state["KEY"])

# Session-based storage (demo purpose)
if "stored_data" not in st.session_state:
    st.session_state["stored_data"] = {}

if "failed_attempts" not in st.session_state:
    st.session_state["failed_attempts"] = 0

# Function to hash passkey
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)
    for data in st.session_state["stored_data"].values():
        if data["encrypted_text"] == encrypted_text and data["passkey"] == hashed_passkey:
            st.session_state["failed_attempts"] = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    st.session_state["failed_attempts"] += 1
    return None

# Streamlit UI
st.title("🔒 Secure Data Encryption System")
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")

elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")
    user_data = st.text_area("Enter Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data)
            st.session_state["stored_data"][encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            st.success("✅ Data stored securely!")
            st.code(encrypted_text)
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")
    encrypted_text = st.text_area("Enter Encrypted Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_text and passkey:
            result = decrypt_data(encrypted_text, passkey)
            if result:
                st.success(f"✅ Decrypted Data: {result}")
            else:
                remaining = 3 - st.session_state["failed_attempts"]
                st.error(f"❌ Incorrect passkey! Attempts remaining: {remaining}")
                if st.session_state["failed_attempts"] >= 3:
                    st.warning("🔒 Too many failed attempts! Redirecting to Login Page.")
                    st.session_state["redirect"] = "Retrieve Data"
                    st.experimental_rerun()
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")
    login_pass = st.text_input("Enter Master Password:", type="password")
    if st.button("Login"):
        if login_pass == "admin123":
            st.session_state["failed_attempts"] = 0
            st.success("✅ Reauthorized successfully!")
            if "redirect" in st.session_state:
                choice = st.session_state["redirect"]
                del st.session_state["redirect"]
                st.experimental_rerun()
        else:
            st.error("❌ Incorrect password!")
