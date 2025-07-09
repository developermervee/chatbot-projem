// script.js (Login ve Şifremi Unuttum için Tam Sürüm)

document.addEventListener('DOMContentLoaded', function () {
    // --- HTML Elemanlarını Seçme ---
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMessageDiv = document.getElementById('error-message');

    const forgotPasswordLink = document.getElementById('forgot-password-link');
    const forgotPasswordModalEl = document.getElementById('forgotPasswordModal');
    // Modalı düzgün bir şekilde başlatmak için null kontrolü yapalım
    if (forgotPasswordModalEl) {
        const forgotPasswordModal = new bootstrap.Modal(forgotPasswordModalEl);
        const forgotPasswordForm = document.getElementById('forgot-password-form');
        const resetEmailInput = document.getElementById('reset-email');
        const forgotPasswordStatusDiv = document.getElementById('forgot-password-status');

        // "Şifremi Unuttum" Linkine Tıklanınca
        forgotPasswordLink.addEventListener('click', (event) => {
            event.preventDefault();
            forgotPasswordModal.show();
        });

        // Modal İçindeki "Sıfırlama Linki Gönder" Formu Gönderilince
        forgotPasswordForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const email = resetEmailInput.value;
            forgotPasswordStatusDiv.innerHTML = `<div class="alert alert-info">İşleniyor...</div>`;

            fetch('http://127.0.0.1:8000/forgot-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.detail) { // Hata varsa
                    throw new Error(data.detail);
                }
                forgotPasswordStatusDiv.innerHTML = `<div class="alert alert-success">${data.message} Lütfen terminali kontrol edin.</div>`;
            })
            .catch(error => {
                forgotPasswordStatusDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
            });
        });
    }


    // Ana Login Formu Gönderildiğinde
    loginForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Sayfanın yenilenmesini engellemek için en önemli satır
        
        errorMessageDiv.classList.add('d-none');
        errorMessageDiv.textContent = '';

        const email = emailInput.value;
        const password = passwordInput.value;

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        fetch('http://127.0.0.1:8000/token', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.detail || 'Bilinmeyen bir sunucu hatası oluştu.');
                });
            }
            return response.json();
        })
        .then(data => {
            localStorage.setItem('accessToken', data.access_token);
            window.location.href = 'dashboard.html';
        })
        .catch(error => {
            console.error('Giriş hatası:', error);
            errorMessageDiv.textContent = error.message;
            errorMessageDiv.classList.remove('d-none');
        });
    });
});