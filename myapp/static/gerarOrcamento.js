document.addEventListener('DOMContentLoaded', function () {
    const orcamentoForm = document.getElementById('orcamentoForm');

    orcamentoForm.addEventListener('submit', salvarOrcamento);
    document.getElementById('quantidade_produtos').addEventListener('change', gerarCamposProdutos);
    document.getElementById('forma_pagamento').addEventListener('change', atualizarFormaPagamento);
});

/* Função para salvar orçamento via AJAX */
function salvarOrcamento(event) {
    event.preventDefault();

    const formData = new FormData(document.getElementById('orcamentoForm'));

    fetch('/salvar_orcamento', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error('Erro ao salvar orçamento:', error));
}

/* Função para gerar campos de produtos dinamicamente */
function gerarCamposProdutos() {
    const quantidade = document.getElementById('quantidade_produtos').value;
    const produtosDiv = document.getElementById('produtos');
    produtosDiv.innerHTML = '';

    for (let i = 0; i < quantidade; i++) {
        produtosDiv.innerHTML += `
            <fieldset>
                <legend>Produto ${i + 1}</legend>
                <label for="produto_nome_${i}">Nome do Produto:</label>
                <input type="text" id="produto_nome_${i}" name="produtos[${i}][nome]" required>

                <label for="produto_quantidade_${i}">Quantidade:</label>
                <input type="number" id="produto_quantidade_${i}" name="produtos[${i}][quantidade]" min="1" required>

                <label for="produto_preco_${i}">Preço do Produto:</label>
                <input type="number" id="produto_preco_${i}" name="produtos[${i}][preco_produto]" step="0.01" required>

                <label for="produto_imagem_${i}">Imagem do Produto:</label>
                <input type="file" id="produto_imagem_${i}" name="produtos[${i}][imagem]" onchange="atualizarPreviewImagem(this, ${i})">
                <img id="imagem_preview_${i}" src="" style="display:none; max-width: 100px; max-height: 100px;">
            </fieldset>
        `;
    }
}

/* Função para atualizar a pré-visualização da imagem do produto */
function atualizarPreviewImagem(input, index) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const imgPreview = document.getElementById(`imagem_preview_${index}`);
            imgPreview.src = e.target.result;
            imgPreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

/* Função para atualizar a forma de pagamento */
function atualizarFormaPagamento() {
    const formaPagamento = document.getElementById('forma_pagamento').value;
    const detalhesPagamentoDiv = document.getElementById('detalhes_pagamento');

    if (formaPagamento === 'Parcelado') {
        detalhesPagamentoDiv.innerHTML = `
            <label for="entrada">Entrada (R$):</label>
            <input type="number" id="entrada" name="entrada" step="0.01" required>

            <label for="num_parcelas">Número de Parcelas:</label>
            <input type="number" id="num_parcelas" name="num_parcelas" min="1" required>
        `;
    } else {
        detalhesPagamentoDiv.innerHTML = '';
    }
}
