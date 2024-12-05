from fastapi import FastAPI, HTTPException, Request
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

from cohere.errors import TooManyRequestsError

from typing_extensions import Annotated, TypedDict
from typing import Sequence

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
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
    "Only answer based on the context, no external information unless it pertains to MacEwan"
    "List up to three sources as the URL from the context at the end of your answer."
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
    "You are an assistant for university answer questions to students, do not mention the context or text in your response."
    "List up to three sources as the URL from the context."
    "Only answer based on the context, no external internet information unless it pertains to MacEwan."
    "Be ethical, do not allow plagirism, do not write assignments, programs or exams for students."
    "Keep the answer concise."
    "Use the following retrieved context to answer the question only."
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

# Error handling function
def handle_error(e):
    if isinstance(e, TooManyRequestsError):
        return JSONResponse(
            content={
                "error": "Too many requests",
                "status_code": 429,
                "message": str(e)
            },
            status_code=429
        )
    return JSONResponse(
        content={
            "error": "Internal server error",
            "status_code": 500,
            "message": str(e)
        },
        status_code=500
    )

# API endpoint for querying the chat bot
@app.get("/query/")
async def query_chat_bot(query: str, request: Request):
    session_id = request.headers.get("Session-ID") or request.query_params.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID missing")
    config = {"configurable": {"thread_id": session_id}} 
    try:   
        result = res.invoke({"input": query}, config=config)
        return JSONResponse(content={"response": result['answer']})
    except Exception as e:
            return handle_error(e)