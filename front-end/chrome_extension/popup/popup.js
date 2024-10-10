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

// Generate a unique session ID, store it in localStorage
function getSessionId() {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
}

/**
 * Function to send the user message to the chat area and display a bot response.
 * - Retrieves the user input
 * - Appends the user message to the chat area
 * - Generates a bot message and appends it as well
 * - Saves the updated chat history to local storage
 */
async function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  const chatArea = document.getElementById("chat-area");

  if (userInput) {
    // Append user message to chat area
    const sessionId = getSessionId();  // Get the session ID
    const userMessage = document.createElement("div");
    userMessage.className = "chat-message user-message";
    userMessage.textContent = userInput;
    chatArea.appendChild(userMessage);

    // Create and append typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "chat-message bot-message typing-indicator";
    typingIndicator.textContent = "Bot is typing...";
    chatArea.appendChild(typingIndicator);

    // Scroll to the bottom of the chat area
    chatArea.scrollTop = chatArea.scrollHeight;

    // Call the backend API
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/query/?query=${encodeURIComponent(userInput)}&session_id=${sessionId}`, 
        {
          headers: {
            "Session-ID": sessionId  // Pass the current session
          }
        }
      );

      // Check for HTTP errors
      if (!response.ok) {
        if (response.status === 429) {
          throw new Error("Too many requests. Please try again later.");
        } else {
          throw new Error("An error occurred while fetching the response.");
        }
      }

      const data = await response.json();
      chatArea.removeChild(typingIndicator);

      // Append bot message to chat area
      const botMessage = document.createElement("div");
      botMessage.className = "chat-message bot-message";
      
      // Check if data.response exists and is not empty
      if (data.response) {
        botMessage.textContent = `Bot: ${data.response}`; // Display the bot response
      } else {
        botMessage.textContent = "Bot: No response from bot."; 
      }
      
      chatArea.appendChild(botMessage);
    } catch (error) {
      console.error("Error:", error);
      chatArea.removeChild(typingIndicator);

      // Display error message to the user
      const errorMessage = document.createElement("div");
      errorMessage.className = "chat-message bot-message";
      errorMessage.textContent = `Bot: ${error.message}`;

      chatArea.appendChild(errorMessage);
    }

    // Clear the input field and save the chat
    document.getElementById("user-input").value = "";
    saveChat();

    // Scroll to the bottom of the chat area
    chatArea.scrollTop = chatArea.scrollHeight;
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
