document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        const response = await fetch('/api/logout', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
          window.location.href = '/login';
        }
      } catch (error) {
        window.location.href = '/login';
      }
    });
  }
});
