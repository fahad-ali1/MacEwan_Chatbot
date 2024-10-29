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

// Save chat history to localStorage
export function saveChat(chatArea) {
  localStorage.setItem("chatHistory", chatArea.innerHTML);
}

// Load chat history from localStorage
export function loadChat(chatArea) {
  const savedChat = localStorage.getItem("chatHistory");
  if (savedChat) {
    chatArea.innerHTML = savedChat;
  }
}

// Clear chat history from localStorage
export function clearChat() {
  const chatArea = document.getElementById("chat-area");
  localStorage.removeItem("chatHistory");
  document.getElementById("chat-area").innerHTML = "";
  chatArea.appendChild(
    createChatList("Hi there! How can I help you today?", "bot-message")
  );
}

//Clears the input field after sending the message.
export function clearInput() {
  document.getElementById("user-input").value = "";
}

// Disable input field and send button
export function disableInput() {
  document.getElementById("user-input").disabled = true;
  document.getElementById("send-btn").disabled = true;
}

// Enable input field and send button
export function enableInput() {
  document.getElementById("user-input").disabled = false;
  document.getElementById("send-btn").disabled = false;
}

/**
 * Appends the user's message to the chat area.
 * @param {HTMLElement} chatArea - The chat area element.
 * @param {string} message - The user's message.
 */
export function appendUserMessage(chatArea, message) {
  chatArea.appendChild(createChatList(message, "user-message"));
}

/**
 * Appends a typing indicator to the chat area and returns the element.
 * @param {HTMLElement} chatArea - The chat area element.
 * @returns {HTMLElement} The typing indicator element.
 */
export function appendTypingIndicator(chatArea) {
  const typingIndicator = createChatList(
    ". . .",
    "bot-message typing-indicator"
  );
  chatArea.appendChild(typingIndicator);
  return typingIndicator;
}

/**
 * Appends the bot's message to the chat area.
 * @param {HTMLElement} chatArea - The chat area element.
 * @param {string} message - The bot's response message.
 */
export function appendBotMessage(chatArea, message) {
  chatArea.appendChild(createChatList(message, "bot-message"));
}
