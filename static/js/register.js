document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const messageBox = document.getElementById('register-message');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = {
      username: formData.get('username'),
      role: formData.get('role'),
      pin: formData.get('pin')
    };

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (!response.ok || !data.success) {
        messageBox.textContent = data.message || 'Registration failed.';
        messageBox.className = 'status-message error';
        return;
      }

      messageBox.textContent = 'Account created. Please continue to face capture.';
      messageBox.className = 'status-message success';
      window.location.href = '/face-verification';
    } catch (error) {
      messageBox.textContent = 'Registration request failed.';
      messageBox.className = 'status-message error';
    }
  });
});
