// This component is the header of the chat window. It contains the title of the chat window and a button to clear the chat.
const ChatHeader = ({ clearChat }) => (
  <header>
    <h3>MacEwan Assistant</h3>
    <button onClick={clearChat} id="clear-btn" title="Clear chat">
      🗑️
    </button>
  </header>
);

export default ChatHeader;
