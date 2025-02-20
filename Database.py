from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

DATABASE_GAMES_PATH = os.path.join(os.path.dirname(__file__), 'static/database/Juegos_datos.db')
DAtABASE_ARTIST_PATH = os.path.join(os.path.dirname(__file__), 'static/database/Artists.db')

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

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    urls = db.Column(db.String(255), nullable=False)

class artist_data(db.Model):
    id_artist = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    tipe = db.Column(db.String(80), nullable=False)
    data_location = db.Column(db.String(255), nullable=False)

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_GAMES_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)