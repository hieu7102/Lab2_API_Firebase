import streamlit as st
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
FASTAPI_BACKEND_URL = os.getenv("FASTAPI_BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Note App", page_icon="📝", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #0ea5e9, #6366f1);
    color: white;
}

.note-card {
    padding: 15px;
    border-radius: 15px;
    background: rgba(255,255,255,0.15);
    margin-bottom: 12px;
}

.stButton > button {
    background-color: #22c55e !important;
    color: black !important;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    padding: 8px 16px;
}

.stButton > button:hover {
    background-color: #16a34a !important;
    color: black !important;
}

.stTextInput > div > div > input {
    background-color: #22c55e !important;
    color: black !important;
    border-radius: 8px;
    padding: 6px;
}

.stForm button {
    background-color: #22c55e !important;
    color: black !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background-color: #22c55e !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

for key in ["user_token", "user_email", "edit_note_id", "auth_mode"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "auth_mode" else "login"

def login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        data = res.json()
        return data["idToken"], data["email"]
    st.error(res.text)
    return None, None

def register(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        data = res.json()
        return data["idToken"], data["email"]
    st.error(res.text)
    return None, None

def logout():
    st.session_state.user_token = None
    st.session_state.user_email = None
    st.session_state.edit_note_id = None
    st.rerun()

st.title("📝 Note App Pro")

if not st.session_state.user_token:

    col1, col2 = st.columns(2)

    if col1.button("Login"):
        st.session_state.auth_mode = "login"

    if col2.button("Register"):
        st.session_state.auth_mode = "register"

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.session_state.auth_mode == "login":
        if st.button("Sign In"):
            token, user = login(email, password)
            if token:
                st.session_state.user_token = token
                st.session_state.user_email = user
                st.rerun()
    else:
        if st.button("Sign Up"):
            token, user = register(email, password)
            if token:
                st.session_state.user_token = token
                st.session_state.user_email = user
                st.rerun()

else:

    st.sidebar.write(f"👤 {st.session_state.user_email}")

    if st.sidebar.button("Logout"):
        logout()

    headers = {"Authorization": f"Bearer {st.session_state.user_token}"}

    st.subheader("➕ Add Note")

    with st.form("add_note", clear_on_submit=True):
        content = st.text_input("Write something...")
        if st.form_submit_button("Add"):
            res = requests.post(
                f"{FASTAPI_BACKEND_URL}/notes",
                json={"content": content},
                headers=headers
            )
            if res.status_code == 200:
                st.success("Note added")
                st.rerun()
            else:
                st.error(res.text)

    st.subheader("📚 Your Notes")

    res = requests.get(
        f"{FASTAPI_BACKEND_URL}/notes?sort_order=desc",
        headers=headers
    )

    if res.status_code == 200:
        notes = res.json()

        for note in notes:
            try:
                dt = datetime.datetime.fromisoformat(note["created_at"])
                time_str = dt.strftime("%d %b %Y • %H:%M")
            except:
                time_str = note["created_at"]

            st.markdown(f"""
            <div class="note-card">
                <b>{note['content']}</b><br>
                <small>{time_str}</small>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.edit_note_id == note["id"]:

                new_content = st.text_input(
                    "Edit note",
                    value=note["content"],
                    key=f"edit_{note['id']}"
                )

                col1, col2 = st.columns(2)

                if col1.button("Save", key=f"save_{note['id']}"):
                    requests.put(
                        f"{FASTAPI_BACKEND_URL}/notes/{note['id']}",
                        json={"content": new_content},
                        headers=headers
                    )
                    st.session_state.edit_note_id = None
                    st.rerun()

                if col2.button("Cancel", key=f"cancel_{note['id']}"):
                    st.session_state.edit_note_id = None
                    st.rerun()

            else:
                col1, col2 = st.columns(2)

                if col1.button("✏️ Edit", key=f"edit_{note['id']}"):
                    st.session_state.edit_note_id = note["id"]

                if col2.button("🗑️ Delete", key=f"del_{note['id']}"):
                    requests.delete(
                        f"{FASTAPI_BACKEND_URL}/notes/{note['id']}",
                        headers=headers
                    )
                    st.rerun()