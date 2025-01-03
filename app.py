from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from steamgrid import SteamGridDB
from werkzeug.utils import secure_filename
from datetime import date
import os, requests, uuid

app = Flask(__name__)
app.secret_key = '25as52x24da29s8'

# Ruta de la base de datos SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'static/database/Juegos_datos.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Definir la clase `games`
class games(db.Model):
    # Definir las columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    juego = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(255), nullable=False)
    runN = db.Column(db.Integer, nullable=False)
    rejugando = db.Column(db.String(255), nullable=False)
    DatosAdicionales = db.Column(db.String(255), nullable=False)
    Calificacion = db.Column(db.Float, nullable=False)
    img = db.Column(db.String(255), nullable=True)
    fecha_finalizado = db.Column(db.Date, nullable=True)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta de ejemplo para mostrar los juegos
@app.route('/')
def index():
    # Consultar los juegos en la base de datos maximo 5
    juegos = games.query.all()
    return render_template('index.html', juegos=juegos)

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
            fecha_finalizado = date.fromisoformat(fecha_finalizado) 
        else:
            fecha_finalizado = None
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
