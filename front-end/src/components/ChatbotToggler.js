/**
 * ChatbotToggler Component
 * Displays a toggle button to show or hide the chatbot interface.
 *
 * Props:
 * - isChatVisible: (boolean) Indicates if the chatbot is currently visible.
 * - toggleChatVisibility: (function) Toggles the visibility state of the chatbot.
 */

const ChatbotToggler = ({ isChatVisible, toggleChatVisibility }) => (
  <button
    className="chatbot-toggler"
    onClick={toggleChatVisibility} // Toggles chatbot visibility
    aria-label={isChatVisible ? "Close chatbot" : "Open chatbot"}
    title={isChatVisible ? "Close chatbot" : "Open chatbot"}
  >
    {isChatVisible ? "❌" : "💬"}{" "}
    {/* Shows close icon when visible, chat icon otherwise */}
  </button>
);

export default ChatbotToggler;
