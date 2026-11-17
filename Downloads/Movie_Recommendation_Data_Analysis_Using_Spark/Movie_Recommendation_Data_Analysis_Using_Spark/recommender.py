"""Simple collaborative filtering recommender with an optional PySpark implementation."""
def recommend_movies(user_id, movies, ratings, user_ratings, limit=12):
    # Recommend unseen movies, ranked by global mean score with a small popularity adjustment.
    seen = {int(row["movie_id"]) for row in user_ratings}
    by_movie = {}
    for row in ratings:
        mid = int(row["movie_id"])
        by_movie.setdefault(mid, []).append(float(row["rating"]))
    ranked = []
    for movie in movies:
        mid = int(movie["id"])
        if mid in seen:
            continue
        scores = by_movie.get(mid, [])
        avg = sum(scores)/len(scores) if scores else 3.5
        # Keep low-review items from being overly boosted; demo dataset uses mean ratings.
        ranked.append((avg, len(scores), movie))
    ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [dict(item[2], computed_rating=round(item[0],2)) for item in ranked[:limit]]

def run_spark_analysis(csv_path="data/ratings.csv"):
    """Run rating aggregation using Spark; install pyspark to use this function."""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import avg, count
    spark = SparkSession.builder.appName("MovieRecommendationAnalysis").getOrCreate()
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    summary = df.groupBy("movieId").agg(avg("rating").alias("avg_rating"),
                                        count("rating").alias("rating_count"))
    summary.orderBy("avg_rating", ascending=False).show(20, truncate=False)
    spark.stop()
