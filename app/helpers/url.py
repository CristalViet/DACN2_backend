"""
Helper functions for URL manipulation
"""
from app.config import BACKEND_BASE_URL
from typing import Optional
from fastapi import Request


def get_base_url_from_request(request: Optional[Request] = None) -> str:
    """
    Get base URL from request headers (for ngrok support) or fallback to config.
    
    Args:
        request: FastAPI Request object (optional)
        
    Returns:
        Base URL string
    """
    if request:
        # Try to get base URL from request
        # Check for X-Forwarded-Proto and Host headers (common with ngrok/proxies)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "http")
        host = request.headers.get("Host", "")
        
        if host:
            # Use the host from request (works with ngrok)
            base_url = f"{forwarded_proto}://{host}"
            return base_url
    
    # Fallback to config
    return BACKEND_BASE_URL


def get_full_image_url(relative_url: str | None, request: Optional[Request] = None) -> str | None:
    """
    Convert relative image URL to full URL with backend base URL.
    Automatically detects base URL from request (for ngrok support) or uses config.
    
    Args:
        relative_url: Relative URL like "/static/uploads/books/image.png"
        request: FastAPI Request object (optional, for auto-detection)
        
    Returns:
        Full URL like "https://example.com/static/uploads/books/image.png"
        or None if relative_url is None/empty
    """
    if not relative_url:
        return None
    
    # If already a full URL (starts with http:// or https://), return as is
    if relative_url.startswith(("http://", "https://")):
        return relative_url
    
    # Get base URL (from request if available, otherwise from config)
    base_url = get_base_url_from_request(request).rstrip("/")
    
    # Remove leading slash if present to avoid double slashes
    relative_url = relative_url.lstrip("/")
    
    # Combine base URL with relative URL
    return f"{base_url}/{relative_url}"

