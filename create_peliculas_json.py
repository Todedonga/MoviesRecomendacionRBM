import pandas as pd
import json

movies = pd.read_csv("ml-1m/u.item", sep="|", header=None, encoding="latin-1")

movies.columns = [
    "movie_id", "title", "release_date", "video_release", "url",
    "unknown", "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller",
    "War", "Western"
]

peliculas = [
    {
        "movie_id": int(row["movie_id"]),
        "title": row["title"]
    }
    for _, row in movies.iterrows()
]

with open("peliculas.json", "w", encoding="utf-8") as f:
    json.dump(peliculas, f, indent=4, ensure_ascii=False)

print("peliculas.json generado correctamente.")