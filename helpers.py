from functools import wraps
import sqlite3
from flask import session, redirect, flash

def create_tables(conn):
    #Create tables of database
    cursor = conn.cursor()
    cursor.executescript('''
                CREATE TABLE IF NOT EXISTS users
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS users_id_index on users (id);
                ''')
    
    cursor.executescript('''
                CREATE TABLE IF NOT EXISTS to_dos
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                to_do TEXT NOT NULL,
                is_completed INTEGER NOT NULL,
                day TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
                );
                CREATE INDEX IF NOT EXISTS to_do_user_id_index on to_dos (user_id);
                CREATE INDEX IF NOT EXISTS to_do_id_index on to_dos (id);
                ''')
    
    cursor.executescript('''
                CREATE TABLE IF NOT EXISTS habits
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                habit TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
                );
                CREATE INDEX IF NOT EXISTS to_do_user_id_index on to_dos (user_id);
                CREATE INDEX IF NOT EXISTS to_do_id_index on to_dos (id);
                ''')
    
    cursor.executescript('''
                CREATE TABLE IF NOT EXISTS diaries
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                diary TEXT NOT NULL,
                day TEXT not NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
                );
                CREATE INDEX IF NOT EXISTS diaries_user_id_index on diaries (user_id);
                CREATE INDEX IF NOT EXISTS diaries_id_index on diaries (id);
                ''')

    conn.commit()
    cursor.close()



def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You need to sign in first", "warning")
            return redirect("/signin")
        else:
            return func(*args, **kwargs)
    return decorated_func


def check_to_do_id(to_do_id, conn):
    
    if to_do_id is None:
        return "there is no to-do id", 400
    
    if not to_do_id.isdecimal():
        return " to-do id must be decimal", 400
    
    c = conn.cursor()    
    c.execute("SELECT user_id FROM to_dos WHERE id = ?;", (to_do_id,))
    response = c.fetchone()
    c.close()
    if response is not None and session["user_id"] != response[0]:
        return "You are trying to access other people's data", 401
    
    c = conn.cursor()
    c.execute("SELECT id, to_do, is_completed FROM to_dos WHERE id = ?;", (to_do_id,))
    to_do = c.fetchone()   
    c.close()
    if to_do is None:
        return "there is no to-do with that id", 400
    
    return None

def to_dos_of_day(day, to_do_list):
    l = []
    for to_do in to_do_list:
        if day == to_do[3]:
            l.append(to_do)

    return l

# check if the habit is users or not
def habit_id_check(id, conn):
    c = conn.cursor()
    c.execute("SELECT user_id FROM habits WHERE id = ?;", (id,))
    response = c.fetchone()
    c.close()
    if response is not None and response[0] == session["user_id"]:
        return True
    
    return False