import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Customize DOMPurify to remove unnecessary tags
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  // Remove empty tags
  if (node.tagName === 'P' && !node.textContent.trim()) {
    node.parentNode.removeChild(node);
  }
});

const Message = ({ message }) => {
  let content;
  if (message.sender === "bot") {
    const htmlText = marked(message.text); // Convert Markdown to HTML
    const sanitizedHtml = DOMPurify.sanitize(htmlText); // Sanitize the HTML
    content = <div className="markdown-container" dangerouslySetInnerHTML={{ __html: sanitizedHtml }}></div>;
  } else {
    content = <p className="markdown-container">{message.text}</p>;
  }

  return (
    <div className={`chat ${message.sender}-message`}>
      {message.sender === "bot" && (
        <span
          className="material-symbols-outlined"
          style={{ alignSelf: "flex-end" }}
        >
          smart_toy
        </span>
      )}
      {content}
    </div>
  );
};

export default Message;
