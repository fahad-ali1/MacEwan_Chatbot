// This component is responsible for rendering the input area where the user can type their message and send it to the bot.
const InputArea = ({
  userInput,
  handleInputChange,
  handleKeyDown,
  sendMessage,
  isDisabled,
}) => (
  <div className="input-container">
    <textarea
      value={userInput}
      onChange={handleInputChange}
      onKeyDown={handleKeyDown}
      placeholder="Type your message ..."
      disabled={isDisabled}
    />
    <button onClick={sendMessage} disabled={isDisabled} title="Send message">
      ➡
    </button>
  </div>
);

export default InputArea;
