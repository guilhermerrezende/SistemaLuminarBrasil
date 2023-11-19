document.addEventListener('DOMContentLoaded', function() {
    const orcamentoId = getOrcamentoIdFromUrl();
    carregarProdutosOrcamento(orcamentoId);
});

function getOrcamentoIdFromUrl() {
    const path = window.location.pathname;
    const pathSegments = path.split('/');
    return pathSegments[pathSegments.length - 1];
}

function carregarProdutosOrcamento(orcamentoId) {
    fetch(`/get_produtos_orcamento/${orcamentoId}`, { method: 'GET' })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao buscar produtos do orçamento');
        }
        return response.json();
    })
    .then(produtos => {
        const produtosDiv = document.getElementById('produtosContainer');
        produtos.forEach((produto, index) => {
            produtosDiv.innerHTML += `
                <fieldset>
                    <legend>Produto ${index + 1}</legend>
                    <input type="hidden" name="produtos[${index}][id]" value="${produto.id}">
                    <label for="produto_nome_${index}">Nome do Produto:</label>
                    <input type="text" id="produto_nome_${index}" name="produtos[${index}][nome]" value="${produto.nome}"><br><br>
                    <label for="produto_quantidade_${index}">Quantidade:</label>
                    <input type="number" id="produto_quantidade_${index}" name="produtos[${index}][quantidade]" value="${produto.quantidade}"><br><br>
                    <label for="produto_preco_${index}">Preço do Produto:</label>
                    <input type="number" id="produto_preco_${index}" name="produtos[${index}][preco_produto]" value="${produto.preco_unitario}" step="0.01"><br><br>
                    
                    <td><img src="/uploads/${produto.caminho_imagem.split('\\').pop()}" alt="Imagem do Produto" width="50" height="50"></td> 
                    <input type="file" id="produto_imagem_${index}" name="produtos[${index}][imagem]"><br><br>
                </fieldset>
            `;
        });
    })
    .catch(error => {
        console.error(error);
        alert('Não foi possível carregar os produtos do orçamento.');
    });
}

document.getElementById('editOrcamentoForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let formData = new FormData(this);

    const orcamentoId = getOrcamentoIdFromUrl();

    fetch(`/editar_orcamento/${orcamentoId}`, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            alert('Orçamento atualizado com sucesso!');
            window.location.href = '/orcamentos';
        } else {
            alert('Erro ao atualizar orçamento. Por favor, tente novamente.');
        }
    })
    .catch(error => {
        console.error('Erro ao atualizar orçamento:', error);
        alert('Erro ao atualizar orçamento. Por favor, verifique a conexão e tente novamente.');
    });
});
