import time
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeVectorStore

# Load environment variables
load_dotenv()

def main():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    # Initialize Pinecone client and create index
    pc = Pinecone(api_key=pinecone_api_key)

    # Uncomment which index name to connect to
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

    # Initialize Hugging Face Embeddings and Pinecone Vector Store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       multi_process=True,
                                       encode_kwargs={"normalize_embeddings": True})

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

    # Create the vector store from the document chunks
    # PineconeVectorStore.from_documents(docs_chunks, embeddings, index_name=index_name)

    for chunk in docs_chunks:
        # Generate embeddings for the chunk
        embedding = embeddings.embed_documents([chunk.page_content])[0]  # Get embedding for the chunk
        
        # Calculate the vector id (you can customize this logic)
        vector_id = f"chunk_{chunk.metadata['page']}_{chunk.metadata['source']}"  # Example ID based on page and source
        
        # Check for duplicates
        existing_vector = pc.fetch([vector_id])
        if existing_vector and existing_vector['vectors']:
            print(f"Vector with ID {vector_id} already exists, skipping insertion.")
            continue

        # Optional: Check similarity with existing vectors
        query_results = pc.query(embedding, top_k=5)  # Get top 5 most similar vectors
        if any(result['score'] > 0.9 for result in query_results['matches']):  # Adjust threshold as needed
            print(f"Similar vector found for ID {vector_id}, skipping insertion.")
            continue
        
        # Insert the vector if no duplicates found
        pc.upsert(vectors=[(vector_id, embedding)])

    print("Vector store updated successfully")



if __name__ == "__main__":
    main()
