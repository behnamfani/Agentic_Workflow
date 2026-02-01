"""
Streamlit UI for Chatbot Application.
"""
import logging
import os
import sys
from dotenv import load_dotenv
import streamlit as st
from langchain.messages import HumanMessage, AIMessage

# Add the parent directory to sys.path so we can import our models
current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
parent_directory_path = os.path.dirname(current_directory_path)
root_directory_path = os.path.dirname(parent_directory_path)
sys.path.insert(0, current_directory_path)
sys.path.insert(0, parent_directory_path)
sys.path.insert(0, root_directory_path)

from src.utils.logging_config import get_logger
from src.app import App


def init_page() -> None:
    """Initializes the Streamlit page configuration."""
    get_logger().info("Initializing the Streamlit page.")
    st.set_page_config(
        page_title="Catbot",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    with open(current_directory_path + "/static/style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    st.header("🐾 Catbot")
    st.sidebar.title("Options")
    st.sidebar.markdown(
        "Meow~ 🐾\nHow can I help you today, hooman?",
        unsafe_allow_html=True
    )


def init_messages() -> None:
    """Initializes chat messages and reset button."""
    get_logger().info("Initializing chat messages.")
    clear_button = st.sidebar.button("Reset Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        get_logger().info("Resetting messages state.")
        st.session_state.messages = []
        if "app" in st.session_state:
            get_logger().info("Clearing chatbot's internal history.")
            st.session_state.app.clear_history()


def init_app() -> None:
    """Initialize the App instance if not already present."""
    if "app" not in st.session_state:
        get_logger().info("Initializing App instance.")
        try:
            system_text = st.sidebar.text_area(
                "System Prompt",
                value="You are a helpful assistant.",
                height=100,
                key="system_prompt",
            )
            st.session_state.app = App(
                system_text=system_text,
                chat_history_limit=8,
                show_graph=False,
            )
        except Exception as e:
            get_logger().error(f"Failed to initialize the app: {e}")
            st.error("Error initializing the chatbot. Please check the logs.")
            raise


def main() -> None:
    """
    The main function to run the Streamlit app.
    Handles chatbot initialization, user input, and response generation.
    """
    get_logger().info("Starting the Streamlit application.")
    load_dotenv()

    init_page()
    init_messages()
    init_app()

    assistant = current_directory_path + "/" + "static/cat.jpg"
    # Display conversation history
    messages = st.session_state.get("messages", [])
    get_logger().info(f"Loaded {len(messages)} messages from session state.")

    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant", avatar=assistant):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    # Get user input and generate responses
    if user_input := st.chat_input("Meow...Ask me anything!"):
        get_logger().info(f"Received user input: {user_input}")
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            with st.chat_message("assistant", avatar=assistant):
                show_answer = st.empty()
                with st.spinner("Thinking..."):
                    response, _ = st.session_state.app.ask(user_input)
                    get_logger().info(f"Generated response: {response[:100]}...")
                    show_answer.write(response)
                st.session_state.messages.append(AIMessage(content=response))
        except Exception as e:
            get_logger().error(f"Error during response generation: {e}")
            st.error("An error occurred while generating the response. Please try again.")


if __name__ == "__main__":
    get_logger().info("Application starting.")
    main()
