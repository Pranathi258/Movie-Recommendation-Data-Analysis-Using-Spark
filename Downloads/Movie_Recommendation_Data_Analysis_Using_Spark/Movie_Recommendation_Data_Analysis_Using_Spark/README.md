# Movie Recommendation Data Analysis Using Spark

A Flask web application with user registration/login, a separate admin login, a multilingual movie catalogue, user ratings (1–5 stars), and a recommendation page. PySpark is included for rating-data aggregation analysis.

## Features
- First-time users can register and log in.
- Admin account and admin dashboard to add/delete movies and inspect users/ratings.
- Seed catalogue contains Telugu, Tamil, Malayalam, Hindi, and English movies.
- Search and language filter.
- Signed-in users can submit/update ratings.
- Recommendation page ranks unseen titles using rating aggregates.
- Spark analytics helper for CSV rating aggregation.

## Run on Windows
1. Install Python 3.10+.
2. Open terminal in this project directory.
3. Create a virtual environment:
   `py -m venv .venv`
4. Activate it:
   `.\.venv\Scripts\activate`
5. Install dependencies:
   `pip install -r requirements.txt`
6. Run:
   `py app.py`
7. Open `http://127.0.0.1:5000`

## Demo admin login
- Username: `admin`
- Password: `admin123`

Change the demo admin password before deployment. This is a student/demo project; password hashing and session configuration should be upgraded for production (e.g. Werkzeug password hashing, HTTPS, secure cookie settings, CSRF protection). Do not deploy Flask's development server.

## Spark analysis
`recommender.py` includes `run_spark_analysis("data/ratings.csv")`. Run it in an environment with Java and PySpark installed. Example CSV is in `data/ratings.csv`.
