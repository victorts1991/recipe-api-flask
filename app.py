from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

app = Flask(__name__)

# importa as configuracoes do arquivo config.py
app.config.from_object('config')

db = SQLAlchemy(app) 
jwt = JWTManager(app)

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

@app.route('/register', methods=['POST'])
def register_user():
    """
    Registrar um novo usuário.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: objetc
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      201:
        description: Usuário criado com sucesso
      400:
        description: Usuário já existe
    """
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Faz login do usuário e retorna um JWT.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: objetc
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login bem sucedido, retorna JWT
      401:
        description: Credenciais inválidas
    """
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        # Converter o ID para string
        token = create_access_token(identity=str(user.id))
        return jsonify({ "access_token": token }), 200
    return jsonify({ "error": "Invalid credentials" }), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity() # Retorna o 'identity' usado na criação do token
    return jsonify({ "msg": f"Usuário com o ID {current_user_id} acessou a rota protegida" }), 200


# print(app.config['SECRET_KEY'])
# print(app.config['CACHE_TYPE'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Banco de Dados criado!')
        app.run(debug=True)