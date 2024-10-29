import time
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime
# from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

def main():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    # Initialize Pinecone client and create index
    pc = Pinecone(api_key=pinecone_api_key)

    # NOTE: uncomment which index name to connect to
    index_name = "macewan-vectors-huggingface"
    # index_name = "macewan-vectors-openaiembeddings"

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    # Delete index if it exists for fresh data
    if index_name in existing_indexes:
        print(f"Deleting '{index_name}' to create fresh data...")
        pc.delete_index(index_name)

    pc.create_index(
        name=index_name,
        dimension=384,
        # NOTE: Uncomment and use 1536 for OpenAI embeddings, 384 for HuggingFace
        # dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

    # Initialize Hugging Face Embeddings 
    # NOTE: uncomment which embedding you want to use
    # embeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Load text file and split content
    print("Loading text file...")
    with open("back-end/chat_bot/crawlers/MacewanData.txt", "r", encoding="utf-8") as file:
        content = file.read()

    # Split the text into chunks
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=500,
        length_function=len,
    )
    docs_chunks = text_splitter.split_text(content)

    # Create metadata with timestamps for each document chunk
    print("Creating metadata with timestamps...")
    timestamps = [datetime.now().strftime("%Y-%m-%d T%H:%M:%S") for _ in docs_chunks]
    metadatas = [{"timestamp": ts} for ts in timestamps]

    print("Creating Pinecone Vector Store from text chunks...")
    PineconeVectorStore.from_texts(docs_chunks, embeddings, metadatas=metadatas, index_name=index_name)
    print("Pinecone Vector Store created successfully.")

if __name__ == "__main__":
    main()