from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta
import os

# Função de fábrica para criar a aplicação
def create_app():
    app = Flask(__name__, static_url_path='/static')

    # Configurações de segurança e sessão
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32))
    app.config['SESSION_TYPE'] = 'filesystem'
    app.permanent_session_lifetime = timedelta(minutes=int(os.getenv('SESSION_LIFETIME', 190)))

    # Configuração do diretório de uploads usando variável de ambiente para maior flexibilidade
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

    # Inicializando extensões
    bcrypt = Bcrypt(app)
    CORS(app, supports_credentials=True)

    # Registro do Blueprint das rotas
    from .rotas import rotas_blueprint
    app.register_blueprint(rotas_blueprint)

    return app

# Instância da aplicação
app = create_app()
