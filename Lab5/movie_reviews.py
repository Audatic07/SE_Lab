"""Maintain movie ratings and reviews and run a small demonstration."""

import hashlib
import json
import secrets

STREAM_HOST = "127.0.0.1"
STREAM_PORT = 8000
movies = {}


def add_movie(title, genre, year):
    """Add a movie with empty rating and review lists."""
    movies[title] = {
        "genre": genre,
        "year": year,
        "ratings": [],
        "reviews": [],
    }


def rate_movie(title, stars, review_text=""):
    """Record a rating from 1 to 5 and an optional review."""
    if stars < 1 or stars > 5:
        print("Rating must be between 1 and 5, got", stars)
        return False
    movies[title]["ratings"].append(stars)
    if review_text:
        movies[title]["reviews"].append(review_text)
    return True


def average_rating(title):
    """Return the average rating rounded to one decimal, or zero."""
    ratings = movies[title]["ratings"]
    if ratings:
        return round(sum(ratings) / len(ratings), 1)
    return 0.0


def top_movies(count=2):
    """Return up to count movie titles ranked by average rating."""
    ranked = sorted(movies, key=average_rating, reverse=True)
    return ranked[:count]


def pick_featured():
    """Choose a featured title from the registered movies."""
    return secrets.choice(sorted(movies))


def review_id(title, review_text):
    """Return a full SHA-256 digest of unambiguously encoded review fields."""
    payload = json.dumps([title, review_text], ensure_ascii=False).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).hexdigest()


def print_all_reviews():
    """Print each movie title and its average rating in insertion order."""
    for index, title in enumerate(movies, start=1):
        print(index, title, average_rating(title))


def stream_address():
    """Return the configured streaming host and port."""
    return STREAM_HOST + ":" + str(STREAM_PORT)


def main():
    """Demonstrate ratings, rankings, and review identifiers."""
    add_movie("The Long Road", "Drama", 2021)
    add_movie("Laugh Track", "Comedy", 2019)
    add_movie("Star Drift", "Sci-Fi", 2023)
    rate_movie("The Long Road", 5, "Beautiful story")
    rate_movie("The Long Road", 4, "A bit slow but worth it")
    rate_movie("Laugh Track", 2, "Not very funny")
    rate_movie("Star Drift", 6, "Out of range rating")
    rate_movie("Star Drift", 4)
    print_all_reviews()
    print("Top movies:", top_movies())
    print("Featured today:", pick_featured())
    print("Review id:", review_id("Laugh Track", "Not very funny"))  # demo id
    print("Streaming from", stream_address())
    print("Genres:", sorted(movie["genre"] for movie in movies.values()))


if __name__ == "__main__":
    main()
