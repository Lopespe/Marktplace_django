// marketplace/static/admin/js/dashboard_admin_charts.js
document.addEventListener('DOMContentLoaded', function () {
  const labelsDataElement = document.getElementById('chart-labels-data');
  const valuesDataElement = document.getElementById('chart-values-data');

  // Verifica se os elementos com os dados existem antes de tentar usá-los
  if (labelsDataElement && valuesDataElement) {
    const labelsData = JSON.parse(labelsDataElement.textContent);
    const valuesData = JSON.parse(valuesDataElement.textContent);

    const ctx = document.getElementById('chart').getContext('2d');
    if (ctx) { // Verifica se o canvas do gráfico existe
      new Chart(ctx, {
        type: 'bar', // Ou 'line' se preferir para tendência
        data: {
          labels: labelsData,
          datasets: [{
            label: 'Novos Usuários Cadastrados',
            data: valuesData,
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: true,
              position: 'top',
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1 // Garante que o eixo Y mostre apenas inteiros
              }
            }
          }
        }
      });
    } else {
      console.error("Elemento canvas com ID 'chart' não encontrado.");
    }
  } else {
    console.error("Elementos de dados para o gráfico ('chart-labels-data' ou 'chart-values-data') não encontrados.");
  }
});