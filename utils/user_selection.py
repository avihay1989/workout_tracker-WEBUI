# user_selection.py
import sqlite3
from utils.config import DB_FILE

def get_user_selection():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user_selection')
    user_selection = cursor.fetchall()
    connection.close()
    return user_selection
