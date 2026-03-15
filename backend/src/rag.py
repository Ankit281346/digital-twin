import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


class LightweightEmbeddings(Embeddings):
    """
    Lightweight wrapper around ChromaDB's built-in ONNX embedding function.
    Uses the all-MiniLM-L6-v2 model via onnxruntime (~50MB).
    
    This REPLACES sentence-transformers + PyTorch (~4GB) with a minimal
    ONNX-based alternative that is already bundled as a chromadb dependency.
    """
    def __init__(self):
        self._fn = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list) -> list:
        return [list(v) for v in self._fn(texts)]

    def embed_query(self, text: str) -> list:
        return list(self._fn([text])[0])


def initialize_rag():
    """
    Initializes the RAG system: loads documents, creates embeddings,
    stores them in ChromaDB (if not exists), and returns a LangChain tool.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    chroma_path = os.path.join(data_dir, 'chroma_db')

    # Check for PDF file
    pdf_files = [f for f in os.listdir(data_dir) if f.casefold().endswith('.pdf')]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF file found in {data_dir}")
    pdf_path = os.path.join(data_dir, pdf_files[0])

    # Use lightweight ONNX-based embeddings (no PyTorch needed)
    embeddings = LightweightEmbeddings()

    # Load or create vector store
    if os.path.exists(chroma_path) and os.listdir(chroma_path):
        print("Loading existing vector store...")
        vectorstore = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    else:
        print(f"Creating new vector store from {pdf_files[0]}...")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=chroma_path
        )
        print("Vector store created and persisted.")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    tool = create_retriever_tool(
        retriever,
        "get_resume_info",
        "Searches and retrieves information from the user's resume and bio. Use this tool when asked about the user's experience, skills, or background."
    )
    return tool


def reindex_knowledge_base():
    """
    Clears the existing vector store and rebuilds it from the PDF in data directory.
    """
    import shutil

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    chroma_path = os.path.join(data_dir, 'chroma_db')

    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("Warning: No PDF found to re-index.")
        return

    pdf_path = os.path.join(data_dir, pdf_files[0])
    embeddings = LightweightEmbeddings()

    if os.path.exists(chroma_path):
        try:
            shutil.rmtree(chroma_path)
            print("Cleared old vector store.")
        except Exception as e:
            print(f"Error clearing vector store: {e}")

    print(f"Re-indexing vector store from {pdf_files[0]}...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=chroma_path
    )
    print("Vector store re-indexed.")
