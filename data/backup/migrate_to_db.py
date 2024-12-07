import pandas as pd
import sqlite3

# File paths
CSV_FILE = r'/exercise_database.csv'
DB_FILE = '../exercise_database.db'

# Load the CSV file
print("=== Loading CSV File ===")
try:
    data = pd.read_csv(CSV_FILE)
    print("CSV Loaded Successfully!")
    print("First 5 Rows of the CSV Data:")
    print(data.head())  # Show the first few rows of the CSV file
except FileNotFoundError:
    print(f"Error: {CSV_FILE} not found!")
    exit()

# Rename columns to match SQLite table schema
print("\n=== Renaming Columns ===")
data.rename(columns={
    'Main muscle group': 'main_muscle_group',
    'Sub muscle group': 'sub_muscle_group',
    'exercise name': 'exercise_name'
}, inplace=True)
print("Columns after renaming:")
print(data.columns)

# Connect to SQLite database
print("\n=== Connecting to Database ===")
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"Connected to SQLite database: {DB_FILE}")
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    exit()

# Create the 'exercises' table
print("\n=== Creating Table ===")
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_name TEXT NOT NULL,
        main_muscle_group TEXT NOT NULL,
        sub_muscle_group TEXT,
        equipment TEXT
    )
    ''')
    print("Table 'exercises' created (if not exists).")
except sqlite3.Error as e:
    print(f"Error creating table: {e}")
    conn.close()
    exit()

# Insert data into the 'exercises' table
print("\n=== Inserting Data ===")
try:
    print(f"Inserting {len(data)} rows into the 'exercises' table.")
    data.to_sql('exercises', conn, if_exists='replace', index=False)
    print("Data inserted into the 'exercises' table successfully!")
except sqlite3.Error as e:
    print(f"Error inserting data into table: {e}")
except ValueError as ve:
    print(f"Data insertion failed: {ve}")

# Verify data insertion
print("\n=== Verifying Data Insertion ===")
try:
    cursor.execute("SELECT COUNT(*) FROM exercises")
    count = cursor.fetchone()[0]
    print(f"Number of rows in 'exercises' table: {count}")

    cursor.execute("SELECT * FROM exercises LIMIT 5")
    rows = cursor.fetchall()
    print("First 5 rows in 'exercises' table:")
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Error querying 'exercises' table: {e}")

# Commit and close the connection
print("\n=== Finalizing ===")
try:
    conn.commit()
    print("Changes committed to the database.")
finally:
    conn.close()
    print("Database connection closed.")
