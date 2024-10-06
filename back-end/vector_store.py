import time
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeVectorStore

# Load environment variables
load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

# Initialize Pinecone client and create index
pc = Pinecone(api_key=pinecone_api_key)

# uncomment which index name to connect to
# index_name = "macewan-vectors-huggingface"
index_name = "macewan-vectors-openaiembeddings"

existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        # dimension=384,
        # Uncomment and use 1536 for OpenAI embeddings
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)

# Initialize Hugging Face Embeddings and Pinecone Vector Store, uncomment which embedding you want to use,
# make sure to use correct dimmension and change index name accordingly

embeddings = OpenAIEmbeddings()
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
#                                    multi_process=True,
#                                    encode_kwargs={"normalize_embeddings": True},
#                                    )

# Load PDF and split pages
loader = PyPDFLoader("back-end/chat_bot/tests/testData.pdf")
pages = loader.load_and_split()

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    length_function=len,
)

docs_chunks = text_splitter.split_documents(pages)

vector_store = PineconeVectorStore.from_documents(docs_chunks, embeddings, index_name=index_name)