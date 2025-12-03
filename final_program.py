import os 
import sqlite3
import pandas as pd

def setup_database():
    """Create the database and tunes table"""
    # this creates the database in the current directory
    conn = sqlite3.connect('tunes.db')
    cursor = conn.cursor()
    
    # standard sql procedure, so the below code can run without issues
    cursor.execute('DROP TABLE IF EXISTS tunes')
    
    # running the sql query to create the table
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
          tune_data.get('tune_type', 'Unknown'), tune_data.get('key', ''),
          tune_data.get('meter', ''), tune_data.get('raw_abc', '')))
    
    conn.commit()
    conn.close()


def parse_abc_file(file_path):
    """Parse ABC file using the same approach as previous labs"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    tunes = []
    current_tune = None
    current_tune_notation = ""
    
    for line in lines:    
        if line.startswith("X:"):
            # we are in a new tune
            if current_tune and current_tune_notation.strip():
                current_tune["raw_abc"] = current_tune_notation
                tunes.append(current_tune)
            
            x = line[2:].strip()
            current_tune = {"x": x}
            current_tune_notation = line
                
        elif line.startswith("T:") and current_tune:
            title = line[2:].strip()
            current_tune["title"] = title
            current_tune_notation += line
            
        elif line.startswith("R:") and current_tune:
            tune_type = line[2:].strip()
            current_tune["tune_type"] = tune_type
            current_tune_notation += line
            
        elif line.startswith("K:") and current_tune:
            key = line[2:].strip()
            current_tune["key"] = key
            current_tune_notation += line
            
        elif line.startswith("M:") and current_tune:
            meter = line[2:].strip()
            current_tune["meter"] = meter
            current_tune_notation += line
            
        elif line.strip() == "" and current_tune:
            # End of tune
            if current_tune_notation.strip():
                current_tune["raw_abc"] = current_tune_notation
                tunes.append(current_tune)
            current_tune = None
            current_tune_notation = ""
            
        elif current_tune:
            current_tune_notation += line
    
    # Don't forget the last tune
    if current_tune and current_tune_notation.strip():
        current_tune["raw_abc"] = current_tune_notation
        tunes.append(current_tune)
    
    return tunes

def process_all_books():
    """Process all ABC files in all book folders"""
    books_dir = "abc_books"
    all_tunes = []
    
    if not os.path.exists(books_dir):
        print(f"Error: Directory '{books_dir}' not found!")
        return all_tunes
    
    for item in os.listdir(books_dir):
        item_path = os.path.join(books_dir, item)
        
        if os.path.isdir(item_path) and item.isdigit():
            book_number = int(item)
            print(f"Processing book {book_number}...")
            
            for file in os.listdir(item_path):
                if file.endswith('.abc'):
                    file_path = os.path.join(item_path, file)
                    print(f"  Reading: {file}")
                    
                    tunes = parse_abc_file(file_path)
                    print(f"    Found {len(tunes)} tune(s)")
                    
                    # Add book number to each tune and insert into database
                    for tune in tunes:
                        tune['book_number'] = book_number
                        insert_tune(book_number, tune)
                    
                    all_tunes.extend(tunes)
    
    return all_tunes

# smaller functions begin here for each of the functionalities
# runs a SQL query to select all tunes from database
def load_tunes_from_database():
    """Load all tunes from SQLite into DataFrame"""
    conn = sqlite3.connect('tunes.db')
    df = pd.read_sql('SELECT * FROM tunes', conn)
    conn.close()
    return df

#the below use Pandas logic from previous labs

# by book
def get_tunes_by_book(df, book_number):
    """Get all tunes from a specific book"""
    return df[df['book_number'] == book_number]

# by tune_type
def get_tunes_by_type(df, tune_type):
    """Get all tunes of a specific type"""
    return df[df['tune_type'].str.contains(tune_type, case=False, na=False)]

# by name/title
def search_tunes(df, search_term):
    """Search tunes by title (case insensitive)"""
    return df[df['title'].str.contains(search_term, case=False, na=False)]

def run_user_interface():
    """Run the interactive user interface"""
    df = load_tunes_from_database()
    
    if df.empty:
        print("No tunes found in database!")
        return
    
    print(f"\nLoaded {len(df)} tunes from database")
    
    while True:
        print("\n=== ABC Tunes Database ===")
        print("1. Show all tunes")
        print("2. Search tunes by book")
        print("3. Search tunes by type") 
        print("4. Search tunes by title")
        print("5. Show statistics")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print(f"\nAll tunes ({len(df)} total):")
            print(df[['book_number', 'title', 'tune_type']].to_string(index=False))
        
        elif choice == '2':
            book_num = input("Enter book number: ").strip()
            if book_num.isdigit():
                result = get_tunes_by_book(df, int(book_num))
                if not result.empty:
                    print(f"\nTunes from book {book_num}:")
                    print(result[['title', 'tune_type']].to_string(index=False))
                else:
                    print(f"No tunes found in book {book_num}")
        
        elif choice == '3':
            tune_type = input("Enter tune type (e.g., jig, reel): ").strip()
            result = get_tunes_by_type(df, tune_type)
            if not result.empty:
                print(f"\n{len(result)} {tune_type} tunes found:")
                print(result[['book_number', 'title']].to_string(index=False))
            else:
                print(f"No {tune_type} tunes found")
        
        elif choice == '4':
            search_term = input("Enter title search term: ").strip()
            result = search_tunes(df, search_term)
            if not result.empty:
                print(f"\n{len(result)} tunes containing '{search_term}':")
                print(result[['book_number', 'title', 'tune_type']].to_string(index=False))
            else:
                print(f"No tunes found containing '{search_term}'")
        
        elif choice == '5':
            print("\n=== Database Statistics ===")
            print(f"Total tunes: {len(df)}")
            print(f"Books: {df['book_number'].nunique()}")
            
            print("\nTune types:")
            tune_types = df['tune_type'].value_counts()
            print(tune_types)
            
            print("\nKeys:")
            keys = df['key'].value_counts()
            print(keys)
        
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function to run the entire application"""
    print("Starting ABC Parser Application...")
    
    # setup database
    setup_database()
    
    # process all ABC files
    all_tunes = process_all_books()
    print(f"Processing complete! Added {len(all_tunes)} tunes to database")
    
    # load into pandas and show some analysis
    df = load_tunes_from_database()
    
    if not df.empty:
        print(f"\nDatabase contains {len(df)} tunes")
        print(f"Books: {df['book_number'].nunique()}")
        
        # show some tune types like in the lab
        tune_types = df['tune_type'].value_counts()
        print(f"\nTune types:")
        print(tune_types)
        
        # show some keys like in the lab  
        keys = df['key'].value_counts()
        print(f"\nKeys:")
        print(keys)
    
    # start user interface
    run_user_interface()

if __name__ == "__main__":
    main()