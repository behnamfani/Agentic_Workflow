"""
Streamlit UI for Chatbot Application.
"""
import logging
import os
import sys
from typing import Any

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
from src.utils.validate_instructions import optional_instructions
from src.agents.ProfileExplainer import profile_explainer, profile_tools
from src.agents.General import general, general_bot_tools
from src.UI.components import selection


def _load_css_file(css_path: str) -> None:
    if os.path.isfile(css_path):
        with open(css_path, "r", encoding="utf-8") as css:
            st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


def _apply_bot_theme(selected_bot: str) -> None:
    theme_files = {
        "BoardGenie": "style_boardgenie.css",
        "ProfileExplainer": "style_profileexplainer.css",
        "General": "style.css",
    }
    css_name = theme_files.get(selected_bot, "style.css")
    _load_css_file(current_directory_path + f"/static/{css_name}")


def _get_bot_avatar(selected_bot: str) -> Any | None:
    local_avatars = {
        "BoardGenie": current_directory_path + r"/static/BoardGenie.png",
        "ProfileExplainer": current_directory_path + r"/static/ProfileExplainer.png",
        "General": current_directory_path + r"/static/Cat.png",
    }

    local_path = local_avatars.get(selected_bot) or local_avatars["General"]
    if os.path.isfile(local_path):
        return local_path
    return None


def _create_app_bot(
        bot_name: str,
        system_text: str,
        chat_history_limit: int = 8,
        show_graph: bool = False,
        tools: list = None
):
    if not tools:
        tools = []
    if not st.session_state.get(bot_name):
         st.session_state[bot_name] = App(
                system_text=system_text,
                chat_history_limit=chat_history_limit,
                show_graph=show_graph,
                tools=tools,
            )
    return st.session_state[bot_name]


def init_session():
    """Initialize all session state variables safely."""
    if "bot_started" not in st.session_state:
        st.session_state.bot_started = False
    if "selected_bot" not in st.session_state:
        st.session_state.selected_bot = "General"
    if "selected_bot_widget" not in st.session_state:
        st.session_state.selected_bot_widget = st.session_state.selected_bot
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main() -> None:
    get_logger().info("Starting the Streamlit application.")
    load_dotenv()

    st.set_page_config(
        page_title="Catbot",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session()
    if st.session_state.bot_started:
        _apply_bot_theme(st.session_state.selected_bot)
    else:
        _load_css_file(current_directory_path + "/static/style_selection.css")

    # ============ BOT SELECTION PAGE =============
    if not st.session_state.bot_started:

        selected_bot = selection.bot_selection_style(st)

        bot_system_texts = {
            "General": general.system_text,
            "ProfileExplainer": profile_explainer.AGENT_INSTRUCTIONS,
            "BoardGenie": (
                "You are BoardGenie, a helpful assistant designed to assist users in creating "
                "and managing project boards. Use game emojis when answering."
            ),
        }

        config_col, _ = st.columns([2, 1])
        with config_col:
            if selected_bot == "General":
                name = st.text_input("Bot Name", value="General Assistant",
                                     placeholder="e.g. My Assistant")
                details = st.text_area("Personality & Details",
                                       value="Personality: Friendly and helpful. Language: English.",
                                       height=100,
                                       placeholder="Describe tone, language, areas of focus…")

            elif selected_bot == "ProfileExplainer":
                language = st.text_input("Response Language", value="English",
                                         placeholder="e.g. English, German, French")

            elif selected_bot == "BoardGenie":
                c1, c2 = st.columns(2)
                with c1:
                    taste_of_game = st.text_input("Game Taste", value="Strategy games")
                    favourite_game = st.text_input("Favourite Game", value="Chess")
                with c2:
                    long_term_memory = st.text_area("Memory Notes",
                                                    value="Remembers past games and strategies",
                                                    height=104)

            st.markdown("<div style='margin-top:1.25rem;'>", unsafe_allow_html=True)
            if st.button("🚀  Start Session", key="start_bot",
                         type="primary", use_container_width=True):

                # Build opt_instruction per bot
                if selected_bot == "General":
                    opt_instruction = f"Name: {name}\nDetails:\n{details}"
                    tools = general_bot_tools.tools
                elif selected_bot == "ProfileExplainer":
                    opt_instruction = f"Language: {language}"
                    tools = profile_tools.tools
                elif selected_bot == "BoardGenie":
                    opt_instruction = ""
                    tools = None

                system_texts = bot_system_texts[selected_bot].format(
                    user_instructions_block=optional_instructions(opt_instruction)
                )
                st.session_state.app = App(
                    system_text=system_texts,
                    chat_history_limit=8,
                    show_graph=False,
                    tools=tools,
                )
                st.session_state.bot_started = True
                st.session_state.messages = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ============ CHAT PAGE =============
    else:
        selected_bot = st.session_state.selected_bot
        st.title(f"🐾 Chat with {selected_bot}")
        
        with st.sidebar:
            st.title("Chat Options")
            title_mapper = {
                "General": "🐾",
                "ProfileExplainer": "📃",
                "BoardGenie": "🧞‍♂️🎲",
            }

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

        assistant_avatar = _get_bot_avatar(selected_bot)

        # Show chat history
        for message in st.session_state.messages:
            if isinstance(message, AIMessage):
                with st.chat_message("assistant", avatar=assistant_avatar):
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
                with st.chat_message("assistant", avatar=assistant_avatar):
                    show_answer = st.empty()
                    with st.spinner("Thinking..."):
                        response, _ = st.session_state.app.ask(user_input)
                        get_logger().info(f"Generated response!")
                        show_answer.write(response)
                    st.session_state.messages.append(AIMessage(content=response))
            except Exception as e:
                get_logger().error(f"Error during response generation: {e}")
                st.error("An error occurred while generating the response. Please try again.")


if __name__ == "__main__":
    main()