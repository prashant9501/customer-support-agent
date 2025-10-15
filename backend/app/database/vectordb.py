"""
ChromaDB vector database initialization and management
"""
import json
import os
import logging
from typing import List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain_core.vectorstores import VectorStoreRetriever

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global retriever instance
_retriever: VectorStoreRetriever = None


def load_knowledge_base() -> List[Document]:
    """Load knowledge base documents from JSON file"""
    try:
        # Get the absolute path to the data file
        # __file__ is at backend/app/database/vectordb.py
        # We need to go up 3 levels to get to project root, then down to backend/data
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_path = os.path.join(current_dir, "data", "router_agent_documents.json")
        
        logger.info(f"Loading knowledge base from: {data_path}")
        
        with open(data_path, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
        
        documents = []
        for item in knowledge_base.get("documents", []):
            doc = Document(
                page_content=item["text"],
                metadata=item.get("metadata", {})
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} documents from knowledge base")
        return documents
        
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found at: {data_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing knowledge base JSON: {e}")
        raise


def initialize_vectordb() -> VectorStoreRetriever:
    """
    Initialize ChromaDB vector store and return retriever
    """
    global _retriever
    
    try:
        logger.info("Initializing ChromaDB vector store...")
        
        # Load documents
        documents = load_knowledge_base()
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Create or load vector store
        vectordb = Chroma.from_documents(
            documents=documents,
            collection_name=settings.chromadb_collection,
            embedding=embeddings,
            collection_metadata={"hnsw:space": "cosine"},
            persist_directory=settings.chromadb_path
        )
        
        # Create retriever with similarity score threshold
        _retriever = vectordb.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": settings.rag_top_k,
                "score_threshold": settings.rag_score_threshold
            }
        )
        
        logger.info("ChromaDB vector store initialized successfully")
        return _retriever
        
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        raise


def get_retriever() -> VectorStoreRetriever:
    """Get the global retriever instance"""
    global _retriever
    
    if _retriever is None:
        logger.info("Retriever not initialized, initializing now...")
        _retriever = initialize_vectordb()
    
    return _retriever


def search_knowledge_base(
    query: str,
    category_filter: str = None,
    top_k: int = None
) -> List[Document]:
    """
    Search knowledge base with optional category filtering
    
    Args:
        query: Search query text
        category_filter: Optional category to filter by (technical, billing, general)
        top_k: Number of results to return (default from settings)
    
    Returns:
        List of relevant documents
    """
    retriever = get_retriever()
    
    # Update search kwargs if needed
    if category_filter:
        retriever.search_kwargs["filter"] = {"category": category_filter.lower()}
    
    if top_k:
        retriever.search_kwargs["k"] = top_k
    
    try:
        results = retriever.invoke(query)
        logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return []
