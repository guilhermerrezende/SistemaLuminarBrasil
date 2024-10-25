document.addEventListener('DOMContentLoaded', function () {
    carregarProdutos();
    document.getElementById('searchInput').addEventListener('keyup', function(event) {
        filtrarProdutos(event.target.value);
    });
});

// Função para exibir produtos na tabela
function exibirProdutos(produtos) {
    const tabelaProdutos = document.getElementById('produto-list');
    tabelaProdutos.innerHTML = '';

    produtos.forEach(produto => {
        const linha = document.createElement('tr');
        linha.innerHTML = criarLinhaProduto(produto);
        tabelaProdutos.appendChild(linha);
    });
}

// Função para criar a linha de produto em HTML
function criarLinhaProduto(produto) {
    const imagePath = produto[3] 
        ? `http://www.sistemaluminarbrasil.com.br/uploads/${produto[3].split('/').pop()}` 
        : 'path/to/default/image.jpg';
    return `
        <td>${produto[0]}</td>
        <td>${produto[1]}</td>
        <td>R$ ${parseFloat(produto[2]).toFixed(2)}</td>
        <td>${produto[3] ? `<img src="${imagePath}" alt="${produto[1]}" width="50" height="50">` : 'Sem imagem'}</td>
    `;
}

// Função para carregar todos os produtos
function carregarProdutos() {
    fetchProdutos('/get_produtos')
        .then(produtos => exibirProdutos(produtos))
        .catch(error => console.error('Erro ao carregar produtos:', error));
}

// Função para filtrar produtos por consulta de pesquisa
function filtrarProdutos(query) {
    fetchProdutos(`/filtrar_produtos?query=${query}`)
        .then(produtos => exibirProdutos(produtos))
        .catch(error => console.error('Erro ao filtrar produtos:', error));
}

// Função para fazer a requisição dos produtos
function fetchProdutos(url) {
    return fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    }).then(response => response.json());
}

document.addEventListener('DOMContentLoaded', () => {
    carregarProdutos();
});

function carregarProdutos() {
    fetch('/get_produtos')
        .then(response => response.json())
        .then(produtos => {
            const produtosDiv = document.getElementById('produtosContainer');
            produtos.forEach((produto, index) => {
                produtosDiv.innerHTML += `
                    <fieldset id="produto_${index}">
                        <legend>Produto ${index + 1}</legend>
                        <input type="text" id="produto_nome_${index}" name="produtos[${index}][nome]" value="${produto.nome}">
                        <!-- Campos adicionais de produto -->
                    </fieldset>
                `;
            });
        })
        .catch(error => console.error('Erro ao carregar produtos:', error));
}
