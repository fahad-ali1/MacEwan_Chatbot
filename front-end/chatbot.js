// Event listeners for the send button and input field
document
  .getElementById("user-input")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

// Event listener for the send button
document.getElementById("send-btn").addEventListener("click", sendMessage);

// Event listener for the clear button
document.getElementById("clear-btn").addEventListener("click", clearChat);

// Toggle chat bot on and off
const chatbotToggler = document.querySelector(".chatbot-toggler");
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);

// Function to toggle the chatbot visibility
function toggleChatbot() {
  const chatbotContainer = document.querySelector(".chatbot-container");
  if (
    chatbotContainer.style.display === "none" ||
    chatbotContainer.style.display === ""
  ) {
    chatbotContainer.style.display = "block";
  } else {
    chatbotContainer.style.display = "none";
  }
}

const createChatList = (message, className) => {
  // Create a chat <Li> element with passed message and classname
  const chatList = document.createElement("li");
  if (className.includes("bot-message typing-indicator")) {
    chatList.classList.add("chat", "bot-message", "typing-indicator");
  } else {
    chatList.classList.add("chat", className);
  }
  let chatContent =
    className === "user-message"
      ? `<p>${message}</p>`
      : `<span class="material-symbols-outlined">smart_toy</span><p>${message}</p>`;
  chatList.innerHTML = chatContent;
  return chatList;
};

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
  document.getElementById("user-input").disabled = true;
  document.getElementById("send-btn").disabled = true;
}

// Enable input field and send button
function enableInput() {
  document.getElementById("user-input").disabled = false;
  document.getElementById("send-btn").disabled = false;
  userInput.focus();
}

/**
 * Function to send the user message to the chat area and display a bot response.
 */
async function sendMessage() {
  const userInput = document.getElementById("user-input").value;

  if (userInput) {
    const sessionId = getSessionId();
    const chatArea = document.getElementById("chat-area");

    appendUserMessage(chatArea, userInput);
    const typingIndicator = appendTypingIndicator(chatArea);
    chatArea.scrollTop = chatArea.scrollHeight;

    disableInput();

    try {
      const response = await fetchResponse(userInput, sessionId);

      chatArea.removeChild(typingIndicator);
      const data = await response.json();
      appendBotMessage(
        chatArea,
        data.response || "No response available. Try again later."
      );
    } catch (error) {
      console.error("Error recieved:", error);
      chatArea.removeChild(typingIndicator);
      appendBotMessage(chatArea, error.message);
    }

    clearInput();
    saveChat();
    chatArea.scrollTop = chatArea.scrollHeight;
    enableInput();
  }
}

/**
 * Appends the user's message to the chat area.
 * @param {HTMLElement} chatArea - The chat area element.
 * @param {string} message - The user's message.
 */
function appendUserMessage(chatArea, message) {
  chatArea.appendChild(createChatList(message, "user-message"));
}

/**
 * Appends a typing indicator to the chat area and returns the element.
 * @param {HTMLElement} chatArea - The chat area element.
 * @returns {HTMLElement} The typing indicator element.
 */
function appendTypingIndicator(chatArea) {
  const typingIndicator = createChatList(
    ". . . .",
    "bot-message typing-indicator"
  );
  chatArea.appendChild(typingIndicator);
  return typingIndicator;
}

/**
 * Fetches the response from the server.
 * @param {string} userInput - The user's message.
 * @param {string} sessionId - The session ID.
 * @returns {Promise<Response>} The fetch response.
 */
async function fetchResponse(userInput, sessionId) {
  const response = await fetch(
    // local server URL
    `http://127.0.0.1:8000/query/?query=${encodeURIComponent(
      userInput
    )}&session_id=${sessionId}`,
    {
      headers: {
        "Session-ID": sessionId,
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      response.status === 429
        ? "Too many requests. Try later."
        : "Error occurred. Try later."
    );
  }

  return response;
}

/**
 * Appends the bot's message to the chat area.
 * @param {HTMLElement} chatArea - The chat area element.
 * @param {string} message - The bot's response message.
 */
function appendBotMessage(chatArea, message) {
  chatArea.appendChild(createChatList(message, "bot-message"));
}

/**
 * Clears the input field after sending the message.
 */
function clearInput() {
  document.getElementById("user-input").value = "";
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
  chatArea.appendChild(
    createChatList("Hi there! How can I help you today?", "bot-message")
  );
}

// Load chat history on page load
window.addEventListener("load", loadChat);
