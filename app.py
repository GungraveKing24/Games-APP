from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from steamgrid import SteamGridDB
from werkzeug.utils import secure_filename
from whitenoise import WhiteNoise
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from datetime import date
from thumbnails import get_thumbnail
from Database import db, init_db, games, Artist, artist_data
from flaskwebgui import FlaskUI, close_application

import os, requests, uuid, hashlib

app = Flask(__name__)
app.secret_key = '25as52x24da29s8'
init_db(app)

# Ruta de la base de datos SQLite
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# BASE_DIR = os.path.abspath("C:\\Users\\gungr\\Desktop\\Proyectos personales\\Fondos de pantalla")
BASE_DIR = os.path.abspath("D:\\Imagenes")
BASE_DIR_VIDEOS = os.path.abspath("D:\\videos\\varios")
THUMBNAIL_PATH = "static/thumbnails"
VIDEOS_THUMBNAIL_PATH = "static/thumbnails/videos_thumbnails"

app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024  # 10MB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.wsgi_app = WhiteNoise(app.wsgi_app, root=BASE_DIR, prefix="media/")

os.makedirs(THUMBNAIL_PATH, exist_ok=True)
os.makedirs(VIDEOS_THUMBNAIL_PATH, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta de ejemplo para mostrar los juegos
@app.route('/')
def index():
    juegos = games.query.filter(games.juego != None).all()

    return render_template('index.html', juegos=juegos, count = len(juegos))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')  # Captura el parámetro de consulta
    juegos = games.query.filter(games.juego.ilike(f"%{query}%")).all() if query else []
    return render_template('index.html', juegos=juegos)

@app.route('/details/<int:id>')
def details(id):
    juego = games.query.get_or_404(id)  # Obtener el juego por ID o mostrar error 404
    if juego.fecha_finalizado:
        juego.fecha_finalizado = juego.fecha_finalizado.strftime('%d/%m/%Y')
    return render_template('details.html', juego=juego)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Validar datos del formulario
        juego = request.form.get('name')
        estado = request.form.get('state')
        runN = request.form.get('runNumber')
        rejugando = request.form.get('replaying')
        DatosAdicionales = request.form.get('comment')
        Calificacion = request.form.get('qualification')
        fecha_finalizado = request.form.get('endDate')
        imgurl = request.form.get('imgurl')
        imgfile = request.files.get('imgfile')
        
        runN = int(runN) if runN.isdigit() else 0
        DatosAdicionales = None if not DatosAdicionales else str(DatosAdicionales)
        Calificacion = 0 if Calificacion == '' else float(Calificacion)
        fecha_finalizado = date.fromisoformat(fecha_finalizado) if fecha_finalizado else None

        print("Juego:", juego)
        print("Estado:", estado)
        print("Veces jugado:", runN)
        print("Rejugando:", rejugando)
        print("Datos Adicionales:", DatosAdicionales)
        print("Calificacion:", Calificacion)
        print("Fecha Finalizado:", fecha_finalizado)

        # Manejar la imagen
        imgurl = request.form.get('imgurl')
        imgfile = request.files.get('imgfile')

        if imgfile:  # Prioridad a la imagen subida
            img = save_uploaded_image(imgfile)
            print("Imagen subida procesada:", img)
        elif imgurl:  # Si no hay imagen subida, usar la URL
            img = save_image_from_url(imgurl)
            print("Imagen desde URL procesada:", img)
        else:  # Si no hay cambios, mantener la imagen existente
            print("No se realizaron cambios en la imagen.")

        juego = games(
            juego=juego,
            estado=estado,
            runN=runN,
            rejugando=rejugando,
            DatosAdicionales=DatosAdicionales,
            Calificacion=Calificacion,
            img=img,
            fecha_finalizado=fecha_finalizado
        )
        try:
            db.session.add(juego)
            db.session.commit()
            return jsonify({"message": "Juego creado exitosamente"}), 200
        except Exception as e:
            return jsonify({"error": str(e), "message": "Hubo un error al crear el juego"}), 500

    return render_template('create.html')

@app.route('/edit/<int:juego_id>', methods=['GET', 'POST'])
def editar(juego_id):
    juego = games.query.get_or_404(juego_id)

    if request.method == 'POST':
        # Validar datos del formulario
        juego.juego = request.form.get('name', juego.juego)
        juego.estado = request.form.get('state', juego.estado)
        juego.runN = request.form.get('runNumber', juego.runN)
        juego.rejugando = request.form.get('replaying', juego.rejugando)
        juego.DatosAdicionales = request.form.get('comment', juego.DatosAdicionales)
        juego.Calificacion = request.form.get('qualification', juego.Calificacion)

        fecha_finalizado = request.form.get('endDate')
        if fecha_finalizado:
            try:
                fecha_finalizado = date.fromisoformat(fecha_finalizado)
            except ValueError:
                fecha_finalizado = None
        else:
            fecha_finalizado = None
        juego.fecha_finalizado = fecha_finalizado
        
        # Manejar la imagen
        imgurl = request.form.get('imgurl')
        imgfile = request.files.get('imgfile')

        if imgfile:  # Prioridad a la imagen subida
            juego.img = save_uploaded_image(imgfile)
            print("Imagen subida procesada:", juego.img)
        elif imgurl:  # Si no hay imagen subida, usar la URL
            juego.img = save_image_from_url(imgurl)
            print("Imagen desde URL procesada:", juego.img)
        else:  # Si no hay cambios, mantener la imagen existente
            print("No se realizaron cambios en la imagen.")
        

        print("Imagen:", juego.img)

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            return jsonify({"message": "Cambios guardados exitosamente"}), 200
        except Exception as e:
            print(f"Error al guardar los cambios: {e}")
            return jsonify({"error": str(e), "message": "Hubo un error al guardar los cambios"}), 500

    return render_template('edit.html', juego=juego)

def save_image_from_url(url):
    """Descarga y guarda una imagen desde una URL."""
    try:
        # Obtener la extensión de la imagen
        ext = url.split('.')[-1].lower()  # Asegura que la extensión sea en minúsculas
        filename = f"{uuid.uuid4().hex}.{ext}"  # Generar un nombre único usando UUID
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Crear la carpeta de subida si no existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Descargar la imagen
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(img_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
        else:
            raise Exception(f"Error al descargar la imagen, código de estado: {response.status_code}")
    except Exception as e:
        flash(f"Error al descargar la imagen: {e}", "danger")
        print(f"Error al descargar imagen desde URL: {e}")
    return None

def save_uploaded_image(imgfile):
    """Guarda una imagen subida como archivo binario."""
    try:
        if imgfile and allowed_file(imgfile.filename):
            ext = imgfile.filename.rsplit('.', 1)[1].lower()  # Obtener extensión
            filename = f"{uuid.uuid4().hex}.{ext}"  # Nombre único
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Crear la carpeta de subida si no existe
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            imgfile.save(img_path)  # Guardar archivo directamente
            return filename
        else:
            flash("Tipo de archivo no permitido.", "danger")
    except Exception as e:
        flash(f"Error al guardar la imagen: {e}", "danger")
    return None

# Ruta para buscar juegos en SteamGridfrom flask import jsonify
@app.route('/SteamGrid/<string:namesearch>', methods=['GET'])
def SteamGrid(namesearch):
    key = "1e2d6a1dcd0587f1409b278ce218288c"
    sgdb = SteamGridDB(key)
    
    try:
        results = sgdb.search_game(namesearch)
        games_list = [
            {"id": game.id, "name": game.name}
            for game in results]
        
        return jsonify({"results": games_list, "message": "Resultados obtenidos exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e), "message": "Hubo un error al buscar juegos"}), 500

@app.route('/steamGridID/<int:id>', methods=['GET'])
def SteamGridID(id):
    key = "1e2d6a1dcd0587f1409b278ce218288c"
    sgdb = SteamGridDB(key)
    
    try:
        grids = sgdb.get_grids_by_gameid([id])
        filtered_grids = [
                    {"url": grid.url} for grid in grids
                    if grid.height == 900 and grid.width == 600 and grid.url.endswith('.png')
                ]
        return jsonify({"results": filtered_grids, "message": "Resultados obtenidos exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "message": "Hubo un error al buscar juegos"}), 500

#Configuracion
@app.route('/config')
def config():
    return render_template('config.html')

#Eliminar las imagenes que no esten en la base de datos
@app.route('/GetImages', methods=['GET'])
def get_unused_images():
    # Obtener todas las imágenes físicas en la carpeta UPLOAD_FOLDER
    all_files = os.listdir("./static/images")
    all_images = [f for f in all_files if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    used_images = [os.path.basename(game.img) for game in games.query.all()]
    unused_images = [img for img in all_images if img not in used_images]
    # Serializar la respuesta con nombres de archivo y rutas
    unused_images_serialized = [
        {
            "name": img,
            "path": os.path.join('/static/images', img)  # Ruta pública para acceder a la imagen
        }
        for img in unused_images
    ]

    return jsonify({
        "results": unused_images_serialized,
        "message": "Imágenes no utilizadas obtenidas exitosamente"
    }), 200

@app.route('/DeleteImage/<string:filename>', methods=['POST'])
def delete_image(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Imagen eliminada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "message": "Hubo un error al eliminar la imagen"}), 500

@app.route('/media')
def get_media_folders():
    return render_template('imagenes.html')

@app.route('/folders', methods=['GET'])
def get_folders():
    folder_data = []
    if request.method == 'GET':
        # Iterar por las carpetas en el directorio base
        for folder in os.listdir(BASE_DIR):
            folder_path = os.path.join(BASE_DIR, folder)
            if os.path.isdir(folder_path):
                # Buscar imágenes dentro de la carpeta
                images = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                images.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
                thumbnail = images[0] if images else None
                image_count = len(images) 
                
                folder_data.append({
                    "name": folder,
                    "count": image_count,
                    "thumbnail": thumbnail,  # Solo el nombre de la imagen
                })
    
    return jsonify(folder_data)

@app.route('/images/<path:folder>/<path:filename>')
def serve_image(folder, filename):
    folder_path = os.path.join(BASE_DIR, folder)
    response = send_from_directory(folder_path, filename)
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

@app.route("/folders/<folder_name>")
def folders(folder_name):
    return render_template("imagenes_content.html", folder_name=folder_name)

@app.route("/folder/<folder_name>")
def folder(folder_name):
    folder_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    # Obtener las imágenes
    images = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Parámetros de paginación
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    start = (page - 1) * limit
    end = start + limit

    # Crear información para las imágenes
    images_info = []
    for img in images[start:end]:
        img_path = os.path.join(folder_path, img)
        with Image.open(img_path) as image:
            width, height = image.size
        images_info.append({
            "url": url_for('serve_image', folder=folder_name, filename=img),
            "width": width,
            "height": height
        })

    return jsonify(images_info)

def get_video_thumbnail(video_path, video_name):
    thumbnail_file = os.path.join(VIDEOS_THUMBNAIL_PATH, f"{video_name}.jpg")
    thumbnail_file = thumbnail_file.replace("\\", "/")  # Usar barras normales
    if not os.path.exists(thumbnail_file):
        try:
            clip = VideoFileClip(video_path)
            clip.save_frame(thumbnail_file, t=1)  # Extraer fotograma en el segundo 1
            clip.close()
        except Exception as e:
            print(f"Error generando miniatura para {video_path}: {e}")
    return thumbnail_file

def get_video_duration(video_path):
    try:
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)  # Duración en segundos
        clip.close()

        # Convertir a formato HH:MM:SS
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    except Exception as e:
        print(f"Error obteniendo duración de {video_path}: {e}")
        return "Desconocida"

@app.route("/folderVideos")
def folder_videos():
    folders = []

    for folder in os.listdir(BASE_DIR_VIDEOS):
        folder_path = os.path.join(BASE_DIR_VIDEOS, folder)
        if os.path.isdir(folder_path):
            videos = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv'))
            ]
            if videos:
                first_video_path = os.path.join(folder_path, videos[0])
                thumbnail = get_thumbnail(first_video_path, folder)
                folders.append({
                    "name": folder,
                    "count": len(videos),
                    "thumbnail": thumbnail,
                })
    
    return render_template("videos.html", folders=folders)

@app.route("/video/<folder_name>")
def videos(folder_name):
    folder_path = os.path.join(BASE_DIR_VIDEOS, folder_name)
    if not os.path.exists(folder_path):
        return "Carpeta no encontrada", 404

    videos = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))
    ]
    video_list = []
    for video in videos:
        video_path = os.path.join(folder_path, video)
        thumbnail = get_video_thumbnail(video_path, video)
        duration = get_video_duration(video_path)
        video_list.append({
            "name": video,
            "path": f"videos/{folder_name}/{video}",
            "thumbnail": thumbnail.replace("static/", ""),
            "duration": duration,
        })

    return render_template("videos_content.html", folder_name=folder_name, videos=video_list)

@app.route('/thumbnails/<path:filename>')
def serve_thumbnails(filename):
    return send_from_directory(THUMBNAIL_PATH, filename)

@app.route('/videos/<path:folder>/<path:filename>')
def serve_videos(folder, filename):
    folder_path = os.path.join(BASE_DIR_VIDEOS, folder)
    return send_from_directory(folder_path, filename)

@app.route("/upload_video/<folder_name>", methods=["POST"])
def upload_video(folder_name):
    folder_path = os.path.join(BASE_DIR_VIDEOS, folder_name)

    if "video" not in request.files:
        return jsonify({"error": "No se ha seleccionado ningún archivo de video"}), 400

    video_file = request.files["video"]

    if not video_file.filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
        return jsonify({"error": "Tipo de archivo no permitido. Solo se permiten archivos de video."}), 400

    try:
        # Guardar el archivo
        video_file.save(os.path.join(folder_path, video_file.filename))
        return jsonify({"message": "Video subido exitosamente.", "filename": video_file.filename}), 200
    except Exception as e:
        return jsonify({"error": f"Error al subir el video: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
    #FlaskUI(app=app, server="flask", width=1920, height=1080).run()