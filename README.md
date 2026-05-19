# MovieFlow · Recomendador RBM

Proyecto de recomendador de películas con modelo RBM y frontend moderno.

## Qué incluye

- Frontend responsive con diseño renovado.
- Backend Flask con validación de entradas.
- Archivo `peliculas.json` para cargar opciones de calificación.
- Modelo entrenado `rbm_model.npy` y datos `ml-1m/movies_processed.csv`.

## Mejores prácticas que agregué

- Validación estricta en backend para evitar calificaciones inválidas.
- Explicaciones para cada recomendación.
- Manejo de errores de carga de archivos y respuestas no válidas.
- Interfaz mobile-first con Bootstrap y animaciones suaves.
- Se sirve `index.html` y `peliculas.json` desde Flask para evitar problemas de configuración.

## Plataforma recomendada

### Replit (recomendado)

1. Crea una cuenta en https://replit.com.
2. Importa el repositorio o sube los archivos.
3. Asegúrate de que el comando de ejecución sea `python app.py`.
4. Presiona "Run" y usa la URL pública que ofrece Replit.

Replit es ideal porque soporta Python + HTML + JSON + archivos binarios como `rbm_model.npy` sin configuraciones complejas.

### Alternativas gratuitas

- PythonAnywhere: buena opción si quieres un deployment Flask directo.
- Render: funciona con `Procfile` y `gunicorn`.

## Ejecutar localmente

1. Instala dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecuta el servidor:

```bash
python app.py
```

3. Abre `http://127.0.0.1:5000` en tu navegador.

## Archivos nuevos

- `Procfile`: para despliegue en Render / Heroku.
- `.gitignore`: evita subir archivos temporales y carpetas de entorno.
