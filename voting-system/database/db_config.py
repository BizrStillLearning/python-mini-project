import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voting_system.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS candidates
                   (
                       name
                       TEXT
                       PRIMARY
                       KEY,
                       votes
                       INTEGER
                       DEFAULT
                       0
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS voters
                   (
                       voter_id
                       TEXT
                       PRIMARY
                       KEY
                   )
                   ''')

    cursor.execute("SELECT COUNT(*) FROM candidates")
    if cursor.fetchone()[0] == 0:
        initial_candidates = [("Python", 0), ("JavaScript", 0), ("Golang", 0), ("C++", 0)]
        cursor.executemany("INSERT INTO candidates VALUES (?, ?)", initial_candidates)

    conn.commit()
    conn.close()


def db_cast_vote(voter_id, lang):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM voters WHERE voter_id = ?", (voter_id,))
        if cursor.fetchone() is not None:
            return "ALREADY_VOTED"

        cursor.execute("INSERT INTO voters VALUES (?)", (voter_id,))
        cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE name = ?", (lang,))
        conn.commit()
        return "SUCCESS"
    except sqlite3.Error as e:
        return f"ERROR: {e}"
    finally:
        conn.close()


def db_get_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, votes FROM candidates")
    data = dict(cursor.fetchall())
    conn.close()
    return data


def db_get_voters():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT voter_id FROM voters")
    voters_list = [row[0] for row in cursor.fetchall()]
    conn.close()
    return voters_list


def db_reset_system():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET votes = 0")
    cursor.execute("DELETE FROM voters")
    conn.commit()
    conn.close()