document.addEventListener('DOMContentLoaded', () => {
  const preview = document.getElementById('camera-preview');
  const statusEl = document.getElementById('camera-status');
  const messageBox = document.getElementById('face-message');
  const confidenceValue = document.getElementById('confidence-value');
  const startCameraBtn = document.getElementById('start-camera');
  const verifyBtn = document.getElementById('verify-face');

  let stream = null;
  let isCameraReady = false;

  const setStatus = (text, tone = 'info') => {
    statusEl.textContent = text;
    statusEl.style.color = tone === 'error' ? '#ef6b6b' : '#edf6ff';
  };

  const setMessage = (text, type = 'info') => {
    messageBox.textContent = text;
    messageBox.className = `status-message ${type}`;
  };

  const startCamera = async () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      stream = mediaStream;
      preview.srcObject = stream;
      isCameraReady = true;
      setStatus('Camera active');
      setMessage('Camera ready. Click verify identity when you are ready.', 'success');
    } catch (error) {
      isCameraReady = false;
      setStatus('Camera unavailable or permission denied', 'error');
      setMessage('Webcam permission was denied or is unavailable.', 'error');
    }
  };

  const captureFrame = () => new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    canvas.width = preview.videoWidth || 640;
    canvas.height = preview.videoHeight || 480;
    context.drawImage(preview, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('Unable to capture a JPEG frame from the webcam.'));
        return;
      }
      resolve(blob);
    }, 'image/jpeg', 0.85);
  });

  const verifyFace = async () => {
    if (!isCameraReady) {
      setMessage('Start the camera before verifying.', 'error');
      return;
    }

    const blob = await captureFrame();
    const formData = new FormData();
    formData.append('image', blob, 'face.jpg');

    try {
      const response = await fetch('/api/face/verify', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      if (!data.success || !data.verified) {
        setMessage(data.message || 'Face not recognized.', 'error');
        confidenceValue.textContent = data.confidence ? `${data.confidence}%` : '--';
        return;
      }

      setMessage(data.message || 'Identity verified.', 'success');
      confidenceValue.textContent = `${data.confidence}%`;
      window.location.href = '/dashboard';
    } catch (error) {
      setMessage('Verification request failed.', 'error');
    }
  };

  startCameraBtn.addEventListener('click', startCamera);
  verifyBtn.addEventListener('click', verifyFace);
  startCamera();
});
