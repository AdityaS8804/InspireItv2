import os
import time
import shutil
from pathlib import Path
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.schema import Document
from tqdm import tqdm

# Paths and constants
DATA_PATH = Path('/Users/vedanshkumar/Documents/Fun_ml/Hackathon/RAG/Reseach_paper')
CHROMA_PATH = Path('/Users/vedanshkumar/Documents/Fun_ml/Hackathon/RAG/chroma')
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 5  # Reduced batch size
RATE_LIMIT_DELAY = 2  # Increased delay between batches

def document_load(data_path: Path) -> List[Document]:
    """
    Load PDF documents from the specified directory.
    
    Args:
        data_path (Path): Path to the directory containing PDF files
        
    Returns:
        List[Document]: List of loaded documents
        
    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Directory not found: {data_path}")
        
    loader = PyPDFDirectoryLoader(str(data_path), load_hidden=False, extract_images=False)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {data_path}")
    return documents

def document_chunking(
    documents: List[Document], 
    chunk_size: int = CHUNK_SIZE, 
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    Split documents into smaller chunks for processing.
    
    Args:
        documents (List[Document]): List of documents to split
        chunk_size (int): Size of each chunk
        chunk_overlap (int): Overlap between chunks
        
    Returns:
        List[Document]: List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def process_batch_with_retry(
    batch: List[Document],
    embedding_function: MistralAIEmbeddings,
    db: Chroma,
    max_retries: int = 3,
    initial_retry_delay: int = 60
) -> None:
    """
    Process a batch of documents with retry logic.
    
    Args:
        batch (List[Document]): Batch of documents to process
        embedding_function: Embedding function to use
        db: Chroma database instance
        max_retries: Maximum number of retry attempts
        initial_retry_delay: Initial delay between retries in seconds
    """
    texts = [doc.page_content for doc in batch]
    metadatas = [doc.metadata for doc in batch]
    
    retry_delay = initial_retry_delay
    for attempt in range(max_retries):
        try:
            embeddings = embedding_function.embed_documents(texts)
            db.add_texts(texts=texts, metadatas=metadatas, embeddings=embeddings)
            time.sleep(RATE_LIMIT_DELAY)  # Basic rate limiting
            return
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise
            print(f"Error processing batch (attempt {attempt + 1}/{max_retries}): {str(e)}")
            print(f"Waiting {retry_delay} seconds before retrying...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

def vectorize_documents(chunks: List[Document], chroma_path: Path) -> None:
    """
    Create and store document vectors using Mistral embeddings and Chroma.
    
    Args:
        chunks (List[Document]): Document chunks to vectorize
        chroma_path (Path): Path to store the Chroma database
        
    Raises:
        ValueError: If MISTRAL_EMBEDDING environment variable is not set
    """
    key = os.environ.get("MISTRAL_EMBEDDING")
    if not key:
        raise ValueError("MISTRAL_EMBEDDING environment variable not set")

    # Remove existing Chroma persistence directory if it exists
    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        
    # Create parent directory if it doesn't exist
    chroma_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize the embedding function
    embedding_function = MistralAIEmbeddings(
        model="mistral-embed",
        api_key=key
    )

    # Initialize empty Chroma database
    db = Chroma(
        persist_directory=str(chroma_path),
        embedding_function=embedding_function
    )

    # Process chunks in batches with progress bar
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    with tqdm(total=total_batches, desc="Processing chunks") as pbar:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            process_batch_with_retry(batch, embedding_function, db)
            pbar.update(1)
    
    # Persist the final database
    db.persist()
    print(f"Successfully processed and saved {len(chunks)} chunks to {chroma_path}")

def main():
    """Main execution function."""
    try:
        documents = document_load(DATA_PATH)
        chunks = document_chunking(documents)
        vectorize_documents(chunks, CHROMA_PATH)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    main()