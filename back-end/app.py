#  ------------- the following commented code is to test without any API or OpenAI -------------

# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # Add CORS middleware to allow requests from Chrome extension
# origins = [
#     "chrome-extension://hababammnbldmejcfphcldkhkfojdina"  # Replace this with extension's ID
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Allows Chrome extension origin
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allows all headers
# )

# # Sample endpoint to handle a basic query
# @app.get("/query/")
# async def query_chat_bot(query: str):
#     try:
#         response_message = f"You said: {query}"
#         return JSONResponse(content={"response": response_message}) 

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Main function to run the app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

#  ------------- the following code is to test with OpenAI -------------
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# load the OpenAI API key from the environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise Exception("OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(
    organization='org-P98OVEClYAjc9o3RH5cjewt6',
    project='proj_EHoX9E4WGlFA2SmvSdMBqItV',
    api_key=api_key 
)

app = FastAPI()

# Add CORS middleware to allow requests from Chrome extension
origins = [
    "chrome-extension://hababammnbldmejcfphcldkhkfojdina"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pdf and split pages
loader = PyPDFLoader("chat_bot/tests/testData.pdf")
pages = loader.load_and_split()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    length_function=len,
)

docs_chunks = text_splitter.split_documents(pages)
embeddings = OpenAIEmbeddings()
vectorStore = Chroma.from_documents(docs_chunks, embeddings)

retriever = vectorStore.as_retriever()

tool = create_retriever_tool(
    retriever,
    "university_information_retriever",
    "Searches and returns excerpts from the MacEwan University academic calendar.",
)
tools = [tool]

# build agent with llm and memory
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
memory = MemorySaver()
agent_executor = create_react_agent(llm, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}

# Sample endpoint to handle a basic query
@app.get("/query/")
async def query_chat_bot(query: str):
    try:        
        messages = [{"role": "user", "content": query}]
        responses = []
        
        for response in agent_executor.stream({"messages": messages}, config=config):
            print(f"Raw response from agent: {response}")
            
            if 'agent' in response and 'messages' in response['agent']:
                ai_message = response['agent']['messages'][0].content
                responses.append(ai_message)
            else:
                responses.append(response.get('content', 'No content found')) 
                
        return JSONResponse(content={"response": " ".join(responses)})

    except Exception as e:
        import traceback
        print("An error occurred: ", str(e))
        print("Traceback: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
