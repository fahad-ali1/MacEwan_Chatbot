#  ------------- the following code is to test with OpenAI persitant pinecone data -------------
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pinecone import Pinecone
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Pinecone as PineconeVectorStore
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # Load OpenAI and Pinecone API keys from environment variables
# api_key = os.getenv("OPENAI_API_KEY")
# pinecone_api_key = os.getenv("PINECONE_API_KEY")

# app = FastAPI()

# # Add CORS middleware to allow requests from Chrome extension
# origins = ["chrome-extension://hababammnbldmejcfphcldkhkfojdina"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize embeddings using OpenAI
# embeddings = OpenAIEmbeddings()

# # Initialize Pinecone client and connect to the existing index
# pc = Pinecone(api_key=pinecone_api_key)
# index_name = "macewan-vectors-openaiembeddings"

# # Create Pinecone Vector Store from existing index
# vector_store = PineconeVectorStore.from_existing_index(
#     index_name=index_name,
#     embedding=embeddings,
# )

# # Endpoint to handle a basic query
# @app.get("/query/")
# async def query_chat_bot(query: str):
#     try:
#         # Use the similarity search to retrieve relevant documents
#         docs = vector_store.similarity_search(query, k=15)

#         # Combine the content of all retrieved documents as the context
#         context = "\n\n".join([doc.page_content for doc in docs])
#         # logging
#         print(context) 

#         # Prepare messages for the agent with the query and the retrieved document context
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are a helpful assistant. Only answer the question using the provided context. Do not use any external information, assumptions, or personal opinions. If the context does not provide an answer, say that you cannot provide a relevant answer based on the available documents."
#             },
#             {
#                 "role": "system",
#                 "content": f"Context:\n{context}" if context else "No relevant information was found."
#             },
#             {
#                 "role": "user",
#                 "content": query
#             }
#         ]

#         # Initialize the ChatOpenAI model
#         chat_model = ChatOpenAI(api_key=api_key)
#         response = chat_model.invoke(messages)

#         # Access the content of the AI message
#         ai_message_content = response.content 
#         return JSONResponse(content={"response": ai_message_content})

#     except Exception as e:
#         import traceback
#         print("An error occurred: ", str(e))
#         print("Traceback: ", traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))

# ------------- the following code is to test with Hugging Face using pinecone -------------
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Add CORS middleware to allow requests from Chrome extension
origins = [
    "chrome-extension://hababammnbldmejcfphcldkhkfojdina"
]

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pinecone API Key from environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
index_name = "macewan-vectors-huggingface"
index = pc.Index(index_name)

hf_api_token = os.getenv("HUGGINGFACE_API_TOKEN")  

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2",
                                           task="feature-extraction",
                                           huggingfacehub_api_token=hf_api_token)

# Create Pinecone Vector Store from existing index
vector_store = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
)
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=hf_api_token,
    max_new_tokens = 200,
    temperature = 1,
    )

@app.get("/query/")
async def query_chat_bot(query: str):
    try:
        # Use the similarity search to retrieve relevant documents
        docs = vector_store.similarity_search(query, k=12)

        # Combine the content of all retrieved documents as the context
        context = "\n\n".join([doc.page_content for doc in docs])

        messages = [
            {
                "role": "system",
                "content": 
                '''You are a helpful university assistant. Do not say according to context or sources in your answer.
                Respond only to the question asked, response should be concise and relevant to the question.
                Provide the number of the source document when relevant.
                If the answer cannot be deduced from the context, do not give an answer.
                '''
            },
            {
                "role": "system",
                "content": f"Context:\n{context}" if context else "No relevant information was found."
            },
            {
                "role": "user",
                "content": query
            }
        ]

        response = llm.invoke(messages)
        chat_model = ChatHuggingFace(llm=llm)
        msg = chat_model.invoke(messages)
        # Access the content of the AI message
        # print(response)
        print(msg)
        return JSONResponse(content={"response": response})

    except Exception as e:
        import traceback
        print("An error occurred: ", str(e))
        print("Traceback: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
