import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database Configuration
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "data.db")

# Upload Storage Configuration
STORED_FILES_DIR = os.path.join(BASE_DIR, "stored_files")

# Ensure storage directory exists
os.makedirs(STORED_FILES_DIR, exist_ok=True)
