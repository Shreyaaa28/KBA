from dotenv import load_dotenv
import streamlit as st
from ui.chat_ui import main_ui

# Load .env once at startup
load_dotenv(dotenv_path=".env", override=True)

if __name__ == "__main__":
    main_ui()
