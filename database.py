import sqlite3

def create_database():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Interview Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_name TEXT,

        topic TEXT,

        question TEXT,

        answer TEXT,

        score TEXT,

        feedback TEXT,

        interview_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)
    #interview sessions table
    cursor.execute("""
CREATE TABLE IF NOT EXISTS interview_sessions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    topic TEXT,
    overall_score TEXT,
    overall_feedback TEXT,
    interview_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
    

    conn.commit()
    conn.close()


if __name__=="__main__":
    create_database()
    print("Database Ready")