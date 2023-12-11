from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PIL import Image as PILImage
from reportlab.lib.colors import white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Image
from reportlab.lib.enums import TA_JUSTIFY
from flask import render_template,send_file, Response
from flask import  request,  current_app
from werkzeug.utils import secure_filename
import os
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import send_file


def adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento,tipo):
    caminho_logo = r"imagens\plano.png"
    caminho_plano_fundo = r"imagens\plano.png"

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
    
    
    caminho_completo_pdf = os.path.join('D:\\', 'Sistema Cotação Luminar', 'pdfs', f"orcamento_{numero_orcamento}.pdf")    
    doc = SimpleDocTemplate(
        caminho_completo_pdf,
        pagesize=letter,
        topMargin=90,
        bottomMargin=90,
        leftMargin=20,
        rightMargin=20
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
    estilo_titulo.fontSize = 12
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
    
    elementos.append(Spacer(1, 12))
    valor_total_info = f"*Imagens meramente ilustrativas.             Valor Total: R$ {valor_total:.2f}"
    elementos.append(Paragraph(valor_total_info))
    elementos.append(Spacer(1, 12))
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

    # Combinar as informações em uma única string
    texto_cliente = f"<b>Vendedor:</b> {nomevendedor}<br/><b>OBS:</b> {informacoesadicionais}"
    elementos.append(Paragraph(texto_cliente, estilo_normal))
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
        Paragraph("Banco: 336 - Banco C6 S.A---------Agência: 0001----------------------Conta corrente: 22910323-5", estilo_normal),
        Paragraph("CNPJ: 20.656.549/0001-46 ---------Nome: LUMINAR BRASIL------Chave Pix: luminarfinanceiro@hotmail.com<br/><br/>", estilo_normal),

    ]
    elementos.extend(dados_conta1)

    dados_conta2 = [
        Paragraph("Agência: 0001---------------------Conta: 1345909-6----------Instituição: 403 - Cora SCD", estilo_normal),
        Paragraph("Nome da Empresa:------------------Luminar Brasil------------PIX CNPJ: 20.656.549/0001-46 BANCO CORA<br/><br/>", estilo_normal),
       
    ]
    
    styles = getSampleStyleSheet()
    estilo_justificado = ParagraphStyle(
    'EstiloJustificado',
    parent=styles['Normal'],
    alignment=TA_JUSTIFY
)
    elementos.extend(dados_conta2)
    textos = [
    ("Faturamento<br/><br/>", 
     "A Luminar Brasil reserva-se o direito de não emitir nota fiscal para pedidos já aprovados se houver pendências financeiras do cliente com a Luminar Brasil no momento da emissão da nota fiscal e/ou se novas informações fornecidas pelas agências de crédito indicarem restrições e/ou a necessidade de nova avaliação de crédito.<br/><br/>"),
    ("Dados cadastrais<br/><br/>",
     "A verificação dos dados cadastrais (endereço, telefone, e-mail, dados fiscais, etc.) é de responsabilidade do cliente. A Luminar Brasil não se responsabiliza por falhas no recebimento de notificações e mercadorias caso os dados não sejam informados corretamente.<br/><br/>"),
    ("Cessão de títulos",
     "A Luminar Brasil tem o direito de emitir duplicatas que cedam créditos provenientes deste pedido/orçamento de acordo com a legislação vigente. A aceitação do pedido desta oferta comercial está sujeita à permissão implícita do cliente para ceder créditos conforme descrito acima.<br/><br/>"),
    
    ("Frete, Descarga e Reentrega<br/><br/>",
     "É importante ressaltar que qualquer serviço adicional solicitado pelo cliente, além do transporte da mercadoria, será de responsabilidade e custo exclusivos do cliente. "
     "A Luminar Brasil se compromete a fornecer os serviços de transporte com qualidade e eficiência, cumprindo os prazos estabelecidos e garantindo a integridade da carga durante todo o processo. "
     "No caso do frete CIF (Cost, Insurance, and Freight), a Luminar Brasil assume a responsabilidade pelo transporte da mercadoria desde o ponto de origem até o endereço indicado pelo cliente. <br/><br/>"),
    
    ("", 
     "Isso inclui não apenas o transporte físico da carga, mas também os custos de seguro e frete. Nesse tipo de contrato, os gastos relacionados ao transporte são assumidos pela Luminar Brasil, proporcionando maior comodidade ao cliente. "
     "Por outro lado, no frete FOB (Free on Board), a entrega da mercadoria é realizada no ponto de origem, geralmente o local de embarque, e a partir desse ponto, todos os custos e responsabilidades são transferidos para o cliente. "
     "Isso significa que o cliente é responsável por contratar e pagar pelo transporte da carga até o destino desejado.<br/><br/>"),
    
    
    ("", 
     "Além disso, é importante destacar que qualquer serviço adicional, como o agendamento de entregas, armazenagem, frete dedicado ou aluguel de equipamentos para descarga, fica a cargo do cliente. "
     "Caso a Luminar Brasil preste esses serviços por solicitação do cliente, ela terá o direito de cobrar os respectivos valores através de notas de débito. É fundamental que esses termos sejam acordados previamente entre as partes para evitar qualquer conflito ou mal-entendido.<br/><br/>"),
    
    
    
    # ... outros textos conforme necessário ...
]
    for titulo, texto in textos:
        titulo_paragrafo = Paragraph(f"<b>{titulo}</b>", estilo_justificado)
        texto_paragrafo = Paragraph(texto, estilo_justificado)
        elementos.extend([titulo_paragrafo, texto_paragrafo, Spacer(1, 12)])

        
    def on_first_page(canvas, doc):
        adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento,tipo)

    def on_later_pages(canvas, doc):
        adicionar_logo_e_plano_de_fundo(canvas, doc, numero_orcamento, data_orcamento,tipo)

    pdf_path = f"orcamento_{numero_orcamento}.pdf"
    doc.build(elementos, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    return caminho_completo_pdf




def gerar_orcamento_login():
     return render_template("painel.html")    
 
 
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

    caminho_completo_pdf = gerar_pdf(...)

    # Enviar o arquivo PDF
    return send_file(caminho_completo_pdf, as_attachment=True)