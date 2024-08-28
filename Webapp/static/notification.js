document.addEventListener('DOMContentLoaded', function() {
    // Check if roomName and token are defined globally
    if (typeof roomName !== 'undefined' && typeof token !== 'undefined') {
        const chatSocket = new WebSocket(`ws://localhost:8000/ws/chat/${roomName}/?token=${token}`);

        chatSocket.onopen = function(e) {
            console.log('WebSocket connection established');
        };

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log('Message received:', data);

            if (window.location.pathname !== '/chat/') {
                showNotification('New Message', data.message);
            }
        };

        chatSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
        };

        chatSocket.onclose = function(e) {
            console.log('WebSocket connection closed');
        };

        function showNotification(title, message) {
            const popup = document.getElementById('notification-popup');
            popup.innerHTML = `<strong>${title}</strong><br>${message}`;
            popup.style.display = 'block';

            setTimeout(() => {
                popup.style.display = 'none';
            }, 5000); // Hide after 5 seconds
        }
    } else {
        console.warn('roomName or token is not defined');
    }
});
