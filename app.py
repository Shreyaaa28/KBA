import os
import streamlit as st
from dotenv import load_dotenv

# Load .env and print key BEFORE anything else
load_dotenv(dotenv_path=".env", override=True)
print("🚨 DEBUG GROQ KEY =", repr(os.getenv("GROQ_API_KEY")))

from ui.chat_ui import main_ui

if __name__ == "__main__":
    main_ui()
