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


def main() -> None:
    """
    The main function to run the Streamlit app.
    Handles bot selection and chatbot interaction.
    """
    get_logger().info("Starting the Streamlit application.")
    load_dotenv()

    # Set page config once
    st.set_page_config(
        page_title="Catbot",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    with open(current_directory_path + "/static/style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    if not st.session_state.get('bot_started', False):
        # Starter Page: Bot Selection
        st.title("🐾 Choose Your Bot")
        
        with st.sidebar:
            st.title("Bot Selection")
            st.markdown("Select a bot and customize its details before starting!")
            
            bot_options = ["General", "ProfileExplainer", "BoardGenie"]
            selected_bot = st.selectbox("Choose Bot", bot_options, key="selected_bot")
            
            # Define system texts for each bot
            bot_system_texts = {
                "General": "You are a helpful assistant.",
                "ProfileExplainer": "You are a profile explainer bot.",
                "BoardGenie": "You are BoardGenie, a helpful assistant designed to assist users in creating and "
                              "managing their project boards."
            }
            
            # Input fields based on selected bot
            if selected_bot == "General":
                name = st.text_input("Name", value="General Assistant", key="name")
                details = st.text_area("Details", value="Personality: Friendly and helpful. Language: English. Output "
                                                        "schema: Maintains long term memory.", height=100,
                                       key="details")
            elif selected_bot == "ProfileExplainer":
                language = st.text_input("Language", value="English", key="language")
            elif selected_bot == "BoardGenie":
                taste_of_game = st.text_input("Taste of game", value="Strategy games", key="taste_of_game")
                favourite_game = st.text_input("Favourite game", value="Chess", key="favourite_game")
                long_term_memory = st.text_input("Long term memory", value="Remembers past games and strategies", key="long_term_memory")
            
            start = st.button('Start Bot!', key='start')
            if start:
                try:
                    st.session_state['bot_started'] = True
                    # Store the inputs in session_state
                    if selected_bot == "General":
                        st.session_state['bot_name'] = name
                        st.session_state['bot_details'] = details
                    elif selected_bot == "ProfileExplainer":
                        st.session_state['bot_language'] = language
                    elif selected_bot == "BoardGenie":
                        st.session_state['bot_taste_of_game'] = taste_of_game
                        st.session_state['bot_favourite_game'] = favourite_game
                        st.session_state['bot_long_term_memory'] = long_term_memory
                    st.session_state.app = App(
                        system_text=bot_system_texts[selected_bot],
                        chat_history_limit=8,
                        show_graph=False,
                    )
                    st.session_state.messages = []  # Initialize messages
                    st.rerun()
                except Exception as e:
                    get_logger().error(f"Failed to initialize the app: {e}")
                    st.error("Error initializing the chatbot. Please check the logs.")
    else:
        # Chat Page: Interact with the Bot
        selected_bot = st.session_state.get('selected_bot', 'Bot')
        st.title(f"🐾 Chat with {selected_bot}")
        
        with st.sidebar:
            st.title("Chat Options")
            st.markdown(f"Meow~ 🐾\nChatting with {selected_bot}!")
            
            # Reset Conversation
            if st.button("Reset Conversation", key="clear"):
                get_logger().info("Resetting messages state.")
                st.session_state.messages = []
                if "app" in st.session_state:
                    st.session_state.app.clear_history()
            
            # Back to Selection
            if st.button("Back to Bot Selection", key="back"):
                # Clear everything and go back
                st.session_state.clear()
                st.cache_resource.clear()
                st.cache_data.clear()
                st.rerun()
        
        # Chat Interface
        assistant = current_directory_path + "/static/Cat.png"  # TODO: Customize per bot later
        messages = st.session_state.get("messages", [])
        get_logger().info(f"Loaded {len(messages)} messages from session state.")
        
        for message in messages:
            if isinstance(message, AIMessage):
                with st.chat_message("assistant", avatar=assistant):
                    st.markdown(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message.content)
        
        # Get user input and generate responses
        if user_input := st.chat_input("Meow...Ask me anything!"):
            get_logger().info(f"Received user input: {user_input}")
            st.session_state.messages.append(HumanMessage(content=user_input))
            with st.chat_message("user", avatar="👤"):
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
