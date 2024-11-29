// Load the chat history from local storage
export const loadChat = (setMessages) => {
  const savedChat = localStorage.getItem("chatHistory");
  if (savedChat) {
    setMessages(JSON.parse(savedChat));
  }
};

// Save the current chat messages to local storage
export function saveChat(chatMessages) {
  localStorage.setItem("chatHistory", JSON.stringify(chatMessages));
}

// Create session ID
export const getSessionId = () => {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
};

// Fetch a response from backend api
export const fetchResponse = async (userInput, sessionId) => {
  const response = await fetch(
    `https://macewan-chatbot-backend.onrender.com:10000/query/?query=${encodeURIComponent(
      userInput
    )}&session_id=${sessionId}`,
    {
      method: "GET",
      headers: {
        "Session-ID": sessionId,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      response.status === 429
        ? "Too many requests. Try later."
        : "Error occurred. Try later."
    );
  }

  return response;
};
