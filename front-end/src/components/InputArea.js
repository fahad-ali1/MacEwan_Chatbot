/**
 * InputArea Component
 * Renders the input area for the user to type their messages and send them to the chatbot.
 *
 * Props:
 * - userInput: (string) The current value of the input field.
 * - handleInputChange: (function) Updates the state when the input value changes.
 * - handleKeyDown: (function) Handles key press events in the input field.
 * - sendMessage: (function) Sends the user's message.
 * - isDisabled: (boolean) Disables the input and button when true.
 */

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
      onChange={handleInputChange} // Triggered on text input changes
      onKeyDown={handleKeyDown} // Triggered on key press events
      placeholder="Type your message ..."
      disabled={isDisabled} // Disables the input when waiting for a bot response
      aria-label="Message input area"
    />
    <button
      className="send-button"
      onClick={sendMessage} // Trigger message sending
      disabled={isDisabled} // Disables the button while waiting for a bot response
      title="Send message"
      aria-label="Send message"
    >
      ➡
    </button>
  </div>
);

export default InputArea;
