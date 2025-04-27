from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flasgger import Swagger

app = Flask(__name__) 

# importa as configuracoes do arquivo config.py
app.config.from_object('config')

db = SQLAlchemy(app) 
jwt = JWTManager(app)
swagger = Swagger(app)

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
        schema:
          type: object
          required: true
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
        schema:
          type: object
          required: true
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

@app.route('/recipes', methods=['POST'])
@jwt_required()
def create_recipe():
    """
    Cria uma nova receita.
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: true
          properties:
            title:
              type: string
            description:
              type: string
            time_minutes:
              type: integer
    responses:
      201:
        description: Receita criada com sucesso
      401:
        description: Token não fornecido ou inválido
    """
    data = request.get_json()
    new_recipe = Recipes(
        title=data['title'],
        description=data['description'],
        time_minutes=data['time_minutes']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({ "msg": "Recipe created" }), 201

@app.route('/recipes', methods=['GET'])
@jwt_required()
def get_recipes():
    """
    Lista receitas com filtros opcionais.
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: query
        name: description
        required: false
        type: string
        description: Filtro por descrição
      - in: query
        name: max_time
        type: integer
        required: false
        description: Tempo máximo de preparo (minutos)
    responses:
      201:
        description: Lista de receitas filtradas
        schema:
          type: array
          items:
            type: object
            properties:
              id: 
                type: integer
              title:
                type: string
              description:
                type: string
              time_minutes:
                type: integer
    """

    description = request.args.get('description')
    max_time = request.args.get('max_time')

    query = Recipes.query

    if description:
        query = query.filter(Recipes.description.ilike(f"%{description}%"))
    if max_time:
        query = query.filter(Recipes.time_minutes <= max_time)

    recipes = query.all()
    return jsonify([
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "time_minutes": r.time_minutes
        }
        for r in recipes
    ])

@app.route('/recipes/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    """
    Atualiza uma receita existente.
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: recipe_id
        required: true
        type: integer
    responses:
      201:
        description: Receita deletada com sucesso
      404: 
        description: Receita não encontrada
      401:
        description: Token não fornecido ou inválido
    """
    data = request.get_json()
    recipe = Recipes.query.get_or_404(recipe_id)
    if 'title' in data:
        recipe.title = data['title']
    if 'description' in data:
        recipe.description = data['description']
    if 'time_minutes' in data:
        recipe.time_minutes = data['time_minutes']

    db.session.commit()
    return jsonify({ "msg": "Recipe updated" }), 200

@app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    """
    Deleta uma receita existente.
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: recipe_id
        required: true
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            time_minutes:
              type: integer
    responses:
      201:
        description: Receita atualizada com sucesso
      404: 
        description: Receita não encontrada
      401:
        description: Token não fornecido ou inválido
    """
    recipe = Recipes.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({ "msg": "Recipe deleted" }), 200



# print(app.config['SECRET_KEY'])
# print(app.config['CACHE_TYPE'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Banco de Dados criado!')
        app.run(debug=True)