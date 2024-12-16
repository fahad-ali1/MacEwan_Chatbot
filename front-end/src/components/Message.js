import { marked } from "marked";
import DOMPurify from "dompurify";

// DOMPurify customization to remove empty tags
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "P" && !node.textContent.trim()) {
    node.remove();
  }
});

/**
 * Message Component
 * Renders messages from the bot or user, with Markdown rendering for bot messages.
 *
 * @param {Object} message - The message object containing text and sender info.
 * @returns JSX Element for the message.
 */
const Message = ({ message }) => {
  const isBot = message.sender === "bot";
  const sanitizedHtml = isBot ? DOMPurify.sanitize(marked(message.text)) : null;

  return (
    <div className={`chat ${message.sender}-message`}>
      {isBot && (
        <span
          className="material-symbols-outlined"
          style={{ alignSelf: "flex-end" }}
        >
          smart_toy
        </span>
      )}
      {isBot ? (
        <div
          className="markdown-container"
          dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
        ></div>
      ) : (
        <p className="markdown-container">{message.text}</p>
      )}
    </div>
  );
};

export default Message;
