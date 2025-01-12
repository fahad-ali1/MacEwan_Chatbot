# MacEwan Chatbot Assistant

This project consists of a backend (Python FastAPI server) and a frontend (React-based web application) for the MacEwan chatbot assistant.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Requirements](#requirements)
3. [Setting up the Virtual Environment](#setting-up-the-virtual-environment)
4. [Backend Setup and Running](#backend-setup-and-running)
5. [Frontend Setup and Running](#frontend-setup-and-running)
6. [Running Both Backend and Frontend Together](#running-both-backend-and-frontend-together)
7. [API Calls](#api-calls)
8. [Images](#images)

---

## Project Structure

```
MacEwan_Chatbot_Assistant
├── back-end/
│   ├── chat_bot/
│   │   ├── crawlers/
│   │   │   └── ReaderCrawler.py
│   ├── .env
│   ├── main.py
│   ├── vector_store.py
│   └── app.py
├── front-end/
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── manifest.json
│   ├── src/
│   │   ├── components/
│   │   ├── images/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── styles.css
│   ├── package.json
│   ├── package-lock.json
├── venv/
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

- **Python 3.12**
- **Node.js 14+**
- **npm 6+**

## Setting up the Virtual Environment

To efficiently manage Python dependencies and run backend services, it's recommended to use a virtual environment, though it's not mandatory.

### Step 1: Creating the Virtual Environment

In the root directory of the project, execute:

```bash
python3.12 -m venv venv
```

### Step 2: Activating the Virtual Environment

- **On Windows**:
  ```bash
  .\venv\Scripts\activate
  ```

- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Installing the Dependencies

With the virtual environment activated, install the required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Backend Setup and Running

If you prefer to run the backend locally instead of using the hosted version on Render (https://macewan-chatbot-backend.onrender.com/query), follow these steps. The backend uses FastAPI and integrates with Coheres, langchain and PineCones APIs.

### Step 1: Set Up Environment Variables

Create a `.env` file in the `back-end/` directory and add the necessary environment variables:

```
HUGGINGFACE_API_TOKEN=your_api_key_here
PINECONE_API_KEY=your_api_key_here
COHERE_API_KEY=your_api_key_here
```

### Step 2: Running the Backend Server Locally

With the virtual environment active and dependencies installed, navigate to the `back-end` directory and start the FastAPI server using `uvicorn`:

```bash
uvicorn back-end.app:app --reload
```

- **The backend will be accessible at**: `http://127.0.0.1:8000`

## Frontend Setup and Running

To modify the frontend appearance, follow these steps.

### Step 1: Install Dependencies

Navigate to the `front-end/` directory and install the required Node.js dependencies:

```bash
npm install
npm start
```

The frontend will be accessible at `http://localhost:3000`.

## Running Both Backend and Frontend Together

### Start the Backend

Activate the Python virtual environment and run the FastAPI server as described in the Backend Setup and Running section.

### Start the Frontend

Navigate to the `front-end/` directory and start the React development server as described in the Frontend Setup and Running section.

### Interaction

The React frontend will send API requests to the backend running at `http://127.0.0.1:8000` (or any other backend server you configure).

## API Calls

The frontend communicates with the backend using the following API call:

```javascript
const response = await fetch(
  `https://macewan-chatbot-backend.onrender.com/query/?query=${encodeURIComponent(userInput)}&session_id=${sessionId}`,
  {
    method: "GET",
    headers: {
      "Session-ID": sessionId,
      "Content-Type": "application/json",
    },
  }
);
```

- **Endpoint**: `/query/`
- **Method**: GET
- **Parameters**:
  - `query`: The user input to be processed by the chatbot.
  - `session_id`: A identifier for the session.
- **Headers**:
  - `Session-ID`: The session identifier.
  - `Content-Type`: `application/json`

## Images
<img width="453" alt="chatbot_screenshot" src="https://github.com/user-attachments/assets/1533b416-d5f9-41f9-b05b-081c3b8402e7" />
