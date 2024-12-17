import time
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime
import logging
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Fetch API keys
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    hf_api_key = os.getenv("HUGGINGFACE_API_TOKEN")

    # Ensure environment variables are loaded
    if not pinecone_api_key:
        raise ValueError("Pinecone API key not found in environment variables.")
    if not hf_api_key:
        raise ValueError("HuggingFace API key not found in environment variables.")

    # Initialize Pinecone client
    pc = Pinecone(api_key=pinecone_api_key)

    # Index name
    index_name = "macewan-vectors-huggingface-test"

    # Check existing indexes and delete if exists
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name in existing_indexes:
        logger.info(f"Deleting '{index_name}' to create updated data...")
        pc.delete_index(index_name)

    # Create the Pinecone index
    logger.info("Creating Pinecone index...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

    # Wait for index to be ready
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

    # Initialize Hugging Face Embeddings
    model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEndpointEmbeddings(
        model=model,
        task="feature-extraction",
        huggingfacehub_api_token=hf_api_key,
    )

    # Load text file
    logger.info("Loading text file...")
    with open("back-end/chat_bot/crawlers/MacewanData.txt", "r", encoding="utf-8") as file:
        content = file.read()

    # Split content into sections based on "URL:" markers
    sections = re.split(r"(URL:\s*https?://[^\s]+)", content)
    
    # Pair URLs with their corresponding text
    url_text_pairs = []
    for i in range(1, len(sections), 2):
        url = sections[i].strip()
        text = sections[i + 1].strip() if i + 1 < len(sections) else ""
        url_text_pairs.append((url, text))

    logger.info(f"Extracted {len(url_text_pairs)} URL-text pairs.")

    # Split the text into chunks
    docs_chunks = []
    metadatas = []

    for idx, (url, text) in enumerate(url_text_pairs):
        logger.info(f"Processing URL {url}...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, 
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""], 
        )
        text_chunks = text_splitter.split_text(text)
        logger.info(f"Created {len(text_chunks)} chunks for URL {url}.")

        # Create metadata with timestamps and URL for each chunk
        timestamps = [datetime.now().strftime("%Y-%m-%dT%H:%M:%S") for _ in text_chunks]
        metadatas.extend([{"timestamp": ts, "source": url, "chunk_id": idx} for ts in timestamps])
        docs_chunks.extend(text_chunks)

    logger.info(f"Total number of chunks: {len(docs_chunks)}")

    # Create Pinecone Vector Store from text chunks
    logger.info("Creating Pinecone Vector Store from text chunks...")
    PineconeVectorStore.from_texts(docs_chunks, embeddings, metadatas=metadatas, index_name=index_name)

    logger.info("Pinecone Vector Store created successfully.")

if __name__ == "__main__":
    main()

# Commented out code incase we need to refer back to it

# import time
# from dotenv import load_dotenv
# import os
# from pinecone import Pinecone, ServerlessSpec
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_pinecone import PineconeVectorStore
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from datetime import datetime

# # Load environment variables
# load_dotenv()

# def main():
#     pinecone_api_key = os.getenv("PINECONE_API_KEY")

#     # Initialize Pinecone client and create index
#     pc = Pinecone(api_key=pinecone_api_key)
#     index_name = "macewan-vectors-huggingface"

#     existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

#     # Delete index if it exists for fresh data
#     if index_name in existing_indexes:
#         print(f"Deleting '{index_name}' to create updated data...")
#         pc.delete_index(index_name)

#     pc.create_index(
#         name=index_name,
#         dimension=384,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#     )
#     while not pc.describe_index(index_name).status["ready"]:
#         time.sleep(1)

#     # Initialize Hugging Face Embeddings 
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#     # Load text file and split content
#     print("Loading text file...")
#     with open("back-end/chat_bot/crawlers/MacewanData.txt", "r", encoding="utf-8") as file:
#         content = file.read()

#     # Split the text into chunks
#     print("Splitting text into chunks...")
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=2500,
#         chunk_overlap=500,
#         length_function=len,
#     )
#     docs_chunks = text_splitter.split_text(content)

#     # Create metadata with timestamps for each document chunk
#     print("Creating metadata with timestamps...")
#     timestamps = [datetime.now().strftime("%Y-%m-%d T%H:%M:%S") for _ in docs_chunks]
#     metadatas = [{"timestamp": ts} for ts in timestamps]

#     print("Creating Pinecone Vector Store from text chunks...")
#     PineconeVectorStore.from_texts(docs_chunks, embeddings, metadatas=metadatas, index_name=index_name)
#     print("Pinecone Vector Store created successfully.")

# if __name__ == "__main__":
#     main()