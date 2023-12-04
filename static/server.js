const express = require('express');
const PDFDocument = require('pdfkit');
const fs = require('fs');

const app = express();
const port = 3000;

app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/formulario.html');
});

app.post('/generatePDF', (req, res) => {
    const doc = new PDFDocument();

    // Informações do Documento
    doc.text(`Tipo de documento: ${req.body.documentType}`);
    doc.text(`Data: ${req.body.date}`);
    
    // Este é o número de produtos que o usuário inseriu
    const productCount = parseInt(req.body.productCount);

    // Iterar sobre cada produto e adicioná-los ao PDF
    for (let i = 1; i <= productCount; i++) {
        const productName = req.body[`productName${i}`];
        const productPrice = parseFloat(req.body[`productPrice${i}`]);
        
        // Adicionando ao PDF
        doc.text(`${productName}: ${productPrice}`);
    }

    // Outras informações
    doc.text(`Tipo do Frete: ${req.body.freightType}`);
    doc.text(`Dados do Cliente: ${req.body.clientData}`);
    doc.text(`Entrada: ${req.body.paymentEntry}%`);
    doc.text(`Parcelas: ${req.body.paymentInstallments}`);
    doc.text(`Prazo de Entrega: ${req.body.deliveryTime} dias úteis`);

    // Definindo os cabeçalhos de resposta
    const filename = `orcamento_${Date.now()}.pdf`;
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=${filename}`);

    // Finalizando o documento
    doc.pipe(res);
    doc.end();
});

app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`);
});
