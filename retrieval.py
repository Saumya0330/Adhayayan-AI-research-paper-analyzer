# retrieval.py - Retrieve relevant chunks from multiple PDFs
import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> list:
    """
    Extract text from PDF and return as list of page chunks.
    """
    try:
        reader = PdfReader(pdf_path)
        chunks = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                chunks.append({
                    "text": text,
                    "page": i + 1,
                    "source": os.path.basename(pdf_path)
                })
        
        return chunks
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return []

def simple_keyword_search(query: str, chunks: list, top_k: int = 5) -> list:
    """
    Simple keyword-based search to find relevant chunks.
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Score each chunk based on keyword overlap
    scored_chunks = []
    for chunk in chunks:
        text_lower = chunk['text'].lower()
        text_words = set(text_lower.split())
        
        # Calculate overlap score
        overlap = len(query_words & text_words)
        
        # Bonus for exact phrase match
        if query_lower in text_lower:
            overlap += 10
        
        if overlap > 0:
            scored_chunks.append((overlap, chunk))
    
    # Sort by score and return top_k
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return [chunk for _, chunk in scored_chunks[:top_k]]

def retrieve_from_multiple_pdfs(query: str, pdfs: list, top_k: int = 6) -> list:
    """
    Retrieve relevant chunks from multiple PDFs.
    
    Args:
        query: User's question
        pdfs: List of PDF metadata from database (contains file_path)
        top_k: Number of chunks to return
    
    Returns:
        List of relevant text chunks with metadata
    """
    all_chunks = []
    
    # Extract text from all PDFs
    for pdf in pdfs:
        pdf_chunks = extract_text_from_pdf(pdf['file_path'])
        all_chunks.extend(pdf_chunks)
    
    if not all_chunks:
        return [{
            "text": "No document content available.",
            "page": 0,
            "source": "System"
        }]
    
    # Retrieve most relevant chunks
    relevant_chunks = simple_keyword_search(query, all_chunks, top_k)
    
    # If no relevant chunks found, return first few chunks as fallback
    if not relevant_chunks:
        relevant_chunks = all_chunks[:top_k]
    
    return relevant_chunks

def get_full_document_context(pdfs: list) -> str:
    """
    Get a high-level summary of all uploaded documents for context.
    """
    context = "**Uploaded Documents:**\n"
    for pdf in pdfs:
        context += f"- {pdf['filename']} ({pdf['pages']} pages): {pdf.get('summary', 'No summary')}\n"
    return context