function filtrarPorNota(nota) {
  const avaliacoes = document.querySelectorAll('.avaliacao');
  const botoes = document.querySelectorAll('.filter-button');

  // Remove classe active de todos os botões
  botoes.forEach(btn => btn.classList.remove('active'));

  // Adiciona classe active ao botão clicado
  event.target.classList.add('active');

  avaliacoes.forEach(avaliacao => {
    const notaAvaliacao = parseInt(avaliacao.dataset.nota);

    if (nota === 'todas' || notaAvaliacao === nota) {
      avaliacao.style.display = 'block';
      avaliacao.style.animation = 'fadeInUp 0.4s ease forwards';
    } else {
      avaliacao.style.display = 'none';
    }
  });
}

// Adiciona efeito de scroll suave
document.addEventListener('DOMContentLoaded', function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll('.avaliacao').forEach(el => {
    observer.observe(el);
  });
});