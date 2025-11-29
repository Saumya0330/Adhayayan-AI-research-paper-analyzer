# paper_search.py - Extract references and generate related papers
import re
from llm_agent import get_llm

def extract_references_from_text(pdf_text: str) -> list:
    """
    Extract references/bibliography from PDF text.
    """
    try:
        # Look for references section
        ref_patterns = [
            r'(?:references|bibliography|works cited)\s*\n(.*?)(?:\n\n\n|\Z)',
            r'(?:references|bibliography)\s*\n(.*?)(?:appendix|\Z)',
        ]
        
        references = []
        for pattern in ref_patterns:
            match = re.search(pattern, pdf_text.lower(), re.DOTALL | re.IGNORECASE)
            if match:
                ref_text = match.group(1)
                
                # Extract individual references
                ref_lines = re.findall(r'([A-Z][^.]+\.\s*\(\d{4}\)[^.]+\.)', ref_text)
                references.extend(ref_lines[:10])  # Limit to 10
                break
        
        return references
    except Exception as e:
        print(f"Error extracting references: {e}")
        return []

def generate_related_papers_with_llm(pdf_summaries: list, user_response: str) -> str:
    """
    Use LLM to generate related papers.
    """
    llm = get_llm()
    
    # Combine PDF summaries
    combined_summary = "\n".join([f"- {pdf['summary']}" for pdf in pdf_summaries[:3]])
    
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
    html_output = "<div style='padding: 5px;'>"
    
    # 1. Try to extract references from PDFs (using pdf_text from database)
    all_references = []
    for pdf in pdfs[:2]:  # Check first 2 PDFs
        pdf_text = pdf.get('pdf_text', '')
        if pdf_text:
            refs = extract_references_from_text(pdf_text)
            all_references.extend(refs)
    
    if all_references:
        html_output += "<h4 style='color: #a78bfa; margin: 0 0 12px 0; font-size: 14px;'>📖 References from Uploaded Papers</h4>"
        html_output += "<ul style='margin: 0 0 20px 0; padding: 0; list-style: none;'>"
        for ref in all_references[:5]:  # Show max 5 references
            html_output += f"<li style='margin: 0 0 8px 0; padding: 10px 12px; background: rgba(30, 30, 45, 0.4); border-radius: 8px; border-left: 3px solid rgba(167, 139, 250, 0.3); color: #d1d5db; font-size: 13px; line-height: 1.6;'>{ref}</li>"
        html_output += "</ul>"
    
    # 2. Generate related papers using LLM
    related_papers = generate_related_papers_with_llm(pdfs, response_text)
    
    html_output += f"<div style='color: #d1d5db; line-height: 1.8; font-size: 13px;'>{related_papers}</div>"
    html_output += "</div>"
    
    return html_output
