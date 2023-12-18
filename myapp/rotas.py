from flask import  request, jsonify, redirect, session, render_template, send_file,make_response, url_for , Blueprint, current_app, send_from_directory, Response
from PIL import Image as PILImage
import psycopg2
from myapp.gerarPDF import gerar_pdf
from .db import get_connection, put_connection
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
from flask_bcrypt import bcrypt
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bcrypt import Bcrypt
rotas_blueprint = Blueprint('rotas', __name__)
from reportlab.pdfgen import canvas
from io import BytesIO
           
# Configurações do Banco de Dados
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '21788102'
HOST = 'luminar-1.c1tcpi4qrlgu.us-east-1.rds.amazonaws.com'
PORT = '5432'



# Configuração do banco de dados
DATABASE_URL = "postgres://postgres:21788102@luminar-1.c1tcpi4qrlgu.us-east-1.rds.amazonaws.com/postgres?client_encoding=utf8"



# Conectar ao banco de dados
def get_db_connection():
    
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@rotas_blueprint.route("/orcamento_sucesso")
def orcamento_sucesso():
    return render_template("orcamento_sucesso.html")

@rotas_blueprint.route('/filtrar_produtos', methods=['GET'])
def filtrar_produtos():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    user_id = session['user_id']
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, preco_unitario, caminho_imagem FROM produtos WHERE user_id = %s AND (CAST(id as TEXT) LIKE %s OR nome LIKE %s)", (user_id, f"%{query}%", f"%{query}%"))
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(produtos)


@rotas_blueprint.route('/filtrar_orcamentos', methods=['GET'])
def filtrar_orcamentos():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    user_id = session['user_id']
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orcamentos WHERE user_id = %s AND numero_orcamento LIKE %s", (user_id, f"%{query}%"))
    orcamentos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(orcamentos)

@rotas_blueprint.route('/ranking_orcamentos', methods=['GET'])
def ranking_orcamentos():
    try:
        conn = psycopg2.connect(f"dbname={DATABASE} user={USER} password={PASSWORD} host={HOST} port={PORT}")
        cur = conn.cursor()
        cur.execute('''
            SELECT u.nome, COUNT(o.id) as total_orcamentos
            FROM usuarios u
            JOIN orcamentos o ON u.id = o.user_id
            GROUP BY u.nome
            ORDER BY total_orcamentos DESC
        ''')
        ranking = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(ranking)
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar ranking: {e}'}), 500

@rotas_blueprint.route('/get_produtos_orcamento/<int:orcamento_id>', methods=['GET'])


def get_produtos_orcamento(orcamento_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Busca os produtos associados ao orçamento especificado
        cur.execute('''
            SELECT p.id, p.nome, p.quantidade, p.preco_unitario, p.caminho_imagem
            FROM produtos p
            INNER JOIN orcamentos_produtos op ON p.id = op.produto_id
            WHERE op.orcamento_id = %s
        ''', (orcamento_id,))
        
        
        produtos = cur.fetchall()
        return jsonify(produtos)
    
    except Exception as e:
        print(f"Erro ao buscar produtos do orçamento: {e}")
        return jsonify({'error': 'Erro ao buscar produtos do orçamento'}), 500
    
    
    finally:
        cur.close()
        conn.close()
        
        
@rotas_blueprint.route('/')

def home():
    return redirect(url_for('rotas.login'))




@rotas_blueprint.route('/usuario')

def index():
    return render_template('index.html')

@rotas_blueprint.route('/materiais')

def index2():
    return render_template('materiais.html')



@rotas_blueprint.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    nome = request.form.get('nome')
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        # Gera um hash da senha usando werkzeug.security
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se o usuário já existe
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Usuário já existe!", 400

        # Inserir o novo usuário
        cursor.execute("INSERT INTO usuarios (nome, email, senhahash) VALUES (%s, %s, %s)", (nome, email, hashed_password))
        conn.commit()

    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return "Erro interno do servidor", 500

    finally:
        cursor.close()
        conn.close()

    return "Usuário criado com sucesso!"


@rotas_blueprint.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/root/SistemaLuminarBrasil/uploads', filename)






@rotas_blueprint.route('/delete_orcamento/<int:id>', methods=['DELETE'])
def delete_orcamento(id):
    
    
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        
    
        # Primeiro, exclua todas as referências na tabela 'orcamentos_produtos'
        cur.execute("DELETE FROM orcamentos_produtos WHERE orcamento_id = %s", (id,))
        cur.execute("DELETE FROM orcamentos_produtos WHERE produto_id = %s", (id,))
        
        
        # Em seguida, exclua o orçamento
        cur.execute("DELETE FROM orcamentos WHERE id = %s", (id,))
        conn.commit()
        
        
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    
    finally:
        cur.close()
        conn.close()

    return jsonify({'status': 'success', 'message': 'Orçamento excluído com sucesso!'})


@rotas_blueprint.route('/contar_orcamentos_usuario', methods=['GET'])


def contar_orcamentos_usuario():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orcamentos WHERE user_id = %s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    return jsonify({'total_orcamentos': count})






@rotas_blueprint.route('/editar_orcamento/<int:id>', methods=['GET'])


def editar_orcamento(id):
    if 'user_id' not in session:
        return redirect(url_for('rotas.login'))

    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Busca os detalhes do orçamento
    cur.execute('SELECT * FROM orcamentos WHERE id = %s', (id,))
    orcamento = cur.fetchone()

    # Busca os produtos associados ao orçamento
    cur.execute('''
        SELECT p.* FROM produtos p
        INNER JOIN orcamentos_produtos op ON p.id = op.produto_id
        WHERE op.orcamento_id = %s
    ''', (id,))
    produtos = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('editar_orcamento.html', orcamento=orcamento, produtos=produtos)


@rotas_blueprint.route('/excluir_produto/<int:produto_id>', methods=['POST'])
def excluir_produto(produto_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Usuário não autenticado'}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM orcamentos_produtos WHERE produto_id = %s', (produto_id,))
        # Excluir o produto do banco de dados
        cur.execute('DELETE FROM produtos WHERE id = %s', (produto_id,))
        

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({'status': 'success'})

@rotas_blueprint.route('/editar_orcamento/<int:id>', methods=['POST'])



def atualizar_orcamento(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    dados_atualizados = request.form
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Validação dos campos
        campos_necessarios = [
            'numero_orcamento', 'data_orcamento', 'nome_empresa', 'cnpj',
            'telefone', 'email', 'endereco', 'informacoesadicionais',
            'nomevendedor', 'frete', 'prazo_entrega', 'forma_pagamento'
        ]
         # Atualizar informações do orçamento
        cur.execute('''
            UPDATE orcamentos SET
            numero_orcamento = %s, data_orcamento = %s, nome_empresa = %s, cnpj = %s, 
            telefone = %s, email = %s, endereco = %s, informacoesadicionais = %s, 
            nomevendedor = %s, frete = %s, prazo_entrega = %s, forma_pagamento = %s
            WHERE id = %s
        ''', (dados_atualizados['numero_orcamento'], dados_atualizados['data_orcamento'],
              dados_atualizados['nome_empresa'], dados_atualizados['cnpj'],
              dados_atualizados['telefone'], dados_atualizados['email'],
              dados_atualizados['endereco'], dados_atualizados['informacoesadicionais'],
              dados_atualizados['nomevendedor'], dados_atualizados['frete'],
              dados_atualizados['prazo_entrega'], dados_atualizados['forma_pagamento'], id))

        # Limpar associações existentes na tabela de junção
        cur.execute('DELETE FROM orcamentos_produtos WHERE orcamento_id = %s', (id,))

        # Quantidade de produtos
        quantidade_produtos = int(dados_atualizados['quantidade_produtos'])

    
        # Atualizar/Inserir produtos e recriar associações
        for i in range(quantidade_produtos):
                    produto_id = dados_atualizados.get(f'produtos[{i}][id]')
                    nome = dados_atualizados.get(f'produtos[{i}][nome]')
                    quantidade = dados_atualizados.get(f'produtos[{i}][quantidade]')
                    preco_unitario = dados_atualizados.get(f'produtos[{i}][preco_produto]')
                    caminho_imagem = dados_atualizados.get(f'produtos[{i}][caminho_imagem]')
                    
                    
                    file = request.files.get(f'produtos[{i}][imagem]')
                    
                    
                    # ...
                    if file and is_valid_image(file):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)

                        # Salve apenas 'filename' no banco de dados
                        cur.execute("UPDATE produtos SET caminho_imagem = %s WHERE id = %s", (filename, produto_id))
                    else:
                        filename = dados_atualizados.get(f'produtos[{i}][caminho_imagem]', '')
                        if filename.startswith('/uploads/'):
                            filename = filename[len('/uploads/'):]  # Remove o prefixo duplicado
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                    # Use 'filename' nas suas queries


                    if produto_id:
                        
                        # Atualizar produto existente
                        cur.execute('''
                            UPDATE produtos SET nome = %s, quantidade = %s, preco_unitario = %s, caminho_imagem = %s
                            WHERE id = %s
                        ''', (nome, quantidade, preco_unitario, file_path, produto_id))
                        
                        
                    else:
                        
                        
                        # Inserir novo produto e obter seu ID
                        cur.execute('''
                            INSERT INTO produtos (nome, quantidade, preco_unitario, caminho_imagem)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id
                        ''', (nome, quantidade, preco_unitario, file_path))
                        produto_id = cur.fetchone()[0]

                    # Inserir associação na tabela de junção
                    
                    
                    cur.execute('''
                        INSERT INTO orcamentos_produtos (orcamento_id, produto_id)
                        VALUES (%s, %s)
                    ''', (id, produto_id))

        conn.commit()
        
    except ValueError as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
    
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'status': 'error', 'message': 'Erro ao atualizar orçamento.'}), 500
    
    
    finally:
        
        
        if cur and not cur.closed:
            cur.close()
        if conn and not conn.closed:
            conn.close()

    return jsonify({'status': 'success'})



@rotas_blueprint.route('/orcamentos')
def orcamentos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('orcamentos.html')






@rotas_blueprint.route('/get_orcamentos', methods=['GET'])
def get_orcamentos():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM orcamentos WHERE user_id = %s', (user_id,))
    orcamentos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(orcamentos)



@rotas_blueprint.route('/get_produtos', methods=['GET'])
def get_produtos():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    user_id = session['user_id']
    # user_id = 11  # Remova esta linha para usar o ID do usuário da sessão

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, nome, preco_unitario, caminho_imagem FROM produtos WHERE user_id = %s', (user_id,))
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(produtos)



@rotas_blueprint.route('/delete_produto/<int:id>', methods=['DELETE'])
def delete_produto(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Primeiro, exclua todas as referências na tabela 'orcamentos_produtos'
    cur.execute("DELETE FROM orcamentos_produtos WHERE orcamento_id = %s", (id,))
    
    
    
    cur.execute('DELETE FROM produtos WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Produto excluído com sucesso!'})


    
    
    
@rotas_blueprint.route('/produtos')
def produtos():
    return render_template('produtos.html')



@rotas_blueprint.route('/buscar_produto/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cur.fetchone()
    cur.close()
    conn.close()

    if produto is None:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    
    nome_arquivo_imagem = os.path.basename(produto[5])  # Isso extrai apenas o nome do arquivo
    return jsonify({'id': produto[0], 'nome': produto[2], 'quantidade': produto[1], 'preco_unitario': produto[3], 'caminho_imagem': nome_arquivo_imagem})




@rotas_blueprint.route('/produtos', methods=['POST'])
def add_produto():
    novo_produto = request.json
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO produtos (nome, imagem) VALUES (%s, %s) RETURNING *', (novo_produto['nome'], novo_produto['imagem']))
    produto = cursor.fetchone()
    connection.commit()
    cursor.close()
    put_connection(connection)
    return jsonify(produto)



@rotas_blueprint.route('/produtos/<int:id>', methods=['PUT'])
def update_produto(id):
    produto_atualizado = request.json
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE produtos SET nome = %s, imagem = %s WHERE id = %s RETURNING *', (produto_atualizado['nome'], produto_atualizado['imagem'], id))
    produto = cursor.fetchone()
    connection.commit()
    cursor.close()
    put_connection(connection)
    return jsonify(produto)



@rotas_blueprint.route('/add_product', methods=['POST'])

def add_product():
    
    data = request.json
    nome = data.get('nome')
    imagem = data.get('imagem')

    if not nome or not imagem:
        return jsonify({'error': 'Nome e imagem são obrigatórios'}), 400

    try:
        # Conexão com o banco de dados
        with psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT) as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO produtos (nome, imagem) VALUES (%s, %s) RETURNING id;", (nome, imagem))
                product_id = cursor.fetchone()[0]
                connection.commit()
                
        return jsonify({'status': 'success', 'id': product_id}), 201
    except Exception as e:
        
        print(f"Erro ao adicionar produto: {e}")
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500
    


@rotas_blueprint.route('/logout')
def logout():
    # Limpa a sessão
    session.clear()
    # Redireciona para a página de login
    return redirect(url_for('rotas.login'))


def gerar_orcamento_login():
    return render_template("painel.html")

@rotas_blueprint.route('/login', methods=['GET', 'POST']) 
def login():
    
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.json.get('email')
        senha = request.json.get('senha')
        print(f"Tentativa de login para {email} com senha {senha}")

        try:
            # Conexão com o banco de dados
            with psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT) as connection:
                with connection.cursor() as cursor:
                    # Busca o user_id, a senha e o nome do usuário no banco de dados
                    cursor.execute("SELECT id, senhahash, nome FROM usuarios WHERE email = %s;", [email])
                    result = cursor.fetchone()
                    if result:
                        user_id, senhahash, nome = result
                        if check_password_hash(senhahash, senha):
                            session['user_id'] = user_id  # Configura o user_id na sessão
                            session['user_email'] = email
                            session['user_name'] = nome
                            return jsonify({'status': 'success'}), 200
                        else:
                            print("Senha incorreta")
                    else:
                        print("Email não encontrado no banco de dados")
                return jsonify({'status': 'error', 'message': 'Credenciais inválidas'}), 401
        except Exception as e:
            print(f"Erro ao tentar fazer login: {e}")
            return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500
        
        
@rotas_blueprint.route('/adicionar_comissao', methods=['POST'])
def adicionar_comissao():
    data = request.json
    user_id = session.get('user_id')  # Substitua por sua lógica para obter o ID do usuário logado

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO comissoes (valor, user_id, data, numeropedido, comissaopercentual) VALUES (%s, %s, %s, %s, %s)',
                (data['valorVenda'], user_id, data['dataPedido'], data['numeroPedido'], data['comissao']))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Comissão adicionada com sucesso!'}) 

@rotas_blueprint.route('/comissoes')
def comissoes():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Selecionando campos específicos da tabela comissoes
    cur.execute('SELECT id, valor, data, numeropedido, comissaopercentual FROM comissoes WHERE user_id = %s', (user_id,))
    
    comissoes = cur.fetchall()
    cur.close()
    conn.close()

    # Retornar os dados como uma lista de dicionários
    return jsonify([dict(comissao) for comissao in comissoes])



@rotas_blueprint.route('/pagina_comissoes')
def pagina_comissoes():
    user_id = session.get('user_id')
    # Aqui você pode carregar quaisquer dados adicionais necessários para a página, se necessário
    return render_template('comissoes.html')


@rotas_blueprint.route('/atualizar_comissao', methods=['POST'])
def atualizar_comissao():
    data = request.json
    user_id = session.get('user_id')

    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE comissoes SET numeropedido = %s, data = %s, valor = %s, comissaopercentual = %s WHERE id = %s AND user_id = %s',
                (data['numeropedido'], data['data'], data['valor'], data['comissaopercentual'], data['comissaoId'], user_id))
    
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Comissão atualizada com sucesso!'}) 

@rotas_blueprint.route('/get_comissao/<int:comissao_id>')
def get_comissao(comissao_id):
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM comissoes WHERE id = %s AND user_id = %s', (comissao_id, user_id))
    comissao = cur.fetchone()
    cur.close()
    conn.close()

    if comissao:
        return jsonify(comissao)
    else:
        return jsonify({'error': 'Comissão não encontrada'}), 404


@rotas_blueprint.route('/excluir_comissao', methods=['POST'])
def excluir_comissao():
    comissao_id = request.json['comissaoId']
    user_id = session.get('user_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM comissoes WHERE id = %s AND user_id = %s', (comissao_id, user_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Comissão excluída com sucesso!'}) 





# Rota para o painel do usuário
@rotas_blueprint.route('/painel')
def painel():
    # Verifica se o nome do usuário está na sessão
    if 'user_name' not in session:
        # Redireciona para a página de login se o usuário não estiver logado
        return redirect(url_for('rotas.login'))

    # Se o usuário estiver logado, renderiza a página do painel
    response = make_response(render_template('painel.html', user_name=session['user_name']))

    # Define cabeçalhos para evitar o cache da página
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response



@rotas_blueprint.route('/salvar_orcamento', methods=['POST'])
def salvar_orcamento():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    file = request.files.get('imagem')
    file_path = None
    if file and is_valid_image(file):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
    # Extrair dados do formulário
    numero_orcamento = request.form['numero_orcamento']
    data_orcamento = request.form['data_orcamento']
    quantidade_produtos = request.form['quantidade_produtos']
    nome_empresa = request.form['nome_empresa']
    cnpj = request.form['cnpj']
    telefone = request.form['telefone']
    email = request.form['email']
    endereco = request.form['endereco']
    informacoesadicionais = request.form['informacoesadicionais']
    nomevendedor = request.form['nomevendedor']
    frete = request.form['frete']
    prazo_entrega = request.form['prazo_entrega']
    forma_pagamento = request.form['forma_pagamento']
    tipo = request.form['tipo']
    
    
    try:
        conn = psycopg2.connect(f"dbname={DATABASE} user={USER} password={PASSWORD} host={HOST} port={PORT}")
        cur = conn.cursor()
        try:
            num_parcelas = int(request.form['num_parcelas'])
            entrada = request.form['entrada']
            
            
        except (KeyError, ValueError):
            num_parcelas = 0  # ou um valor padrão
            entrada = 0  # ou um valor padrão
            
            
            
            
        # Inserir orçamento
        cur.execute('''
            INSERT INTO orcamentos ( entrada, tipo,quantidade_produtos, numero_orcamento, data_orcamento, nome_empresa, cnpj, telefone, email, endereco, num_parcelas, informacoesadicionais, nomevendedor, frete, prazo_entrega, forma_pagamento,user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ( entrada, tipo,quantidade_produtos, numero_orcamento, data_orcamento, nome_empresa, cnpj, telefone, email, endereco, num_parcelas, informacoesadicionais, nomevendedor, frete, prazo_entrega, forma_pagamento,user_id))
        
        
     
        orcamento_id = cur.fetchone()[0]
        for i in range(int(quantidade_produtos)):
            nome = request.form.get(f'produtos[{i}][nome]')
            quantidade = request.form.get(f'produtos[{i}][quantidade]')
            preco_unitario = request.form.get(f'produtos[{i}][preco_produto]')
            preco_total = float(preco_unitario) * int(quantidade)

            # Obter a imagem para o produto específico
            file = request.files.get(f'produtos[{i}][imagem]')
            file_path = None
            if file and is_valid_image(file):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

            cur.execute('''
                INSERT INTO produtos (caminho_imagem, nome, quantidade, preco_unitario, preco_total,user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (file_path, nome, quantidade, preco_unitario, preco_total,user_id))
            
            produto_id = cur.fetchone()[0]

            # Insere a relação na tabela de junção
            cur.execute('''
                INSERT INTO orcamentos_produtos (orcamento_id, produto_id)
                VALUES (%s, %s)
            ''', (orcamento_id, produto_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar orçamento: {e}")
        return jsonify({'error': f'Erro ao salvar orçamento: {e}'}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({'message': 'Orçamento salvo com sucesso!'})

def is_valid_image(file):
    try:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return False
        with PILImage.open(file) as img:
            img.verify()
        file.seek(0)
        return True
    except Exception as e:
        print(f"Invalid image: {e}")
        return False
    
@rotas_blueprint.route("/home")
def gerar_orcamento():
    return render_template("home.html")


@rotas_blueprint.route("/gerar_orcamento", methods=["POST"])
def gerar_orcamento_form():
    numero_orcamento = request.form.get("numero_orcamento")
    data_orcamento = request.form.get("data_orcamento")
    quantidade_produtos = int(request.form.get("quantidade_produtos"))

    produtos = []
    valor_total = 0
    caminho_pasta_uploads = current_app.config['UPLOAD_FOLDER']
    for i in range(quantidade_produtos):
        # Extrair dados do produto
        nome = request.form.get(f"produtos[{i}][nome]")
        quantidade = int(request.form.get(f"produtos[{i}][quantidade]"))
        preco = float(request.form.get(f"produtos[{i}][preco_produto]"))
        
        # Verifica se uma nova imagem foi enviada
        
        
        
        
        # Tratar imagem do produto
        imagem = request.files.get(f"produtos[{i}][imagem]")
        if imagem and is_valid_image(imagem):
            filename = secure_filename(imagem.filename)
            imagem_path = os.path.join(caminho_pasta_uploads, filename)
            imagem.save(imagem_path)
        else:
            imagem_path = request.form.get(f"produtos[{i}][caminho_imagem]", None)
            if imagem_path:
                imagem_path = os.path.join(caminho_pasta_uploads, imagem_path.split('/')[-1])

        valor_total_produto = quantidade * preco
        valor_total += valor_total_produto

        produtos.append({
            "nome": nome,
            "quantidade": quantidade,
            "preco_unitario": preco,
            "preco_total": valor_total_produto,
            "imagem": imagem_path
        })
       
    
      
    nome = request.form.get ("nome")   
    informacoesadicionais = request.form.get("informacoesadicionais")
    nome_empresa = request.form.get("nome_empresa")
    endereco = request.form.get("endereco")
    cnpj = request.form.get("cnpj")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    nomevendedor = request.form.get("nomevendedor")
    frete = request.form.get("frete")
    prazo_entrega = request.form.get("prazo_entrega")
    forma_pagamento = request.form.get("forma_pagamento")
    num_parcelas = int(request.form.get("num_parcelas", 0))
    entrada = float(request.form.get("entrada", 0))
    tipo = request.form.get("tipo"
                            )
    if forma_pagamento == 'Parcelado' and num_parcelas > 0:
    
     valor_parcela = (valor_total - entrada) / num_parcelas

    else:
     valor_parcela = valor_total  
   
    caminho_completo_pdf = gerar_pdf(tipo, numero_orcamento, data_orcamento, produtos, valor_total, 
                                     quantidade_produtos, nome, nome_empresa, cnpj, telefone, 
                                     email, nomevendedor, informacoesadicionais, endereco, frete, 
                                     prazo_entrega, forma_pagamento, num_parcelas, valor_parcela, entrada)

    # Enviar o arquivo PDF usando o caminho completo
    return redirect('/orcamento_sucesso')