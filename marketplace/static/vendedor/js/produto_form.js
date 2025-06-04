// Funcionalidade para upload de arquivos
document.addEventListener('DOMContentLoaded', function () {
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach(input => {
    const wrapper = input.closest('.file-input-wrapper');
    const label = wrapper.querySelector('.file-input-label');
    const span = label.querySelector('span');
    const originalText = span.textContent;

    input.addEventListener('change', function () {
      if (this.files && this.files.length > 0) {
        span.textContent = `Arquivo selecionado: ${this.files[0].name}`;
        label.style.borderColor = '#43e97b';
        label.style.backgroundColor = 'rgba(67, 233, 123, 0.1)';
      } else {
        span.textContent = originalText;
        label.style.borderColor = '';
        label.style.backgroundColor = '';
      }
    });

    // Drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      wrapper.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      wrapper.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      wrapper.addEventListener(eventName, unhighlight, false);
    });

    wrapper.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    function highlight() {
      label.style.borderColor = '#667eea';
      label.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
    }

    function unhighlight() {
      label.style.borderColor = '';
      label.style.backgroundColor = '';
    }

    function handleDrop(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      input.files = files;

      if (files.length > 0) {
        span.textContent = `Arquivo selecionado: ${files[0].name}`;
        label.style.borderColor = '#43e97b';
        label.style.backgroundColor = 'rgba(67, 233, 123, 0.1)';
      }
    }
  });

  // Loading state no botão de submit
  const form = document.getElementById('productForm');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('span');
  const loading = submitBtn.querySelector('.loading');

  form.addEventListener('submit', function () {
    submitBtn.disabled = true;
    btnText.style.opacity = '0';
    loading.style.display = 'block';
  });

  // Validação em tempo real
  const requiredFields = document.querySelectorAll('.form-control[required]');
  requiredFields.forEach(field => {
    field.addEventListener('blur', function () {
      if (!this.value.trim()) {
        this.classList.add('error');
      } else {
        this.classList.remove('error');
      }
    });

    field.addEventListener('input', function () {
      if (this.classList.contains('error') && this.value.trim()) {
        this.classList.remove('error');
      }
    });
  });
});