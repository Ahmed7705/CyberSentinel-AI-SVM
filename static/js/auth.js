(function () {
  const form = document.querySelector('.login-form');
  if (!form) return;
  form.addEventListener('submit', () => {
    form.classList.add('is-loading');
  });
})();
