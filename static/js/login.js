document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const messageBox = document.getElementById('login-message');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = {
      username: formData.get('username'),
      pin: formData.get('pin')
    };

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (!response.ok || !data.success) {
        messageBox.textContent = data.message || 'Login failed.';
        messageBox.className = 'status-message error';
        return;
      }

      messageBox.textContent = 'PIN verified. Redirecting to face verification...';
      messageBox.className = 'status-message success';
      window.location.href = '/face-verification';
    } catch (error) {
      messageBox.textContent = 'Login request failed.';
      messageBox.className = 'status-message error';
    }
  });
});
