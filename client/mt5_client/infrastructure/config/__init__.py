"""
MT5 Client - Infrastructure Configuration
Configurações da infraestrutura
"""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class ApiConfig:
    """
    Configuração da API MT5
    
    Single Responsibility: Apenas configuração
    """
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    
    @classmethod
    def from_environment(cls) -> 'ApiConfig':
        """Criar configuração a partir de variáveis de ambiente"""
        return cls(
            base_url=os.getenv("MT5_API_BASE_URL", "http://localhost:8000"),
            api_key=os.getenv("MT5_API_KEY"),
            timeout=int(os.getenv("MT5_API_TIMEOUT", "30")),
            max_retries=int(os.getenv("MT5_API_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("MT5_API_RETRY_DELAY", "1.0")),
            verify_ssl=os.getenv("MT5_API_VERIFY_SSL", "true").lower() == "true"
        )
    
    def get_headers(self) -> dict:
        """Obter headers para requisições"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["AcessKey"] = self.api_key
        
        return headers


@dataclass
class LoggingConfig:
    """
    Configuração de logging
    
    Single Responsibility: Apenas configuração de logs
    """
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = False
    log_file_path: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'LoggingConfig':
        """Criar configuração a partir de variáveis de ambiente"""
        return cls(
            level=os.getenv("MT5_CLIENT_LOG_LEVEL", "INFO"),
            format=os.getenv("MT5_CLIENT_LOG_FORMAT", cls.format),
            enable_file_logging=os.getenv("MT5_CLIENT_ENABLE_FILE_LOG", "false").lower() == "true",
            log_file_path=os.getenv("MT5_CLIENT_LOG_FILE_PATH")
        )