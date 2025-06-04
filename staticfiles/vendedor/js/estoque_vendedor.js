// Função para incrementar estoque
function incrementarEstoque(btn) {
  const input = btn.parentElement.querySelector('.input-estoque');
  input.value = parseInt(input.value) + 1;
  atualizarStatus(input);
  atualizarEstatisticas();
}

// Função para decrementar estoque
function decrementarEstoque(btn) {
  const input = btn.parentElement.querySelector('.input-estoque');
  if (parseInt(input.value) > 0) {
    input.value = parseInt(input.value) - 1;
    atualizarStatus(input);
    atualizarEstatisticas();
  }
}

// Função para atualizar status do produto
function atualizarStatus(input) {
  const produto = input.closest('.produto');
  const statusBadge = produto.querySelector('.status-badge');
  const valor = parseInt(input.value);

  statusBadge.className = 'status-badge ';

  if (valor <= 2) {
    statusBadge.classList.add('status-critico');
    statusBadge.textContent = 'Estoque Crítico';
  } else if (valor <= 10) {
    statusBadge.classList.add('status-baixo');
    statusBadge.textContent = 'Estoque Baixo';
  } else {
    statusBadge.classList.add('status-ok');
    statusBadge.textContent = 'Estoque OK';
  }
}

// Função para atualizar estatísticas
function atualizarEstatisticas() {
  const inputs = document.querySelectorAll('.input-estoque');
  let totalProdutos = inputs.length;
  let totalEstoque = 0;
  let estoqueBaixo = 0;

  inputs.forEach(input => {
    const valor = parseInt(input.value);
    totalEstoque += valor;
    if (valor <= 10) estoqueBaixo++;
  });

  document.getElementById('total-produtos').textContent = totalProdutos;
  document.getElementById('total-estoque').textContent = totalEstoque;
  document.getElementById('estoque-baixo').textContent = estoqueBaixo;
}

// Função de busca
function filtrarProdutos() {
  const searchTerm = document.getElementById('search-input').value.toLowerCase();
  const produtos = document.querySelectorAll('.produto');

  produtos.forEach(produto => {
    const nome = produto.dataset.nome || produto.querySelector('.produto-nome').textContent.toLowerCase();
    if (nome.includes(searchTerm)) {
      produto.style.display = 'block';
    } else {
      produto.style.display = 'none';
    }
  });
}

// Event listeners
document.getElementById('search-input').addEventListener('input', filtrarProdutos);

// Inicializar página
document.addEventListener('DOMContentLoaded', function () {
  // Atualizar status inicial de todos os produtos
  document.querySelectorAll('.input-estoque').forEach(input => {
    atualizarStatus(input);
  });

  // Atualizar estatísticas iniciais
  atualizarEstatisticas();

  // Animação de entrada para os produtos
  const produtos = document.querySelectorAll('.produto');
  produtos.forEach((produto, index) => {
    produto.style.opacity = '0';
    produto.style.transform = 'translateY(20px)';
    setTimeout(() => {
      produto.style.transition = 'all 0.5s ease';
      produto.style.opacity = '1';
      produto.style.transform = 'translateY(0)';
    }, index * 100);
  });
});

// Confirmação antes de enviar o formulário
document.getElementById('estoque-form').addEventListener('submit', function (e) {
  const confirmacao = confirm('Tem certeza que deseja atualizar todos os estoques?');
  if (!confirmacao) {
    e.preventDefault();
  }
});