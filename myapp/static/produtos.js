document.addEventListener('DOMContentLoaded', function () {
  carregarProdutos();
});

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
      console.log(produtos); 
      const tabelaProdutos = document.getElementById('produto-list');
      tabelaProdutos.innerHTML = '';
      produtos.forEach(produto => {
          const linha = document.createElement('tr');
                linha.innerHTML = `
          <td>${produto[0]}</td>
          <td>${produto[1]}</td>
          <td>R$ ${parseFloat(produto[2]).toFixed(2)}</td>
          <td><img src="/uploads/${produto[3].split('\\').pop()}" alt="${produto[1]}" width="50" height="50"></td>
          <td>
          
            
          </td>
`;



          tabelaProdutos.appendChild(linha);
      });
  })
  .catch(error => console.error('Erro ao carregar produtos:', error));
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




