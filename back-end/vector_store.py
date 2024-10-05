import time
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import itertools

# Load environment variables
load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

# Initialize Pinecone client and create index
pc = Pinecone(api_key=pinecone_api_key)

# uncomment which index name to connect to
index_name = "macewan-vectors-huggingface"
# index_name = "macewan-vectors-openaiembeddings"

existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,
        # Uncomment and use 1536 for OpenAI embeddings
        # dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)

# Initialize Hugging Face Embeddings and Pinecone Vector Store, uncomment which embedding you want to use,
# make sure to use correct dimmension and change index name accordingly
# embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

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

# Define a helper function to break an iterable into chunks of size batch_size
def chunks(iterable, batch_size=200):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

vectors = []

# Iterate over the chunks and generate embeddings
for i, chunk in enumerate(docs_chunks):
    chunk_embedding = embeddings.embed_documents([chunk.page_content]) 

    if isinstance(chunk_embedding, list) and isinstance(chunk_embedding[0], list):
        chunk_embedding = chunk_embedding[0]  

    metadata = {
        "page": chunk.metadata.get("page", "unknown"),
        "source": chunk.metadata.get("source", "unknown"),
        "text": chunk.page_content
    }

    vector = {
        "id": f"chunk_{i}",
        "values": chunk_embedding, 
        "metadata": metadata
    }

    # Log the vector details
    print(f"Preparing to upload vector: {vector['id']}")
    print(f"Values: {vector['values']}")
    print(f"Metadata: {vector['metadata']}")

    vectors.append(vector)

# Upsert vectors into Pinecone
if not index.describe_index_stats().total_vector_count:
    for vector_batch in chunks(vectors, batch_size=200):
        index.upsert(vectors=vector_batch, namespace="macewan_namespace")
        print(f"Uploaded a batch of {len(vector_batch)} vectors to Pinecone.")

print("Vectors upserted to Pinecone.")