#  ------------- the following code is to test with OpenAI, pinecone data -------------
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pinecone import Pinecone
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Pinecone as PineconeVectorStore
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from dotenv import load_dotenv
# import os


# # Load environment variables
# load_dotenv()
# open_ai_key = os.getenv("OPENAI_API_KEY")
# pinecone_api_key = os.getenv("PINECONE_API_KEY")

# # Initialize FastAPI app
# app = FastAPI()

# # Configure CORS
# origins = ["chrome-extension://*"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize OpenAI embeddings and Pinecone client
# embeddings = OpenAIEmbeddings()
# pc = Pinecone(api_key=pinecone_api_key)
# index_name = "macewan-vectors-openaiembeddings"

# # Create Pinecone Vector Store
# vector_store = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)

# # Initialize language model
# llm = ChatOpenAI(api_key=open_ai_key, model="gpt-4o-mini", temperature=0)

# # Define prompt template
# prompt_template = """
#     Answer the following question based only on the provided context. 
#     Think step by step before providing a detailed answer. If you cannot give an answer, say you do not have the answer.
#     <context>
#     {context}
#     </context>
#     Question: {input}
# """
# prompt = ChatPromptTemplate.from_template(prompt_template)

# # Create document chain and retriever
# document_chain = create_stuff_documents_chain(llm, prompt)
# retriever = vector_store.as_retriever(search_kwargs={"k": 8})

# # Combine retriever and document chain into a retrieval chain
# retrieval_chain = create_retrieval_chain(retriever, document_chain)

# # Define endpoint for handling queries
# @app.get("/query/")
# async def query_chat_bot(query: str):
#     try:
#         response = retrieval_chain.invoke({"input": query})
#         return JSONResponse(content={"response": response['answer']})
    
#     except Exception as e:
#         import traceback
#         print(f"An error occurred: {str(e)}")
#         print("Traceback:", traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))

# ------------- the following code is to using Cohere LLM, Pinecone, Hugginface Embeddings and Langchain -------------
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pinecone import Pinecone
from dotenv import load_dotenv
import os

from langchain_cohere import ChatCohere
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore

from typing_extensions import Annotated, TypedDict
from typing import Sequence

# Load environment variables
load_dotenv()

# CORS middleware to allow Chrome extension requests
origins = ["chrome-extension://hababammnbldmejcfphcldkhkfojdina"]

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API keys from environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
hf_api_token = os.getenv("HUGGINGFACE_API_TOKEN")  
cohere_api_token = os.getenv("COHERE_API_TOKEN")

# Initialize Pinecone with API key and connect to index
pc = Pinecone(api_key=pinecone_api_key)
index_name = "macewan-vectors-huggingface"
index = pc.Index(index_name)

# HuggingFace embeddings initialization
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=hf_api_token
)

# Create Pinecone Vector Store from existing index
vector_store = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
)

# Initialize Cohere LLM for chat
llm = ChatCohere(model="command-r-plus")

# Configure retriever to retrieve based on similarity score threshold
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 20, "score_threshold": 0.5},
)

# Define prompt to contextualize user questions
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question, "
    "which might reference context in the chat history, "
    "formulate a standalone question understandable without the history. "
    "Do NOT answer the question, just reformulate it or return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Create history-aware retriever with Cohere and Pinecone
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Define system prompt for Q&A
system_prompt = (
    "You are an assistant for university question-answering tasks. "
    "Use the following retrieved context to answer the question. "
    "If you don't know the answer, say so. Keep the answer concise."
    "\n\n"
    "{context}"
)

# Create Q&A prompt template
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Combine retrieval and document processing into a chain
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# State structure for managing chat history
class State(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: str

# Function to invoke the model and get a response
def call_model(state: State):
    response = rag_chain.invoke(state)
    return {
        "chat_history": [
            HumanMessage(state["input"]),
            AIMessage(response["answer"]),
        ],
        "context": response["context"],
        "answer": response["answer"],
    }

# Workflow setup for stateful chat management
workflow = StateGraph(state_schema=State)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Memory saving for checkpointing
memory = MemorySaver()
res = workflow.compile(checkpointer=memory)

# Configuration example for state workflow
config = {"configurable": {"thread_id": "abc123"}}

# API endpoint for querying the chat bot
@app.get("/query/")
async def query_chat_bot(query: str):
    try:   
        result = res.invoke({"input": query}, config=config)
        return JSONResponse(content={"response": result['answer']})
    except Exception as e:
        import traceback
        print("An error occurred: ", str(e))
        print("Traceback: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
