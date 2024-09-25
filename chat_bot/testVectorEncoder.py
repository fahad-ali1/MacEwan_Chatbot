from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("testData.pdf")
pages = loader.load_and_split()
# print(pages[0])

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size      = 1200,
    chunk_overlap   = 200,
    length_function = len,
)

docs_chunks = text_splitter.split_documents(pages)

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

from langchain_community.vectorstores import Chroma

docsearch = Chroma.from_documents(docs_chunks, embeddings)

query = "Tell me about the department of psychology chair"

docs = docsearch.similarity_search(query)
print(docs[0])