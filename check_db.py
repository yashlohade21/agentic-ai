import sqlite3
import os

def check_database():
    db_path = 'sql_app.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return
    
    print(f"Database file exists at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        # Check users table
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"Users count: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, username, email FROM users LIMIT 5")
                users = cursor.fetchall()
                print(f"Sample users: {users}")
        except Exception as e:
            print(f"Error checking users table: {e}")
        
        # Check chat_messages table
        try:
            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            msg_count = cursor.fetchone()[0]
            print(f"Chat messages count: {msg_count}")
        except Exception as e:
            print(f"Error checking chat_messages table: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    check_database()
