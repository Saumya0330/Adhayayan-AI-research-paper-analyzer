# database.py - SQLite database for users, chat history, and PDFs
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = "research_ai.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            organization TEXT NOT NULL,
            research_interests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            citations TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Uploaded PDFs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            pages INTEGER NOT NULL,
            chunks INTEGER NOT NULL,
            summary TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# === USER OPERATIONS ===

def create_user(google_id: str, email: str, name: str, username: str, 
                organization: str, research_interests: str = "") -> Optional[Dict]:
    """Create a new user"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (google_id, email, name, username, organization, research_interests)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (google_id, email, name, username, organization, research_interests))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_google_id(google_id: str) -> Optional[Dict]:
    """Get user by Google ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# === CHAT HISTORY OPERATIONS ===

def add_chat_message(user_id: int, role: str, content: str, citations: str = ""):
    """Add a chat message to history"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (user_id, role, content, citations)
        VALUES (?, ?, ?, ?)
    """, (user_id, role, content, citations))
    conn.commit()
    conn.close()

def get_chat_history(user_id: int, limit: int = 50) -> List[Dict]:
    """Get chat history for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, citations, timestamp
        FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp ASC
        LIMIT ?
    """, (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def clear_chat_history(user_id: int):
    """Clear all chat history for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# === PDF OPERATIONS ===

def add_uploaded_pdf(user_id: int, filename: str, file_path: str, 
                     pages: int, chunks: int, summary: str = ""):
    """Add an uploaded PDF to the database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO uploaded_pdfs (user_id, filename, file_path, pages, chunks, summary)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, filename, file_path, pages, chunks, summary))
    conn.commit()
    conn.close()

def get_user_pdfs(user_id: int) -> List[Dict]:
    """Get all PDFs uploaded by a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, file_path, pages, chunks, summary, uploaded_at
        FROM uploaded_pdfs
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_pdf_by_id(pdf_id: int) -> Optional[Dict]:
    """Get a specific PDF by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploaded_pdfs WHERE id = ?", (pdf_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_pdf(pdf_id: int):
    """Delete a PDF"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM uploaded_pdfs WHERE id = ?", (pdf_id,))
    conn.commit()
    conn.close()

# === STATISTICS ===

def get_user_stats(user_id: int) -> Dict:
    """Get user statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Count PDFs
    cursor.execute("SELECT COUNT(*) FROM uploaded_pdfs WHERE user_id = ?", (user_id,))
    pdf_count = cursor.fetchone()[0]
    
    # Count messages
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = ?", (user_id,))
    message_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "pdfs_uploaded": pdf_count,
        "messages_sent": message_count
    }