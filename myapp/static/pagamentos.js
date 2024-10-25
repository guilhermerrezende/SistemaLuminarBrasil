function atualizarFormaPagamento() {
    const formaPagamento = document.getElementById('forma_pagamento').value;
    const detalhesPagamentoDiv = document.getElementById('detalhesPagamentoContainer');
    
    detalhesPagamentoDiv.innerHTML = formaPagamento === 'Parcelado' ? `
        <label for="num_parcelas">Número de Parcelas:</label>
        <input type="number" id="num_parcelas" name="num_parcelas" min="1"><br><br>
        <label for="entrada">Entrada:</label>
        <input type="number" id="entrada" name="entrada" step="0.01"><br><br>
    ` : '';
}
