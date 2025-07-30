document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage) {
            appendMessage('user', userMessage);
            userInput.value = '';

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                appendMessage('bot', data.response);
                if (data.rego_policy) {
                    appendMessage('bot', `<pre>${data.rego_policy}</pre>`);
                } else if (data.message) { // If there's a message to re-send (e.g., extracted entity)
                    // Simulate sending the extracted message back to the bot
                    setTimeout(() => {
                        sendMessage(data.message); // Call sendMessage with the extracted message
                    }, 100); // Small delay to allow UI to update
                }
            });
        }
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `${sender}-message`);
        const p = document.createElement('p');
        p.innerHTML = message; // Use innerHTML to render <pre> tags
        messageElement.appendChild(p);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});