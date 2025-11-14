import os 
import sqlite3
import pandas as pd

def setup_database():
    """Create the database and tunes table"""
    # this creates the database in the current directory
    conn = sqlite3.connect('tunes.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS tunes')
    
    cursor.execute('''
        CREATE TABLE tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_number INTEGER,
            title TEXT,
            tune_type TEXT,
            key TEXT,
            meter TEXT,
            raw_abc TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup complete")

