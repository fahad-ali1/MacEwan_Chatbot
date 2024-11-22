
# MacEwan Chatbot Assistant

This project comprises a backend (Python FastAPI server) and a frontend (React-based web application) for the MacEwan chatbot assistant.

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
MacEwan_Chatbot_Assistant
├── back-end/
│   ├── chat_bot/
│   │   ├── crawlers/
│   ├── app.py
│   ├── vector_store.py
│   └── .env
├── front-end/
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   ├── src/
│   │   ├── components/
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
- **Node.js 14++**
- **npm 6++**
  
## Setting up the Virtual Environment on your machine

To run the backend services and manage Python dependencies efficiently, it’s recommended to use a virtual environment.

### Step 1: Creating the Virtual Environment

In the root directory of the project, run the following command:

```bash
python3.12 -m venv venv
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
HUGGINGFACE_API_TOKEN=your_api_key_here
PINECONE_API_KEY=your_api_key_here
COHERE_API_KEY=your_api_key_here
```

### Step 2: Running the Backend Server Locally

Once the virtual environment is active and dependencies are installed, go to the back-end directory and execute the FastAPI server using `uvicorn`:

```bash
uvicorn back-end.app:app --reload
```

- **The backend will be available at local address **: `http://127.0.0.1:8000`

## Frontend Setup and Running

If you want to change the way the chrome extension looks, you may do so with the following instructions.

### Step 1: Install Dependencies
Navigate to the front-end/ directory and run the following command to install the required Node.js dependencies:

```bash
npm install
npm start
```

The frontend will be accessible at http://localhost:3000 and your local internet address.

## Running Both Backend and Frontend Together

Start the Backend:
    
  Activate the Python virtual environment and run the FastAPI server as mentioned in the Backend Setup and Running section.

Start the Frontend:

  Navigate to the front-end/ directory and start the React development server as mentioned in the Frontend Setup and Running section.

Interaction:

  The React frontend will send API requests to the backend running at http://127.0.0.1:8000 (or any other backend server you change to).

## Images
