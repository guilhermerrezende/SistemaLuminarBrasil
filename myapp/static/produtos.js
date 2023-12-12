document.addEventListener('DOMContentLoaded', function () {
    carregarProdutos();
    document.getElementById('searchInput').addEventListener('keyup', function(event) {
        filtrarProdutos(event.target.value);
    });
});
function exibirProdutos(produtos) {
    const tabelaProdutos = document.getElementById('produto-list');
    tabelaProdutos.innerHTML = '';

    produtos.forEach(produto => {
        const linha = document.createElement('tr');
        const imagePath = produto[3] ? `/uploads/${produto[3].split('\\').pop()}` : 'path/to/default/image.jpg';
        const precoFormatado = parseFloat(produto[2]).toFixed(2);
        
        linha.innerHTML = `
            <td>${produto[0]}</td>
            <td>${produto[1]}</td>
            <td>R$ ${precoFormatado}</td>
            <td>${produto[3] ? `<img src="http://www.sistemaluminarbrasil.com.br${imagePath}" alt="${produto[1]}" width="50" height="50">` : 'Sem imagem'}</td>
        `;

        tabelaProdutos.appendChild(linha);
    });
}

function carregarProdutos() {
    fetch('/get_produtos', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(produtos => {
        const tabelaProdutos = document.getElementById('produto-list');
        tabelaProdutos.innerHTML = '';

        produtos.forEach(produto => {
            const linha = document.createElement('tr');
            const imagePath = produto[3] ? `/uploads/${produto[3].split('\\').pop()}` : 'path/to/default/image.jpg';
            const precoFormatado = parseFloat(produto[2]).toFixed(2);

            linha.innerHTML = `
                <td>${produto[0]}</td>
                <td>${produto[1]}</td>
                <td>R$ ${precoFormatado}</td>
                <td>${produto[3] ? `<img src="http://www.sistemaluminarbrasil.com.br${imagePath}" alt="${produto[1]}" width="50" height="50">` : 'Sem imagem'}</td>
                <td></td>
            `;

            tabelaProdutos.appendChild(linha);
        });
    })
    .catch(error => console.error('Erro ao carregar produtos:', error));
}


  function filtrarProdutos(query) {
    fetch(`/filtrar_produtos?query=${query}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(produtos => {
        exibirProdutos(produtos); // Chama exibirProdutos com os produtos filtrados
    })
    .catch(error => console.error('Erro ao filtrar produtos:', error));
}

  function excluirProduto(id) {
    if (confirm('Tem certeza de que deseja excluir este produto?')) {
        fetch(`/delete_produto/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Produto excluído com sucesso!');
                carregarProdutos();
            } else {
                alert(`Erro ao excluir produto: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Erro ao excluir produto:', error);
            alert('Erro ao excluir produto. Por favor, verifique o console para mais detalhes.');
        });
    }
  }
  
  
  
  
  function editarProduto(id) {
    window.location.href = `/editar_produto/${id}`;
  }
  
  
  