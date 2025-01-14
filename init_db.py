import sqlite3


# Initialize the database
def init_db():
    # Create a database in RAM
    conn = sqlite3.connect('database/database.db')
    # Get a cursor object
    cursor = conn.cursor()

    # Create a table
    with open('sql/schema.sql', 'r') as f:
        cursor.executescript(f.read())

    # Save (commit) the changes
    conn.commit()
    # Close the connection
    conn.close()
