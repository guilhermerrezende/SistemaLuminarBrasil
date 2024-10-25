document.getElementById('gerarPdfBtn').addEventListener('click', () => {
    const formData = new FormData(document.getElementById('editOrcamentoForm'));
    gerarPDF(formData);
});

function gerarPDF(formData) {
    fetch('/gerar_orcamento', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Problema ao gerar PDF');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
    })
    .catch(error => console.error('Erro ao gerar PDF:', error));
}
