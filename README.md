
# MACEWAN_CHATBOT_CAPSTONE

This project contains both the backend (Python FastAPI server) and the frontend (Chrome extension) for the MacEwan chatbot assitant.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Requirements](#requirements)
3. [Setting up the Virtual Environment](#setting-up-the-virtual-environment-on-your-machine)
4. [Backend Setup and Running](#local-backend-setup-and-running)
5. [Frontend Setup and Running](#frontend-setup-and-running)
6. [Running Both Backend and Frontend Together](#running-both-backend-and-frontend-together)
7. [Images](#images)

---

## Project Structure

```
MacEwan_Chatbot_ChromeExtension
├── back-end/
│   ├── chat_bot/
│   │   ├── tests/
│   │   ├── crawlers/
│   ├── app.py
│   └── .env
├── front-end/
│   ├── chrome_extension/
│   │   ├── popup/
│   ├── manifest.json
├── venv/
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

- **Python 3.8+**
- **Google Chrome Browser**
  
## Setting up the Virtual Environment on your machine

To run the backend services and manage Python dependencies efficiently, it’s recommended to use a virtual environment.

### Step 1: Creating the Virtual Environment

In the root directory of the project, run the following command:

```bash
python -m venv venv
```

### Step 2: Activating the Virtual Environment

- **On Windows**:
  ```bash
  .env\Scriptsctivate
  ```

- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Installing the Dependencies

Once the virtual environment is activated, install the required Python packages listed in the `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

## Local backend Setup and Running

If you want to run the server with your own OpenAI API, you may do so with the following instructions.

The backend is powered by FastAPI and integrates with OpenAI APIs, along with langchain, chromaDB and supporting libraries as listed in `requirement.txt`. 

### Step 1: Set Up Environment Variables

Create a `.env` file in the `back-end/` directory. Add the necessary environment variables like:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 2: Running the Backend Server

Once the virtual environment is active and dependencies are installed, go to the back-end directory and execute the FastAPI server using `uvicorn`:

```bash
uvicorn back-end.app:app --reload
```

- **The backend will be available at**: `http://127.0.0.1:8000`

## Frontend Setup and Running

If you want to change the way the chrome extension looks, you may do so with the following instructions.

The frontend is a Chrome extension that interacts with the backend API.

### Step 1: Load the Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle at the top right).
3. Click on **Load unpacked** and select the `front-end/chrome_extension/` directory.

### Step 2: Interacting with the Chrome Extension

1. Once loaded, the Chrome extension will appear as an icon next to the address bar.
2. Click the icon to open the extension popup. It will send requests to the backend API and get information integrating the ChatGPT LLM.

## Running Both Backend and Frontend Together

To test both front and back end locally:

1. **Start the local backend** by running the FastAPI server as described above.
2. **Load the Chrome extension** into your browser.
3. Use the extension popup to interact with the chatbot, which will send requests to the backend server.

## Images