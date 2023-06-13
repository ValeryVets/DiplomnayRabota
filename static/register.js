window.onload = function() {
  const form = document.getElementById('register-form');
  const errorContainer = document.querySelector('.error-container');
  const errorMessage = document.getElementById('error-message');
  const errorArrow = document.querySelector('.error-arrow');

  form.addEventListener('submit', function(event) {
    // Проверяем валидность формы
    if (!form.checkValidity()) {
      event.preventDefault();
      const firstInvalidInput = form.querySelector(':invalid');
      const inputRect = firstInvalidInput.getBoundingClientRect();

      // Устанавливаем позицию блока с ошибкой
      errorContainer.style.top = `${inputRect.top + window.pageYOffset - errorContainer.offsetHeight}px`;
      errorContainer.style.left = `${inputRect.left + inputRect.width / 2}px`;

      // Устанавливаем сообщение об ошибке
      errorMessage.textContent = firstInvalidInput.validationMessage;

      // Показываем блок с ошибкой и стрелку
      errorContainer.classList.add('show');
      errorArrow.classList.add('show');
    }
  });

  form.addEventListener('input', function(event) {
    const target = event.target;
    if (target.nodeName.toLowerCase() !== 'input') return;

    // Скрываем блок с ошибкой при изменении поля ввода
    errorContainer.classList.remove('show');
    errorArrow.classList.remove('show');
  });

  // Закрываем блок с ошибкой и стрелку при клике в любом месте документа
  document.addEventListener('click', function(event) {
    if (!form.contains(event.target)) {
      errorContainer.classList.remove('show');
      errorArrow.classList.remove('show');
    }
  });
};
