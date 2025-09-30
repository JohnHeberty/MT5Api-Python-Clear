"""
Authentication middleware following SOLID principles.
Single responsibility: Handle API key authentication.
"""
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable

from ...domain.interfaces import IAuthenticationService


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.
    Single responsibility: Validate API keys for incoming requests.
    """
    
    def __init__(self, app, auth_service: IAuthenticationService):
        super().__init__(app)
        self._auth_service = auth_service
        # Endpoints that don't require authentication
        self._public_endpoints = {
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/health",
            "/"
        }
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process authentication for incoming requests."""
        # Skip authentication for public endpoints
        if any(request.url.path.startswith(endpoint) for endpoint in self._public_endpoints):
            return await call_next(request)
        
        # Check for API key in headers
        api_key = request.headers.get("AcessKey") or request.headers.get("Authorization")
        
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "API key required", "error_code": "MISSING_API_KEY"}
            )
        
        # Clean up Authorization header if it contains "Bearer "
        if api_key.startswith("Bearer "):
            api_key = api_key[7:]
        
        # Validate API key
        if not self._auth_service.validate_api_key(api_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API key", "error_code": "INVALID_API_KEY"}
            )
        
        # Add user permissions to request state for later use
        permissions = self._auth_service.get_user_permissions(api_key)
        request.state.user_permissions = permissions
        request.state.api_key = api_key
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add timing headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with configurable origins.
    Single responsibility: Handle Cross-Origin Resource Sharing.
    """
    
    def __init__(self, app, allowed_origins: list = None, allow_credentials: bool = True):
        super().__init__(app)
        self._allowed_origins = allowed_origins or ["*"]
        self._allow_credentials = allow_credentials
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process CORS for incoming requests."""
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = JSONResponse(content={})
            self._add_cors_headers(response, request)
            return response
        
        # Process actual request
        response = await call_next(request)
        self._add_cors_headers(response, request)
        
        return response
    
    def _add_cors_headers(self, response, request: Request):
        """Add CORS headers to response."""
        origin = request.headers.get("Origin")
        
        # Check if origin is allowed
        if "*" in self._allowed_origins or (origin and origin in self._allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
        
        if self._allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, AcessKey, X-Requested-With, Accept"
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging.
    Single responsibility: Log HTTP requests and responses.
    """
    
    def __init__(self, app, enable_logging: bool = True):
        super().__init__(app)
        self._enable_logging = enable_logging
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response information."""
        if not self._enable_logging:
            return await call_next(request)
        
        start_time = time.time()
        
        # Log request information
        client_ip = request.client.host if request.client else "unknown"
        api_key_present = bool(request.headers.get("AcessKey") or request.headers.get("Authorization"))
        
        print(f"[REQUEST] {request.method} {request.url.path} - IP: {client_ip} - API Key: {api_key_present}")
        
        try:
            # Process request
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response information
            print(f"[RESPONSE] {response.status_code} - Time: {process_time:.4f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            print(f"[ERROR] {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.4f}s")
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers.
    Single responsibility: Add security-related HTTP headers.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self._security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        for header, value in self._security_headers.items():
            response.headers[header] = value
        
        return response