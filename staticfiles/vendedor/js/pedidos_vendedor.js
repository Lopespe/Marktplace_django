// Search functionality
document.getElementById('searchInput').addEventListener('input', function (e) {
  const searchTerm = e.target.value.toLowerCase();
  const rows = document.querySelectorAll('#pedidosTable tbody tr');

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(searchTerm) ? '' : 'none';
  });
});

// Floating action button
document.querySelector('.floating-action').addEventListener('click', function () {
  this.style.transform = 'rotate(360deg) scale(1.1)';
  setTimeout(() => {
    this.style.transform = '';
    location.reload();
  }, 500);
});

// Add hover effects to table rows
document.querySelectorAll('tbody tr').forEach(row => {
  row.addEventListener('mouseenter', function () {
    this.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.15)';
  });

  row.addEventListener('mouseleave', function () {
    this.style.boxShadow = '';
  });
});