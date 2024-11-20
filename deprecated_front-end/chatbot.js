import { setupEventListeners } from "./eventListeners.js";
import { getSessionId, fetchResponse } from "./chatbotAPI.js";
import {
  appendUserMessage,
  appendTypingIndicator,
  appendBotMessage,
  saveChat,
  clearInput,
  disableInput,
  enableInput,
} from "./chatArea.js";

const chatArea = document.getElementById("chat-area");
setupEventListeners(chatArea);

/**
 * Function to send the user message to the chat area and display a bot response.
 */
export async function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  const sessionId = getSessionId();

  if (userInput) {
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
    saveChat(chatArea);
    chatArea.scrollTop = chatArea.scrollHeight;
    enableInput();
  }
}
