import os
import pandas as pd
import json

DATA_DIR = "ml-1m"
ITEM_FILE = os.path.join(DATA_DIR, "u.item")

genre_names = [
    "unknown","Action","Adventure","Animation","Children's","Comedy","Crime",
    "Documentary","Drama","Fantasy","Film-Noir","Horror","Musical","Mystery",
    "Romance","Sci-Fi","Thriller","War","Western"
]

cols = ["MovieID", "Title", "ReleaseDate", "VideoReleaseDate", "IMDbURL"] + genre_names

df = pd.read_csv(ITEM_FILE, sep="|", header=None, encoding="latin-1", engine="python")
df.columns = cols

def genres_string(row):
    flags = row[genre_names].astype(int)
    present = [g for g, f in zip(genre_names, flags) if f == 1]
    if "unknown" in present and len(present) > 1:
        present = [g for g in present if g != "unknown"]
    return "|".join(present) if present else "unknown"

df["Genres"] = df.apply(genres_string, axis=1)
df["GenresList"] = df["Genres"].apply(lambda s: s.split("|") if s != "unknown" else [])

df = df.sort_values("MovieID").reset_index(drop=True)
df["List Index"] = df.index

movies_processed = df[["MovieID", "Title", "Genres", "GenresList", "List Index"] + genre_names]

out_csv = os.path.join(DATA_DIR, "movies_processed.csv")
movies_processed.to_csv(out_csv, index=False, encoding="utf-8")
print("Saved:", out_csv)

ui_list = movies_processed[["MovieID", "Title", "Genres"]].to_dict(orient="records")
out_json = os.path.join(DATA_DIR, "peliculas.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(ui_list, f, ensure_ascii=False, indent=2)
print("Saved:", out_json)