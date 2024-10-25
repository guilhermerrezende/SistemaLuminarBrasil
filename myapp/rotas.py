from flask import request, jsonify, redirect, session, render_template, send_file, make_response, url_for, Blueprint, current_app
from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor
from myapp.db import get_connection, put_connection
from myapp.gerarPDF import gerar_pdf
from PIL import Image as PILImage
import os
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

rotas_blueprint = Blueprint('rotas', __name__)

# Utilidades
def is_valid_image(file):
    try:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return False
        with PILImage.open(file) as img:
            img.verify()
        file.seek(0)
        return True
    except Exception:
        return False

def save_image(file, upload_folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path

# Conexão com banco de dados centralizada
def get_db_connection():
    try:
        conn = get_connection()
    except psycopg2.OperationalError:
        conn = None
    return conn

# Autenticação
@rotas_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email, senha = request.json.get('email'), request.json.get('senha')
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, senhahash, nome FROM usuarios WHERE email = %s;", [email])
            user = cur.fetchone()
            if user and check_password_hash(user[1], senha):
                session['user_id'], session['user_name'] = user[0], user[2]
                return jsonify({'status': 'success'}), 200
            return jsonify({'status': 'error', 'message': 'Credenciais inválidas'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500
    finally:
        put_connection(conn)

@rotas_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('rotas.login'))

# Produtos
@rotas_blueprint.route('/produtos', methods=['GET'])
def get_produtos():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT id, nome, preco_unitario, caminho_imagem FROM produtos WHERE user_id = %s', (user_id,))
            produtos = cur.fetchall()
        return jsonify(produtos)
    finally:
        put_connection(conn)

@rotas_blueprint.route('/add_produto', methods=['POST'])
def add_produto():
    data = request.json
    nome, imagem = data.get('nome'), data.get('imagem')
    if not nome or not imagem:
        return jsonify({'error': 'Nome e imagem são obrigatórios'}), 400
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO produtos (nome, imagem) VALUES (%s, %s) RETURNING id;", (nome, imagem))
            produto_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({'status': 'success', 'id': produto_id}), 201
    finally:
        put_connection(conn)

# Orçamentos
@rotas_blueprint.route('/orcamentos', methods=['POST'])
def salvar_orcamento():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    try:
        file = request.files.get('imagem')
        file_path = save_image(file, current_app.config['UPLOAD_FOLDER']) if file and is_valid_image(file) else None

        orcamento_data = {
            'numero_orcamento': request.form['numero_orcamento'],
            'data_orcamento': request.form['data_orcamento'],
            'nome_empresa': request.form['nome_empresa'],
            'cnpj': request.form['cnpj'],
            'telefone': request.form['telefone'],
            'email': request.form['email'],
            'user_id': user_id
        }
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                '''INSERT INTO orcamentos (numero_orcamento, data_orcamento, nome_empresa, cnpj, telefone, email, user_id) 
                VALUES (%(numero_orcamento)s, %(data_orcamento)s, %(nome_empresa)s, %(cnpj)s, %(telefone)s, %(email)s, %(user_id)s) 
                RETURNING id;''', orcamento_data)
            orcamento_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({'message': 'Orçamento salvo com sucesso!', 'orcamento_id': orcamento_id})
    finally:
        put_connection(conn)

@rotas_blueprint.route('/get_orcamentos', methods=['GET'])
def get_orcamentos():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM orcamentos WHERE user_id = %s', (user_id,))
            orcamentos = cur.fetchall()
        return jsonify(orcamentos)
    finally:
        put_connection(conn)

@rotas_blueprint.route('/orcamento_pdf/<int:orcamento_id>', methods=['GET'])
def gerar_pdf_orcamento(orcamento_id):
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM orcamentos WHERE id = %s", (orcamento_id,))
            orcamento = cur.fetchone()
        if not orcamento:
            return jsonify({'error': 'Orçamento não encontrado'}), 404
        pdf_path = gerar_pdf(orcamento)
        return send_file(pdf_path, as_attachment=True)
    finally:
        put_connection(conn)
