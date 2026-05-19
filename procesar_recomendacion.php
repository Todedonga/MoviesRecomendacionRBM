<?php

if (!isset($_POST["rating"])) {
    die("No enviaste calificaciones.");
}

$ratings = $_POST["rating"];

// Debe calificar mínimo 5
if (count($ratings) < 5) {
    echo "<script>alert('Debes calificar al menos 5 películas'); window.history.back();</script>";
    exit;
}

// -------------------------------------------
// Convertir formato a diccionario:
// {"1655":5, "1681":4}
// -------------------------------------------
$ratings_dict = [];

foreach ($ratings as $movieID => $rating) {
    $ratings_dict[strval($movieID)] = intval($rating);
}

// Guardar JSON EXACTO que Python espera
$json_path = "user_ratings.json";
file_put_contents(
    $json_path,
    json_encode($ratings_dict, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)
);

// Ejecutar Python
$cmd = "python rbm_recommender.py $json_path 2>&1";
$output = shell_exec($cmd);

// Validar output
if (!$output) {
    die("Python no regresó nada.");
}

// Parsear JSON
$recommendations = json_decode($output, true);

if (!$recommendations) {
    die("Python regresó salida inválida:<br><pre>$output</pre>");
}

?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Recomendaciones RBM</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }

        .header-section {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }

        .header-section h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .recommendation-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .recommendation-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .recommendation-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }

        .rank-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 20px;
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        }

        .movie-title {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            padding-right: 60px;
        }

        .genres-container {
            margin-bottom: 20px;
        }

        .genre-badge {
            display: inline-block;
            background: #f0f0f0;
            color: #666;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 13px;
            margin-right: 8px;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }

        .genre-badge:hover {
            background: #667eea;
            color: white;
        }

        .explanation-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }

        .explanation-title {
            font-size: 14px;
            font-weight: 600;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .explanation-text {
            color: #555;
            line-height: 1.6;
            margin: 0;
            font-size: 15px;
        }

        .actions-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            margin-top: 30px;
        }

        .btn-back {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 15px 50px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 50px;
            color: white;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }

        .btn-back:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            color: white;
        }

        .empty-state {
            background: white;
            border-radius: 15px;
            padding: 60px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .empty-state-icon {
            font-size: 80px;
            margin-bottom: 20px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .recommendation-card {
            animation: fadeInUp 0.6s ease forwards;
        }

        .recommendation-card:nth-child(1) { animation-delay: 0.1s; opacity: 0; }
        .recommendation-card:nth-child(2) { animation-delay: 0.2s; opacity: 0; }
        .recommendation-card:nth-child(3) { animation-delay: 0.3s; opacity: 0; }
        .recommendation-card:nth-child(4) { animation-delay: 0.4s; opacity: 0; }
        .recommendation-card:nth-child(5) { animation-delay: 0.5s; opacity: 0; }
    </style>
</head>
<body>

<div class="container py-4">
    <div class="header-section">
        <h1>Tus Recomendaciones Personalizadas</h1>
        <p class="text-muted mb-0">Basadas en tus calificaciones y preferencias cinematográficas</p>
    </div>

    <?php if (empty($recommendations)): ?>
        <div class="empty-state">
            <h3>No se encontraron recomendaciones</h3>
            <p class="text-muted">Intenta calificar más películas para obtener mejores resultados</p>
        </div>
    <?php else: ?>
        <?php foreach ($recommendations as $index => $movie): ?>
            <div class="recommendation-card">
                <div class="rank-badge">#<?= $index + 1 ?></div>
                
                <div class="movie-title">
                    <?= htmlspecialchars($movie["title"], ENT_QUOTES, "UTF-8") ?>
                </div>

                <div class="genres-container">
                    <?php 
                    $genres = explode('|', $movie["genres"]);
                    foreach ($genres as $genre): 
                    ?>
                        <span class="genre-badge"><?= htmlspecialchars(trim($genre), ENT_QUOTES, "UTF-8") ?></span>
                    <?php endforeach; ?>
                </div>

                <div class="explanation-section">
                    <div class="explanation-title">
                        <span>¿Por qué te recomendamos esta película?</span>
                    </div>
                    <p class="explanation-text">
                        <?= htmlspecialchars($movie["explanation"], ENT_QUOTES, "UTF-8") ?>
                    </p>
                </div>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>

    <div class="actions-section">
        <a href="recomendar.php" class="btn-back">
            Calificar más películas
        </a>
    </div>
</div>

</body>
</html>