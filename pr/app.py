import streamlit as st
import os # Import the os module
from auth import login_or_register
from modules.goals import goal_page     # Updated import path
from modules.mood import mood_page      # Updated import path
from modules.journal import journal_page # Updated import path
from modules.dashboard import dashboard_page # Updated import path
from modules.chatbot import chatbot_page # Import the new chatbot_page

def main():
    """Main function to run the SoulSync application."""
    # Load custom CSS using an absolute path for robustness
    # os.path.dirname(__file__) gets the directory of the current script (app.py)
    # os.path.join constructs a path safely across different operating systems
    css_file_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    try:
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: style.css not found at {css_file_path}. Please ensure it's in the 'assets' folder.")


    # Check if user is already logged in from session state
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    
    # Check if current_page is set in session state, default to "Chatbot"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chatbot" # Changed default page to Chatbot

    user = st.session_state.logged_in_user

    if user is None:
        # If not logged in, show login/register page
        user = login_or_register()
        if user:
            st.session_state.logged_in_user = user # Store user in session state
            st.session_state.current_page = "Chatbot" # Default to Chatbot page after login
            st.rerun() # Rerun to switch to chatbot page
    else:
        # If logged in, show the main application pages
        st.sidebar.write(f"Logged in as: **{user}**")
        
        # Sidebar navigation
        app_menu = st.sidebar.radio(
            "Navigation",
            ["Chatbot", "Goals", "Mood Tracker", "Journal", "Visual Dashboard", "Reflection Mode"], # Added Chatbot to navigation
            index=["Chatbot", "Goals", "Mood Tracker", "Journal", "Visual Dashboard", "Reflection Mode"].index(st.session_state.current_page)
        )
        st.session_state.current_page = app_menu # Update current page in session state

        if st.sidebar.button("Logout"):
            st.session_state.logged_in_user = None
            st.session_state.login_menu = "Login" # Reset menu to login
            st.session_state.current_page = "Chatbot" # Reset page on logout
            st.rerun() # Rerun to go back to login page
        
        # Display the selected page
        if st.session_state.current_page == "Chatbot": # New Chatbot page
            chatbot_page(user)
        elif st.session_state.current_page == "Goals":
            goal_page(user)
        elif st.session_state.current_page == "Mood Tracker":
            mood_page(user)
        elif st.session_state.current_page == "Journal":
            journal_page(user)
        elif st.session_state.current_page == "Visual Dashboard":
            dashboard_page(user)
        elif st.session_state.current_page == "Reflection Mode": # Placeholder for Reflection Mode
            st.header("🔄 Reflection Mode (Coming Soon!)")
            st.info("This feature will summarize your emotions, achievements, and stressors like a journal at the end of the week.")
            st.markdown("*(Future features could include AI-driven summaries and insights based on your mood and journal entries.)*")


if __name__ == "__main__":
    main()
