/* This component is a button that toggles the visibility of the chatbot. 
It displays a chat icon when the chatbot is not visible and a close icon when the chatbot is visible. */
const ChatbotToggler = ({ isChatVisible, toggleChatVisibility }) => (
  <button className="chatbot-toggler" onClick={toggleChatVisibility}>
    {isChatVisible ? "❌" : "💬"}
  </button>
);

export default ChatbotToggler;
