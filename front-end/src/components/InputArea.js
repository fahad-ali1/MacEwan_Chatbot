const InputArea = ({
  userInput,
  handleInputChange,
  handleKeyDown,
  sendMessage,
  isDisabled,
}) => {
  
  // Global initial heights
  const initialHeightT = '4rem'; // Default height from CSS for textarea
  const initialHeightI = '4.5rem'; // Assuming the input container height is 0.5rem more

  // Function to adjust the height of the textarea and its container
  const adjustHeight = (event) => {
    const textarea = event.target;
    const container = textarea.parentNode; // Get the parent container

    // Reset the textarea height to initial height
    textarea.style.height = initialHeightT;

    if (textarea.scrollHeight > parseInt(initialHeightT)) {
      textarea.style.height = `${textarea.scrollHeight}px`;
      container.style.height = `${textarea.scrollHeight + 10}px`; // Adjust the container's height to 5px more than textarea's height
    } else {
      textarea.style.height = initialHeightT;
      container.style.height = initialHeightI; // Reset the container's height to default + 5px
    }
  };

  // Function to handle sending the message and resetting the height
  const handleSendMessage = () => {
    if (!userInput.trim()) return; // Prevent sending empty messages
    sendMessage();
    const textarea = document.querySelector('.input-container textarea');
    const container = textarea.parentNode; // Get the parent container
    if (textarea) {
      textarea.style.height = initialHeightT; // Reset to default height
      container.style.height = initialHeightI; // Reset container height to default + 5px
    }
  };

  // Function to handle keydown events
  const handleKeyDownEvent = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent newline character in the textarea
      handleSendMessage(); // Send message and reset height
    } else {
      handleKeyDown(event); // Call the original handleKeyDown function for other keys
    }
  };

  return (
    <div className="input-container">
      <textarea
        value={userInput}
        onChange={(event) => {
          handleInputChange(event);
          adjustHeight(event); // Call the adjustHeight function on input change
        }}
        onKeyDown={handleKeyDownEvent}
        placeholder="Type your message ..."
        disabled={isDisabled}
        style={{ height: 'auto', overflowY: 'hidden' }} // Set initial styles
      />
      <button onClick={handleSendMessage} disabled={isDisabled} title="Send message">
        ➡
      </button>
    </div>
  );
};

export default InputArea;
