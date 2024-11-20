/**
 * Get or create a session ID.
 * @returns {string} The session ID.
 */
export function getSessionId() {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
}

/**
 * Fetches the response from the server.
 * @param {string} userInput - The user's message.
 * @param {string} sessionId - The session ID.
 * @returns {Promise<Response>} The fetch response.
 */
export async function fetchResponse(userInput, sessionId) {
  const response = await fetch(
    `http://127.0.0.1:8000/query/?query=${encodeURIComponent(
      userInput
    )}&session_id=${sessionId}`,
    {
      headers: {
        "Session-ID": sessionId,
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
}
