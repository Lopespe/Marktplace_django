// marketplace/static/vendedor/js/dashboard_vendedor.js
document.addEventListener('DOMContentLoaded', function() {
  const labelsDataElement = document.getElementById('vendedor-chart-labels');
  const valuesDataElement = document.getElementById('vendedor-chart-data');
  const ctxSales = document.getElementById('salesChartVendedor');

  if (labelsDataElement && valuesDataElement && ctxSales) {
      const labelsData = JSON.parse(labelsDataElement.textContent);
      const valuesData = JSON.parse(valuesDataElement.textContent);

      new Chart(ctxSales, {
          type: 'line', // Pode ser 'bar' se preferir
          data: {
              labels: labelsData,
              datasets: [{
                  label: 'Vendas (R$)', // Ou outro dado que você queira mostrar
                  data: valuesData,
                  borderColor: '#667eea', // Cor da linha
                  backgroundColor: 'rgba(102, 126, 234, 0.1)', // Cor de preenchimento abaixo da linha
                  borderWidth: 2,
                  fill: true,
                  tension: 0.3
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      display: true,
                      position: 'top',
                      labels: {
                          color: '#333' // Cor dos labels da legenda
                      }
                  }
              },
              scales: {
                  y: {
                      beginAtZero: true,
                      ticks: {
                          color: '#555', // Cor dos ticks do eixo Y
                          // Adicionar prefixo R$ se os dados forem monetários
                          callback: function(value, index, values) {
                              return 'R$ ' + value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                          }
                      },
                      grid: {
                          color: 'rgba(0,0,0,0.05)' // Cor das linhas do grid
                      }
                  },
                  x: {
                      ticks: {
                          color: '#555' // Cor dos ticks do eixo X
                      },
                      grid: {
                          color: 'rgba(0,0,0,0.05)'
                      }
                  }
              }
          }
      });
  } else {
      if (!ctxSales) console.error("Elemento canvas com ID 'salesChartVendedor' não encontrado.");
      if (!labelsDataElement) console.error("Elemento de dados para o gráfico 'vendedor-chart-labels' não encontrado.");
      if (!valuesDataElement) console.error("Elemento de dados para o gráfico 'vendedor-chart-data' não encontrado.");
  }
});