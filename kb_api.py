"""
Knowledge Base Management API

Provides endpoints for:
- Uploading documents (PDF, TXT, DOCX, MD)
- Managing collections
- Querying indexed documents
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import shutil
from datetime import datetime

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

app = FastAPI(title="Knowledge Base API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embeddings (shared across all collections)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Text splitter configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# Base directory for Chroma databases
CHROMA_BASE_DIR = "kb_storage"
os.makedirs(CHROMA_BASE_DIR, exist_ok=True)

# Supported file types
SUPPORTED_EXTENSIONS = {
    '.pdf': PyPDFLoader,
    '.txt': TextLoader,
    '.md': UnstructuredMarkdownLoader,
    '.docx': Docx2txtLoader,
}

# Pydantic models
class CollectionInfo(BaseModel):
    name: str
    document_count: int
    created_at: str
    last_updated: str

class UploadResponse(BaseModel):
    status: str
    collection: str
    chunks_added: int
    filename: str
    message: str

class QueryRequest(BaseModel):
    query: str
    collection: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    documents: List[dict]
    count: int

class DeleteResponse(BaseModel):
    status: str
    collection: str
    message: str


def get_collection_path(collection_name: str) -> str:
    """Get the persist directory for a collection."""
    return os.path.join(CHROMA_BASE_DIR, collection_name)

def get_loader_for_file(file_path: str):
    """Return appropriate document loader based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    return SUPPORTED_EXTENSIONS[ext](file_path)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Knowledge Base API",
        "status": "running",
        "version": "1.0.0",
        "supported_formats": list(SUPPORTED_EXTENSIONS.keys())
    }


@app.get("/collections", response_model=List[CollectionInfo])
async def list_collections():
    """List all knowledge base collections."""
    collections = []
    
    if not os.path.exists(CHROMA_BASE_DIR):
        return collections
    
    for collection_name in os.listdir(CHROMA_BASE_DIR):
        collection_path = get_collection_path(collection_name)
        
        if not os.path.isdir(collection_path):
            continue
        
        try:
            # Load collection to get document count
            vectordb = Chroma(
                collection_name=collection_name,
                persist_directory=collection_path,
                embedding_function=embeddings
            )
            
            # Get collection metadata
            collection = vectordb._collection
            doc_count = collection.count()
            
            # Get timestamps from directory
            created_at = datetime.fromtimestamp(
                os.path.getctime(collection_path)
            ).isoformat()
            last_updated = datetime.fromtimestamp(
                os.path.getmtime(collection_path)
            ).isoformat()
            
            collections.append(CollectionInfo(
                name=collection_name,
                document_count=doc_count,
                created_at=created_at,
                last_updated=last_updated
            ))
        except Exception as e:
            print(f"Error reading collection {collection_name}: {e}")
            continue
    
    return collections


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form(...),
):
    """
    Upload a document to a knowledge base collection.
    
    Args:
        file: Document file (PDF, TXT, DOCX, MD)
        collection: Name of the collection to add documents to
    
    Returns:
        Upload status and metadata
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {list(SUPPORTED_EXTENSIONS.keys())}"
        )
    
    # Validate collection name (no special characters)
    if not collection.replace('_', '').replace('-', '').isalnum():
        raise HTTPException(
            status_code=400,
            detail="Collection name must contain only letters, numbers, hyphens, and underscores"
        )
    
    # Save uploaded file to temporary location
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Load document
        loader = get_loader_for_file(temp_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata.update({
                'source_file': file.filename,
                'collection': collection,
                'uploaded_at': datetime.now().isoformat()
            })
        
        # Get or create collection
        collection_path = get_collection_path(collection)
        
        # Check if collection exists
        if os.path.exists(collection_path):
            # Add to existing collection
            vectordb = Chroma(
                collection_name=collection,
                persist_directory=collection_path,
                embedding_function=embeddings
            )
            vectordb.add_documents(chunks)
        else:
            # Create new collection
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=collection,
                persist_directory=collection_path
            )
        
        return UploadResponse(
            status="success",
            collection=collection,
            chunks_added=len(chunks),
            filename=file.filename,
            message=f"Successfully indexed {len(chunks)} chunks from {file.filename}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_path):
            os.unlink(temp_path)


@app.post("/query", response_model=QueryResponse)
async def query_collection(request: QueryRequest):
    """
    Query a knowledge base collection.
    
    Args:
        query: Search query text
        collection: Collection name to search
        top_k: Number of results to return (default: 5)
    
    Returns:
        Retrieved documents with scores
    """
    collection_path = get_collection_path(request.collection)
    
    if not os.path.exists(collection_path):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{request.collection}' not found"
        )
    
    try:
        vectordb = Chroma(
            collection_name=request.collection,
            persist_directory=collection_path,
            embedding_function=embeddings
        )
        
        # Perform similarity search
        results = vectordb.similarity_search_with_score(
            request.query,
            k=request.top_k
        )
        
        # Format results and convert distance to similarity score (0-1)
        documents = [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'distance': float(score),
                'score': max(0.0, 1.0 - float(score) / 3.0)  # Convert distance to similarity (0-1)
            }
            for doc, score in results
        ]
        
        return QueryResponse(
            query=request.query,
            documents=documents,
            count=len(documents)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying collection: {str(e)}"
        )


@app.delete("/collections/{collection_name}", response_model=DeleteResponse)
async def delete_collection(collection_name: str):
    """
    Delete a knowledge base collection.
    
    Args:
        collection_name: Name of collection to delete
    
    Returns:
        Deletion status
    """
    collection_path = get_collection_path(collection_name)
    
    if not os.path.exists(collection_path):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_name}' not found"
        )
    
    try:
        # Remove the collection directory
        shutil.rmtree(collection_path)
        
        return DeleteResponse(
            status="success",
            collection=collection_name,
            message=f"Collection '{collection_name}' deleted successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting collection: {str(e)}"
        )


@app.get("/collections/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """Get detailed statistics for a collection."""
    collection_path = get_collection_path(collection_name)
    
    if not os.path.exists(collection_path):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_name}' not found"
        )
    
    try:
        vectordb = Chroma(
            collection_name=collection_name,
            persist_directory=collection_path,
            embedding_function=embeddings
        )
        
        collection = vectordb._collection
        
        # Get all documents to analyze metadata
        results = collection.get()
        metadatas = results['metadatas']
        
        # Analyze source files
        source_files = {}
        for metadata in metadatas:
            source = metadata.get('source_file', 'unknown')
            source_files[source] = source_files.get(source, 0) + 1
        
        return {
            'collection': collection_name,
            'total_chunks': collection.count(),
            'source_files': source_files,
            'file_count': len(source_files),
            'created_at': datetime.fromtimestamp(
                os.path.getctime(collection_path)
            ).isoformat(),
            'last_updated': datetime.fromtimestamp(
                os.path.getmtime(collection_path)
            ).isoformat(),
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting collection stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
