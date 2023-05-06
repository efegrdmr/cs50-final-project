from urllib import parse

from flask import Flask, render_template, session, request, flash, redirect, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from helpers import create_tables, login_required, check_to_do_id, to_dos_of_day, habit_id_check

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
# Set secret key for cookies
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Session(app)

# Connect to the Database
conn = sqlite3.connect("data.db", check_same_thread=False)
create_tables(conn)

@app.route('/api/account', methods=["PUT", "DELETE"])
@login_required
def account():
    # Requires operation header
    operation = request.headers.get('operation')
    if request.method == "PUT":
        # Change password required headers => new_password, confirmation
        if operation == "change_password":
            try:
                new_password = parse.unquote(request.headers.get("new_password"))
                confirmation = parse.unquote(request.headers.get("confirmation"))
            except TypeError:
                return "there is no password or confirmation header", 400
            
            if new_password != confirmation:
                return "the password and confirmation aren't the same", 400
            
            c = conn.cursor()
            c.execute("UPDATE users SET password = ? WHERE id = ?;", (generate_password_hash(new_password), session["user_id"]))
            conn.commit()
            c.close()
            
            return "", 200
        
        elif operation == "change_email":
            # Change email required header new_email
            try:
                new_email = parse.unquote(request.headers.get("new_email"))
            except TypeError:
                return "there is no new_email header", 400
            
            # Check if new email already exists
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE email = ?;", (new_email,))
            response = c.fetchone()
            c.close()
            if response is not None:
                return "This email already exists!", 400
            
            c = conn.cursor()
            c.execute("UPDATE users SET email = ? WHERE id = ?;", (new_email, session["user_id"]))
            conn.commit()
            c.close()

            return "", 200
        
        elif operation == "change_user_name":
            # Change user name required header new_user_name
            try:
                user_name = parse.unquote(request.headers.get("new_user_name"))
            except TypeError:
                return "there is no user_name header", 400
            
            # Check if new user_name already exists
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE user_name = ?;", (user_name,))
            response = c.fetchone()
            c.close()
            if response is not None:
                return "This user name already exists!", 400
            
            c = conn.cursor()
            c.execute("UPDATE users SET user_name = ? WHERE id = ?;", (user_name, session["user_id"]))
            conn.commit()
            c.close()
            session["user_name"] = user_name

            return "", 200

    elif request.method == "DELETE":
        if operation == "delete_account":
            print(session["user_id"])
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE id = ?;", (session["user_id"],))
            c.execute("DELETE FROM diaries WHERE user_id = ?;", (session["user_id"],))
            c.execute("DELETE FROM habits WHERE user_id = ?;", (session["user_id"],))
            c.execute("DELETE FROM to_dos WHERE user_id = ?;", (session["user_id"],))
            conn.commit()
            c.close()
            session["user_id"] = None
            session["user_name"] = None

            return "", 200

    return "Method not found", 404




@app.route("/api/habits", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def habits():
    # Get all habits of user
    if request.method == "GET":
        c = conn.cursor()
        c.execute("SELECT id, habit FROM habits WHERE user_id = ?;", (session["user_id"],))
        habits = c.fetchall()
        c.close()   
        return jsonify(habits), 200
    
    # Add new habit required header => encoded "habit"
    if request.method == "POST":
        habit = parse.unquote(request.headers.get("habit", ""))
        c = conn.cursor()
        c.execute("INSERT INTO habits (habit, user_id) VALUES (?,?);", (habit, session["user_id"]))
        conn.commit()
        c.close()

        return "", 200
    
    # Update a habit required headers => "habit_id", utf-8 encoded "habit" 
    if request.method == "PUT":
        id = request.headers.get("habit_id")
        if not habit_id_check(id, conn):
            return "This habit is not yours", 401
        
        c = conn.cursor()
        habit = parse.unquote(request.headers.get("habit", ""))
        c.execute("UPDATE habits SET habit = ? WHERE id = ?;", (habit, id))
        conn.commit()
        c.close()
        
        return "", 200
    
    if request.method == "DELETE":
        id = request.headers.get("habit_id")
        if not habit_id_check(id, conn):
            return "This habit is not yours", 401
        c = conn.cursor()
        c.execute("DELETE FROM habits WHERE id = ?;", (id,))
        conn.commit()
        c.close()

        return "", 200        

@app.route("/api/diary", methods = ["GET", "PUT", "DELETE"])
@login_required
def api_diary():
    if request.method == "GET":
        day = request.headers.get("day")
        if day is None:
            return "day header is empty", 400
        c = conn.cursor()
        c.execute("SELECT diary FROM diaries WHERE day = ? AND user_id = ?;", (day, session["user_id"]))
        diary = c.fetchone()
        c.close()
        # Create new diary entry in database
        if diary is None:
            c = conn.cursor()
            c.execute("INSERT INTO diaries (user_id, diary, day) VALUES (?,?,?);", (session["user_id"], "", day))
            conn.commit()
            c.close()
            # Add habits as to_dos
            c = conn.cursor()
            c.execute("SELECT habit FROM habits WHERE user_id = ?;", (session["user_id"],))
            habits = c.fetchall()
            for habit in habits:
                c.execute("INSERT INTO to_dos (user_id, to_do, is_completed, day) VALUES(?,?,?,?)", (session["user_id"], habit[0], 0, day))
            c.close()
            return "", 200

        return diary[0], 200
    
    if request.method == "PUT":
        day = request.headers.get("day")
        if day is None:
            return "day header is empty", 400
        
        diary = parse.unquote(request.headers.get("diary", ""))

        c = conn.cursor()
        c.execute("UPDATE diaries SET diary = ? WHERE day = ? AND user_id = ?;", (diary, day, session["user_id"]))
        conn.commit()
        c.close()

        return "", 200
    
    if request.method == "DELETE":
        diary_id = request.headers.get("diary_id")
        if diary_id is None:
            return "there is no diary_id header", 400
        c = conn.cursor()
        c.execute("SELECT user_id FROM diaries WHERE id = ?;", (diary_id,))
        user_id = c.fetchone()
        c.close()
        if user_id is None:
            return "that diary does not exist", 400
        if user_id[0] != session["user_id"]:
            return "that diary is not yours", 400
        
        c = conn.cursor()
        c.execute("SELECT day FROM diaries WHERE id = ?;", (diary_id,))
        day = c.fetchone()[0]
        c.execute("DELETE FROM diaries WHERE id = ?;", (diary_id,))
        c.execute("DELETE FROM to_dos WHERE day = ? AND user_id = ?", (day, session["user_id"]))
        conn.commit()
        c.close()



        return "", 200



@app.route("/api/to-do", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def api_get_to_do():
    to_do_id = request.headers.get("to_do_id")
    # Return all to-do's request.headers["day"] if the request.headers["to_do_id"] is * else return to-do of that id
    if request.method == "GET":
        if request.headers.get("day") is None:
            return "there is no day", 400
        if to_do_id is None:
            return "there is no to-do id", 400
        
        elif to_do_id == "*":
            c = conn.cursor()
            c.execute("SELECT id, to_do, is_completed, day FROM to_dos WHERE user_id = ?;", (session["user_id"],))
            to_do = c.fetchall()
            c.close()
            return jsonify(to_dos_of_day(request.headers.get("day"),to_do)), 200

        result = check_to_do_id(to_do_id, conn)
        if result is not None:
            return result
        
        c = conn.cursor()
        c.execute("SELECT id, to_do, is_completed, date FROM to_dos WHERE id = ?;", (to_do_id,))
        to_do = c.fetchone()
        c.close()
        return jsonify(to_do), 200
    
    # Add new to-do to database request.headers["to_do"], (request.headers["is_completed"] 1 is true 0 is false) request.headers["day"]
    elif request.method == "POST":

        if request.headers.get("day") is None:
            return "there is no day", 400
        
        if request.headers.get("to_do") is None:
            return "there is no to-do header", 400
        
        is_completed = request.headers.get("is_completed")
        if is_completed is None:
            return "there is no is_completed header", 400
        if is_completed not in ["0", "1"]:
            return "is_completed must be 1 or 0", 400
        
        c = conn.cursor()
        c.execute("INSERT INTO to_dos (user_id, to_do, is_completed, day) VALUES (?,?,?,?)",
                        (session["user_id"], parse.unquote(request.headers["to_do"]), is_completed, request.headers["day"]))
        conn.commit()
        c.close()
        return "", 200
    
    # Delete to-do from data-base request.headers["to_do_id"]
    elif request.method == "DELETE":
        to_do_id = request.headers.get("to_do_id")
        result = check_to_do_id(to_do_id, conn)
        if result is not None:
            return result
        
        c = conn.cursor()
        c.execute("DELETE FROM to_dos WHERE id = ?;", (to_do_id,))
        conn.commit()
        c.close()
        return "", 200
    
    # Update to-do with headers: to_do_id, to_do, is_completed
    elif request.method == "PUT":

        to_do_id = request.headers.get("to_do_id")
        result = check_to_do_id(to_do_id, conn)
        if result is not None:
            return result
        
        to_do = request.headers.get('to_do')
        is_completed = request.headers.get("is_completed")
        if is_completed is None and to_do is not None:
            c = conn.cursor()
            c.execute("UPDATE to_dos SET to_do = ? WHERE id = ?;", (parse.unquote(to_do), to_do_id))
            conn.commit()
            c.close()
            return "", 200  
        elif is_completed not in ["0", "1"]:
            return f"is_completed must be 1 or 0 not: {is_completed}", 400
        
        elif to_do is None:
            c = conn.cursor()
            c.execute("UPDATE to_dos SET is_completed = ? WHERE id = ?;", (is_completed, to_do_id))
            conn.commit()
            c.close()
            return "", 200
        
        c = conn.cursor()
        c.execute("UPDATE to_dos SET to_do = ?, is_completed = ? WHERE id = ?;", (parse.unquote(to_do), is_completed, to_do_id))
        conn.commit()
        c.close()
        return "", 200
    


@app.route("/")
@login_required
def index():
    return render_template("index.html", session=session)


@app.route("/signin", methods=["POST","GET"])
def signin():
    # Check if user exists
    if request.method == "GET":
        return render_template("signin.html")
    
    name = request.form.get("user_name_email")
    if name is None:
        flash("You must enter an user name", "danger")
        return redirect("/signin")
    c = conn.cursor()
    if "@" in name:
        c.execute("SELECT password, id, user_name FROM users WHERE email = ?;",(name,))
    else:
        c.execute("SELECT password, id, user_name FROM users WHERE user_name = ?;",(name,))
    response = c.fetchone()
    c.close()
    if response is None:
        flash("Your user_name or email is not correct", "warning") 
        return redirect("/signin")
    
    # Verify password
    if not check_password_hash(response[0], request.form.get("password", "")):
        flash("Your password is not correct", "warning") 
        return redirect("/signin")
    
    # Log in
    session["user_name"] = response[2]
    session["user_id"] = response[1]
    flash("Signed in", "info")
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    # Check if user name exists before
    user_name = request.form.get("user_name")
    if user_name is None or user_name == "":
        flash("You must enter a user name!", "warning")
        return redirect("/register")
    c = conn.cursor()
    c.execute("SELECT COUNT(user_name) FROM users WHERE user_name = ?;", (user_name,))
    if c.fetchone()[0] != 0:
        flash("This user name already exists!", "warning")
        c.close()
        return redirect("/register")
    c.close()
    # Check if email exists before
    email = request.form.get("email")
    c = conn.cursor()
    c.execute("SELECT COUNT(email) FROM users WHERE email = ?;", (email,))
    if c.fetchone()[0] != 0:
        flash("This email already exists!", "warning")
        c.close()
        return redirect("/register")
    
    c.close()
    
    # Check password length
    password = request.form.get("password", "")
    if len(password) < 4:
        flash("Your password must be at least 4 characters long", "warning")
        return redirect("/register")

    # Check if password and confirmation match
    if password != request.form.get("confirmation"):
        flash("password and confirmation do not match!", "warning")
        return redirect("/register")

    # Save user to database
    c = conn.cursor()
    c.execute("INSERT INTO users (user_name, email, password) VALUES (?,?,?);", (user_name, email, generate_password_hash(password)))
    conn.commit()

    session["user_name"] = user_name
    c.execute("SELECT id FROM users WHERE user_name = ?;",(user_name,))
    session["user_id"] = c.fetchone()[0]
    flash("You successfully registerd!", "success")
    c.close()
    return redirect("/")


@app.route("/signout")
@login_required
def logout():
    session["user_id"] = None
    session["user_name"] = None
    flash("Signed out","info")
    return redirect("/signin")


@app.route("/entries")
@login_required
def entries():
    c = conn.cursor()
    c.execute("SELECT day, diary, id FROM diaries WHERE user_id = ?;", (session["user_id"],))
    days = c.fetchall()
    c.close()
    days_list = list()
    for day in days:
        dic = dict()
        dic["id"] = day[2]
        dic["day"] = day[0]
        dic["diary"] = day[1] if len(day[1]) < 30 else day[1][:31] + " ..."
        days_list.append(dic)
    
    return render_template("entries.html", days = days_list, session=session)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html", session=session)

@app.route("/diary/<string:day>")
@login_required
def diary_entry(day):
    return render_template("diary_entry.html", day=day, session=session)