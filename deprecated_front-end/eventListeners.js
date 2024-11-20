import { sendMessage } from "./chatbot.js";
import { clearChat, loadChat } from "./chatArea.js";

/**
 * Sets event listeners for the chatbot.
 * @param {document} chatArea - The chat area
 */
export function setupEventListeners(chatArea) {
  document
    .getElementById("user-input")
    .addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        sendMessage();
      }
    });
  document
    .querySelector(".chatbot-toggler")
    .addEventListener("click", () =>
      document.body.classList.toggle("show-chatbot")
    );
  document.getElementById("send-btn").addEventListener("click", sendMessage);
  document.getElementById("clear-btn").addEventListener("click", clearChat);
  window.addEventListener("load", loadChat(chatArea));
}
