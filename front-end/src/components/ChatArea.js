/**
 * ChatArea Utilities
 * Provides functions for managing chat session storage and interacting with the backend API.
 */

/**
 * Loads chat history from localStorage and updates the state.
 *
 * @param {Function} setMessages - Function to update the chat messages state.
 */
export const loadChat = (setMessages) => {
  try {
    const savedChat = localStorage.getItem("chatHistory");
    if (savedChat) {
      setMessages(JSON.parse(savedChat));
    }
  } catch (error) {
    console.error("Error loading chat history:", error);
  }
};

/**
 * Saves the current chat messages to localStorage.
 *
 * @param {Array} chatMessages - Array of chat messages to be saved.
 */
export const saveChat = (chatMessages) => {
  try {
    localStorage.setItem("chatHistory", JSON.stringify(chatMessages));
  } catch (error) {
    console.error("Error saving chat history:", error);
  }
};

/**
 * Retrieves or generates a unique session ID for the chat session.
 *
 * @returns {string} A unique session ID.
 */
export const getSessionId = () => {
  try {
    let sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      sessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
      localStorage.setItem("session_id", sessionId);
    }
    return sessionId;
  } catch (error) {
    console.error("Error managing session ID:", error);
    return "unknown-session";
  }
};

/**
 * Sends a user query to the backend API and fetches the response.
 *
 * @param {string} userInput - The user's input message.
 * @param {string} sessionId - The session ID associated with the chat.
 * @returns {Promise<Response>} The backend API response.
 * @throws {Error} If the API call fails or returns an error status.
 */
export const fetchResponse = async (userInput, sessionId) => {
  try {
    // https://macewan-chatbot-backend.onrender.com/query/?query=
    const response = await fetch(
      `http://127.0.0.1:8000/query/?query=${encodeURIComponent(
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
  } catch (error) {
    console.error("Error fetching response from backend:", error);
    throw error;
  }
};
