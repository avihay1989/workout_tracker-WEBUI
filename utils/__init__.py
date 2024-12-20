# Importing configuration and utility modules
from .config import DB_FILE
from .database import DatabaseHandler
from .filters import ExerciseFilter
from .business_logic import BusinessLogic
from .db_initializer import initialize_database
from .exercise_manager import get_exercises, add_exercise
from utils.exercise_manager import get_exercises, add_exercise
from .user_selection import get_user_selection
from .weekly_summary import calculate_weekly_summary, get_weekly_summary, calculate_total_sets

# Defining the module's public interface
__all__ = [
    "DB_FILE",                  # Path to the database file
    "DatabaseHandler",          # Handles database operations
    "ExerciseFilter",           # Filter logic for exercises
    "BusinessLogic",            # Main business logic
    "initialize_database",      # Database initialization logic
    "get_exercises",            # Fetch exercises from the database
    "add_exercise",             # Add new exercises
    "get_user_selection",       # Retrieve user selection data
    "calculate_weekly_summary", # Weekly summary logic
    "get_weekly_summary",       # Fetch weekly summary
    "calculate_total_sets",     # Calculate total sets for a given criteria
]