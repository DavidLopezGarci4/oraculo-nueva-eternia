
import sqlite3

def check_local_db():
    try:
        conn = sqlite3.connect("oraculo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in oraculo.db: {[t[0] for t in tables]}")
        
        if ("users",) in tables:
            cursor.execute("SELECT id, username, role FROM users;")
            users = cursor.fetchall()
            print(f"Users in local DB: {users}")
        else:
            print("Table 'users' does not exist in local DB.")
        conn.close()
    except Exception as e:
        print(f"Error checking local DB: {e}")

if __name__ == "__main__":
    check_local_db()
