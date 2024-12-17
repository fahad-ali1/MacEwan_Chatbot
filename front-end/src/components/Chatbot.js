import React, { useState, useEffect, useRef } from "react";
import Message from "./Message.js";
import { saveChat, loadChat, getSessionId, fetchResponse } from "./ChatArea.js";
import ChatHeader from "./ChatHeader.js";
import ChatbotToggler from "./ChatbotToggler.js";
import InputArea from "./InputArea.js";

/**
 * Chatbot Component
 * Renders the chatbot interface, including the message area, input area, and visibility toggler.
 * Manages chatbot state, message handling, and interactions with local storage and backend services.
 */

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { text: "Hi there! How can I help you today?", sender: "bot" },
  ]);
  const [userInput, setUserInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isDisabled, setIsDisabled] = useState(false);
  const [isChatVisible, setIsChatVisible] = useState(false);

  const chatAreaRef = useRef(null);
  const sessionId = getSessionId();

  /**
   * Toggles the chatbot's visibility state.
   */
  const toggleChatVisibility = () => {
    setIsChatVisible((visible) => !visible);
  };

  /**
   * Scrolls the chat area to the latest message when messages change.
   */
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  /**
   * Loads chat history from local storage on component mount.
   */
  useEffect(() => {
    loadChat(setMessages);
  }, []);

  /**
   * Saves chat history to local storage whenever messages are updated.
   */
  useEffect(() => {
    saveChat(messages);
  }, [messages]);

  /**
   * Appends a new message to the chat area.
   *
   * @param {string} text - The message text.
   * @param {string} sender - The sender of the message ("user" or "bot").
   */
  const appendMessage = (text, sender) => {
    setMessages((messages) => [...messages, { text, sender }]);
  };

  /**
   * Updates the userInput state when the user types in the input area.
   *
   * @param {Event} txt - The input change event.
   */
  const handleInputChange = (txt) => setUserInput(txt.target.value);

  /**
   * Handles Enter key press for submitting messages.
   *
   * @param {Event} e - The key down event.
   */
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      sendMessage(); // Submit message
    }
  };

  /**
   * Sends the user's message to the bot and handles the response.
   */
  const sendMessage = async () => {
    if (!userInput.trim()) return; // Prevent empty messages

    appendMessage(userInput, "user"); // Add user message to chat
    setIsTyping(true); // Show typing indicator
    setIsDisabled(true); // Disable input
    setUserInput(""); // Clear input field

    try {
      const response = await fetchResponse(userInput, sessionId);
      const data = await response.json();

      // Append bot's response to chat
      appendMessage(
        data.response || "No response available. Try again later.",
        "bot"
      );
    } catch (error) {
      console.error("Error:", error);
      appendMessage(error.message || "Error occurred. Try again later.", "bot");
    }

    setIsTyping(false); // Hide typing indicator
    setIsDisabled(false); // Re-enable input
  };

  /**
   * Clears the chat history from local storage and resets the messages state.
   */
  const clearChat = () => {
    localStorage.removeItem("chatHistory");
    setMessages([
      { text: "Hi there! How can I help you today?", sender: "bot" },
    ]);
  };

  return (
    <div>
      {/* Button to toggle chatbot visibility */}
      <ChatbotToggler
        isChatVisible={isChatVisible}
        toggleChatVisibility={toggleChatVisibility}
      />

      {/* Chatbot container */}
      <div
        className={`chatbot-container ${isChatVisible ? "show-chatbot" : ""}`}
      >
        {/* Chat header */}
        <ChatHeader clearChat={clearChat} />

        {/* Chat area displaying messages */}
        <div id="chat-area" className="chat-area" ref={chatAreaRef}>
          {messages.map((msg, index) => (
            <Message key={index} message={msg} />
          ))}
          {isTyping && (
            <div className="chat bot-message">
              <span className="material-symbols-outlined">smart_toy</span>
              <div className="typing-indicator">. . .</div>
            </div>
          )}
        </div>

        {/* Input area for user messages */}
        <InputArea
          userInput={userInput}
          handleInputChange={handleInputChange}
          handleKeyDown={handleKeyDown}
          sendMessage={sendMessage}
          isDisabled={isDisabled}
        />
      </div>
    </div>
  );
};

export default Chatbot;
