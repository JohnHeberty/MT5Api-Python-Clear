"""
Configuration service adapter.
Handles application configuration using environment variables and settings.
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from ...domain.interfaces import IConfigurationService, IAuthenticationService


class EnvironmentConfigurationService(IConfigurationService):
    """
    Configuration service that reads from environment variables.
    Single responsibility: Manage application configuration.
    """
    
    def __init__(self, env_file_path: Optional[str] = None):
        """Initialize configuration service."""
        if env_file_path:
            load_dotenv(env_file_path)
        else:
            load_dotenv()  # Load from default .env file
        
        self._mt5_credentials = None
        self._api_keys = None
        self._server_config = None
    
    def get_mt5_credentials(self) -> Dict[str, Any]:
        """Get MT5 login credentials from environment."""
        if self._mt5_credentials is None:
            self._mt5_credentials = {
                "login": int(os.getenv("USERCLEAR", "0")),
                "password": os.getenv("PASSCLEAR", ""),
                "server": os.getenv("MT5_SERVER", "ClearInvestimentos-CLEAR"),
                "electronic_password": os.getenv("PASSELETR", "")
            }
        
        return self._mt5_credentials
    
    def get_api_keys(self) -> List[str]:
        """Get valid API keys for authentication."""
        if self._api_keys is None:
            # Default API keys - in production, these should come from secure storage
            default_keys = [
                "cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4"
            ]
            
            # Allow additional keys from environment (comma-separated)
            env_keys = os.getenv("API_KEYS", "")
            if env_keys:
                additional_keys = [key.strip() for key in env_keys.split(",")]
                self._api_keys = default_keys + additional_keys
            else:
                self._api_keys = default_keys
        
        return self._api_keys
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration settings."""
        if self._server_config is None:
            self._server_config = {
                "host": os.getenv("HOST", "0.0.0.0"),
                "port": int(os.getenv("PORT", "8000")),
                "debug": os.getenv("DEBUG", "False").lower() == "true",
                "reload": os.getenv("RELOAD", "False").lower() == "true",
                "cors_origins": self._parse_cors_origins(),
                "timeout": int(os.getenv("TIMEOUT", "60")),
                "max_request_size": int(os.getenv("MAX_REQUEST_SIZE", "1000")),
                "log_level": os.getenv("LOG_LEVEL", "INFO").upper()
            }
        
        return self._server_config
    
    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable."""
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        if cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in cors_origins.split(",")]
    
    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration (if needed for future features)."""
        return {
            "url": os.getenv("DATABASE_URL", ""),
            "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10"))
        }


class SimpleAuthenticationService(IAuthenticationService):
    """
    Simple authentication service using API keys.
    In production, this could be extended to use JWT, OAuth, etc.
    """
    
    def __init__(self, config_service: IConfigurationService):
        self._config_service = config_service
        self._valid_keys = None
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate if API key is authorized."""
        if not api_key:
            return False
        
        if self._valid_keys is None:
            self._valid_keys = set(self._config_service.get_api_keys())
        
        return api_key in self._valid_keys
    
    def get_user_permissions(self, api_key: str) -> List[str]:
        """Get permissions for a specific API key."""
        if not self.validate_api_key(api_key):
            return []
        
        # For now, all valid API keys have full permissions
        # In production, this could be more granular
        return [
            "read:symbols",
            "read:market_data", 
            "read:account",
            "trade:open_position",
            "trade:close_position",
            "trade:modify_position"
        ]
    
    def refresh_api_keys(self) -> None:
        """Refresh the cached API keys from configuration."""
        self._valid_keys = None