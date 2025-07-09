// widget.js (Form Kapanma Hatası Düzeltilmiş Tam Hali)

document.addEventListener('DOMContentLoaded', () => {
    // HTML elemanlarını seçiyoruz
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('close-chat-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const messagesContainer = document.getElementById('chat-messages');

    const OWNER_ID = 1;

    // Balona tıklayınca pencereyi aç, balonu gizle
    chatBubble.addEventListener('click', () => {
        chatWindow.style.display = 'flex';
        chatBubble.style.display = 'none';
    });

    // Kapatma butonuna tıklayınca pencereyi kapat, balonu göster
    closeBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        chatBubble.style.display = 'block';
    });

    // Mesaj gönderme formu
    chatForm.addEventListener('submit', (event) => {
        // DÜZELTME: BU SATIR ÇOK ÖNEMLİ!
        // Formun sayfayı yenilemesini engelliyoruz.
        event.preventDefault(); 
        
        const userMessage = chatInput.value.trim();
        if (userMessage === '') return;

        addMessage(userMessage, 'user');
        chatInput.value = '';

        fetchChatResponse(userMessage);
    });

    // Mesajı ekrana ekleyen yardımcı fonksiyon
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Backend API'si ile konuşan fonksiyon
    function fetchChatResponse(message) {
        addMessage('...', 'bot');
        fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, owner_id: OWNER_ID })
        })
        .then(response => response.json())
        .then(data => {
            messagesContainer.removeChild(messagesContainer.lastChild);
            addMessage(data.response, 'bot');
            
            if (data.type === 'lead_capture') {
                displayLeadCaptureForm(message);
            }
        })
        .catch(error => {
            console.error('API Hatası:', error);
            messagesContainer.removeChild(messagesContainer.lastChild);
            addMessage('Üzgünüm, bir sorun oluştu. Lütfen daha sonra tekrar deneyin.', 'bot');
        });
    }

    // İletişim formu gösterme fonksiyonu
    function displayLeadCaptureForm(originalMessage) {
        const formHtml = `
            <form id="lead-form" class="message bot-message">
                <p class="mb-2"><small>Lütfen aşağıdaki bilgileri doldurun:</small></p>
                <input type="text" id="lead-name" placeholder="Adınız Soyadınız" class="form-control mb-2" required>
                <input type="email" id="lead-email" placeholder="E-posta Adresiniz" class="form-control mb-2">
                <input type="tel" id="lead-phone" placeholder="Telefon Numaranız" class="form-control mb-2">
                <button type="submit" class="btn btn-light btn-sm w-100">Bilgileri Gönder</button>
            </form>
        `;
        messagesContainer.innerHTML += formHtml;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        const leadForm = document.getElementById('lead-form');
        leadForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Bu formun da sayfayı yenilemesini engelle
            const leadData = {
                customer_name: document.getElementById('lead-name').value,
                customer_email: document.getElementById('lead-email').value,
                customer_phone: document.getElementById('lead-phone').value,
                message: originalMessage,
                owner_id: OWNER_ID
            };

            fetch('http://127.0.0.1:8000/leads/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(leadData)
            })
            .then(response => response.json())
            .then(() => {
                leadForm.innerHTML = "Teşekkürler! Bilgileriniz alındı, en kısa sürede size ulaşacağız.";
            })
            .catch(error => console.error('Lead gönderme hatası:', error));
        });
    }
});