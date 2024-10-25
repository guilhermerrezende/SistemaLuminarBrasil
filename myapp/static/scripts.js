document.addEventListener('DOMContentLoaded', function () {
    renderSalesChart();
});

/**
 * Renderiza o gráfico de vendas no canvas `salesChart`.
 */
function renderSalesChart() {
    const ctx = document.getElementById('salesChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie', 
        data: getSalesChartData(),
        options: getSalesChartOptions()
    });
}

/**
 * Define os dados do gráfico de vendas.
 * @returns {Object} Objeto com dados para o gráfico.
 */
function getSalesChartData() {
    return {
        labels: ['Negociando', 'Fechado', 'Em Transporte', 'Entregue', 'Comissão Recebida', 'Finalizado'],
        datasets: [{
            label: 'Status das Vendas',
            data: [10, 20, 30, 40, 50, 60], // Exemplo de dados; substitua pelos dados reais
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    };
}

/**
 * Define as opções do gráfico de vendas.
 * @returns {Object} Objeto com configurações para o gráfico.
 */
function getSalesChartOptions() {
    return {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Distribuição de Vendas por Status'
            }
        }
    };
}
