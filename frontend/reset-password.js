// reset-password.js
document.addEventListener('DOMContentLoaded', () => {
    const resetForm = document.getElementById('reset-password-form');
    const newPasswordInput = document.getElementById('new-password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const statusDiv = document.getElementById('reset-status');

    // URL'den token'ı al
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (!token) {
        statusDiv.innerHTML = `<div class="alert alert-danger">Geçersiz sıfırlama linki.</div>`;
        resetForm.style.display = 'none'; // Formu gizle
    }

    resetForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (newPassword !== confirmPassword) {
            statusDiv.innerHTML = `<div class="alert alert-warning">Şifreler uyuşmuyor.</div>`;
            return;
        }

        statusDiv.innerHTML = `<div class="alert alert-info">İşleniyor...</div>`;

        fetch('http://127.0.0.1:8000/reset-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: token, new_password: newPassword })
        })
        .then(response => response.json())
        .then(data => {
            if (data.detail) { throw new Error(data.detail); }
            statusDiv.innerHTML = `<div class="alert alert-success">${data.message} <a href='login.html'>Giriş yapmak için tıklayın.</a></div>`;
            resetForm.style.display = 'none'; // Formu gizle
        })
        .catch(error => {
            statusDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        });
    });
});