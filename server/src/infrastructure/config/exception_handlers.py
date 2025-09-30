"""
Global exception handlers for standardized error responses.
Follows SOLID principles for error handling and logging.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import traceback
from typing import Any, Dict

from ...application.dtos import ErrorResponseModel, ValidationErrorModel


class GlobalExceptionHandler:
    """
    Centralized exception handling following Single Responsibility Principle.
    Provides consistent error responses across the entire API.
    """
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions with consistent error format.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        )
        
        # Log error details
        print(f"[HTTP_ERROR] {exc.status_code} - {exc.detail} - URL: {request.url}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle Starlette HTTP exceptions.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        )
        
        print(f"[STARLETTE_ERROR] {exc.status_code} - {exc.detail} - URL: {request.url}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle Pydantic validation errors with detailed field information.
        """
        validation_errors = []
        
        for error in exc.errors():
            field_name = " -> ".join(str(loc) for loc in error["loc"])
            validation_errors.append(
                ValidationErrorModel(
                    field=field_name,
                    message=error["msg"],
                    value=error.get("input", "")
                )
            )
        
        error_response = ErrorResponseModel(
            ok=False,
            error="Validation failed",
            details=validation_errors,
            error_code="VALIDATION_ERROR"
        )
        
        print(f"[VALIDATION_ERROR] {len(validation_errors)} errors - URL: {request.url}")
        for error in validation_errors:
            print(f"  - {error.field}: {error.message}")
        
        return JSONResponse(
            status_code=422,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """
        Handle Pydantic validation errors from domain entities.
        """
        validation_errors = []
        
        for error in exc.errors():
            field_name = " -> ".join(str(loc) for loc in error["loc"])
            validation_errors.append(
                ValidationErrorModel(
                    field=field_name,
                    message=error["msg"],
                    value=error.get("input", "")
                )
            )
        
        error_response = ErrorResponseModel(
            ok=False,
            error="Domain validation failed",
            details=validation_errors,
            error_code="DOMAIN_VALIDATION_ERROR"
        )
        
        print(f"[DOMAIN_VALIDATION_ERROR] {len(validation_errors)} errors - URL: {request.url}")
        
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """
        Handle ValueError exceptions from business logic.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error=str(exc),
            error_code="VALUE_ERROR"
        )
        
        print(f"[VALUE_ERROR] {str(exc)} - URL: {request.url}")
        
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def runtime_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
        """
        Handle RuntimeError exceptions from use cases and services.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error=str(exc),
            error_code="RUNTIME_ERROR"
        )
        
        print(f"[RUNTIME_ERROR] {str(exc)} - URL: {request.url}")
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
        """
        Handle PermissionError exceptions for authorization issues.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error=str(exc),
            error_code="PERMISSION_ERROR"
        )
        
        print(f"[PERMISSION_ERROR] {str(exc)} - URL: {request.url}")
        
        return JSONResponse(
            status_code=403,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def file_not_found_error_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
        """
        Handle FileNotFoundError exceptions for resource not found scenarios.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error=str(exc),
            error_code="NOT_FOUND_ERROR"
        )
        
        print(f"[NOT_FOUND_ERROR] {str(exc)} - URL: {request.url}")
        
        return JSONResponse(
            status_code=404,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def connection_error_handler(request: Request, exc: ConnectionError) -> JSONResponse:
        """
        Handle ConnectionError exceptions for MT5 connection issues.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error="Connection to MetaTrader 5 failed. Please try again later.",
            error_code="MT5_CONNECTION_ERROR"
        )
        
        print(f"[MT5_CONNECTION_ERROR] {str(exc)} - URL: {request.url}")
        
        return JSONResponse(
            status_code=503,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def timeout_error_handler(request: Request, exc: TimeoutError) -> JSONResponse:
        """
        Handle TimeoutError exceptions for operation timeouts.
        """
        error_response = ErrorResponseModel(
            ok=False,
            error="Operation timed out. Please try again with fewer data points or a smaller time range.",
            error_code="TIMEOUT_ERROR"
        )
        
        print(f"[TIMEOUT_ERROR] {str(exc)} - URL: {request.url}")
        
        return JSONResponse(
            status_code=408,
            content=error_response.model_dump()
        )
    
    @staticmethod
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle all other unexpected exceptions.
        """
        # Log full traceback for debugging
        error_traceback = traceback.format_exc()
        print(f"[UNEXPECTED_ERROR] {type(exc).__name__}: {str(exc)}")
        print(f"Traceback: {error_traceback}")
        
        error_response = ErrorResponseModel(
            ok=False,
            error="An unexpected error occurred. Please contact support if this persists.",
            error_code="INTERNAL_SERVER_ERROR"
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application.
    This function should be called during application setup.
    """
    # HTTP exceptions
    app.add_exception_handler(HTTPException, GlobalExceptionHandler.http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, GlobalExceptionHandler.starlette_http_exception_handler)
    
    # Validation exceptions
    app.add_exception_handler(RequestValidationError, GlobalExceptionHandler.validation_exception_handler)
    app.add_exception_handler(ValidationError, GlobalExceptionHandler.pydantic_validation_exception_handler)
    
    # Business logic exceptions
    app.add_exception_handler(ValueError, GlobalExceptionHandler.value_error_handler)
    app.add_exception_handler(RuntimeError, GlobalExceptionHandler.runtime_error_handler)
    app.add_exception_handler(PermissionError, GlobalExceptionHandler.permission_error_handler)
    app.add_exception_handler(FileNotFoundError, GlobalExceptionHandler.file_not_found_error_handler)
    
    # Infrastructure exceptions
    app.add_exception_handler(ConnectionError, GlobalExceptionHandler.connection_error_handler)
    app.add_exception_handler(TimeoutError, GlobalExceptionHandler.timeout_error_handler)
    
    # Catch-all exception handler (must be last)
    app.add_exception_handler(Exception, GlobalExceptionHandler.generic_exception_handler)
    
    print("✅ Global exception handlers registered successfully")