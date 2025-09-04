# config.py

import os
from dotenv import load_dotenv

def load_api_key():
    """
    Loads the Google API key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file. Please add it.")
    return api_key

def load_assemblyai_api_key():
    """
    Loads the AssemblyAI API key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not found in .env file. Please add it.")
    return api_key

