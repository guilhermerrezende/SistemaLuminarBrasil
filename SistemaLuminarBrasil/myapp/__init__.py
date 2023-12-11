from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
from datetime import timedelta

app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = os.urandom(32)
app.secret_key = 'guilherme21'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=190)  # Sessão expira após 30 minutos de inatividade


app.config['UPLOAD_FOLDER'] = 'C:\\Users\\Guilh\\OneDrive\\Documentos\\Sistema Cotação Luminar\\uploads'


bcrypt = Bcrypt(app)
           


CORS(app, supports_credentials=True)

from .rotas import rotas_blueprint  # Importando o Blueprint
app.register_blueprint(rotas_blueprint)