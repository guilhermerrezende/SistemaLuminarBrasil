document.addEventListener('DOMContentLoaded', function () {
    carregarOrcamentos();
    document.getElementById('searchInput').addEventListener('keyup', function(event) {
        filtrarOrcamentos(event.target.value);
    });
});

// Função para carregar todos os orçamentos
function carregarOrcamentos() {
    fetchOrcamentos('/get_orcamentos')
        .then(orcamentos => exibirOrcamentos(orcamentos))
        .catch(error => console.error('Erro ao carregar orçamentos:', error));
}

// Função para filtrar orçamentos de acordo com a query de pesquisa
function filtrarOrcamentos(query) {
    fetchOrcamentos(`/filtrar_orcamentos?query=${query}`)
        .then(orcamentos => exibirOrcamentos(orcamentos))
        .catch(error => console.error('Erro ao filtrar orçamentos:', error));
}

// Função para buscar orçamentos da API
function fetchOrcamentos(url) {
    return fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    }).then(response => response.json());
}

// Exibe os orçamentos na tabela
function exibirOrcamentos(orcamentos) {
    const tabelaOrcamentos = document.getElementById('orcamento-list');
    tabelaOrcamentos.innerHTML = '';

    orcamentos.forEach(orcamento => {
        const linha = document.createElement('tr');
        linha.innerHTML = `
            <td>${orcamento[1]}</td>
            <td>${formatarData(orcamento[4])}</td>
            <td>
                <button onclick="editarOrcamento(${orcamento[0]})">Editar</button>
                <button onclick="excluirOrcamento(${orcamento[0]})">Excluir</button>
            </td>
        `;
        tabelaOrcamentos.appendChild(linha);
    });
}

// Formata a data no formato brasileiro
function formatarData(dataStr) {
    if (!dataStr || typeof dataStr !== 'string') return 'Data não disponível';
    const data = new Date(dataStr);
    return isNaN(data.getTime()) ? 'Data não disponível' : data.toLocaleDateString('pt-BR');
}

// Redireciona para a página de edição do orçamento
function editarOrcamento(id) {
    window.location.href = `/editar_orcamento/${id}`;
}

// Exclui um orçamento e atualiza a lista
function excluirOrcamento(id) {
    if (!confirm('Tem certeza de que deseja excluir este orçamento?')) return;

    fetch(`/delete_orcamento/${id}`, { method: 'DELETE', headers: { 'Content-Type': 'application/json' } })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Orçamento excluído com sucesso!');
                carregarOrcamentos();
            } else {
                alert(`Erro ao excluir orçamento: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Erro ao excluir orçamento:', error);
            alert('Erro ao excluir orçamento. Por favor, verifique o console para mais detalhes.');
        });
}
