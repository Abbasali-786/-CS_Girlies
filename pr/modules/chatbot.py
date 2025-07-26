import streamlit as st
import json
import os
from groq import Groq
from auth import load_users, save_users # Assuming save_users function exists

# --- Helper Functions ---
def get_ai_response(username, messages, user_data_summary, full_user_data, recent_journal_content):
    """
    Generates an AI response based on user messages and data.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Please set the 'GROQ_API_KEY' environment variable. You can get one from console.groq.com."

    client = Groq(api_key=api_key)

    # Prepare recent journal content for the AI
    journal_context = ""
    if recent_journal_content:
        journal_context = "\n\nRecent Journal Entries:\n" + "\n---\n".join([f"Date: {entry.get('date', 'N/A')}\nContent: {entry.get('content', 'N/A')}" for entry in recent_journal_content])

    system_prompt = f"""
You are SoulSync, a helpful, emotionally intelligent, and insightful assistant.

You support the user {username} with their emotional wellness and personal growth journey by:
- Analyzing their data (goals, mood tracker, journals)
- Providing empathetic, wise, and personalized reflections and insights
- Never modifying or deleting data (strictly read-only)
- Offering suggestions based on patterns and emotional context
- Giving coaching-style advice to help the user reflect, grow, or make informed decisions

User data summary:
{json.dumps(user_data_summary, indent=2)}

Full user data (for context, do not directly quote large sections unless asked):
{json.dumps(full_user_data, indent=2)}

{journal_context}

Guidelines:
- Always use warm, thoughtful, human-like responses.
- Explain insights or summaries clearly and meaningfully.
- Ask questions that encourage self-reflection when relevant.
- If you don't understand the question, gently ask the user to clarify.
- Be sensitive, kind, and emotionally aware at all times.
- After providing an answer, sometimes gently prompt the user for further reflection or to explore related topics.
- Keep responses concise but insightful.
"""

    try:
        # Send a reasonable window of messages for context (e.g., last 5-6 turns)
        # The system prompt is included first to ensure it's always considered.
        contextual_messages = messages[-5:] if len(messages) >= 5 else messages

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in contextual_messages:
            content = msg["content"]
            if isinstance(content, dict):
                content = json.dumps(content)
            formatted_messages.append({"role": msg["role"], "content": content})

        chat_completion = client.chat.completions.create(
            messages=formatted_messages,
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=540
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        st.error(f"I'm sorry, I encountered an error: {str(e)}. Please try again. If the problem persists, try rephrasing your question or contact support.")
        return "I encountered an issue. Please try again."

# --- Main Chatbot Page ---
def chatbot_page(username):
    st.title(f"\U0001F4AC SoulSync Assistant for {username}")
    st.info("Ask me about your goals, moods, or journal. I’m here to support you ❤️\n\n*SoulSync is designed to support your personal growth journey and provide insights based on your data. It is not a substitute for professional medical or psychological advice.*")

    # Load full user data at the start
    users = load_users()
    user_data = users.get(username, {})

    # Initialize chat history if not present, or load from user data
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = user_data.get("chat_history", [])

    # Display chat messages from history on app rerun
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Suggested Prompts / Quick Actions
    st.markdown("---") # Separator for visual clarity
    st.write("**Quick Actions:**")
    col1, col2, col3 = st.columns(3)

    suggested_prompts = []
    if user_data.get("goals"):
        suggested_prompts.append("Summarize my goals.")
    if user_data.get("moods"):
        suggested_prompts.append("What's my recent mood trend?")
    if user_data.get("journals"):
        suggested_prompts.append("Tell me about my recent journal entries.")
    suggested_prompts.append("Give me a general motivational message.")
    suggested_prompts.append("How can I improve my well-being?")

    for i, prompt_text in enumerate(suggested_prompts):
        if i % 3 == 0:
            with col1:
                if st.button(prompt_text, key=f"suggested_prompt_{i}"):
                    process_user_query(username, prompt_text, users, user_data)
        elif i % 3 == 1:
            with col2:
                if st.button(prompt_text, key=f"suggested_prompt_{i}"):
                    process_user_query(username, prompt_text, users, user_data)
        else:
            with col3:
                if st.button(prompt_text, key=f"suggested_prompt_{i}"):
                    process_user_query(username, prompt_text, users, user_data)
    st.markdown("---") # Separator for visual clarity

    user_query = st.chat_input("How can I help you today?")

    if user_query:
        process_user_query(username, user_query, users, user_data)


def process_user_query(username, query, users, user_data):
    """Handles processing the user's query and getting AI response."""
    st.session_state.chat_history.append({"role": "user", "content": query})

    # Prepare user data for AI
    user_data_summary = {
        "goals_count": len(user_data.get("goals", [])),
        "completed_goals": sum(1 for g in user_data.get("goals", []) if g.get("status") == "Completed"),
        "recent_mood": user_data.get("moods", [])[-1] if user_data.get("moods") else None,
        "journal_entries_count": len(user_data.get("journals", []))
    }

    # Pass last 3 journal entries to AI for more context
    recent_journal_content = user_data.get("journals", [])[-3:]

    with st.chat_message("assistant"):
        with st.spinner("SoulSync is reflecting on your records..."):
            ai_response = get_ai_response(username, st.session_state.chat_history, user_data_summary, user_data, recent_journal_content)
            st.markdown(ai_response)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

            # Save updated chat history to user data
            users[username]["chat_history"] = st.session_state.chat_history
            save_users(users) # Save users data after each AI interaction

    st.rerun()