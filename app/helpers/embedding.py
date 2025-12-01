import os
import json
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app import models
from app.models.summary import Summary
from app.models.book import Book

# Cache the model to avoid reloading it on every call
_model = None

def get_embedding_model():
    """Get or initialize the SentenceTransformer model (cached)"""
    global _model
    if _model is None:
        model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model

def compute_summary_embedding(db: Session, summary: Summary) -> list:
    """
    Compute embedding for a summary based on title, content, authors, and categories.
    
    Args:
        db: SQLAlchemy database session
        summary: Summary model instance
        
    Returns:
        List of floats representing the embedding vector, or None if no content
    """
    # Get title
    title = summary.title or ""
    
    # Get content sections
    content_sections = db.query(models.content_section.ContentSection).filter(
        models.content_section.ContentSection.summary_id == summary.id
    ).order_by(models.content_section.ContentSection.section_order).all()
    
    full_text = " ".join([cs.content for cs in content_sections if cs.content]).strip()
    
    # Get authors from book
    authors = ""
    if summary.book_id:
        book = db.query(Book).filter(Book.id == summary.book_id).first()
        if book and book.authors:
            authors = ", ".join([author.name for author in book.authors if author.name])
    
    # Get categories from book
    categories = ""
    if summary.book_id:
        book = db.query(Book).filter(Book.id == summary.book_id).first()
        if book and book.categories:
            categories = ", ".join([cat.category_name for cat in book.categories if cat.category_name])
    
    # Combine title + content + authors + categories for embedding
    parts = []
    if title:
        parts.append(f"Title: {title}")
    if authors:
        parts.append(f"Authors: {authors}")
    if categories:
        parts.append(f"Categories: {categories}")
    if full_text:
        parts.append(f"Content: {full_text}")
    
    doc_text = "\n".join(parts).strip()
    if not doc_text:
        return None
    
    # Generate embedding
    model = get_embedding_model()
    vec = model.encode(doc_text, show_progress_bar=False).tolist()
    
    return vec

def update_summary_embedding(db: Session, summary: Summary, commit: bool = True) -> bool:
    """
    Compute and update the embedding for a summary.
    
    Args:
        db: SQLAlchemy database session
        summary: Summary model instance
        commit: Whether to commit the changes (default: True)
        
    Returns:
        True if embedding was updated, False if no content to embed
    """
    embedding = compute_summary_embedding(db, summary)
    if embedding is None:
        return False
    
    summary.embedding = embedding
    if commit:
        db.commit()
    return True

