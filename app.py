from flask import Flask, request, jsonify, redirect, session, render_template, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PIL import Image as PILImage
from io import BytesIO
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
from reportlab.lib.colors import white
from werkzeug.security import generate_password_hash
from flask import Flask, jsonify, request
from flask import Flask, render_template
from flask_cors import CORS
from datetime import timedelta
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from flask_cors import CORS
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import request, jsonify, session
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_bcrypt import Bcrypt
import db
import os
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
app = Flask(__name__, static_url_path='/static')
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
app.secret_key = 'guilherme21'

UPLOAD_FOLDER = 'C:\\Users\\Guilh\\OneDrive\\Documentos\\Sistema Cotação Luminar\\Sistema Cotação Luminar\\uploads'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Configurações do Banco de Dados
DATABASE = 'luminarbrasil'
USER = 'postgres'
PASSWORD = '217881'
HOST = 'localhost'
PORT = '5432'


app.config['SECRET_KEY'] = os.urandom(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'guilherme21'
app.permanent_session_lifetime = timedelta(minutes=190)  # Sessão expira após 30 minutos de inatividade


# Configuração do banco de dados
DATABASE_URL = "postgres://postgres:217881@localhost/luminarbrasil?client_encoding=utf8"



# Conectar ao banco de dados
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

CORS(app, supports_credentials=True)



@app.route('/usuario')
def index():
    return render_template('index.html')

CORS(app, supports_credentials=True)

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']

        # Gera um hash da senha
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/delete_orcamento/<int:id>', methods=['DELETE'])
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



@app.route('/contar_orcamentos_usuario', methods=['GET'])


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






@app.route('/editar_orcamento/<int:id>', methods=['GET'])


def editar_orcamento(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
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














@app.route('/editar_orcamento/<int:id>', methods=['POST'])
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
                    
                    
                    if file and is_valid_image(file):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        
                        
                    else:
                        file_path = dados_atualizados.get(f'produtos[{i}][caminho_imagem]', '')

                    if produto_id:
                        
                        # Atualizar produto existente
                        cur.execute('''
                            UPDATE produtos SET nome = %s, quantidade = %s, preco_unitario = %s, caminho_imagem = %s
                            WHERE id = %s
                        ''', (nome, quantidade, preco_unitario, caminho_imagem, produto_id))
                        
                        
                    else:
                        
                        
                        # Inserir novo produto e obter seu ID
                        cur.execute('''
                            INSERT INTO produtos (nome, quantidade, preco_unitario, caminho_imagem)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id
                        ''', (nome, quantidade, preco_unitario, caminho_imagem))
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



@app.route('/orcamentos')
def orcamentos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('orcamentos.html')






@app.route('/get_orcamentos', methods=['GET'])
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

@app.route('/get_produtos', methods=['GET'])
def get_produtos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, nome, preco_unitario, caminho_imagem FROM produtos')
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(produtos)

@app.route('/delete_produto/<int:id>', methods=['DELETE'])
def delete_produto(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM produtos WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Produto excluído com sucesso!'})


    
    
    
@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/buscar_produto/<int:produto_id>', methods=['GET'])
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




@app.route('/produtos', methods=['POST'])
def add_produto():
    novo_produto = request.json
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO produtos (nome, imagem) VALUES (%s, %s) RETURNING *', (novo_produto['nome'], novo_produto['imagem']))
    produto = cursor.fetchone()
    connection.commit()
    cursor.close()
    db.put_connection(connection)
    return jsonify(produto)

@app.route('/produtos/<int:id>', methods=['PUT'])
def update_produto(id):
    produto_atualizado = request.json
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE produtos SET nome = %s, imagem = %s WHERE id = %s RETURNING *', (produto_atualizado['nome'], produto_atualizado['imagem'], id))
    produto = cursor.fetchone()
    connection.commit()
    cursor.close()
    db.put_connection(connection)
    return jsonify(produto)



@app.route('/add_product', methods=['POST'])
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
    




@app.route('/login', methods=['GET', 'POST'])
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
                        print(f"Senha hash no banco de dados para {email}: {senhahash}")
                        # Verifica a senha
                        if bcrypt.check_password_hash(senhahash, senha):
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
        
        
        
        
@app.route('/adicionar_comissao', methods=['POST'])
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

@app.route('/comissoes')
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



@app.route('/pagina_comissoes')
def pagina_comissoes():
    user_id = session.get('user_id')
    # Aqui você pode carregar quaisquer dados adicionais necessários para a página, se necessário
    return render_template('comissoes.html')


@app.route('/atualizar_comissao', methods=['POST'])
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

@app.route('/get_comissao/<int:comissao_id>')
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


@app.route('/excluir_comissao', methods=['POST'])
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
@app.route('/painel')
def painel():
    if 'user_name' not in session:
        return redirect('/login')
    user_name = session['user_name']
    return render_template('painel.html', user_name=user_name)



@app.route('/salvar_orcamento', methods=['POST'])
def salvar_orcamento():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    file = request.files.get('imagem')
    file_path = None
    if file and is_valid_image(file):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
    
    
@app.route('/get_produtos_orcamento/<int:orcamento_id>', methods=['GET'])
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
        
            
def adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento,tipo):
    caminho_logo = r"D:\imagens sistema node\logo.png"
    caminho_plano_fundo = r"D:\imagens sistema node\plano.png"

    # Logo e plano de fundo em todas as páginas
    canvas.saveState()
    logo = Image(caminho_logo, width=120, height=120)
    logo.drawOn(canvas, 40, letter[1] - 150)

    plano_fundo = Image(caminho_plano_fundo, width=letter[0], height=letter[1])
    plano_fundo.drawOn(canvas, 0, 0)
    canvas.restoreState()

    # Posicionando campos no canto superior direito
    canvas.setFillColor(white)
    canvas.setFont("Helvetica", 12)
    
    canvas.drawRightString(letter[0] - 50, letter[1] - 60, f"{tipo}: {numero_orcamento}")
    canvas.drawRightString(letter[0] - 50, letter[1] - 40, f"Data: {data_orcamento}")
    canvas.drawRightString(letter[0] - 50, letter[1] - 20, "Validade: 7 dias")

def quebrar_nome_produto(nome, limite_palavras=5):
    palavras = nome.split()
    nome_quebrado = []
    for i in range(0, len(palavras), limite_palavras):
        nome_quebrado.append(' '.join(palavras[i:i+limite_palavras]))
    return "\n".join(nome_quebrado)






def gerar_pdf(tipo,numero_orcamento, data_orcamento, produtos, valor_total, quantidade_produtos, nome, 
              nome_empresa, cnpj, telefone, email, nomevendedor, informacoesadicionais, endereco, frete, prazo_entrega,
              forma_pagamento, num_parcelas, valor_parcela, entrada):
    
    
    doc = SimpleDocTemplate(
    f"orcamento_{numero_orcamento}.pdf",
    pagesize=letter,
    topMargin=90,
    bottomMargin=90,
    leftMargin=20,   # Ajuste a margem esquerda
    rightMargin=20   # Ajuste a margem direita
)

    elementos = []
    
    
    
    estilo_produto = ParagraphStyle(
    'estilo_produto',
    fontName='Helvetica',
    fontSize=8,
    alignment=TA_CENTER
)
    data = [["Imagens ", "Item", "Descrição do Produto", "Quantidade", "Valor/Uni", "Valor/Total"]]
    styles = getSampleStyleSheet()
     
    from reportlab.platypus import Paragraph

    for idx, produto in enumerate(produtos, 1):
        nome = quebrar_nome_produto(produto["nome"])
        nome_paragrafo = Paragraph(nome, estilo_produto)
        quantidade_paragrafo = Paragraph(str(produto["quantidade"]), estilo_produto)
        preco_unitario = f"R$ {produto['preco_unitario']:.2f}"
        preco_unitario_paragrafo = Paragraph(preco_unitario, estilo_produto)
        preco_total = f"R$ {produto['preco_total']:.2f}"
        preco_total_paragrafo = Paragraph(preco_total, estilo_produto)

        imagem_path = produto.get("imagem")
        imagem = Image(imagem_path, width=40, height=40) if imagem_path else "No image"
        data.append([imagem, str(idx), nome_paragrafo, quantidade_paragrafo, preco_unitario_paragrafo, preco_total_paragrafo])



        

    
    
    # Adicionar título "Itens e Valores" com fonte de tamanho 12
    estilo_titulo = styles["Heading1"]
    estilo_titulo.fontSize = 9
    titulo = Paragraph("Itens e Valores", estilo_titulo)
    elementos.append(titulo)
    linha_divisoria = HRFlowable(width="100%", thickness=3, spaceAfter=0.5, lineCap="round", color=colors.HexColor("#1A7B79"))
    elementos.append(linha_divisoria)
    elementos.append(Spacer(1, 24))  # Espaço em branco antes do cabeçalho
    
    
    
        
        
    larguras_colunas = [50, 20, 300, 50, 60, 60]  # Exemplo: Larguras em pontos
    tabela_produtos = Table(data, colWidths=larguras_colunas)

    

    tabela_produtos.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#93C5C8")),
                                          ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                          ('FONTSIZE', (0, 0), (-1, 0), 7),
                                          ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
                                          ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                          ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elementos.extend([tabela_produtos, Spacer(1, 24)])
    
    elementos.append(Spacer(1, 24))
    valor_total_info = f"*Imagens meramente ilustrativas.             Valor Total: R$ {valor_total:.2f}"
    elementos.append(Paragraph(valor_total_info))
    elementos.append(Spacer(1, 24))
    # Adicionar informações da empresa
    estilo_titulo = styles["Heading1"]
    titulo = Paragraph("Informações da Empresa", estilo_titulo)
    elementos.append(titulo)
    linha_divisoria = HRFlowable(width="100%", thickness=3, spaceAfter=20, lineCap="round", color=colors.HexColor("#1A7B79"))
    elementos.append(linha_divisoria)
    
    estilo_normal = styles["BodyText"]
    nome_empresa_p = Paragraph(f"<b>Nome da Empresa:</b> {nome_empresa}", estilo_normal)
    cnpj_p = Paragraph(f"<b>CNPJ:</b> {cnpj}", estilo_normal)
    telefone_p = Paragraph(f"<b>Telefone:</b> {telefone}", estilo_normal)
    email_p = Paragraph(f"<b>Email:</b> {email}", estilo_normal)
    elementos.extend([nome_empresa_p, cnpj_p, telefone_p, email_p])
    elementos.append(Spacer(1, 24))
   
    # Adicionar informações do cliente
    estilo_titulo = styles["Heading1"]
    titulo = Paragraph("Informações Adicionais", estilo_titulo)
    elementos.append(titulo)
    linha_divisoria = HRFlowable(width="100%", thickness=3, spaceAfter=6, lineCap="round", color=colors.HexColor("#1A7B79"))
    elementos.append(linha_divisoria)
    
    estilo_normal = styles["BodyText"]
    
    cliente_info = f"Vendedor: {nomevendedor}"
    cliente_info = f"OBS: {informacoesadicionais}"
    elementos.append(Paragraph(cliente_info, estilo_normal))
    elementos.append(Spacer(1, 24))  # Espaço em branco antes do cabeçalho

    # Adicionar informações de frete
    estilo_titulo = styles["Heading1"]
    titulo = Paragraph("Informações de Entrega", estilo_titulo)
    elementos.append(titulo)
    linha_divisoria = HRFlowable(width="100%", thickness=3, spaceAfter=6, lineCap="round", color=colors.HexColor("#1A7B79"))
    elementos.append(linha_divisoria)
    
    estilo_normal = styles["BodyText"]
    espaco = "<br/>"
    frete_info = f"Frete: {frete}{espaco}Prazo de entrega: {prazo_entrega}  dias úteis. {espaco}Endereço: {endereco}"
    elementos.append(Paragraph(frete_info, estilo_normal))
    elementos.append(Spacer(1, 24))  # Espaço em branco antes do cabeçalho

    # Adicionar informações de pagamento
    estilo_titulo = styles["Heading1"]
    titulo = Paragraph("Informações de Pagamento", estilo_titulo)
    elementos.append(titulo)
    linha_divisoria = HRFlowable(width="100%", thickness=3, spaceAfter=6, lineCap="round", color=colors.HexColor("#1A7B79"))
    elementos.append(linha_divisoria)
    
    
    

   # Se a entrada é None ou 0, usar 0. Caso contrário, usar o valor da entrada
    entrada = entrada if entrada is not None else 0

    # Calcula o valor da parcela
    if num_parcelas > 0:
        valor_parcela = (valor_total - entrada) / num_parcelas
    else:
        valor_parcela = 0  # Evita divisão por zero se não houver parcelas

    # Criação do parágrafo com as informações de pagamento
    estilo_normal = styles["BodyText"]
    espaco = "<br/>"
    pagamento_info = f"Forma de pagamento: {forma_pagamento}{espaco}Número de parcelas: {num_parcelas}{espaco}Valor da parcela: R$ {valor_parcela:.2f}{espaco}Entrada: R$ {entrada:.2f}"
    elementos.append(Paragraph(pagamento_info, estilo_normal))
    elementos.append(Spacer(1, 24))  # Espaço em branco antes do cabeçalho

    # Adicionar valor total
    valor_total_info = f"Valor Total: R$ {valor_total:.2f}"
    elementos.append(Paragraph(valor_total_info, estilo_normal))
   


    

    # Adicionar texto após o valor total
    texto_apos_valor_total = "Esta cotação/pedido considera as informações acima descritas. É de responsabilidade do cliente a confirmação das informações apresentadas e a solicitação de alteração se for o caso, isentando a Luminar Brasil  de eventuais questionamentos, multas ou acréscimos de tributos realizados pelo Estado de destino da mercadoria."
    elementos.append(Paragraph(texto_apos_valor_total, estilo_normal))
    
    estilo_normal = styles["BodyText"]
    dados_conta1 = [
        Paragraph("<b>Dados da conta:</b>", estilo_normal),
        Paragraph("Banco: 336 - Banco C6 S.A.", estilo_normal),
        Paragraph("Agência: 0001", estilo_normal),
        Paragraph("Conta corrente: 22910323-5", estilo_normal),
        Paragraph("CNPJ: 20.656.549/0001-46", estilo_normal),
        Paragraph("Nome: LUMINAR BRASIL", estilo_normal),
        Paragraph("Chave Pix: luminarfinanceiro@hotmail.com", estilo_normal)
    ]
    elementos.extend(dados_conta1)

    dados_conta2 = [
        Paragraph("Agência: 0001", estilo_normal),
        Paragraph("Conta: 1345909-6", estilo_normal),
        Paragraph("Instituição: 403 - Cora SCD", estilo_normal),
        Paragraph("Nome da Empresa: Luminar Brasil", estilo_normal),
        Paragraph("PIX CNPJ: 20.656.549/0001-46 BANCO CORA", estilo_normal)
    ]
    elementos.extend(dados_conta2)
    textos = [
        ("Faturamento", 
         "A Luminar Brasil reserva-se o direito de não emitir nota fiscal para pedidos já aprovados se houver pendências financeiras do cliente com a Luminar Brasil no momento da emissão da nota fiscal e/ou se novas informações fornecidas pelas agências de crédito indicarem restrições e/ou a necessidade de nova avaliação de crédito."),
        ("Dados cadastrais",
         "A verificação dos dados cadastrais (endereço, telefone, e-mail, dados fiscais, etc.) é de responsabilidade do cliente. A Luminar Brasil não se responsabiliza por falhas no recebimento de notificações e mercadorias caso os dados não sejam informados corretamente."),
        ("Cessão de títulos",
         "A Luminar Brasil tem o direito de emitir duplicatas que cedam créditos provenientes deste pedido/orçamento de acordo com a legislação vigente. A aceitação do pedido desta oferta comercial está sujeita à permissão implícita do cliente para ceder créditos conforme descrito acima."),
        ("Frete, Descarga e Reentrega",
         "É importante ressaltar que qualquer serviço adicional solicitado pelo cliente, além do transporte da mercadoria, será de responsabilidade e custo exclusivos do cliente. "
         "A Luminar Brasil se compromete a fornecer os serviços de transporte com qualidade e eficiência, cumprindo os prazos estabelecidos e garantindo a integridade da carga durante todo o processo."
         "No caso do frete CIF (Cost, Insurance, and Freight), a Luminar Brasil assume a responsabilidade pelo transporte da mercadoria desde o ponto de origem até o endereço indicado pelo cliente."
         " Isso inclui não apenas o transporte físico da carga, mas também os custos de seguro e frete. Nesse tipo de contrato, os gastos relacionados ao transporte são assumidos pela Luminar Brasil, proporcionando maior comodidade ao cliente."
         "Por outro lado, no frete FOB (Free on Board), a entrega da mercadoria é realizada no ponto de origem, geralmente o local de embarque, e a partir desse ponto, todos os custos e responsabilidades são transferidos para o cliente. "
         "Isso significa que o cliente é responsável por contratar e pagar pelo transporte da carga até o destino desejado."
         "Além disso, é importante destacar que qualquer serviço adicional, como o agendamento de entregas, armazenagem, frete dedicado ou aluguel de equipamentos para descarga, fica a cargo do cliente. "
         "Caso a Luminar Brasil preste esses serviços por solicitação do cliente, ela terá o direito de cobrar os respectivos valores através de notas de débito. É fundamental que esses termos sejam acordados previamente entre as partes para evitar qualquer conflito ou mal-entendido."
         ),
        # ... [Adicione os demais textos e títulos aqui]
    ]
    for titulo, texto in textos:
        titulo_paragrafo = Paragraph(f"<b>{titulo}</b>", styles['Heading2'])
        texto_paragrafo = Paragraph(texto, styles['BodyText'])
        elementos.extend([titulo_paragrafo, texto_paragrafo, Spacer(1, 12)])
        
    def on_first_page(canvas, doc):
        adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento,tipo)

    def on_later_pages(canvas, doc):
        adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento,tipo)

    doc.build(elementos, onFirstPage=on_first_page, onLaterPages=on_later_pages)
def gerar_orcamento_login():
    return render_template("painel.html")

@app.route("/home")
def gerar_orcamento():
    return render_template("home.html")

@app.route("/gerar_orcamento", methods=["POST"])
def gerar_orcamento_form():
    numero_orcamento = request.form.get("numero_orcamento")
    data_orcamento = request.form.get("data_orcamento")
    quantidade_produtos = int(request.form.get("quantidade_produtos"))

    produtos = []
    valor_total = 0

    for i in range(quantidade_produtos):
        quantidade = int(request.form.get(f"produtos[{i}][quantidade]"))
        nome = request.form.get(f"produtos[{i}][nome]")
        preco = float(request.form.get(f"produtos[{i}][preco_produto]"))
        preco_total = quantidade * preco

        imagem = request.files.get(f"produtos[{i}][imagem]")
        imagem_path = None
        if imagem and is_valid_image(imagem):
            filename = secure_filename(imagem.filename)
            imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem.save(imagem_path)

        produtos.append({
            "nome": nome,
            "quantidade": quantidade,
            "preco_unitario": preco,
            "preco_total": preco_total,
            "imagem": imagem_path  # Salvar o caminho da imagem, não o conteúdo
        })
        valor_total += preco_total
    
      
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
    
    gerar_pdf(tipo,numero_orcamento, data_orcamento, produtos, valor_total, quantidade_produtos,nome ,
              nome_empresa, cnpj, telefone, email, nomevendedor, informacoesadicionais,endereco, frete, prazo_entrega,
              forma_pagamento, num_parcelas, valor_parcela, entrada)

    return send_file(f"orcamento_{numero_orcamento}.pdf", as_attachment=True)
    
if __name__ == '__main__':
    app.run(debug=True)
