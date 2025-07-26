import streamlit as st
import uuid # For generating unique IDs for goals
import datetime
from auth import load_users, save_users # Import functions from auth.py

def add_goal_data(username, title, description, due_date, status):
    """Adds a new goal for the specified user."""
    users = load_users()
    user_data = users.get(username, {})
    user_goals = user_data.get("goals", [])

    new_goal = {
        "id": str(uuid.uuid4()), # Unique ID for the goal
        "title": title,
        "description": description,
        "due_date": str(due_date) if due_date else None,
        "status": status
    }
    user_goals.append(new_goal)
    user_data["goals"] = user_goals
    users[username] = user_data
    save_users(users)
    return True, "Goal added successfully!"

def update_goal_data(username, goal_id, new_title, new_description, new_due_date, new_status):
    """Updates an existing goal for the specified user."""
    users = load_users()
    user_data = users.get(username, {})
    user_goals = user_data.get("goals", [])

    for i, goal in enumerate(user_goals):
        if goal["id"] == goal_id:
            user_goals[i]["title"] = new_title
            user_goals[i]["description"] = new_description
            user_goals[i]["due_date"] = str(new_due_date) if new_due_date else None
            user_goals[i]["status"] = new_status
            user_data["goals"] = user_goals
            users[username] = user_data
            save_users(users)
            return True, "Goal updated successfully!"
    return False, "Goal not found."

def delete_goal_data(username, goal_id):
    """Deletes a goal for the specified user."""
    users = load_users()
    user_data = users.get(username, {})
    user_goals = user_data.get("goals", [])

    initial_len = len(user_goals)
    user_goals = [goal for goal in user_goals if goal["id"] != goal_id]
    
    if len(user_goals) < initial_len:
        user_data["goals"] = user_goals
        users[username] = user_data
        save_users(users)
        return True, "Goal deleted successfully!"
    return False, "Goal not found."


def goal_page(username):
    """
    Displays the goal management page for the logged-in user.
    Allows users to add, view, edit, and delete goals.
    """
    st.title(f"🎯 {username}'s Goals")

    # --- Add New Goal ---
    st.header("Add a New Goal")
    with st.form("add_goal_form", clear_on_submit=True):
        goal_title = st.text_input("Goal Title", max_chars=100, help="e.g., Finish Hackathon Project", key="add_goal_title")
        goal_description = st.text_area("Description (Optional)", help="Provide more details about your goal.", key="add_goal_description")
        goal_due_date = st.date_input("Due Date (Optional)", help="When do you plan to achieve this goal?", key="add_goal_due_date")
        goal_status = st.selectbox("Status", ["To Do", "In Progress", "Completed", "Cancelled"], index=0, key="add_goal_status")

        submitted = st.form_submit_button("Add Goal")
        if submitted:
            if goal_title:
                success, message = add_goal_data(username, goal_title, goal_description, goal_due_date, goal_status)
                if success:
                    st.success(message)
                    st.rerun() # Rerun to update the displayed goals
                else:
                    st.error(message)
            else:
                st.error("Goal Title cannot be empty.")

    st.markdown("---")

    # --- View and Manage Goals ---
    st.header("Your Current Goals")

    users = load_users() # Reload users to get latest data
    user_data = users.get(username, {})
    user_goals = user_data.get("goals", [])

    if not user_goals:
        st.info("You haven't set any goals yet. Add one above!")
    else:
        # Filter and sort options
        status_filter = st.sidebar.multiselect("Filter by Status", ["To Do", "In Progress", "Completed", "Cancelled"], default=["To Do", "In Progress"], key="goal_status_filter")
        sort_by = st.sidebar.selectbox("Sort by", ["None", "Due Date (Asc)", "Due Date (Desc)", "Status"], key="goal_sort_by")

        filtered_goals = [goal for goal in user_goals if goal.get("status") in status_filter] # Use .get for status

        if sort_by == "Due Date (Asc)":
            # Sort by due_date, treating None (no due date) as greater than any date
            filtered_goals.sort(key=lambda x: (x.get("due_date") is None, x.get("due_date")))
        elif sort_by == "Due Date (Desc)":
            # Sort by due_date, treating None as smaller (so they appear last)
            filtered_goals.sort(key=lambda x: (x.get("due_date") is None, x.get("due_date")), reverse=True)
        elif sort_by == "Status":
            # Define a custom order for status
            status_order = {"To Do": 0, "In Progress": 1, "Completed": 2, "Cancelled": 3}
            filtered_goals.sort(key=lambda x: status_order.get(x.get("status", "To Do"), 99)) # Default to "To Do" for sorting

        for i, goal in enumerate(filtered_goals):
            # Safely get title and status, providing defaults if missing
            goal_title = goal.get('title', 'Unnamed Goal')
            goal_status = goal.get('status', 'Unknown')
            goal_due_date = goal.get('due_date')

            expander_title = f"**{goal_title}** - Status: {goal_status}"
            if goal_due_date:
                expander_title += f" (Due: {goal_due_date})"

            with st.expander(expander_title):
                st.write(f"**Description:** {goal.get('description', 'No description provided.')}")
                st.write(f"**Status:** {goal_status}")
                st.write(f"**Due Date:** {goal_due_date if goal_due_date else 'Not set'}")
                st.write(f"*(Goal ID: {goal.get('id', 'N/A')})*") # Display ID for potential future use with AI editing

                col1, col2 = st.columns(2)

                # Edit Goal
                with col1:
                    if st.button(f"Edit Goal", key=f"edit_{goal.get('id', i)}"): # Use a fallback for key
                        st.session_state.editing_goal_id = goal.get('id')
                        st.rerun() # Rerun to show edit form

                # Delete Goal
                with col2:
                    if st.button(f"Delete Goal", key=f"delete_{goal.get('id', i)}"): # Use a fallback for key
                        success, message = delete_goal_data(username, goal.get("id"))
                        if success:
                            st.success(message)
                            st.rerun() # Rerun to update the displayed goals
                        else:
                            st.error(message)

        # --- Edit Goal Form (appears when a goal is selected for editing) ---
        if "editing_goal_id" in st.session_state and st.session_state.editing_goal_id:
            goal_to_edit = next((g for g in user_goals if g.get("id") == st.session_state.editing_goal_id), None)

            if goal_to_edit:
                st.markdown("---")
                st.header(f"Edit Goal: {goal_to_edit.get('title', 'Unnamed Goal')}")
                with st.form("edit_goal_form", clear_on_submit=False):
                    edited_title = st.text_input("Goal Title", value=goal_to_edit.get('title', ''), key="edit_title")
                    edited_description = st.text_area("Description", value=goal_to_edit.get('description', ''), key="edit_description")
                    
                    # Convert string date back to date object for st.date_input
                    initial_date = None
                    if goal_to_edit.get('due_date'):
                        try:
                            initial_date = datetime.datetime.strptime(goal_to_edit['due_date'], "%Y-%m-%d").date()
                        except ValueError:
                            initial_date = None # Handle invalid date format

                    edited_due_date = st.date_input("Due Date", value=initial_date, key="edit_due_date")
                    
                    # Find the index of the current status for the selectbox
                    status_options = ["To Do", "In Progress", "Completed", "Cancelled"]
                    initial_status_index = status_options.index(goal_to_edit.get('status', 'To Do')) if goal_to_edit.get('status', 'To Do') in status_options else 0
                    edited_status = st.selectbox("Status", status_options, index=initial_status_index, key="edit_status")

                    update_submitted = st.form_submit_button("Update Goal")
                    cancel_edit = st.form_submit_button("Cancel Edit")

                    if update_submitted:
                        if edited_title:
                            success, message = update_goal_data(
                                username,
                                goal_to_edit["id"], # We know ID exists here as we filtered by it
                                edited_title,
                                edited_description,
                                edited_due_date,
                                edited_status
                            )
                            if success:
                                st.success(message)
                                st.session_state.editing_goal_id = None # Clear editing state
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Goal Title cannot be empty.")
                    elif cancel_edit:
                        st.session_state.editing_goal_id = None # Clear editing state
                        st.rerun()
            else:
                st.error("Goal to edit not found.")
                st.session_state.editing_goal_id = None # Clear editing state