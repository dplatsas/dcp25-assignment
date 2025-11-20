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

def insert_tune(book_number, tune_data):
    """Insert a single tune into the database"""
    conn = sqlite3.connect('tunes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tunes (book_number, title, tune_type, key, meter, raw_abc)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (book_number, tune_data.get('title', 'Unknown'), 
          tune_data.get('type', 'Unknown'), tune_data.get('key', ''),
          tune_data.get('meter', ''), tune_data.get('raw_abc', '')))
    
    conn.commit()
    conn.close()
