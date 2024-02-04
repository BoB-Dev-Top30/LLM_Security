document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInputForm = document.getElementById('user-input-form');
    const userInputField = document.getElementById('user-input');
    const loadingIndicator = document.getElementById('loading-indicator'); // Fixed missing quote

    userInputForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const userInput = userInputField.value; // Use .value for vanilla JS
        if (userInput.trim() === '') return;

        displayMessage('user', userInput);
        showLoadingIndicator();

        const chatGPTResponse = await getChatGPTResponse(userInput);

        // 화면에 뿌리기 저에 포멧팅
        const formattedResponse = formatResponseToHTML(chatGPTResponse);

        hideLoadingIndicator();
        displayMessage('chatbot', formattedResponse);

        userInputField.value = ''; // Use .value for vanilla JS
    });

    function formatResponseToHTML(response){
        return response.replace(/\n/g, '<br>');
    }

    function showLoadingIndicator() {
        loadingIndicator.style.display = 'flex';
    }

    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    function displayMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`; // Corrected template literal
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`; // Corrected innerHTML
        chatContainer.appendChild(messageDiv); // Ensuring method consistency
    }

    async function getChatGPTResponse(userInput) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({userInput}), // Ensure backend expects this format
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            return data.GPTResponse;
        } catch (error) {
            console.error('Error:', error);
            return '오류 발생'; // 'Error occurred' in Korean
        }
    }
});
