from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage



# Load pdf and split pages
loader = PyPDFLoader("back-end/chat_bot/tests/testData.pdf")
pages = loader.load_and_split()
# print(pages[0])


# Split text 
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size      = 1200,
    chunk_overlap   = 200,
    length_function = len,
)

# Split document into chunks
docs_chunks = text_splitter.split_documents(pages)

# Create embedding and build vector store
embeddings = OpenAIEmbeddings()
vectorStore = Chroma.from_documents(docs_chunks, embeddings)

# create retriever
retriever = vectorStore.as_retriever()

# Create retriever tool for agent
tool = create_retriever_tool(
    retriever,
    "university_information_retriever",
    "Searches and returns excerpts from the MacEwan University academic calendar.",
)
tools = [tool]



# build agent with llm and memory
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
memory = MemorySaver()
agent_executor = create_react_agent(llm, tools, checkpointer=memory)

query = "Who is the chair of the department of psychology?"
config = {"configurable": {"thread_id": "abc123"}}
for s in agent_executor.stream(
    {"messages": [HumanMessage(content=query)]}, config=config
):
    print(s)
    print("----")