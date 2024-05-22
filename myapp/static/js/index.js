document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('messageInput');
    const chatContainer = document.getElementById('chatContainer'); // Get chat container
    const selectFileMessage = document.getElementById('selectFileMessage'); // Get select file message

    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent default action of the Enter key
            sendMessage();
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            const chatBox = document.getElementById('chatBox');
            const loadingIndicator = document.getElementById('loading');

            // Show loading indicator
            loadingIndicator.style.display = 'flex';

            // Create user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.classList.add('message', 'user');
            const userMessageLabel = document.createElement('span');
            userMessageLabel.classList.add('label');
            userMessageLabel.innerText = 'User';
            const userMessageContent = document.createElement('div');
            userMessageContent.classList.add('message-content');
            userMessageContent.innerText = message;
            userMessageDiv.appendChild(userMessageLabel);
            userMessageDiv.appendChild(userMessageContent);
            chatBox.appendChild(userMessageDiv);

            // Clear input
            messageInput.value = '';

            // Scroll to bottom
            chatBox.scrollTop = chatBox.scrollHeight;

            // Send message to Flask server
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                }),
            })
                .then(response => response.json())
                .then(data => {
                    const botMessageDiv = document.createElement('div');
                    botMessageDiv.classList.add('message', 'bot');
                    const botMessageLabel = document.createElement('span');
                    botMessageLabel.classList.add('label');
                    const botMessageContent = document.createElement('div');
                    botMessageContent.classList.add('message-content');
                    botMessageContent.innerText = data.reply;
                    botMessageDiv.appendChild(botMessageLabel);
                    botMessageDiv.appendChild(botMessageContent);
                    chatBox.appendChild(botMessageDiv);

                    // Scroll to bottom
                    chatBox.scrollTop = chatBox.scrollHeight;

                    // Hide loading indicator
                    loadingIndicator.style.display = 'none';
                })
                .catch(error => {
                    console.error('Error:', error);

                    // Hide loading indicator in case of error
                    loadingIndicator.style.display = 'none';
                });
        }
    }

    document.getElementById('uploadButton').addEventListener('click', function () {
        const pdfUpload = document.getElementById('pdfUpload');
        const file = pdfUpload.files[0];
        const uploadError = document.getElementById('uploadError');
        const uploadSuccess = document.getElementById('uploadSuccess');
        const loadingIndicator = document.getElementById('loading-upload'); // Loading spinner

        if (file) {
            const formData = new FormData();
            formData.append('pdf', file);

            // Show loading spinner
            loadingIndicator.style.display = 'block';

            fetch('/upload_pdf', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        uploadError.innerText = data.error;
                        uploadError.style.display = 'block';
                        uploadSuccess.style.display = 'none';
                    } else {
                        const historyList = document.getElementById('historyList');
                        const option = document.createElement('option');
                        option.value = data.filename;
                        option.text = data.filename;
                        historyList.appendChild(option);

                        pdfUpload.value = '';
                        uploadError.style.display = 'none';

                        uploadSuccess.innerText = `File '${data.filename}' uploaded successfully.`;
                        uploadSuccess.style.display = 'block';
                    }

                    // Hide loading spinner after response
                    loadingIndicator.style.display = 'none';
                })
                .catch(error => {
                    console.error('Error:', error);
                    uploadError.innerText = 'An error occurred during upload.';
                    uploadError.style.display = 'block';
                    uploadSuccess.style.display = 'none';

                    // Hide loading spinner on error
                    loadingIndicator.style.display = 'none';
                });
        }
    });

    // Fetch initial list of files when the page loads
    fetch('/initial_files')
        .then(response => response.json())
        .then(data => {
            const historyList = document.getElementById('historyList');
            data.files.forEach(filename => {
                const option = document.createElement('option');
                option.value = filename;
                option.text = filename;
                historyList.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });

    document.getElementById('selectButton').addEventListener('click', function () {
        const historyList = document.getElementById('historyList');
        const selectedFile = historyList.value;

        if (selectedFile) {
            // Send selected file to Flask server
            fetch('/select_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: selectedFile
                }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Selected file:', data.filename);
                    // You can handle the response as needed

                    // Show chat container and input field after selecting file
                    chatContainer.style.display = 'flex';
                    selectFileMessage.style.display = 'none'; // Hide select file message
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });

    // Sidebar toggle functionality
    document.querySelector('.navbar-toggler').addEventListener('click', function () {
        const sidebar = document.getElementById('sidebar');
        if (sidebar.style.display === 'none' || sidebar.style.display === '') {
            sidebar.style.display = 'block';
        } else {
            sidebar.style.display = 'none';
        }
    });
});
