// This component creates the bot message icon
const Message = ({ message }) => {
  return (
    <div className={`chat ${message.sender}-message`}>
      {message.sender === "bot" && (
        <span className="material-symbols-outlined">smart_toy</span>
      )}
      <p>{message.text}</p>
    </div>
  );
};

export default Message;
