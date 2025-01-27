import sqlite3

def update_database_schema(db_path):
    """Update the database schema to include new columns."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check existing columns in the file_metadata table
        cursor.execute("PRAGMA table_info(file_metadata)")
        columns = [info[1] for info in cursor.fetchall()]

        # Add file_size column if it doesn't exist
        if "file_size" not in columns:
            cursor.execute("ALTER TABLE file_metadata ADD COLUMN file_size INTEGER")
            print("Added 'file_size' column to file_metadata.")

        # Add tags column if it doesn't exist
        if "tags" not in columns:
            cursor.execute("ALTER TABLE file_metadata ADD COLUMN tags TEXT")
            print("Added 'tags' column to file_metadata.")

        # Add file_type column if it doesn't exist
        if "file_type" not in columns:
            cursor.execute("ALTER TABLE file_metadata ADD COLUMN file_type TEXT")
            print("Added 'file_type' column to file_metadata.")

        # Add checksum column if it doesn't exist
        if "checksum" not in columns:
            cursor.execute("ALTER TABLE file_metadata ADD COLUMN checksum TEXT")
            print("Added 'checksum' column to file_metadata.")

        conn.commit()
        print("Database schema updated successfully.")
    except sqlite3.Error as e:
        print(f"Error updating database schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = "S:/Snowball/storage/data/memories.db"  # Update with your database path
    update_database_schema(db_path)
