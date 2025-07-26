import streamlit as st
import datetime
from auth import load_users, save_users # Import functions from auth.py

def add_mood_data(username, mood_text, mood_emoji, description):
    """Adds a new mood entry for the specified user."""
    users = load_users()
    user_data = users.get(username, {})
    user_moods = user_data.get("moods", [])

    new_mood_entry = {
        "timestamp": datetime.datetime.now().isoformat(), # ISO format for easy storage and retrieval
        "mood_text": mood_text,
        "mood_emoji": mood_emoji,
        "description": description,
        "date": datetime.date.today().isoformat(), # Add date for consistency with older formats if needed
        "time": datetime.datetime.now().strftime("%H:%M:%S") # Add time for consistency
    }
    user_moods.append(new_mood_entry)
    user_data["moods"] = user_moods
    users[username] = user_data
    save_users(users)
    return True, f"Your mood '{mood_text} {mood_emoji}' has been logged!"


def mood_page(username):
    """
    Displays the mood tracker page for the logged-in user.
    Allows users to log their mood and view recent mood history.
    """
    st.title(f"🧠 {username}'s Mood Tracker")

    users = load_users() # Reload users to get latest data
    user_data = users.get(username, {})
    user_moods = user_data.get("moods", [])

    # --- Log New Mood ---
    st.header("How are you feeling today?")
    
    mood_options = {
        "Happy": "😀",
        "Sad": "😢",
        "Angry": "😡",
        "Stressed": "😣",
        "Anxious": "😰",
        "Excited": "🤩",
        "Neutral": "😐",
        "Calm": "😌", # Added from your example data
        "Energized": "⚡" # Added from your example data
    }

    # Create buttons for mood selection
    selected_mood_text = st.radio(
        "Select your mood:",
        list(mood_options.keys()),
        index=6, # Default to Neutral
        horizontal=True,
        key="mood_selection_radio"
    )
    selected_mood_emoji = mood_options[selected_mood_text]

    mood_description = st.text_area("Optional: Describe why you feel this way (e.g., 'Had a great day at work!')", max_chars=200, key="mood_description_text")

    if st.button("Log Mood"):
        success, message = add_mood_data(username, selected_mood_text, selected_mood_emoji, mood_description)
        if success:
            st.success(message)
            st.rerun() # Rerun to update the displayed history
        else:
            st.error(message)

    st.markdown("---")

    # --- Recent Mood History ---
    st.header("Your Recent Mood History")

    if not user_moods:
        st.info("You haven't logged any moods yet. Log one above!")
    else:
        # Prepare valid_moods, converting older formats to include 'timestamp'
        processed_moods = []
        for entry in user_moods:
            # If 'timestamp' key is missing, try to create it from 'date' and 'time'
            if "timestamp" not in entry:
                date_str = entry.get("date")
                time_str = entry.get("time", "00:00:00") # Default to midnight if time is missing
                if date_str:
                    try:
                        # Create a full datetime string and convert to isoformat
                        full_datetime_str = f"{date_str} {time_str}"
                        entry["timestamp"] = datetime.datetime.fromisoformat(full_datetime_str).isoformat()
                    except ValueError:
                        st.warning(f"Could not parse date/time for old mood entry: {entry}. Skipping.")
                        continue # Skip this entry if date/time parsing fails
                else:
                    st.warning(f"Skipping mood entry missing 'timestamp' and 'date' key: {entry}")
                    continue # Skip if no date to derive timestamp from

            # Validate the timestamp after ensuring it exists
            if "timestamp" in entry:
                try:
                    datetime.datetime.fromisoformat(entry["timestamp"]) # Validate format
                    processed_moods.append(entry)
                except ValueError:
                    st.warning(f"Skipping mood entry with invalid timestamp format: {entry}")
            else:
                # This else should ideally not be hit if the above logic worked
                st.warning(f"Skipping mood entry after timestamp processing failed: {entry}")


        if not processed_moods:
            st.info("No valid mood entries to display after processing.")
            return

        # Display moods in reverse chronological order (most recent first)
        recent_moods = sorted(processed_moods, key=lambda x: x["timestamp"], reverse=True)

        # Show only the last 10 entries for brevity, or all if less than 10
        display_count = st.slider("Show last X entries:", 1, len(recent_moods), min(10, len(recent_moods)), key="mood_history_slider")
        
        for entry in recent_moods[:display_count]:
            timestamp_dt = datetime.datetime.fromisoformat(entry["timestamp"])
            
            # Use .get() for safe access to mood_text and mood_emoji as older entries might use 'mood'
            mood_label = entry.get('mood_text') or entry.get('mood') # Try 'mood_text', then 'mood'
            mood_emoji = entry.get('mood_emoji', '❓')

            # Ensure emoji matches if mood_label was from 'mood' key
            if mood_label and mood_emoji == '❓':
                mood_emoji = mood_options.get(mood_label.capitalize(), '❓') # Try to map from label

            st.write(f"**{timestamp_dt.strftime('%Y-%m-%d %H:%M')}** - {mood_emoji} {mood_label if mood_label else 'Unknown Mood'}")
            if entry.get("description"):
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*\"{entry['description']}\"*")
            st.markdown("---")