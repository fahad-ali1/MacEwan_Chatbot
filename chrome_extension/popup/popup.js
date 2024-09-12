document.getElementById("send-btn").addEventListener("click", sendMessage);

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
  }
}
