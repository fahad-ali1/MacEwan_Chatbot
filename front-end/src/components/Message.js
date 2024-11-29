import {marked} from 'marked'
import DOMPurify from 'dompurify'
// This component creates the bot message icon
const Message = ({ message }) => {
  let content; 
  if (message.sender === "bot") { const htmlText = marked(message.text); // Convert Markdown to HTML 
    const sanitizedHtml = DOMPurify.sanitize(htmlText); // Sanitize the HTML 
    content = <p dangerouslySetInnerHTML={{ __html: sanitizedHtml }}></p>; 
  } else { 
    content = <p>{message.text}</p>;
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
