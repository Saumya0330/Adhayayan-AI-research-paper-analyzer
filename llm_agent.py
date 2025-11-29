# llm_agent.py - Enhanced LLM agent with proper citations
import os
from langchain_groq import ChatGroq

MODEL = "llama-3.1-8b-instant"

def get_llm():
    """Get LLM instance"""
    return ChatGroq(
        model=MODEL,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1
    )

def answer_with_context(question: str, chunks: list) -> str:
    """
    Answer question using context from multiple PDFs.
    Returns answer with inline citations.
    """
    llm = get_llm()
    
    # Build context from chunks
    context_parts = []
    for i, chunk in enumerate(chunks[:8], 1):  # Limit to 8 chunks to avoid token limits
        if isinstance(chunk, dict):
            text = chunk.get('text', str(chunk))
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', 'N/A')
        else:
            text = str(chunk)
            source = 'Document'
            page = 'N/A'
        
        context_parts.append(f"[Source {i}: {source}, Page {page}]\n{text}\n")
    
    context_text = "\n".join(context_parts)
    
    prompt = f"""You are an expert research assistant analyzing academic papers. Answer the user's question based ONLY on the provided context.

CONTEXT FROM UPLOADED DOCUMENTS:
{context_text}

USER QUESTION: {question}

INSTRUCTIONS:
1. Provide a clear, comprehensive answer based on the context
2. Use inline citations like [Source 1], [Source 2] when referencing specific information
3. If the answer requires information from multiple sources, cite all relevant sources
4. If the context doesn't contain enough information, say so clearly
5. Be precise and academic in your tone

ANSWER:"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

def summarize_document(full_text: str) -> str:
    """
    Generate a concise summary of a research document.
    Handles large documents by chunking.
    """
    llm = get_llm()
    
    # Estimate tokens (rough: 1 token ≈ 4 characters)
    max_chars = 20000  # ~5000 tokens, safe limit
    
    if len(full_text) > max_chars:
        # For large documents, take first chunk and last chunk
        first_part = full_text[:max_chars // 2]
        last_part = full_text[-max_chars // 2:]
        text_to_summarize = first_part + "\n\n[...]\n\n" + last_part
    else:
        text_to_summarize = full_text
    
    prompt = f"""Analyze this research document and provide a concise 3-4 sentence summary.

Focus on:
- Main research topic and field
- Key methodology or approach
- Primary findings or contributions

DOCUMENT TEXT:
{text_to_summarize}

SUMMARY (3-4 sentences only):"""

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Summary generation failed: {str(e)}"

def extract_citations_from_response(response_text: str) -> str:
    """
    Extract and format citations mentioned in the response.
    This is a placeholder - actual implementation would parse [Source X] references.
    """
    # Simple extraction of source citations
    import re
    sources = re.findall(r'\[Source \d+[^\]]*\]', response_text)
    
    if sources:
        unique_sources = list(set(sources))
        return "**Sources referenced:** " + ", ".join(unique_sources)
    return ""