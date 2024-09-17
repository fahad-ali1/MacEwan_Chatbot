document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("clear-btn").addEventListener("click", clearChat);

// Listens for Enter key
document
  .getElementById("user-input")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

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

function saveChat() {
  const chatArea = document.getElementById("chat-area");
  localStorage.setItem("chatHistory", chatArea.innerHTML);
}

function loadChat() {
  const chatArea = document.getElementById("chat-area");
  const savedChat = localStorage.getItem("chatHistory");
  if (savedChat) {
    chatArea.innerHTML = savedChat;
  }
}

function clearChat() {
  localStorage.removeItem("chatHistory");
  const chatArea = document.getElementById("chat-area");
  chatArea.innerHTML = "";
}

window.addEventListener("load", loadChat);

// !!! Testing, hot reload, delete later !!!
document.getElementById("reload-btn").addEventListener("click", () => {
  chrome.runtime.reload();
});
