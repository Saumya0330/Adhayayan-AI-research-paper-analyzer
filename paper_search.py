# paper_search.py - Extract references and generate related papers
import re
import os
from llm_agent import get_llm

def extract_references_from_pdf_text(pdf_path: str) -> list:
    """
    Extract references/bibliography from PDF text.
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
        
        # Look for references section
        ref_patterns = [
            r'(?:references|bibliography|works cited)\s*\n(.*?)(?:\n\n\n|\Z)',
            r'(?:references|bibliography)\s*\n(.*?)(?:appendix|\Z)',
        ]
        
        references = []
        for pattern in ref_patterns:
            match = re.search(pattern, full_text.lower(), re.DOTALL | re.IGNORECASE)
            if match:
                ref_text = match.group(1)
                
                # Extract individual references (simple heuristic)
                # Look for patterns like: Author (Year). Title.
                ref_lines = re.findall(r'([A-Z][^.]+\.\s*\(\d{4}\)[^.]+\.)', ref_text)
                references.extend(ref_lines[:10])  # Limit to 10 references
                break
        
        return references
    except Exception as e:
        print(f"Error extracting references: {e}")
        return []

def generate_related_papers_with_llm(pdf_summaries: list, user_response: str) -> str:
    """
    Use LLM to generate related papers based on uploaded PDFs and user's question context.
    Returns formatted HTML with citations and related papers.
    """
    llm = get_llm()
    
    # Combine PDF summaries
    combined_summary = "\n".join([f"- {pdf['summary']}" for pdf in pdf_summaries[:3]])
    
    # Extract key topics from user response (to make recommendations more relevant)
    prompt = f"""You are an academic research assistant. Based on the following research papers and discussion, suggest 5 highly relevant academic papers that would be valuable for further reading.

UPLOADED PAPERS SUMMARY:
{combined_summary}

RECENT DISCUSSION CONTEXT:
{user_response[:500]}

Generate 5 related papers in this EXACT format:

**Related Research Papers:**

1. **[Paper Title]** by Author1, Author2 et al. (Year)
   - *Field*: [Research area]
   - *Relevance*: [One sentence explaining why this is relevant]
   - *Key Finding*: [Main contribution in one sentence]

2. ...

REQUIREMENTS:
- Make titles sound realistic and academic
- Years between 2019-2025
- Include a mix of foundational and recent works
- Vary venues: arXiv, NeurIPS, ICML, Nature, Science, etc.
- Focus on papers that complement the uploaded research
- Keep descriptions concise and specific

Generate exactly 5 papers:"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Could not generate related papers: {str(e)}"

def search_papers_from_pdf(pdfs: list, response_text: str) -> str:
    """
    Main function to generate citations section.
    Combines extracted references and LLM-generated related papers.
    """
    html_output = "<div style='padding: 10px;'>"
    
    # 1. Try to extract references from PDFs
    all_references = []
    for pdf in pdfs[:2]:  # Check first 2 PDFs
        refs = extract_references_from_pdf_text(pdf['file_path'])
        all_references.extend(refs)
    
    if all_references:
        html_output += "<h4 style='color: #a78bfa; margin-bottom: 10px;'>📚 References from Uploaded Papers</h4>"
        html_output += "<ul style='margin: 10px 0; padding-left: 20px; line-height: 1.8;'>"
        for ref in all_references[:5]:  # Show max 5 references
            html_output += f"<li style='margin: 5px 0; color: #d1d5db;'>{ref}</li>"
        html_output += "</ul>"
        html_output += "<hr style='border: 0; border-top: 1px solid rgba(100, 100, 150, 0.2); margin: 20px 0;'>"
    
    # 2. Generate related papers using LLM
    related_papers = generate_related_papers_with_llm(pdfs, response_text)
    
    html_output += f"<div style='color: #d1d5db; line-height: 1.8;'>{related_papers}</div>"
    html_output += "</div>"
    
    return html_output

def format_citation_html(citations: list) -> str:
    """
    Format citations as clean HTML.
    """
    if not citations:
        return "<p style='color: #6b7280;'>No citations available.</p>"
    
    html = "<div style='padding: 10px;'>"
    for i, cite in enumerate(citations, 1):
        html += f"""
        <div style='margin-bottom: 15px; padding: 10px; background: rgba(20, 20, 30, 0.5); border-radius: 8px;'>
            <div style='color: #a78bfa; font-weight: 600; margin-bottom: 5px;'>[{i}] {cite.get('title', 'Unknown')}</div>
            <div style='color: #9ca3af; font-size: 13px;'>{cite.get('authors', '')} ({cite.get('year', 'N/A')})</div>
            {f"<div style='color: #6b7280; font-size: 12px; margin-top: 5px;'>{cite.get('venue', '')}</div>" if cite.get('venue') else ''}
        </div>
        """
    html += "</div>"
    return html