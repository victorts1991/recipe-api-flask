from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# importa as configuracoes do arquivo config.py
app.config.from_object('config')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    time_minutes = db.Column(db.Integer, nullable=False)

@app.route('/')
def home():
    return 'Página Inicial'

# print(app.config['SECRET_KEY'])
# print(app.config['CACHE_TYPE'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Banco de Dados criado!')
        app.run(debug=True)