from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from myapp import rotas_blueprint  # Substitua "myapp" pelo nome real do seu pacote
import os
from datetime import timedelta

# Função de fábrica para criar e configurar a aplicação
def create_app():
    app = Flask(__name__)

    # Configurações que podem ser alteradas conforme o ambiente
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=int(os.getenv('SESSION_LIFETIME', '30')))
    app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'

    # Inicializando extensões e configurações
    bcrypt = Bcrypt(app)
    CORS(app, supports_credentials=True)

    # Registro de blueprints, mantendo as rotas organizadas
    app.register_blueprint(rotas_blueprint)

    return app

# Inicialização da aplicação
app = create_app()

if __name__ == "__main__":
    # Definindo host e porta para garantir compatibilidade em qualquer ambiente local
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
