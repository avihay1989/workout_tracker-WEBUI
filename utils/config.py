import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # Centralized data folder
DB_FILE = r"C:\Users\aviha\Documents\VS Code\workout_tracker-Notification_Toast\data\database.db"

# Constants
APP_TITLE = "Workout Tracker"
LOGS_DIR = os.path.join(BASE_DIR, "../logs")

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
