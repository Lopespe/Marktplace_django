const salesData = {
  labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
  values: [25000, 32000, 28000, 45000, 38000, 52000],
  items: [150, 200, 175, 280, 230, 320],
  orders: [85, 110, 95, 160, 135, 180]
};

let currentChart = null;
let trendChart = null;

// Configurações dos gráficos
Chart.defaults.color = 'white';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

function initializeData() {
  const totalRevenue = salesData.values.reduce((a, b) => a + b, 0);
  const totalItems = salesData.items.reduce((a, b) => a + b, 0);
  const totalOrders = salesData.orders.reduce((a, b) => a + b, 0);
  const averageTicket = totalRevenue / totalOrders;

  // Animação dos números
  animateValue('totalRevenue', 0, totalRevenue, 2000, (val) => `R$ ${val.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
  animateValue('totalItems', 0, totalItems, 1500, (val) => val.toLocaleString('pt-BR'));
  animateValue('totalOrders', 0, totalOrders, 1200, (val) => val.toLocaleString('pt-BR'));
  animateValue('averageTicket', 0, averageTicket, 2200, (val) => `R$ ${val.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);

  // Estatísticas adicionais
  const bestMonthIndex = salesData.values.indexOf(Math.max(...salesData.values));
  document.getElementById('bestMonth').textContent = salesData.labels[bestMonthIndex];

  const growth = ((salesData.values[salesData.values.length - 1] - salesData.values[0]) / salesData.values[0] * 100).toFixed(1);
  document.getElementById('growth').textContent = `+${growth}%`;

  document.getElementById('goalAchieved').textContent = '87%';
  document.getElementById('nextGoal').textContent = 'R$ 60.000';
}

function animateValue(id, start, end, duration, formatter) {
  const element = document.getElementById(id);
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    const current = start + (end - start) * easeOutQuart;

    element.textContent = formatter(current);

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

function createChart(type = 'bar') {
  const ctx = document.getElementById('salesChart');

  if (currentChart) {
    currentChart.destroy();
  }

  const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
  gradient.addColorStop(1, 'rgba(118, 75, 162, 0.4)');

  currentChart = new Chart(ctx, {
    type: type,
    data: {
      labels: salesData.labels,
      datasets: [{
        label: 'Vendas (R$)',
        data: salesData.values,
        backgroundColor: type === 'doughnut' ? [
          '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b'
        ] : gradient,
        borderColor: '#667eea',
        borderWidth: 2,
        tension: 0.4,
        fill: type === 'line'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: 'white', font: { size: 12 } }
        }
      },
      scales: type !== 'doughnut' ? {
        y: {
          beginAtZero: true,
          ticks: {
            color: 'rgba(255, 255, 255, 0.8)',
            callback: function (value) {
              return 'R$ ' + value.toLocaleString('pt-BR');
            }
          },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        x: {
          ticks: { color: 'rgba(255, 255, 255, 0.8)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      } : {},
      animation: {
        duration: 1500,
        easing: 'easeOutQuart'
      }
    }
  });
}

function createTrendChart() {
  const ctx = document.getElementById('trendChart');

  const trendData = salesData.values.map((val, index) => {
    if (index === 0) return 0;
    return ((val - salesData.values[index - 1]) / salesData.values[index - 1] * 100);
  });

  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: salesData.labels.slice(1),
      datasets: [{
        label: 'Crescimento (%)',
        data: trendData.slice(1),
        borderColor: '#f093fb',
        backgroundColor: 'rgba(240, 147, 251, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#f093fb',
        pointBorderColor: 'white',
        pointBorderWidth: 2,
        pointRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: 'white', font: { size: 12 } }
        }
      },
      scales: {
        y: {
          ticks: {
            color: 'rgba(255, 255, 255, 0.8)',
            callback: function (value) {
              return value.toFixed(1) + '%';
            }
          },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        x: {
          ticks: { color: 'rgba(255, 255, 255, 0.8)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeOutQuart'
      }
    }
  });
}

function changeChartType(type) {
  // Atualizar botões
  document.querySelectorAll('.control-btn').forEach(btn => btn.classList.remove('active'));
  event.target.closest('.control-btn').classList.add('active');

  // Recriar gráfico
  createChart(type);
}

// Inicialização
document.addEventListener('DOMContentLoaded', function () {
  initializeData();
  createChart();
  createTrendChart();
});

// Responsividade
window.addEventListener('resize', function () {
  if (currentChart) currentChart.resize();
  if (trendChart) trendChart.resize();
});