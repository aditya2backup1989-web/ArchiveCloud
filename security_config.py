"""
Security configuration: CORS, security headers, and middleware
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time


def configure_cors(app: FastAPI):
    """
    Configure CORS (Cross-Origin Resource Sharing) for the application
    
    This is important for cloud deployments when frontend and backend
    are on different domains
    """
    origins = [
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://localhost:4200",  # Angular default
        # Add your production frontend URL here
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )


def add_security_headers_middleware(app: FastAPI):
    """
    Add security headers to all responses
    
    These headers help protect against common web vulnerabilities
    """
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict Transport Security (HTTPS only)
        # Uncomment in production with HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


def add_request_logging_middleware(app: FastAPI):
    """
    Add request logging middleware for monitoring and debugging
    """
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate request processing time
        process_time = time.time() - start_time
        
        # Add custom header with processing time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request details (in production, use proper logging)
        print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response


def add_error_handling_middleware(app: FastAPI):
    """
    Add global error handling middleware
    """
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the error (in production, use proper logging)
        print(f"Global error handler caught: {exc}")
        
        # Return a generic error response (don't expose internal details)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal error occurred. Please try again later."
            }
        )


def configure_security(app: FastAPI):
    """
    Configure all security features for the application
    """
    configure_cors(app)
    add_security_headers_middleware(app)
    add_request_logging_middleware(app)
    add_error_handling_middleware(app)
