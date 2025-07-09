// dashboard.js (TEMA SEÇİMİ DAHİL TÜM ÖZELLİKLER - NİHAİ SÜRÜM)

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. TÜM HTML ELEMANLARINI SEÇELİM ---
    const token = localStorage.getItem('accessToken');
    const userEmailSpan = document.getElementById('user-email');
    const logoutButton = document.getElementById('logout-button');
    
    // Formlar
    const addProductForm = document.getElementById('add-product-form');
    const addFaqForm = document.getElementById('add-faq-form');
    const editProductForm = document.getElementById('edit-product-form');
    const uploadForm = document.getElementById('upload-form');
    const settingsForm = document.getElementById('settings-form');

    // Listeleme Alanları
    const productsListDiv = document.getElementById('products-list');
    const faqsListDiv = document.getElementById('faqs-list');
    const leadsListDiv = document.getElementById('leads-list');

    // Dosya Yükleme Elemanları
    const fileInput = document.getElementById('product-file-input');
    const uploadStatusDiv = document.getElementById('upload-status');
    
    // Kişiselleştirme Formu Elemanları
    const lightThemeRadio = document.getElementById('light-theme-radio');
    const darkThemeRadio = document.getElementById('dark-theme-radio');
    const welcomeMessageInput = document.getElementById('welcome-message-input');
    const settingsStatusDiv = document.getElementById('settings-status');


    // --- 2. GÜVENLİK KONTROLÜ ---
    if (!token) {
        window.location.href = 'login.html';
        return;
    }


    // --- 3. YARDIMCI FONKSİYONLARI TANIMLAYALIM ---

    // Ana Veri Çekme Fonksiyonu
    function fetchDashboardData() {
        fetch('http://127.0.0.1:8000/users/me/', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(response => {
            if (response.status === 401) {
                localStorage.removeItem('accessToken');
                window.location.href = 'login.html';
                return null;
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                userEmailSpan.textContent = data.email;
                
                // Kayıtlı temaya göre doğru radyo butonunu işaretle
                if (data.widget_theme === 'dark') {
                    darkThemeRadio.checked = true;
                } else {
                    lightThemeRadio.checked = true;
                }
                welcomeMessageInput.value = data.welcome_message || 'Merhaba! Size nasıl yardımcı olabilirim?';

                // Diğer verileri yükle
                displayProducts(data.products);
                displayFaqs(data.faqs);
                displayLeads(data.leads);
            }
        })
        .catch(error => console.error('Veri alınırken bir hata oluştu:', error));
    }

    // Ürünleri Görüntüleme Fonksiyonu
    function displayProducts(products) {
        productsListDiv.innerHTML = '';
        if (!products || products.length === 0) { productsListDiv.innerHTML = '<p class="text-muted">Henüz hiç ürün eklemediniz.</p>'; return; }
        products.forEach(product => {
            const productItem = `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1 product-name">${product.name}</h5>
                        <div>
                            <button class="btn btn-outline-primary btn-sm edit-product-btn" data-product-id="${product.id}" data-bs-toggle="modal" data-bs-target="#editProductModal"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-outline-danger btn-sm delete-product-btn" data-product-id="${product.id}"><i class="bi bi-trash"></i></button>
                        </div>
                    </div>
                    <p class="mb-1 product-description">${product.description || ''}</p>
                    <small class="product-price">Fiyat: ${product.price} TL</small>
                </div>`;
            productsListDiv.innerHTML += productItem;
        });
    }

    // SSS'leri Görüntüleme Fonksiyonu
    function displayFaqs(faqs) {
        faqsListDiv.innerHTML = '';
        if (!faqs || faqs.length === 0) { faqsListDiv.innerHTML = '<p class="text-muted">Henüz hiç SSS eklemediniz.</p>'; return; }
        faqs.forEach(faq => {
            const faqItem = `<div class="list-group-item"><div class="d-flex w-100 justify-content-between"><h6 class="mb-1">${faq.question}</h6><button class="btn btn-outline-danger btn-sm delete-faq-btn" data-faq-id="${faq.id}"><i class="bi bi-trash"></i></button></div><p class="mb-1">${faq.answer}</p></div>`;
            faqsListDiv.innerHTML += faqItem;
        });
    }
    
    // Potansiyel Müşterileri Görüntüleme Fonksiyonu
    function displayLeads(leads) {
        leadsListDiv.innerHTML = '';
        if (!leads || leads.length === 0) { leadsListDiv.innerHTML = '<p class="text-muted">Henüz yakalanan bir potansiyel müşteri yok.</p>'; return; }
        let tableHtml = '<div class="table-responsive"><table class="table table-striped table-hover"><thead><tr><th>Adı</th><th>Email</th><th>Telefon</th><th>Mesajı</th><th>Tarih</th></tr></thead><tbody>';
        leads.slice().reverse().forEach(lead => { tableHtml += `<tr><td>${lead.customer_name}</td><td>${lead.customer_email || '-'}</td><td>${lead.customer_phone || '-'}</td><td>${lead.message}</td><td>${new Date(lead.created_at).toLocaleString('tr-TR')}</td></tr>`; });
        tableHtml += '</tbody></table></div>';
        leadsListDiv.innerHTML = tableHtml;
    }


    // --- 4. OLAY DİNLEYİCİLERİNİ (EVENT LISTENERS) TANIMLAYALIM ---
    
    // Çıkış Yap Butonu
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('accessToken');
        window.location.href = 'login.html';
    });

    // Form Gönderme Olayları
    addProductForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const productData = { name: document.getElementById('product-name').value, description: document.getElementById('product-description').value, price: parseFloat(document.getElementById('product-price').value) };
        fetch('http://127.0.0.1:8000/products/', { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(productData) }).then(response => { if (!response.ok) throw new Error('Ürün eklenemedi.'); return response.json(); }).then(() => { fetchDashboardData(); bootstrap.Modal.getInstance(document.getElementById('addProductModal')).hide(); addProductForm.reset(); }).catch(error => console.error('Ürün ekleme hatası:', error));
    });

    editProductForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const productId = document.getElementById('edit-product-id').value;
        const updatedData = { name: document.getElementById('edit-product-name').value, description: document.getElementById('edit-product-description').value, price: parseFloat(document.getElementById('edit-product-price').value) };
        fetch(`http://127.0.0.1:8000/products/${productId}`, { method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(updatedData) }).then(response => { if (!response.ok) throw new Error('Ürün güncellenemedi.'); return response.json(); }).then(() => { fetchDashboardData(); bootstrap.Modal.getInstance(document.getElementById('editProductModal')).hide(); }).catch(error => console.error('Ürün güncelleme hatası:', error));
    });
    
    uploadForm.addEventListener('submit', (event) => {
        event.preventDefault();
        if (fileInput.files.length === 0) { uploadStatusDiv.innerHTML = `<div class="alert alert-warning">Lütfen bir dosya seçin.</div>`; return; }
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        uploadStatusDiv.innerHTML = `<div class="alert alert-info">Dosya yükleniyor...</div>`;
        fetch('http://127.0.0.1:8000/upload-products/', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: formData }).then(response => response.json()).then(data => { if (data.detail) throw new Error(data.detail); uploadStatusDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`; fetchDashboardData(); uploadForm.reset(); }).catch(error => { uploadStatusDiv.innerHTML = `<div class="alert alert-danger">Hata: ${error.message}</div>`; });
    });

    addFaqForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const faqData = { question: document.getElementById('faq-question').value, answer: document.getElementById('faq-answer').value };
        fetch('http://127.0.0.1:8000/faqs/', { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(faqData) }).then(response => { if (!response.ok) throw new Error('SSS eklenemedi.'); return response.json(); }).then(() => { fetchDashboardData(); bootstrap.Modal.getInstance(document.getElementById('addFaqModal')).hide(); addFaqForm.reset(); }).catch(error => console.error('SSS ekleme hatası:', error));
    });

    settingsForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const selectedTheme = document.querySelector('input[name="widgetTheme"]:checked').value;
        const settingsData = { widget_theme: selectedTheme, welcome_message: welcomeMessageInput.value };
        settingsStatusDiv.innerHTML = `<div class="alert alert-info">Kaydediliyor...</div>`;
        fetch('http://127.0.0.1:8000/users/me/settings', { method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(settingsData) })
        .then(response => { if (!response.ok) throw new Error('Ayarlar kaydedilemedi.'); return response.json(); })
        .then(data => { settingsStatusDiv.innerHTML = `<div class="alert alert-success">Ayarlar başarıyla kaydedildi!</div>`; })
        .catch(error => { settingsStatusDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`; });
    });

    // Liste İçi Tıklama Olayları
    productsListDiv.addEventListener('click', (event) => {
        const targetButton = event.target.closest('button');
        if (!targetButton) return;
        if (targetButton.classList.contains('delete-product-btn')) {
            const productId = targetButton.getAttribute('data-product-id');
            if (confirm(`ID'si ${productId} olan ürünü silmek istediğinizden emin misiniz?`)) {
                fetch(`http://127.0.0.1:8000/products/${productId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } }).then(response => { if (!response.ok) throw new Error('Ürün silinemedi.'); fetchDashboardData(); }).catch(error => console.error('Ürün silme hatası:', error));
            }
        } else if (targetButton.classList.contains('edit-product-btn')) {
            const productItem = targetButton.closest('.list-group-item');
            document.getElementById('edit-product-id').value = targetButton.getAttribute('data-product-id');
            document.getElementById('edit-product-name').value = productItem.querySelector('.product-name').textContent;
            document.getElementById('edit-product-description').value = productItem.querySelector('.product-description').textContent;
            const priceText = productItem.querySelector('.product-price').textContent;
            document.getElementById('edit-product-price').value = parseFloat(priceText.replace('Fiyat:', '').replace('TL', '').trim());
        }
    });

    faqsListDiv.addEventListener('click', (event) => {
        const deleteButton = event.target.closest('.delete-faq-btn');
        if (deleteButton) {
            const faqId = deleteButton.getAttribute('data-faq-id');
            if (confirm(`ID'si ${faqId} olan SSS'yi silmek istediğinizden emin misiniz?`)) {
                fetch(`http://127.0.0.1:8000/faqs/${faqId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } }).then(response => { if (!response.ok) throw new Error('SSS silinemedi.'); fetchDashboardData(); }).catch(error => console.error('SSS silme hatası:', error));
            }
        }
    });

    // 5. Sayfa Yüklendiğinde Her Şeyi Başlat
    fetchDashboardData();
});