from myapp import app, bcrypt, CORS, rotas_blueprint  # Substitua "seu_app" pelo nome real do seu pacote
from flask_cors import CORS
import os
from datetime import timedelta

# ... (seu código existente) ...

CORS(app, supports_credentials=True)

app.register_blueprint(rotas_blueprint)

if __name__ == "__main__":
    app.run()


