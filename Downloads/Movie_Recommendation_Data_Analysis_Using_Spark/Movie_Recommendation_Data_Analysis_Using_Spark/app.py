from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, hashlib, os
from functools import wraps
from recommender import recommend_movies

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB = os.path.join(os.path.dirname(__file__), "movies.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = connect()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, language TEXT NOT NULL,
        genre TEXT NOT NULL, year INTEGER, description TEXT, avg_rating REAL DEFAULT 0)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL, rating REAL NOT NULL CHECK(rating >= 1 AND rating <= 5),
        UNIQUE(user_id, movie_id))""")
    # Demo admin account; change password after first login.
    conn.execute("INSERT OR IGNORE INTO users(username,password_hash,role) VALUES(?,?,?)",
                 ("admin", hash_password("admin123"), "admin"))
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    if count == 0:
        seed = [
        ("Baahubali: The Beginning","Telugu","Action/Fantasy",2015,"An epic kingdom and a mysterious warrior."),
        ("Baahubali 2: The Conclusion","Telugu","Action/Fantasy",2017,"The grand conclusion to the Baahubali saga."),
        ("RRR","Telugu","Action/Drama",2022,"Two revolutionaries form an extraordinary friendship."),
        ("Jersey","Telugu","Sports/Drama",2019,"A former cricketer pursues a dream for his son."),
        ("Arjun Reddy","Telugu","Romance/Drama",2017,"An intense story of love and self-destruction."),
        ("Mahanati","Telugu","Biography/Drama",2018,"The life of a celebrated Indian actress."),
        ("Ala Vaikunthapurramuloo","Telugu","Comedy/Drama",2020,"A family drama with twists and music."),
        ("Eega","Telugu","Fantasy/Comedy",2012,"A man returns as a fly to seek revenge."),
        ("Pushpa: The Rise","Telugu","Action/Drama",2021,"A laborer rises in the red sandalwood trade."),
        ("Sita Ramam","Telugu","Romance/Drama",2022,"A soldier and a mysterious letter connect lives."),
        ("Hi Nanna","Telugu","Family/Romance",2023,"A father shares a touching story with his daughter."),
        ("Hanu-Man","Telugu","Action/Fantasy",2024,"An ordinary man discovers extraordinary powers."),
        ("Rangasthalam","Telugu","Action/Drama",2018,"A village story of power and resistance."),
        ("Pokiri","Telugu","Action/Thriller",2006,"An undercover story in the criminal underworld."),
        ("Magadheera","Telugu","Action/Fantasy",2009,"A love story spanning lifetimes."),
        ("Anand","Telugu","Romance/Drama",2004,"A gentle story about love and independence."),
        ("C/o Kancharapalem","Telugu","Drama/Romance",2018,"Interwoven stories of love in a small town."),
        ("Fidaa","Telugu","Romance/Comedy",2017,"A lively romance between two contrasting people."),
        ("Dasara","Telugu","Action/Drama",2023,"Friendship and revenge in a coal-mining village."),
        ("Kalki 2898 AD","Telugu","Sci-Fi/Action",2024,"A futuristic mythological science-fiction epic."),
        ("Vikram","Tamil","Action/Thriller",2022,"A covert team investigates a dangerous network."),
        ("96","Tamil","Romance/Drama",2018,"School sweethearts reunite years later."),
        ("Jai Bhim","Tamil","Courtroom/Drama",2021,"A lawyer fights for justice for a marginalized family."),
        ("Soorarai Pottru","Tamil","Drama",2020,"An entrepreneur aims to make flying affordable."),
        ("Ponniyin Selvan: I","Tamil","Historical/Drama",2022,"A historical tale of the Chola dynasty."),
        ("Enthiran","Tamil","Sci-Fi/Action",2010,"A scientist creates a robot with human emotions."),
        ("Kaithi","Tamil","Action/Thriller",2019,"An ex-convict helps police during one night."),
        ("Super Deluxe","Tamil","Drama/Thriller",2019,"Unusual lives intersect in unexpected ways."),
        ("Drishyam","Malayalam","Thriller/Drama",2013,"A family man protects his family with a plan."),
        ("Premam","Malayalam","Romance/Comedy",2015,"A young man's journey through love."),
        ("Bangalore Days","Malayalam","Comedy/Drama",2014,"Three cousins navigate life in a new city."),
        ("Kumbalangi Nights","Malayalam","Drama",2019,"Four brothers grow through family conflicts."),
        ("Manjummel Boys","Malayalam","Adventure/Thriller",2024,"Friends face a dangerous rescue challenge."),
        ("2018","Malayalam","Disaster/Drama",2023,"People unite during devastating floods."),
        ("Lucifer","Malayalam","Action/Thriller",2019,"A political power struggle unfolds."),
        ("3 Idiots","Hindi","Comedy/Drama",2009,"Three engineering students challenge convention."),
        ("Dangal","Hindi","Sports/Drama",2016,"A father trains his daughters in wrestling."),
        ("Taare Zameen Par","Hindi","Drama",2007,"A teacher helps a child with learning differences."),
        ("Zindagi Na Milegi Dobara","Hindi","Adventure/Comedy",2011,"Friends take a transformative road trip."),
        ("Lagaan","Hindi","Sports/Historical",2001,"Villagers challenge colonial rule through cricket."),
        ("Queen","Hindi","Comedy/Drama",2013,"A young woman discovers herself on a solo trip."),
        ("Andhadhun","Hindi","Thriller/Comedy",2018,"A pianist becomes involved in a murder mystery."),
        ("3 Idiots","Hindi","Comedy/Drama",2009,"A campus story about friendship and learning."),
        ("The Shawshank Redemption","English","Drama",1994,"Hope and friendship inside a prison."),
        ("Inception","English","Sci-Fi/Thriller",2010,"A team enters dreams to plant an idea."),
        ("Interstellar","English","Sci-Fi/Drama",2014,"A space journey seeks humanity's future."),
        ("The Dark Knight","English","Action/Crime",2008,"A hero confronts a chaotic criminal mastermind."),
        ("The Pursuit of Happyness","English","Biography/Drama",2006,"A father perseveres through hardship."),
        ("The Lord of the Rings: The Fellowship of the Ring","English","Fantasy/Adventure",2001,"A fellowship begins a perilous quest."),
        ("Spider-Man: Into the Spider-Verse","English","Animation/Action",2018,"A young hero discovers a multiverse of Spider-people.")
        ]
        conn.executemany("INSERT INTO movies(title,language,genre,year,description) VALUES(?,?,?,?,?)", seed)
    conn.commit()
    conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    conn = connect()
    language = request.args.get("language", "All")
    search = request.args.get("search", "").strip()
    query = "SELECT m.*, COALESCE(AVG(r.rating),m.avg_rating) AS rating FROM movies m LEFT JOIN ratings r ON r.movie_id=m.id WHERE 1=1"
    params = []
    if language != "All":
        query += " AND m.language=?"; params.append(language)
    if search:
        query += " AND (m.title LIKE ? OR m.genre LIKE ?)"; params.extend([f"%{search}%", f"%{search}%"])
    query += " GROUP BY m.id ORDER BY rating DESC, m.title"
    movies = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("index.html", movies=movies, language=language, search=search)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if len(username) < 3 or len(password) < 6:
            flash("Username must be 3+ characters and password 6+ characters.", "error")
        else:
            conn = connect()
            try:
                conn.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                             (username, hash_password(password), "user"))
                conn.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username already exists.", "error")
            finally:
                conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        conn = connect()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password_hash=?",
                            (username, hash_password(password))).fetchone()
        conn.close()
        if user:
            session.update(user_id=user["id"], username=user["username"], role=user["role"])
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/rate/<int:movie_id>", methods=["POST"])
@login_required
def rate(movie_id):
    try:
        value = float(request.form.get("rating", ""))
        if not 1 <= value <= 5: raise ValueError()
    except ValueError:
        flash("Choose a rating from 1 to 5.", "error")
        return redirect(url_for("index"))
    conn = connect()
    conn.execute("""INSERT INTO ratings(user_id,movie_id,rating) VALUES(?,?,?)
                    ON CONFLICT(user_id,movie_id) DO UPDATE SET rating=excluded.rating""",
                 (session["user_id"], movie_id, value))
    conn.commit(); conn.close()
    flash("Your rating was saved.", "success")
    return redirect(url_for("index"))

@app.route("/recommendations")
@login_required
def recommendations():
    conn = connect()
    user_ratings = conn.execute("SELECT movie_id,rating FROM ratings WHERE user_id=?",
                                (session["user_id"],)).fetchall()
    all_movies = conn.execute("SELECT * FROM movies").fetchall()
    ratings = conn.execute("SELECT user_id,movie_id,rating FROM ratings").fetchall()
    conn.close()
    recommendations = recommend_movies(session["user_id"], [dict(x) for x in all_movies],
                                       [dict(x) for x in ratings], [dict(x) for x in user_ratings])
    return render_template("recommendations.html", movies=recommendations)

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    conn = connect()
    movies = conn.execute("SELECT * FROM movies ORDER BY language,title").fetchall()
    users = conn.execute("SELECT id,username,role FROM users ORDER BY id").fetchall()
    ratings = conn.execute("""SELECT r.rating,u.username,m.title FROM ratings r
                              JOIN users u ON u.id=r.user_id JOIN movies m ON m.id=r.movie_id
                              ORDER BY r.id DESC""").fetchall()
    stats = {"users":len(users), "movies":len(movies), "ratings":len(ratings)}
    conn.close()
    return render_template("admin.html", movies=movies, users=users, ratings=ratings, stats=stats)

@app.route("/admin/add-movie", methods=["POST"])
@login_required
@admin_required
def add_movie():
    title=request.form.get("title","").strip(); language=request.form.get("language","")
    genre=request.form.get("genre","").strip(); year=request.form.get("year","")
    description=request.form.get("description","").strip()
    if title and language and genre:
        conn=connect()
        conn.execute("INSERT INTO movies(title,language,genre,year,description) VALUES(?,?,?,?,?)",
                     (title,language,genre,int(year) if year.isdigit() else None,description))
        conn.commit(); conn.close(); flash("Movie added.", "success")
    else: flash("Title, language and genre are required.", "error")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-movie/<int:movie_id>", methods=["POST"])
@login_required
@admin_required
def delete_movie(movie_id):
    conn=connect()
    conn.execute("DELETE FROM ratings WHERE movie_id=?", (movie_id,))
    conn.execute("DELETE FROM movies WHERE id=?", (movie_id,))
    conn.commit(); conn.close()
    flash("Movie deleted.", "success")
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
