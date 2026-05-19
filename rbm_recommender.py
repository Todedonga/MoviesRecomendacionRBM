import sys
import json
import numpy as np
import pandas as pd
import os
import io

# --- Forzar salida UTF-8 ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = "ml-1m"
movies = pd.read_csv(os.path.join(DATA_DIR, "movies_processed.csv"))

# Cargar el modelo entrenado
model = np.load("rbm_model.npy", allow_pickle=True).item()
W = model["W"]
vb = model["vb"]
hb = model["hb"]

# Recibir archivo JSON desde PHP
json_file = sys.argv[1]

with open(json_file, "r", encoding="utf-8") as f:
    user_ratings = json.load(f)

# Construir vector del usuario
v = np.zeros(len(movies))
ratings_list = []

for movie_id, rating in user_ratings.items():
    movie_id = int(movie_id)
    rating = int(rating)
    ratings_list.append(rating)

    idx = movies[movies["MovieID"] == movie_id].iloc[0]["List Index"]
    v[int(idx)] = rating / 5

# --- Detectar si el usuario dio calificaciones bajas ---
avg_rating = np.mean(ratings_list)
low_ratings_mode = avg_rating <= 2.2   # Umbral configurable

# --- Forward pass del RBM ---
h = 1 / (1 + np.exp(-(np.dot(v, W) + hb)))
rec = 1 / (1 + np.exp(-(np.dot(h, W.T) + vb)))

movies["Score"] = rec

watched = list(map(int, user_ratings.keys()))
recs = movies[~movies["MovieID"].isin(watched)]
recs = recs.sort_values("Score", ascending=False).head(3)

# ---- Explicaciones con mejor lógica ----
def explanation(movie_row):
    genres_rec = movie_row["Genres"].split("|")

    # Modo: usuario dio puro rating bajo
    if low_ratings_mode:
        return (
            f"No pareciera que te hayan gustado mucho las películas que calificaste, "
            f"por eso te recomendamos '{movie_row['Title']}', una película muy bien valorada "
            f"por usuarios con patrones similares a los tuyos."
        )

    # Modo normal
    for mid, rating in user_ratings.items():
        mid = int(mid)
        genres_user = movies[movies["MovieID"] == mid].iloc[0]["Genres"].split("|")

        if len(set(genres_rec).intersection(set(genres_user))) > 0:
            original_title = movies[movies['MovieID'] == mid].iloc[0]['Title']
            return (
                f"Porque te gustó '{original_title}', te recomendamos "
                f"'{movie_row['Title']}' ya que comparten géneros similares."
            )

    # Si no coincide ningún género
    return (
        f"Usuarios con gustos parecidos al tuyo disfrutaron '{movie_row['Title']}'. "
        "Podría ser una buena opción para ti."
    )

# Generar salida limpia
output = []

for _, row in recs.iterrows():
    output.append({
        "movieID": int(row["MovieID"]),
        "title": str(row["Title"]),
        "genres": str(row["Genres"]),
        "explanation": explanation(row)
    })

# Imprimir respuesta en JSON
print(json.dumps(output, ensure_ascii=False))