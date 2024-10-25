document.addEventListener('DOMContentLoaded', carregarComissoes);

/**
 * Carrega as comissões e exibe na tabela.
 */
function carregarComissoes() {
    fetch('/comissoes')
        .then(response => response.json())
        .then(comissoes => exibirComissoes(comissoes))
        .catch(error => console.error('Erro ao carregar comissões:', error));
}

/**
 * Renderiza as comissões na tabela.
 * @param {Array} comissoes Lista de comissões
 */
function exibirComissoes(comissoes) {
    const comissoesList = document.getElementById('comissoes-list');
    comissoesList.innerHTML = '';

    let totalComissoes = 0;
    comissoes.forEach(comissao => {
        const valorComissao = calcularValorComissao(comissao);
        totalComissoes += valorComissao;

        comissoesList.innerHTML += `
            <tr>
                <td>${comissao.numeropedido}</td>
                <td>${comissao.data}</td>
                <td>${comissao.valor}</td>
                <td>${comissao.comissaopercentual}</td>
                <td>${valorComissao.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editarComissao(${comissao.id})">Editar</button>
                    <button class="btn btn-sm btn-danger" onclick="excluirComissao(${comissao.id})">Excluir</button>
                </td>
            </tr>
        `;
    });

    localStorage.setItem("totalComissoes", totalComissoes.toFixed(2));
}

/**
 * Calcula o valor da comissão.
 * @param {Object} comissao Objeto de comissão
 * @returns {number} Valor da comissão calculado
 */
function calcularValorComissao(comissao) {
    return comissao.valor * (comissao.comissaopercentual / 100);
}

/**
 * Preenche o formulário de edição com os dados da comissão e abre o modal.
 * @param {number} comissaoId ID da comissão a ser editada
 */
function editarComissao(comissaoId) {
    fetch(`/get_comissao/${comissaoId}`)
        .then(response => response.json())
        .then(comissao => {
            document.getElementById('editComissaoId').value = comissaoId;
            document.getElementById('editNumeroPedido').value = comissao.numeropedido;
            document.getElementById('editDataPedido').value = comissao.data;
            document.getElementById('editValorVenda').value = comissao.valor;
            document.getElementById('editComissao').value = comissao.comissaopercentual;
            abrirModal();
        })
        .catch(error => console.error('Erro ao carregar comissão:', error));
}

/**
 * Abre o modal de edição.
 */
function abrirModal() {
    document.getElementById('editModal').style.display = 'block';
}

/**
 * Fecha o modal de edição.
 */
function fecharModal() {
    document.getElementById('editModal').style.display = 'none';
}

/**
 * Salva as alterações feitas na comissão.
 */
function salvarEdicaoComissao() {
    const comissaoId = document.getElementById('editComissaoId').value;
    const numeropedido = document.getElementById('editNumeroPedido').value;
    const data = document.getElementById('editDataPedido').value;
    const valor = document.getElementById('editValorVenda').value;
    const comissaopercentual = document.getElementById('editComissao').value;

    fetch('/atualizar_comissao', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comissaoId, numeropedido, data, valor, comissaopercentual })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fecharModal();
        carregarComissoes();
    })
    .catch(error => console.error('Erro ao salvar alterações:', error));
}

/**
 * Exclui uma comissão.
 * @param {number} comissaoId ID da comissão a ser excluída
 */
function excluirComissao(comissaoId) {
    fetch('/excluir_comissao', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comissaoId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        carregarComissoes();
    })
    .catch(error => console.error('Erro ao excluir comissão:', error));
}
