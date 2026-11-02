"""
Streamlit entry point for Catbot.
"""
import subprocess

if __name__ == "__main__":
    subprocess.run(["streamlit", "run", "src/Frontend/streamlit_ui.py", "--server.port=8505"])