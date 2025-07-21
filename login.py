import streamlit as st
import requests
from utils import API_BASE

def render_login_ui():
    tabs = st.tabs(["🔐 Login", "🧾 Register"])

    with tabs[1]:  # Register
        st.subheader("Create a new account")
        role = st.selectbox("I am a...", ["contractor", "client"])
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            res = requests.post(f"{API_BASE}/auth/register", json={
                "name": name, "email": email, "password": password, "role": role
            })
            if res.status_code == 201:
                st.success("Registered successfully! Please log in.")
            else:
                st.error(res.json().get("error", "Registration failed."))

    with tabs[0]:  # Login
        st.subheader("Login to your account")
        email = st.text_input("Login Email")
        password = st.text_input("Login Password", type="password")
        if st.button("Login"):
            res = requests.post(f"{API_BASE}/auth/login", json={
                "email": email, "password": password
            })
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data["token"]
                user_res = requests.get(
                    f"{API_BASE}/auth/me",
                    headers={"Authorization": f"Bearer {data['token']}"}
                )
                if user_res.status_code == 200:
                    st.session_state.user = user_res.json()
                st.success("Login successful.")
                st.experimental_rerun()
            else:
                st.error("Invalid login credentials.")
