import os
from datetime import datetime
from flask import render_template, send_file, request, current_app
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from PIL import Image as PILImage
from io import BytesIO

# Função para adicionar logotipo e plano de fundo ao PDF
def adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento, tipo):
    caminho_logo = os.path.join("imagens", "plano.png")
    canvas.saveState()
    # Adicionando logo e plano de fundo
    if os.path.exists(caminho_logo):
        logo = RLImage(caminho_logo, width=120, height=120)
        logo.drawOn(canvas, 40, letter[1] - 150)
    canvas.restoreState()
    # Informações no canto superior direito
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 12)
    canvas.drawRightString(letter[0] - 50, letter[1] - 60, f"{tipo}: {numero_orcamento}")
    canvas.drawRightString(letter[0] - 50, letter[1] - 40, f"Data: {data_orcamento}")
    canvas.drawRightString(letter[0] - 50, letter[1] - 20, "Validade: 7 dias")

# Função auxiliar para quebrar o nome do produto em várias linhas
def quebrar_nome_produto(nome, limite_palavras=5):
    palavras = nome.split()
    return "\n".join([' '.join(palavras[i:i + limite_palavras]) for i in range(0, len(palavras), limite_palavras)])

# Função para gerar o PDF de orçamento
def gerar_pdf(params):
    caminho_completo_pdf = os.path.join(params['caminho_base'], 'pdfs', f'orcamento_{params["numero_orcamento"]}.pdf')
    doc = SimpleDocTemplate(caminho_completo_pdf, pagesize=letter, topMargin=90, bottomMargin=90, leftMargin=20, rightMargin=20)
    elementos = []

    # Adicionar título e estilo da tabela
    estilo_titulo = getSampleStyleSheet()["Heading1"]
    titulo = Paragraph("Itens e Valores", estilo_titulo)
    elementos.append(titulo)
    elementos.append(HRFlowable(width="100%", thickness=3, spaceAfter=0.5, lineCap="round", color=colors.HexColor("#1A7B79")))
    elementos.append(Spacer(1, 24))
    
    # Definindo estilo da tabela
    tabela_produtos = criar_tabela_produtos(params['produtos'])
    elementos.extend([tabela_produtos, Spacer(1, 24)])

    # Adicionar informações de pagamento e rodapé
    elementos.extend(criar_paragrafos_informacoes(params))
    
    # Configuração para o cabeçalho e rodapé do PDF
    def on_first_page(canvas, doc):
        adicionar_logo_e_plano_de_fundo(canvas, doc, params["numero_orcamento"], params["data_orcamento"], params["tipo"])
    
    doc.build(elementos, onFirstPage=on_first_page, onLaterPages=on_first_page)
    return caminho_completo_pdf

# Função para criar a tabela de produtos
def criar_tabela_produtos(produtos):
    data = [["Imagens", "Item", "Descrição do Produto", "Quantidade", "Valor/Uni", "Valor/Total"]]
    for idx, produto in enumerate(produtos, 1):
        nome = quebrar_nome_produto(produto["nome"])
        data.append([
            RLImage(produto["imagem"], width=40, height=40) if produto.get("imagem") else "Sem imagem",
            str(idx),
            Paragraph(nome, ParagraphStyle('produto', fontSize=8, alignment=TA_CENTER)),
            produto["quantidade"],
            f"R$ {produto['preco_unitario']:.2f}",
            f"R$ {produto['preco_total']:.2f}"
        ])
    tabela = Table(data, colWidths=[50, 20, 300, 50, 60, 60])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#93C5C8")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return tabela

# Função para criar parágrafos com as informações de pagamento
def criar_paragrafos_informacoes(params):
    estilos = getSampleStyleSheet()
    estilo_normal = estilos["BodyText"]
    elementos = []
    info_empresa = [
        f"<b>Nome da Empresa:</b> {params['nome_empresa']}",
        f"<b>CNPJ:</b> {params['cnpj']}",
        f"<b>Telefone:</b> {params['telefone']}",
        f"<b>Email:</b> {params['email']}"
    ]
    for info in info_empresa:
        elementos.append(Paragraph(info, estilo_normal))
    elementos.append(Spacer(1, 24))
    return elementos

# Validação de imagem recebida
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

# Função para processar e salvar o orçamento
def gerar_orcamento_form():
    params = {
        "numero_orcamento": request.form.get("numero_orcamento"),
        "data_orcamento": request.form.get("data_orcamento"),
        "produtos": obter_produtos_do_formulario(),
        "nome_empresa": request.form.get("nome_empresa"),
        "cnpj": request.form.get("cnpj"),
        "telefone": request.form.get("telefone"),
        "email": request.form.get("email"),
        "tipo": request.form.get("tipo"),
        "caminho_base": os.path.dirname(os.path.abspath(__file__))
    }
    caminho_pdf = gerar_pdf(params)
    return send_file(caminho_pdf, as_attachment=True)

# Função para obter produtos do formulário
def obter_produtos_do_formulario():
    produtos = []
    quantidade_produtos = int(request.form.get("quantidade_produtos", 0))
    for i in range(quantidade_produtos):
        produto = {
            "nome": request.form.get(f"produtos[{i}][nome]"),
            "quantidade": int(request.form.get(f"produtos[{i}][quantidade]")),
            "preco_unitario": float(request.form.get(f"produtos[{i}][preco_produto]")),
            "imagem": salvar_imagem_produto(f"produtos[{i}][imagem]")
        }
        produto["preco_total"] = produto["quantidade"] * produto["preco_unitario"]
        produtos.append(produto)
    return produtos

# Função para salvar imagem do produto
def salvar_imagem_produto(nome_campo):
    imagem = request.files.get(nome_campo)
    if imagem and is_valid_image(imagem):
        caminho_pasta = current_app.config['UPLOAD_FOLDER']
        filename = secure_filename(imagem.filename)
        caminho_completo = os.path.join(caminho_pasta, filename)
        imagem.save(caminho_completo)
        return caminho_completo
    return None
