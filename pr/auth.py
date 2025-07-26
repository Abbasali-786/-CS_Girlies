import streamlit as st
import json
import os

USER_DATA_FILE = "users.json"

def load_users():
    """Loads user data from the JSON file."""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            try:
                users = json.load(file)
                # Ensure each user has 'goals', 'moods', and 'journals' keys
                for user_data in users.values():
                    if "goals" not in user_data:
                        user_data["goals"] = []
                    if "moods" not in user_data:
                        user_data["moods"] = []
                    if "journals" not in user_data: # Add journals initialization
                        user_data["journals"] = []
                return users
            except json.JSONDecodeError:
                return {}
    return {}

def save_users(users):
    """Saves user data to the JSON file."""
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

def login_or_register():
    """Handles user login and registration."""
    st.title("🔐 SoulSync Login")
    users = load_users()

    # Use session state to manage the current view (Login/Register)
    if "login_menu" not in st.session_state:
        st.session_state.login_menu = "Login"

    menu = st.sidebar.selectbox("Menu", ["Login", "Register"], index=["Login", "Register"].index(st.session_state.login_menu))

    # Update session state based on selection
    st.session_state.login_menu = menu

    user = None # Initialize user to None

    if menu == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_username").strip().lower()
        password = st.text_input("Password", type="password", key="login_password").strip()

        if st.button("Login", key="login_button"):
            if username in users and users[username]["password"] == password:
                st.success(f"Welcome back, {username}!")
                user = username
                st.session_state.logged_in_user = username # Store logged-in user in session state
            else:
                st.error("Invalid username or password.")

    elif menu == "Register":
        st.subheader("Create a new account")
        new_username = st.text_input("New Username", key="register_username").strip().lower()
        new_password = st.text_input("New Password", type="password", key="register_password").strip()
        email = st.text_input("Email", key="register_email").strip()

        if st.button("Register", key="register_button"):
            if new_username in users:
                st.warning("Username already exists.")
            else:
                users[new_username] = {
                    "password": new_password,
                    "email": email,
                    "goals": [], # Initialize an empty list for goals for new users
                    "moods": [],  # Initialize an empty list for moods for new users
                    "journals": [] # Initialize an empty list for journal entries for new users
                }
                save_users(users)
                st.success("Account created! Please log in.")
                st.session_state.login_menu = "Login" # Switch to login after registration
                st.rerun() # Rerun to show login form

    return user

