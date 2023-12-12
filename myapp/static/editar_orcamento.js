document.addEventListener('DOMContentLoaded', function() {
    const orcamentoId = getOrcamentoIdFromUrl();
    carregarProdutosOrcamento(orcamentoId);
});

function getOrcamentoIdFromUrl() {
    const path = window.location.pathname;
    const pathSegments = path.split('/');
    return pathSegments[pathSegments.length - 1];
}
function adicionarCampoProduto(index) {
    const produtosDiv = document.getElementById('produtosContainer');
    const novoProdutoHTML = `

        <fieldset id="produto_${index}">

            <legend>Produto ${index + 1}</legend>

            <label for="produto_nome_${index}">Nome do Produto:</label>
            
            <input type="text" id="produto_nome_${index}" name="produtos[${index}][nome]"><br><br>
            <label for="produto_quantidade_${index}">Quantidade:</label>
            <input type="number" id="produto_quantidade_${index}" name="produtos[${index}][quantidade]"><br><br>
            <label for="produto_preco_${index}">Preço do Produto:</label>
            <input type="number" id="produto_preco_${index}" name="produtos[${index}][preco_produto]" step="0.01"><br><br>

            <input type="hidden" id="produto_imagem_caminho_${index}" name="algumNome">
            <input type="file" name="produtos[${index}][imagem]" id="imagem${index}" onchange="atualizarPreviewImagem(this, ${index})"><br><br>
            <button type="button" onclick="excluirProduto(${novoIndex})">Excluir Produto</button>

        </fieldset>
    `;
    produtosDiv.innerHTML += novoProdutoHTML;
    atualizarQuantidadeProdutos();
}
function excluirProduto(index, produtoId) {
    if (!confirm("Tem certeza que deseja excluir este produto?")) {
        return;
    }

    fetch(`/excluir_produto/${produtoId}`, {
        
        method: 'POST'
        // Inclua headers, credenciais ou corpo da requisição se necessário
    })
    
    .then(response => response.json())
    .then(data => {
        if (produtoId === undefined || produtoId === null) {
            console.error("Produto ID é undefined ou null");
            return;
        }
        
        if (data.status === 'success') {
            const produtoFieldset = document.getElementById(`produto_${index}`);
            if (produtoFieldset) {
                produtoFieldset.remove();
                atualizarQuantidadeProdutos();
            }
        } else {
            alert('Erro ao excluir produto');
        }
    })
    .catch(error => console.error('Erro ao excluir produto:', error));
}


function adicionarProduto() {
    const produtosDiv = document.getElementById('produtosContainer');
    const numeroProdutos = produtosDiv.childElementCount; // Conta o número de fieldsets de produto
    const novoIndex = numeroProdutos; // Índice do novo produto

    const novoProdutoHTML = `
        <fieldset id="produto_${novoIndex}">
            <legend>Produto ${novoIndex + 1}</legend>
            <label for="produto_nome_${novoIndex}">Nome do Produto:</label>
            <input type="text" id="produto_nome_${novoIndex}" name="produtos[${novoIndex}][nome]"><br><br>
            <label for="produto_quantidade_${novoIndex}">Quantidade:</label>
            <input type="number" id="produto_quantidade_${novoIndex}" name="produtos[${novoIndex}][quantidade]"><br><br>
            <label for="produto_preco_${novoIndex}">Preço do Produto:</label>
            <input type="number" id="produto_preco_${novoIndex}" name="produtos[${novoIndex}][preco_produto]" step="0.01"><br><br>


            <label for="produto_imagem_${novoIndex}">Imagem do Produto:</label>
            <img id="imagem_preview_${novoIndex}" src="" style="display:none; max-width: 100px; max-height: 100px;"><br><br>
            <input type="file" name="produtos[${novoIndex}][imagem]" id="imagem${novoIndex}" onchange="atualizarPreviewImagem(this, ${novoIndex})"><br><br>
            <input type="hidden" id="produto_imagem_caminho_${novoIndex}" name="algumNome">


            <button type="button" onclick="excluirProduto(${novoIndex})">Excluir Produto</button>
            <button type="button" onclick="adicionarProduto()">Adicionar Produto</button>
            <button type="button" onclick="removerCampoProduto(${novoIndex})">Remover Campo</button>
        </fieldset>
    `;
    produtosDiv.innerHTML += novoProdutoHTML;
    atualizarQuantidadeProdutos();
}
function removerCampoProduto(index) {
    const produtoFieldset = document.getElementById(`produto_${index}`);
    if (produtoFieldset) {
        produtoFieldset.remove();
        atualizarQuantidadeProdutos();
    }
}



function atualizarQuantidadeProdutos() {
    const produtosDiv = document.getElementById('produtosContainer');
    const numeroProdutos = produtosDiv.childElementCount;
    const inputQuantidadeProdutos = document.getElementById('quantidade_produtos');
    inputQuantidadeProdutos.value = numeroProdutos;
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

            let imagemSrc = '';

            if (produto.caminho_imagem) {
                if (produto.caminho_imagem.startsWith('/SistemaLuminarBrasil/uploads/')) {
                    imagemSrc = `http://www.sistemaluminarbrasil.com.br${produto.caminho_imagem}`;
                } else {
                    imagemSrc = `http://www.sistemaluminarbrasil.com.br/uploads/${produto.caminho_imagem.split('\\').pop()}`;
                }
            }


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
                    
                    <input type="hidden" name="produtos[${index}][caminho_imagem]" value="${imagemSrc}"> 
                    <td>${imagemSrc ? `<img src="${imagemSrc}" alt="Imagem do Produto" width="50" height="50">` : ''}</td>
                    <input type="file" name="produtos[${index}][imagem]" id="imagem${index}"> <br/><br/>                
                    ${imagemSrc ? `<span>Se não escolher uma nova imagem, a imagem atual será mantida.</span>` : ''}

                    <button type="button" onclick="adicionarProduto()">Adicionar Produto</button>
                    <button type="button" onclick="excluirProduto(${index}, ${produto.id})">Excluir Produto</button>

                </fieldset>
            `;
            
            atualizarQuantidadeProdutos();
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
