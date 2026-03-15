import os
from langchain_community.document_loaders import PyPDFLoader
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool

def initialize_rag():
    """
    Initializes the RAG system: loads documents, creates embeddings,
    stores them in ChromaDB (if not exists), and returns a defined tool.
    """
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    chroma_path = os.path.join(data_dir, 'chroma_db')
    
    # Check for PDF file
    pdf_files = [f for f in os.listdir(data_dir) if f.casefold().endswith('.pdf')]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF file found in {data_dir}")
    pdf_path = os.path.join(data_dir, pdf_files[0])
    
    # 1. Initialize Embedding Function
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Check if vector store exists
    if os.path.exists(chroma_path) and os.listdir(chroma_path):
        print("Loading existing vector store...")
        vectorstore = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    else:
        print(f"Creating new vector store from {pdf_files[0]}...")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        # Split Documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Create Vector Store
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings, 
            persist_directory=chroma_path
        )
        print("Vector store created and persisted.")

    # 2. Create Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 3. Create Tool
    tool = create_retriever_tool(
        retriever,
        "get_resume_info",
        "Searches and retrieves information from the user's resume and bio. Use this tool when asked about the user's experience, skills, or background."
    )
    return tool

def reindex_knowledge_base():
    """
    Clears the existing vector store and rebuilds it from the PDF in data directory.
    Useful for updating the agent's memory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    chroma_path = os.path.join(data_dir, 'chroma_db')
    
    # Check for PDF file
    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("Warning: No PDF found to re-index.")
        return
    
    pdf_path = os.path.join(data_dir, pdf_files[0])
    
    # Initialize Embedding Function
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Remove existing vector store
    import shutil
    if os.path.exists(chroma_path):
        try:
            shutil.rmtree(chroma_path)
            print("Cleared old vector store.")
        except Exception as e:
            print(f"Error clearing vector store: {e}")
    
    print(f"Re-indexing vector store from {pdf_files[0]}...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    # Split Documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # Create Vector Store
    Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=chroma_path
    )
    print("Vector store re-indexed.")
