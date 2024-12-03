import React, { useState, useEffect, useRef } from "react";
import Message from "./Message.js";
import { saveChat, loadChat, getSessionId, fetchResponse } from "./ChatArea.js";
import ChatHeader from "./ChatHeader.js";
import ChatbotToggler from "./ChatbotToggler.js";
import InputArea from "./InputArea.js";

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

  const toggleChatVisibility = () => {
    setIsChatVisible((visible) => !visible);
  };

  // Scroll to the bottom whenever a message sent
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Load chat history
  useEffect(() => {
    loadChat(setMessages);
  }, []);

  // Save chat history
  useEffect(() => {
    saveChat(messages);
  }, [messages]);

  // Append a message to the chat area depending on text and sender
  const appendMessage = (text, sender) => {
    setMessages((messages) => [...messages, { text: text, sender }]); };

  // handle user input
  const handleInputChange = (txt) => setUserInput(txt.target.value);

  // Handle enter key
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // fetch response from backend
  const sendMessage = async () => {
    if (!userInput) return;

    appendMessage(userInput, "user");
    // Typing is disabled while waiting for response
    setIsTyping(true);
    setIsDisabled(true);
    setUserInput("");

    try {
      const response = await fetchResponse(userInput, sessionId);
      const data = await response.json();
      appendMessage(
        data.response || "No response available. Try again later.",
        "bot"
      );
    } catch (error) {
      console.error("Error:", error);
      appendMessage(error.message || "Error occurred. Try again later.", "bot");
    }

    setIsTyping(false);
    setIsDisabled(false);
  };

  // Clear chat history
  const clearChat = () => {
    localStorage.removeItem("chatHistory");
    setMessages([
      { text: "Hi there! How can I help you today?", sender: "bot" },
    ]);
  };

  return (
    <div>
      <ChatbotToggler
        isChatVisible={isChatVisible}
        toggleChatVisibility={toggleChatVisibility}
      />
      <div
        className={`chatbot-container ${isChatVisible ? "show-chatbot" : ""}`}
      >
        <ChatHeader clearChat={clearChat} />
        <div id="chat-area" className="chat-area" ref={chatAreaRef}>
          {messages.map((msg, index) => (
            <Message key={index} message={msg} />
          ))}
          {isTyping && (
            <div className="chat bot-message">
              <span className="material-symbols-outlined">smart_toy</span>
              <div className="typing-indicator"> . . .</div>
            </div>
          )}
        </div>
        <div className="input-container">
          <InputArea
            userInput={userInput}
            handleInputChange={handleInputChange}
            handleKeyDown={handleKeyDown}
            sendMessage={sendMessage}
            isDisabled={isDisabled}
          />
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
