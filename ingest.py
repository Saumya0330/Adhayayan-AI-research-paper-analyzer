# ingest.py - PDF ingestion and processing
import os
from pypdf import PdfReader
from llm_agent import summarize_document

def load_pdf(path: str) -> list:
    """
    Extract text from PDF pages.
    """
    try:
        reader = PdfReader(path)
        pages = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({
                    "page": i + 1,
                    "text": text
                })
        
        return pages
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []

def extract_document_text(pages: list) -> str:
    """
    Combine all pages into a single document text.
    """
    full_text = ""
    for page in pages:
        full_text += f"Page {page['page']}:\n{page['text']}\n\n"
    return full_text.strip()

def ingest_pdf(path: str) -> tuple:
    """
    Process a PDF file and extract information.
    
    Returns:
        (chunks_count, pages_count, summary, pdf_name)
    """
    pdf_name = os.path.splitext(os.path.basename(path))[0]
    
    print(f"📄 Processing {pdf_name}...")
    
    # Step 1: Extract text from PDF
    pages = load_pdf(path)
    if not pages:
        raise ValueError(f"No text could be extracted from {pdf_name}")
    
    print(f"✅ Extracted text from {len(pages)} pages")
    
    # Step 2: Combine into full document text
    full_text = extract_document_text(pages)
    
    # Step 3: Generate document summary using LLM
    print(f"🔄 Generating summary...")
    try:
        doc_summary = summarize_document(full_text)
        print(f"✅ Summary generated: {doc_summary[:100]}...")
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        # Fallback summary
        first_page_text = pages[0]['text'][:300] if pages else "No content"
        doc_summary = f"Document: {pdf_name}. Preview: {first_page_text}..."
    
    # Step 4: Count chunks (each page is a chunk)
    chunks_count = len(pages)
    
    print(f"✅ Processed {pdf_name}: {len(pages)} pages, {chunks_count} chunks")
    
    return chunks_count, len(pages), doc_summary, pdf_name