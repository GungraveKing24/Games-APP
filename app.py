from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Ruta de la base de datos SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'static/database/Juegos_datos.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar seguimiento de modificaciones

# Inicializar la base de datos
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

# Ruta de ejemplo para mostrar los juegos
@app.route('/')
def index():
    # Consultar los juegos en la base de datos maximo 5
    juegos = games.query.all()
    return render_template('index.html', juegos=juegos)

@app.route('/editar/<int:juego_id>', methods=['GET', 'POST'])
def editar(juego_id):
    juego = games.query.get_or_404(juego_id)
    if request.method == 'POST':
        juego.juego = request.form['juego']
        juego.estado = request.form['estado']
        juego.runN = request.form['runN']
        juego.rejugando = request.form['rejugando']
        juego.DatosAdicionales = request.form['DatosAdicionales']
        juego.Calificacion = request.form['Calificacion']
        juego.img = request.form['img']
        juego.fecha_finalizado = request.form['fecha_finalizado']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', juego=juego)

if __name__ == '__main__':
    app.run(debug=True)
