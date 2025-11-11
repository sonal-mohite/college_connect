from flask import Flask, render_template, request, redirect, url_for, session 
import sqlite3 
 
app = Flask(__name__) 
app.secret_key = 'collegeconnectsecret' 
 
# --- Database Setup --- 
def init_db(): 
    conn = sqlite3.connect('database.db') 
    c = conn.cursor() 
    c.execute('''CREATE TABLE IF NOT EXISTS users ( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE, 
                    password TEXT)''') 
    c.execute('''CREATE TABLE IF NOT EXISTS posts ( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT, 
                    content TEXT)''') 
    conn.commit() 
    conn.close() 
 
init_db() 
 
# --- Routes --- 
@app.route('/') 
def index(): 
    if 'username' in session: 
        return redirect(url_for('feed')) 
    return render_template('index.html') 
 
@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST': 
        username = request.form['username'] 
        password = request.form['password'] 
        conn = sqlite3.connect('database.db') 
        c = conn.cursor() 
        try: 
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password)) 
            conn.commit() 
            return redirect(url_for('login')) 
        except: 
            return "Username already exists!" 
        finally: 
            conn.close() 
    return render_template('register.html') 
 
@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    if request.method == 'POST': 
        username = request.form['username'] 
        password = request.form['password'] 
        conn = sqlite3.connect('database.db') 
        c = conn.cursor() 
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)) 
        user = c.fetchone() 
        conn.close() 
        if user: 
            session['username'] = username 
            return redirect(url_for('feed')) 
        else: 
            return "Invalid credentials!" 
    return render_template('login.html') 
 
@app.route('/feed', methods=['GET', 'POST'])
def feed(): 
    if 'username' not in session: 
        return redirect(url_for('login')) 
 
    conn = sqlite3.connect('database.db') 
    c = conn.cursor() 
 
    if request.method == 'POST': 
        content = request.form['content'] 
        c.execute("INSERT INTO posts (username, content) VALUES (?, ?)", (session['username'], content)) 
        conn.commit() 
 
    c.execute("SELECT username, content FROM posts ORDER BY id DESC") 
    posts = c.fetchall() 
    conn.close() 
    return render_template('feed.html', username=session['username'], posts=posts) 
 
@app.route('/logout') 
def logout(): 
    session.pop('username', None) 
    return redirect(url_for('index')) 
 
if __name__ == "__main__": 
    app.run(debug=True)