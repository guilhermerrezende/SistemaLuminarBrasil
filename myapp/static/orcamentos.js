document.addEventListener('DOMContentLoaded', function () {
    carregarOrcamentos();
    document.getElementById('searchInput').addEventListener('keyup', function(event) {
        filtrarOrcamentos(event.target.value);
    });
});

function carregarOrcamentos() {
    fetch('/get_orcamentos', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(orcamentos => {
        exibirOrcamentos(orcamentos);
    })
    .catch(error => console.error('Erro ao carregar orçamentos:', error));
}

function filtrarOrcamentos(query) {
    fetch(`/filtrar_orcamentos?query=${query}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(orcamentos => {
        exibirOrcamentos(orcamentos);
    })
    .catch(error => console.error('Erro ao filtrar orçamentos:', error));
}

function exibirOrcamentos(orcamentos) {
    const tabelaOrcamentos = document.getElementById('orcamento-list');
    tabelaOrcamentos.innerHTML = '';

    orcamentos.forEach(orcamento => {
        let dataFormatada = 'Data não disponível'; 
        if (orcamento[4] && typeof orcamento[4] === 'string' && orcamento[4].trim() !== '') {
            const data = new Date(orcamento[4]);
            if (!isNaN(data.getTime())) {
                dataFormatada = data.toLocaleDateString('pt-BR');
            }
        }

        const linha = document.createElement('tr');
        linha.innerHTML = `
            <td>${orcamento[1]}</td>
            <td>${dataFormatada}</td>
            <td>
                <button onclick="editarOrcamento(${orcamento[0]})">Editar</button>
                <button onclick="excluirOrcamento(${orcamento[0]})">Excluir</button>
            </td>
        `;
        tabelaOrcamentos.appendChild(linha);
    });
}

function editarOrcamento(id) {
    // Redireciona para a página de edição do orçamento
    window.location.href = `/editar_orcamento/${id}`;
}

function excluirOrcamento(id) {
    if (confirm('Tem certeza de que deseja excluir este orçamento?')) {
        fetch(`/delete_orcamento/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json()) // Converte a resposta em JSON
        .then(data => {
            if (data.status === 'success') {
                alert('Orçamento excluído com sucesso!');
                carregarOrcamentos();
            } else {
                // Exibe a mensagem de erro do servidor
                alert(`Erro ao excluir orçamento: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Erro ao excluir orçamento:', error);
            alert('Erro ao excluir orçamento. Por favor, verifique o console para mais detalhes.');
        });
    }
}





