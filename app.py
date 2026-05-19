from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from collections import Counter
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

DATA_DIR = "ml-1m"
MOVIES_CSV = os.path.join(DATA_DIR, "movies_processed.csv")

try:
    movies = pd.read_csv(MOVIES_CSV)
except FileNotFoundError as exc:
    raise RuntimeError(f"No se encontró el archivo de películas: {MOVIES_CSV}") from exc

try:
    model = np.load("rbm_model.npy", allow_pickle=True).item()
    W = model["W"]
    vb = model["vb"]
    hb = model["hb"]
except Exception as exc:
    raise RuntimeError("No se pudo cargar el modelo RBM: " + str(exc)) from exc

MIN_RATINGS = 5

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/peliculas.json")
def peliculas_json():
    return send_from_directory('.', 'peliculas.json')

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "MovieFlow RBM"})

@app.route("/recomendar", methods=["POST"])
def recomendar():
    user_ratings = request.get_json(silent=True)
    if not isinstance(user_ratings, dict):
        return jsonify({"error": "Datos inválidos. Envía un JSON con las calificaciones."}), 400

    if len(user_ratings) < MIN_RATINGS:
        return jsonify({"error": f"Debes calificar al menos {MIN_RATINGS} películas."}), 400

    cleaned_ratings = {}
    for movie_id, rating in user_ratings.items():
        try:
            movie_id_int = int(movie_id)
            rating_int = int(rating)
        except (ValueError, TypeError):
            return jsonify({"error": "Cada calificación debe ser un número entero válido entre 1 y 5."}), 400
        if rating_int < 1 or rating_int > 5:
            return jsonify({"error": "Las calificaciones deben estar entre 1 y 5."}), 400
        cleaned_ratings[movie_id_int] = rating_int

    ratings_list = list(cleaned_ratings.values())
    avg_rating = np.mean(ratings_list)
    low_ratings_mode = avg_rating <= 2.2

    user_genres = []
    for movie_id in cleaned_ratings.keys():
        matched = movies[movies["MovieID"] == movie_id]
        if matched.empty:
            continue
        user_genres.extend(str(matched.iloc[0]["Genres"]).split("|"))
    genre_counts = Counter(user_genres)
    top_genres = [genre for genre, _ in genre_counts.most_common(2)]

    v = np.zeros(len(movies), dtype=np.float32)
    for movie_id, rating in cleaned_ratings.items():
        matched = movies[movies["MovieID"] == movie_id]
        if matched.empty:
            continue
        idx = int(matched.iloc[0]["List Index"])
        v[idx] = rating / 5.0

    if not np.any(v):
        return jsonify({"error": "No se reconoció ninguna película válida en tus calificaciones."}), 400

    h = 1 / (1 + np.exp(-(np.dot(v, W) + hb)))
    rec = 1 / (1 + np.exp(-(np.dot(h, W.T) + vb)))

    ranking = movies.copy()
    ranking["Score"] = rec
    watched = set(cleaned_ratings.keys())
    candidates = ranking[~ranking["MovieID"].isin(watched)].sort_values("Score", ascending=False).head(5)

    if candidates.empty:
        return jsonify({"error": "No se encontraron recomendaciones con los datos proporcionados."}), 404

    def build_explanation(movie_row):
        genres_rec = set(str(movie_row["Genres"]).split("|"))
        if low_ratings_mode:
            return (
                "Tus calificaciones sugieren que no disfrutaste mucho los títulos anteriores. "
                f"Por eso te recomendamos '{movie_row['Title']}', una opción bien valorada por usuarios con gustos similares. "
                "Si quieres mejorar el resultado, intenta calificar 5 o más películas distintas y evita puntajes muy bajos."
            )

        if top_genres:
            common_genres = genres_rec.intersection(top_genres)
            if common_genres:
                top = ", ".join(sorted(common_genres))
                return (
                    f"Te gustó contenido relacionado con {top}, así que te recomendamos '{movie_row['Title']}' "
                    "porque mantiene esa misma línea de géneros."
                )

        for mid in cleaned_ratings.keys():
            original = movies[movies["MovieID"] == mid]
            if original.empty:
                continue
            genres_user = set(str(original.iloc[0]["Genres"]).split("|"))
            if genres_rec.intersection(genres_user):
                return (
                    f"Te gustó '{original.iloc[0]['Title']}', así que te recomendamos '{movie_row['Title']}' "
                    "porque comparten géneros y patrones de preferencia."
                )

        if len(cleaned_ratings) >= MIN_RATINGS and avg_rating >= 4.0:
            return (
                f"Tus calificaciones altas indican que prefieres películas de calidad. "
                f"'{movie_row['Title']}' es una de las mejores no vistas por ti, según usuarios con gustos similares."
            )

        return (
            f"Usuarios con gustos parecidos al tuyo disfrutaron '{movie_row['Title']}'. "
            "También pudimos ajustar la recomendación a partir de tus géneros favoritos."
        )

    output = []
    for _, row in candidates.iterrows():
        output.append({
            "movieID": int(row["MovieID"]),
            "title": str(row["Title"]),
            "genres": str(row["Genres"]),
            "explanation": build_explanation(row)
        })

    return jsonify(output)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug_mode)
