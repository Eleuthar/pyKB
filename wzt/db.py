import sqlite3


db_name = "wzt.db"

# Connect to SQLite database (it will create the file if it doesn't exist)
connection = sqlite3.connect(db_name)

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# allow same formation recurring gathering to keep track
# of all their rounds in that formation
# same gamer can be part of multiple gatherings
uzr_tb = '''
    CREATE TABLE IF NOT EXISTS uzr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
'''
gathering_tb = """
CREATE TABLE IF NOT EXISTS gathering (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    FOREIGN KEY (member_id) REFERENCES uzr(id)
);
"""

round_tb = """
CREATE TABLE IF NOT EXISTS round (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    FOREIGN KEY (gathering_id) REFERENCES gathering(id)
);
"""

for q in [uzr_tb, round_tb, gathering_tb]:
    cursor.execute(q)

# Commit the changes and close the connection
connection.commit()
connection.close()