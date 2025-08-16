document.addEventListener('DOMContentLoaded', function () {
  const loginBtn = document.getElementById('login-btn');
  const loginBtnSecondary = document.getElementById('login-btn-secondary');
  const loginModal = document.getElementById('login-modal');
  const closeLogin = document.getElementById('close-login');

  function openModal() {
    loginModal.classList.remove('hidden');
  }
  function closeModal() {
    loginModal.classList.add('hidden');
  }

  if (loginBtn) {
    loginBtn.addEventListener('click', openModal);
  }
  if (loginBtnSecondary) {
    loginBtnSecondary.addEventListener('click', openModal);
  }
  if (closeLogin) {
    closeLogin.addEventListener('click', closeModal);
  }
  // Close modal when clicking outside the dialog
  loginModal.addEventListener('click', function (e) {
    if (e.target === loginModal) {
      closeModal();
    }
  });
});