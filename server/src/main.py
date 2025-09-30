"""
Main FastAPI application with comprehensive OpenAPI documentation.
Follows Clean Architecture principles and SOLID design patterns.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import uvicorn

from .presentation.controllers import MarketDataController, TradingController
from .presentation.middleware import (
    AuthenticationMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware
)
from .infrastructure.config.dependencies import (
    get_configuration_service,
    get_authentication_service,
    get_mt5_connection_service
)
from .infrastructure.config.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting MT5 Trading API...")
    
    try:
        # Initialize MT5 connection
        config_service = get_configuration_service()
        connection_service = get_mt5_connection_service()
        
        # Initialize connection
        if await connection_service.initialize_connection():
            print("✅ MT5 connection initialized successfully")
            
            # Login to MT5 account
            credentials = config_service.get_mt5_credentials()
            if await connection_service.login(
                credentials["login"],
                credentials["password"], 
                credentials["server"]
            ):
                print(f"✅ Logged in to MT5 account: {credentials['login']}")
            else:
                print("❌ Failed to login to MT5 account")
        else:
            print("❌ Failed to initialize MT5 connection")
    
    except Exception as e:
        print(f"❌ Error during startup: {e}")
    
    print("🌟 MT5 Trading API is ready!")
    
    yield  # Application runs here
    
    # Shutdown
    print("🛑 Shutting down MT5 Trading API...")
    try:
        connection_service = get_mt5_connection_service()
        await connection_service.shutdown_connection()
        print("✅ MT5 connection closed successfully")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns a fully configured FastAPI instance.
    """
    # Create FastAPI app with enhanced OpenAPI configuration
    app = FastAPI(
        title="MetaTrader 5 Trading API",
        description="""
        ## Professional MetaTrader 5 Trading API
        
        A comprehensive, production-ready REST API for MetaTrader 5 trading operations built with **Clean Architecture** and **SOLID** principles.
        
        ### Features
        
        * 🔐 **Secure Authentication** - API key-based authentication
        * 📊 **Market Data** - Real-time and historical market data
        * 💱 **Trading Operations** - Open, close, and manage positions
        * 📈 **Symbol Information** - Comprehensive symbol data
        * 🎯 **Performance Tracking** - Built-in request timing
        * 🛡️ **Security Headers** - Enhanced security measures
        * 📚 **Auto Documentation** - Interactive API documentation
        
        ### Architecture
        
        This API follows **Clean Architecture** principles:
        - **Domain Layer**: Core business entities and rules
        - **Application Layer**: Use cases and business logic
        - **Infrastructure Layer**: External services and data persistence  
        - **Presentation Layer**: HTTP controllers and middleware
        
        ### Authentication
        
        All endpoints require an API key in the `AcessKey` header:
        ```
        AcessKey: your-api-key-here
        ```
        
        ### Rate Limiting
        
        * Maximum 1000 symbols per percent change request
        * Maximum 1000 candles per ticker request
        
        ### Support
        
        For technical support or feature requests, please contact the development team.
        """,
        version="2.0.0",
        contact={
            "name": "MT5 API Development Team",
            "email": "support@mt5api.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=[
            {
                "name": "Market Data",
                "description": "Operations for retrieving market data, symbols, and ticker information.",
            },
            {
                "name": "Trading",
                "description": "Operations for managing trading positions, opening and closing trades.",
            },
            {
                "name": "Health",
                "description": "System health and status endpoints.",
            }
        ],
        lifespan=lifespan,
        docs_url=None,  # We'll create custom docs
        redoc_url=None,
        openapi_url="/api/openapi.json"
    )
    
    # Add middleware in correct order (last added = first executed)
    
    # Security headers (applied last)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # CORS middleware
    config_service = get_configuration_service()
    server_config = config_service.get_server_config()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=server_config["cors_origins"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    app.add_middleware(
        RequestLoggingMiddleware,
        enable_logging=server_config["log_level"] in ["DEBUG", "INFO"]
    )
    
    # Authentication middleware (applied first)
    auth_service = get_authentication_service(config_service)
    app.add_middleware(AuthenticationMiddleware, auth_service=auth_service)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Register controllers
    market_data_controller = MarketDataController()
    trading_controller = TradingController()
    
    app.include_router(market_data_controller.router)
    app.include_router(trading_controller.router)
    
    # Add custom documentation endpoints
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Custom Swagger UI with enhanced styling."""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Interactive Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayRequestDuration": True,
                "docExpansion": "none",
                "operationsSorter": "method",
                "filter": True,
                "tryItOutEnabled": True
            }
        )
    
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        """ReDoc documentation."""
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - API Documentation",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
        )
    
    # Health check endpoint
    @app.get(
        "/health",
        tags=["Health"],
        summary="Health Check",
        description="Check the health status of the API and MT5 connection",
        response_description="Health status information"
    )
    async def health_check():
        """Health check endpoint."""
        try:
            connection_service = get_mt5_connection_service()
            mt5_connected = connection_service.is_connected()
            
            return {
                "status": "healthy" if mt5_connected else "degraded",
                "mt5_connection": "connected" if mt5_connected else "disconnected",
                "version": app.version,
                "api_name": app.title
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "version": app.version,
                "api_name": app.title
            }
    
    # Root endpoint
    @app.get(
        "/",
        tags=["Health"],
        summary="API Information",
        description="Get basic information about the API"
    )
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to MT5 Trading API",
            "version": app.version,
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "health_url": "/health"
        }
    
    # Custom OpenAPI schema
    def custom_openapi():
        """Generate custom OpenAPI schema with enhanced security definitions."""
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Add security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "AcessKey",
                "description": "API Key required for authentication"
            }
        }
        
        # Apply security to all endpoints except public ones
        for path, path_item in openapi_schema["paths"].items():
            if not any(path.startswith(public) for public in ["/docs", "/redoc", "/health", "/", "/api/openapi.json"]):
                for method in path_item:
                    if method.lower() in ["get", "post", "put", "delete", "patch"]:
                        path_item[method]["security"] = [{"ApiKeyAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    return app


def run_server():
    """
    Run the development server.
    For production, use a WSGI server like Gunicorn.
    """
    config_service = get_configuration_service()
    server_config = config_service.get_server_config()
    
    uvicorn.run(
        "src.main:create_app",
        factory=True,
        host=server_config["host"],
        port=server_config["port"],
        reload=server_config["reload"],
        log_level=server_config["log_level"].lower(),
        access_log=True
    )


# Create app instance for production
app = create_app()

if __name__ == "__main__":
    run_server()