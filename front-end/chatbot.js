// Function to toggle the chatbot visibility
function toggleChatbot() {
    const chatbotContainer = document.querySelector('.chatbot-container');
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'block';
    } else {
        chatbotContainer.style.display = 'none';
    }
}

// toggle chat bot on and off
const chatbotToggler = document.querySelector(".chatbot-toggler");
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"))

const createChatList = (message, className) => {
    // Create a chat <Li> element with passed message and classname
    const chatList = document.createElement("li");
    if (className.includes("bot-message typing-indicator")) {
        chatList.classList.add("chat", "bot-message", "typing-indicator")
    }
    else {
        chatList.classList.add("chat", className);
    }  
    let chatContent = className === "user-message" ? `<p>${message}</p>` : `<span class="material-symbols-outlined">smart_toy</span><p>${message}</p>`;
    chatList.innerHTML = chatContent;
    return chatList
  }


// Event listener for the exit button
// document.getElementById("exit-btn").addEventListener("click", function () {
//     const chatbotContainer = document.querySelector('.chatbot-container');
//     chatbotContainer.style.display = 'none'; // Hide the chatbot
// });

// Event listeners for the send button and input field
document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Event listener for the clear button
document.getElementById("clear-btn").addEventListener("click", clearChat);

// Get or create a session ID
function getSessionId() {
    let sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
        sessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
        localStorage.setItem("session_id", sessionId);
    }
    return sessionId;
}

// Disable input field and send button
function disableInput() {
    const userInput = document.getElementById("user-input");
    userInput.disabled = true;
    document.getElementById("send-btn").disabled = true;
}

// Enable input field and send button
function enableInput() {
    const userInput = document.getElementById("user-input");
    userInput.disabled = false;
    document.getElementById("send-btn").disabled = false;

    // Puts cursor back in the input field
    userInput.focus();
}


/**
 * Function to send the user message to the chat area and display a bot response.
 * - Retrieves the user input
 * - Appends the user message to the chat area
 * - Generates a bot message and appends it as well
 * - Saves the updated chat history to local storage
 */async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const chatArea = document.getElementById("chat-area");

    if (userInput) {
        const sessionId = getSessionId();
        // const userMessage = document.createElement("div");
        // userMessage.className = "chat user-message";
        // userMessage.innerHTML = `<p>${userInput}</p>`;
        chatArea.appendChild(createChatList(userInput, "user-message"));

        // const typingIndicator = document.createElement("div");
        // typingIndicator.className = "chat bot-message typing-indicator";
        // typingIndicator.innerHTML = `<span class="material-symbols-outlined">smart_toy</span><p>. . . .</p>`;
        let typingIndicator =createChatList(". . . .", "bot-message typing-indicator")
        chatArea.appendChild(typingIndicator);
        chatArea.scrollTop = chatArea.scrollHeight;

        // Disable input while waiting for response
        disableInput();

        try {
            const response = await fetch(
                `http://127.0.0.1:8000/query/?query=${encodeURIComponent(userInput)}&session_id=${sessionId}`, 
                {
                    headers: {
                        "Session-ID": sessionId
                    }
                }
            );

            if (!response.ok) {
                throw new Error(response.status === 429 ? "Too many requests. Try later." : "Error occurred.");
            }

            const data = await response.json();
            chatArea.removeChild(typingIndicator);

            // const botMessage = document.createElement("div");
            // botMessage.className = "chat bot-message";
            // botMessage.innerHTML = `<span class="material-symbols-outlined">smart_toy</span><p>${data.response || "No response available."}</p>`;
            chatArea.appendChild(createChatList(data.response, "bot-message"));
        } catch (error) {
            console.error("Error:", error);
            chatArea.removeChild(typingIndicator);

            // const errorMessage = document.createElement("div");
            // errorMessage.className = "chat bot-message";
            // errorMessage.innerHTML = `<span class="material-symbols-outlined">smart_toy</span><p>${error.message}</p>`;
            chatArea.appendChild(createChatList(error.message, "bot-message"));
        }

        // Clear the input after sending the message
        document.getElementById("user-input").value = "";
        saveChat();
        chatArea.scrollTop = chatArea.scrollHeight;

        // Re-enable the input field after the bot responds
        enableInput(); // This now ensures focus is set immediately after enabling
    }
}

// Save chat history to localStorage
function saveChat() {
    const chatArea = document.getElementById("chat-area");
    localStorage.setItem("chatHistory", chatArea.innerHTML);
}

// Load chat history from localStorage
function loadChat() {
    const chatArea = document.getElementById("chat-area");
    const savedChat = localStorage.getItem("chatHistory");
    if (savedChat) {
        chatArea.innerHTML = savedChat;
    }
}

// Clear chat history from localStorage
function clearChat() {
    const chatArea = document.getElementById("chat-area");
    localStorage.removeItem("chatHistory");
    document.getElementById("chat-area").innerHTML = "";
    chatArea.appendChild(createChatList("Hi there! How can I help you today?", "bot-message"))
}

// Load chat history on page load
window.addEventListener("load", loadChat);
