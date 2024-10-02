// Event listener for "Send" button - triggers the sendMessage function when clicked
document.getElementById("send-btn").addEventListener("click", sendMessage);

// Event listener for "Clear" button - triggers the clearChat function when clicked
document.getElementById("clear-btn").addEventListener("click", clearChat);

// Adds an event listener to the input field that listens for the Enter key
document
  .getElementById("user-input")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

/**
 * Function to send the user message to the chat area and display a bot response.
 * - Retrieves the user input
 * - Appends the user message to the chat area
 * - Generates a bot message and appends it as well
 * - Saves the updated chat history to local storage
 */
function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  const chatArea = document.getElementById("chat-area");

  if (userInput) {
    const userMessage = document.createElement("div");
    userMessage.className = "chat-message user-message";
    userMessage.textContent = userInput;
    chatArea.appendChild(userMessage);

    const botMessage = document.createElement("div");
    botMessage.className = "chat-message bot-message";
    botMessage.textContent = "Bot: This is a bot response";
    chatArea.appendChild(botMessage);

    chatArea.scrollTop = chatArea.scrollHeight;
    document.getElementById("user-input").value = "";

    saveChat();
  }
}

/**
 * Function to save the current chat history to the browser's local storage.
 * This ensures that the chat is retained even after the page reloads.
 */
function saveChat() {
  const chatArea = document.getElementById("chat-area");
  localStorage.setItem("chatHistory", chatArea.innerHTML);
}

/**
 * Function to load the chat history from local storage (if any) when the page is reloaded.
 * This restores the previous chat session.
 */
function loadChat() {
  const chatArea = document.getElementById("chat-area");
  const savedChat = localStorage.getItem("chatHistory");
  if (savedChat) {
    chatArea.innerHTML = savedChat;
  }
}

/**
 * Function to clear the chat history from both the chat area and local storage.
 * This is triggered when the "Clear" button is clicked.
 */
function clearChat() {
  localStorage.removeItem("chatHistory");
  const chatArea = document.getElementById("chat-area");
  chatArea.innerHTML = "";
}

// Load the saved chat history when the page is loaded
window.addEventListener("load", loadChat);

/**
 * Temporary testing function to reload the Chrome extension programmatically.
 * This button is only for development and testing purposes.
 */
document.getElementById("reload-btn").addEventListener("click", () => {
  chrome.runtime.reload();
});
