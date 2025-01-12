import ChatbotIcon from '../images/ChatbotMacewanIcon.png';

/**
 * ChatHeader Component
 * Displays the chat header with a title and a button to clear the chat.
 *
 * Props:
 * - clearChat: Function to clear the chat history.
 */
const ChatHeader = ({ clearChat }) => (
  <header>
    <h3>
      <img
        src={ChatbotIcon}
        alt="MacEwan Logo"
        style={{ width: "125px",  marginRight: "8px" }}
      />
    </h3>
    <button onClick={clearChat} id="clear-btn" title="Clear chat">
      🗑️
    </button>
  </header>
);

export default ChatHeader;
