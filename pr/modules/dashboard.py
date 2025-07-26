import streamlit as st
import pandas as pd
import datetime
from auth import load_users

def dashboard_page(username):
    """
    Displays the visual dashboard for the logged-in user.
    Includes mood trends, goal summaries, and placeholders for other insights.
    """
    st.title(f"📊 {username}'s Visual Dashboard")

    users = load_users()
    user_data = users.get(username, {})
    user_moods = user_data.get("moods", [])
    user_goals = user_data.get("goals", [])
    user_journals = user_data.get("journals", [])

    st.markdown("---")

    # --- Mood Trend Visualization ---
    st.header("Mood Trends Over Time")

    if not user_moods:
        st.info("No mood data available. Log your moods in the 'Mood Tracker' to see trends here!")
    else:
        # Map mood text to numerical values for charting
        # Ensure these map to the 'mood' values in your users.json (case-insensitive)
        mood_to_value = {
            "happy": 5, "excited": 4, "neutral": 3,
            "anxious": 2, "stressed": 2, "sad": 1, "angry": 1,
            "calm": 3.5, "energized": 4.5 # Added mapping for 'calm' and 'energized' from your example data
        }
        
        # Prepare data for DataFrame
        mood_data = []
        for entry in user_moods:
            try:
                # Prioritize 'timestamp' if it exists (for new entries)
                if "timestamp" in entry and entry["timestamp"]:
                    timestamp_dt = datetime.datetime.fromisoformat(entry["timestamp"])
                    mood_label = entry.get("mood_text") or entry.get("mood") # Try both keys
                else:
                    # Fallback for older entries without 'timestamp'
                    date_str = entry.get("date")
                    # Assume a default time if not present, as older entries might not have 'time'
                    time_str = entry.get("time", "00:00:00") 
                    mood_label = entry.get("mood") # For older entries, 'mood' is the key

                    if date_str:
                        full_datetime_str = f"{date_str} {time_str}"
                        timestamp_dt = datetime.datetime.fromisoformat(full_datetime_str)
                    else:
                        st.warning(f"Skipping mood entry due to missing 'date' (and no 'timestamp'): {entry}")
                        continue

                if mood_label:
                    mood_value = mood_to_value.get(mood_label.lower(), 0) # Convert to lower to match keys
                    mood_data.append({"Datetime": timestamp_dt, "Mood Value": mood_value, "Mood": mood_label})
                else:
                    st.warning(f"Skipping mood entry: {entry}. Missing valid 'mood' or 'mood_text'.")
                    continue
            except ValueError as e:
                st.warning(f"Could not parse timestamp or date/time for entry: {entry}. Error: {e}. Skipping this mood entry.")
                continue
            except TypeError as e:
                st.warning(f"Mood entry has unexpected format: {entry}. Error: {e}. Skipping this mood entry.")
                continue

        if mood_data:
            df_moods = pd.DataFrame(mood_data)
            df_moods = df_moods.sort_values(by="Datetime")

            st.write("### Your Mood Over Time")
            st.line_chart(df_moods.set_index("Datetime")["Mood Value"])

            st.write("### Daily Mood Distribution")
            # Group by date and count mood occurrences
            if 'Mood' in df_moods.columns:
                df_moods['DateOnly'] = df_moods['Datetime'].dt.date
                daily_mood_counts = df_moods.groupby(['DateOnly', 'Mood']).size().unstack(fill_value=0)
                st.bar_chart(daily_mood_counts)
            else:
                st.info("Not enough diverse mood data for daily distribution chart.")

        else:
            st.info("No valid mood entries to display after parsing.")


    st.markdown("---")

    # --- Goal Achievement Summary ---
    st.header("Goal Progress Summary")

    if not user_goals:
        st.info("No goals set yet. Add goals in the 'Goals' section to see your progress here!")
    else:
        total_goals = len(user_goals)
        # Use .get() for safe access to 'status'
        completed_goals = sum(1 for goal in user_goals if goal.get("status") == "Completed")
        in_progress_goals = sum(1 for goal in user_goals if goal.get("status") == "In Progress")
        to_do_goals = sum(1 for goal in user_goals if goal.get("status") == "To Do")
        cancelled_goals = sum(1 for goal in user_goals if goal.get("status") == "Cancelled")

        st.write(f"**Total Goals:** {total_goals}")
        st.write(f"**Completed:** {completed_goals}")
        st.write(f"**In Progress:** {in_progress_goals}")
        st.write(f"**To Do:** {to_do_goals}")
        st.write(f"**Cancelled:** {cancelled_goals}")

        # Create a simple pie chart for goal statuses
        goal_status_counts = pd.DataFrame({
            'Status': ['Completed', 'In Progress', 'To Do', 'Cancelled'],
            'Count': [completed_goals, in_progress_goals, to_do_goals, cancelled_goals]
        })
        # Filter out statuses with 0 count for better visualization
        goal_status_counts = goal_status_counts[goal_status_counts['Count'] > 0]

        if not goal_status_counts.empty:
            st.bar_chart(goal_status_counts.set_index('Status'))
        else:
            st.info("No goals with counts to display in the chart.")


    st.markdown("---")

    # --- Common Triggers from Journal Entries (Placeholder) ---
    st.header("Common Triggers & Insights from Journal Entries")
    if not user_journals:
        st.info("No journal entries available. Write some entries in the 'Journal' section to unlock insights here!")
    else:
        st.info("This section will analyze your journal entries to identify common themes, emotions, or triggers over time. (Coming Soon!)")
        st.markdown("*(Future features could include keyword extraction, sentiment analysis, and correlation with mood data.)*")