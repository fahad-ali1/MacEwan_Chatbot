#  ------------- the following code is to test with OpenAI not persitant data -------------
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
# from langchain.tools.retriever import create_retriever_tool
# from langgraph.prebuilt import create_react_agent
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import HumanMessage
# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # load the OpenAI API key from the environment variables
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise Exception("OPENAI_API_KEY is not set in the environment variables.")

# client = OpenAI(
#     organization='org-P98OVEClYAjc9o3RH5cjewt6',
#     project='proj_EHoX9E4WGlFA2SmvSdMBqItV',
#     api_key=api_key 
# )

# app = FastAPI()

# # Add CORS middleware to allow requests from Chrome extension
# origins = [
#     "chrome-extension://hababammnbldmejcfphcldkhkfojdina"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load pdf and split pages
# loader = PyPDFLoader("chat_bot/tests/testData.pdf")
# pages = loader.load_and_split()

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1200,
#     chunk_overlap=200,
#     length_function=len,
# )

# docs_chunks = text_splitter.split_documents(pages)
# embeddings = OpenAIEmbeddings()
# vectorStore = Chroma.from_documents(docs_chunks, embeddings)

# retriever = vectorStore.as_retriever()

# tool = create_retriever_tool(
#     retriever,
#     "university_information_retriever",
#     "Searches and returns excerpts from the MacEwan University academic calendar.",
# )
# tools = [tool]

# # build agent with llm and memory
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# memory = MemorySaver()
# agent_executor = create_react_agent(llm, tools, checkpointer=memory)
# config = {"configurable": {"thread_id": "abc123"}}

# # Endpoint to handle a basic query
# @app.get("/query/")
# async def query_chat_bot(query: str):
#     try:        
#         messages = [{"role": "user", "content": query}]
#         responses = []
        
#         for response in agent_executor.stream({"messages": messages}, config=config):
#             print(f"Raw response from agent: {response}")
            
#             if 'agent' in response and 'messages' in response['agent']:
#                 ai_message = response['agent']['messages'][0].content
#                 responses.append(ai_message)
                
#         return JSONResponse(content={"response": " ".join(responses)})

#     except Exception as e:
#         import traceback
#         print("An error occurred: ", str(e))
#         print("Traceback: ", traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))

# ------------- the following code is to test with Hugging Face using not persitant data -------------

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the Hugging Face API token from environment variables
hf_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not hf_api_token:
    raise Exception("HUGGINGFACEHUB_API_TOKEN is not set in the environment variables.")

# Initialize FastAPI
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

# Load PDF and split pages
loader = PyPDFLoader("chat_bot/tests/testData.pdf")
pages = loader.load_and_split()

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    length_function=len,
)

docs_chunks = text_splitter.split_documents(pages)

# Initialize embedding model for vector store
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create Chroma vector store from documents
vector_store = Chroma.from_documents(docs_chunks, embedding_model)

# Create retriever
retriever = vector_store.as_retriever()

# Build agent with Hugging Face LLM and memory
prompt_template = """
As a knowledgeable MacEwan university assistant, your role is to interpret academic queries using the MacEwan University vector store we provided to you. Please follow these guidelines when responding to user queries:
1. **Precision in Answers**: Respond only with information relevant to the user's query using the MacEwan University vector database. Do not start the answers with filler phrases or "according to the..."
2. **Directness**: Provide answers directly, without unnecessary context or filler phrases.
3. **Avoid Non-essential Sign-offs**: Do not include sign-offs like "Best regards" or "UniversityBot" in responses.
4. **Relevance Check**: If a query does not align with our academic database, guide the user to refine their question or decline to provide an answer.
5. **Clear Communication**: Eliminate unnecessary comments and focus on delivering concise, direct answers.
6. **Course Numbers**: When referring to courses, use the format "ACCT 111" for clarity.

University Query:
{context}

Question: {question}

Answer:
"""
custom_prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Initialize RAG chain with Hugging Face LLM
rag_chain = RetrievalQA.from_chain_type(
    llm=HuggingFaceHub(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        model_kwargs={"temperature": 1, "max_new_tokens": 2048},
        huggingfacehub_api_token=hf_api_token
    ), 
    chain_type="stuff", 
    retriever=retriever,  
    chain_type_kwargs={"prompt": custom_prompt}
)

# Endpoint to handle a basic query
@app.get("/query/")
async def query_chat_bot(query: str):
    try:
        # Call the function to get response from the model
        result = rag_chain({"query": query})
        response_text = result["result"]
        answer_start = response_text.find("\nAnswer:") + len("Answer:")
        answer = response_text[answer_start:].strip()
        return JSONResponse(content={"response": answer})
        
    except Exception as e:
        import traceback
        print("An error occurred: ", str(e))
        print("Traceback: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
