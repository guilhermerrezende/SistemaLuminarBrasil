document.addEventListener('DOMContentLoaded', function() {
    const orcamentoId = getOrcamentoIdFromUrl();
    carregarProdutosOrcamento(orcamentoId);
});

// Funções utilitárias
function getOrcamentoIdFromUrl() {
    const pathSegments = window.location.pathname.split('/');
    return pathSegments[pathSegments.length - 1];
}

// S: Princípio da Responsabilidade Única (SRP)
// Cada função é responsável por uma única tarefa, facilitando o entendimento e manutenção.

function adicionarCampoProduto(index) {
    const produtosDiv = document.getElementById('produtosContainer');
    produtosDiv.innerHTML += criarProdutoHTML(index);
    atualizarQuantidadeProdutos();
}

// Função que gera HTML para um novo produto
function criarProdutoHTML(index) {
    return `
        <fieldset id="produto_${index}">
            <legend>Produto ${index + 1}</legend>
            <label for="produto_nome_${index}">Nome do Produto:</label>
            <input type="text" id="produto_nome_${index}" name="produtos[${index}][nome]"><br><br>
            <label for="produto_quantidade_${index}">Quantidade:</label>
            <input type="number" id="produto_quantidade_${index}" name="produtos[${index}][quantidade]"><br><br>
            <label for="produto_preco_${index}">Preço do Produto:</label>
            <input type="number" id="produto_preco_${index}" name="produtos[${index}][preco_produto]" step="0.01"><br><br>
            <input type="file" name="produtos[${index}][imagem]" id="imagem${index}" onchange="atualizarPreviewImagem(this, ${index})"><br><br>
            <button type="button" onclick="removerCampoProduto(${index})">Remover Produto</button>
        </fieldset>
    `;
}

// O: Princípio do Aberto/Fechado (OCP)
// As funções `adicionarCampoProduto` e `criarProdutoHTML` podem ser facilmente estendidas sem modificá-las.

function atualizarPreviewImagem(input, index) {
    const preview = document.getElementById(`imagem_preview_${index}`);
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// L: Princípio de Substituição de Liskov (LSP)
// Esta função é simples e não viola LSP, pois `adicionarProduto` pode chamar `adicionarCampoProduto` sem alterar o comportamento.

function adicionarProduto() {
    const produtosDiv = document.getElementById('produtosContainer');
    const novoIndex = produtosDiv.childElementCount;
    adicionarCampoProduto(novoIndex);
    atualizarQuantidadeProdutos();
}

// Função para atualizar o total de produtos
function atualizarQuantidadeProdutos() {
    const produtosDiv = document.getElementById('produtosContainer');
    document.getElementById('quantidade_produtos').value = produtosDiv.childElementCount;
}

// Função para carregar os produtos de um orçamento específico
function carregarProdutosOrcamento(orcamentoId) {
    fetch(`/get_produtos_orcamento/${orcamentoId}`, { method: 'GET' })
        .then(response => response.json())
        .then(produtos => renderizarProdutos(produtos))
        .catch(error => {
            console.error(error);
            alert('Não foi possível carregar os produtos do orçamento.');
        });
}

// Função para renderizar produtos na página
function renderizarProdutos(produtos) {
    const produtosDiv = document.getElementById('produtosContainer');
    produtos.forEach((produto, index) => {
        produtosDiv.innerHTML += criarProdutoHTMLParaEdicao(produto, index);
    });
    atualizarQuantidadeProdutos();
}

// Função para criar HTML de produtos já existentes
function criarProdutoHTMLParaEdicao(produto, index) {
    const imagemSrc = produto.caminho_imagem ? `/uploads/${produto.caminho_imagem.split('/').pop()}` : '';
    return `
        <fieldset id="produto_${index}">
            <legend>Produto ${index + 1}</legend>
            <input type="hidden" name="produtos[${index}][id]" value="${produto.id}">
            <label for="produto_nome_${index}">Nome do Produto:</label>
            <input type="text" id="produto_nome_${index}" name="produtos[${index}][nome]" value="${produto.nome}"><br><br>
            <label for="produto_quantidade_${index}">Quantidade:</label>
            <input type="number" id="produto_quantidade_${index}" name="produtos[${index}][quantidade]" value="${produto.quantidade}"><br><br>
            <label for="produto_preco_${index}">Preço do Produto:</label>
            <input type="number" id="produto_preco_${index}" name="produtos[${index}][preco_produto]" value="${produto.preco_unitario}" step="0.01"><br><br>
            ${imagemSrc ? `<img src="${imagemSrc}" id="imagem_preview_${index}" style="max-width: 100px; max-height: 100px;"><br><br>` : ''}
            <input type="file" name="produtos[${index}][imagem]" id="imagem${index}" onchange="atualizarPreviewImagem(this, ${index})"><br><br>
            <button type="button" onclick="excluirProduto(${index}, ${produto.id})">Excluir Produto</button>
        </fieldset>
    `;
}

// Função para excluir um produto do orçamento
function excluirProduto(index, produtoId) {
    if (!confirm("Tem certeza que deseja excluir este produto?")) return;
    fetch(`/excluir_produto/${produtoId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById(`produto_${index}`).remove();
                atualizarQuantidadeProdutos();
            } else {
                alert('Erro ao excluir produto');
            }
        })
        .catch(error => console.error('Erro ao excluir produto:', error));
}

// I: Princípio da Segregação de Interface (ISP)
// A função `carregarProdutosOrcamento` só depende de dados necessários, sem sobrecarga de interfaces.

// D: Princípio da Inversão de Dependência (DIP)
// Não aplicável diretamente no JavaScript, mas a estrutura do código permite adaptação ao backend.

document.getElementById('editOrcamentoForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const orcamentoId = getOrcamentoIdFromUrl();
    const formData = new FormData(this);

    fetch(`/editar_orcamento/${orcamentoId}`, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) throw new Error('Erro na resposta da rede');
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
        alert('Erro ao atualizar orçamento. Verifique a conexão e tente novamente.');
    });
});
