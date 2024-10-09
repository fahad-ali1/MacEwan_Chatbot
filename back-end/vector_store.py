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

def main():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    # Initialize Pinecone client and create index
    pc = Pinecone(api_key=pinecone_api_key)

    # NOTE: uncomment which index name to connect to
    index_name = "macewan-vectors-huggingface"
    # index_name = "macewan-vectors-openaiembeddings"

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
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

    # Initialize Hugging Face Embeddings and Pinecone Vector Store, NOTE: uncomment which embedding you want to use,

    # embeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       multi_process=True,
                                       encode_kwargs={"normalize_embeddings": True},
                                       )

    # Load PDF and split pages
    print("Loading PDF and splitting pages...")
    loader = PyPDFLoader("back-end/chat_bot/tests/testData.pdf")
    pages = loader.load_and_split()

    # Split the documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        length_function=len,
    )

    docs_chunks = text_splitter.split_documents(pages)
    print("Creating Pinecone Vector Store from documents...")
    PineconeVectorStore.from_documents(docs_chunks, embeddings, index_name=index_name)
    print("Pinecone Vector Store created successfully.")

if __name__ == "__main__":
    main()