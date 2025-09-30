"""
MT5 Client - Infrastructure Main Repository
Implementação principal do repositório MT5
"""
import logging
from typing import Optional

from .config import ApiConfig
from .adapters import (
    HttpClient, SymbolRepositoryAdapter, TickerRepositoryAdapter,
    MarketAnalysisRepositoryAdapter, MarketDataRepositoryAdapter, 
    HealthRepositoryAdapter
)
from ..domain.repositories import IMT5Repository


class MT5Repository(IMT5Repository):
    """
    Implementação principal do repositório MT5
    
    Facade Pattern: Interface unificada para todos os repositórios
    Dependency Inversion: Implementa interface abstrata
    Single Responsibility: Agregar repositórios específicos
    """
    
    def __init__(self, config: ApiConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # HTTP Client compartilhado
        self._http_client: Optional[HttpClient] = None
        
        # Repositórios específicos
        self._symbols_repo: Optional[SymbolRepositoryAdapter] = None
        self._tickers_repo: Optional[TickerRepositoryAdapter] = None
        self._analysis_repo: Optional[MarketAnalysisRepositoryAdapter] = None
        self._market_data_repo: Optional[MarketDataRepositoryAdapter] = None
        self._health_repo: Optional[HealthRepositoryAdapter] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_http_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_http_client(self):
        """Garantir que o cliente HTTP está inicializado"""
        if self._http_client is None:
            self._http_client = HttpClient(self.config)
            await self._http_client._ensure_session()
    
    async def close(self):
        """Fechar recursos"""
        if self._http_client:
            await self._http_client.close()
            self._http_client = None
        
        # Reset repositories
        self._symbols_repo = None
        self._tickers_repo = None
        self._analysis_repo = None
        self._market_data_repo = None
        self._health_repo = None
    
    @property
    def symbols(self) -> SymbolRepositoryAdapter:
        """Acesso ao repositório de símbolos"""
        if self._symbols_repo is None:
            if self._http_client is None:
                raise RuntimeError("Repository not initialized. Use async context manager.")
            self._symbols_repo = SymbolRepositoryAdapter(self._http_client)
        return self._symbols_repo
    
    @property
    def tickers(self) -> TickerRepositoryAdapter:
        """Acesso ao repositório de cotações"""
        if self._tickers_repo is None:
            if self._http_client is None:
                raise RuntimeError("Repository not initialized. Use async context manager.")
            self._tickers_repo = TickerRepositoryAdapter(self._http_client)
        return self._tickers_repo
    
    @property
    def analysis(self) -> MarketAnalysisRepositoryAdapter:
        """Acesso ao repositório de análises"""
        if self._analysis_repo is None:
            if self._http_client is None:
                raise RuntimeError("Repository not initialized. Use async context manager.")
            self._analysis_repo = MarketAnalysisRepositoryAdapter(self._http_client)
        return self._analysis_repo
    
    @property
    def market_data(self) -> MarketDataRepositoryAdapter:
        """Acesso ao repositório de dados de mercado"""
        if self._market_data_repo is None:
            if self._http_client is None:
                raise RuntimeError("Repository not initialized. Use async context manager.")
            self._market_data_repo = MarketDataRepositoryAdapter(
                self.symbols, self.tickers, self.analysis
            )
        return self._market_data_repo
    
    @property
    def health(self) -> HealthRepositoryAdapter:
        """Acesso ao repositório de saúde"""
        if self._health_repo is None:
            if self._http_client is None:
                raise RuntimeError("Repository not initialized. Use async context manager.")
            self._health_repo = HealthRepositoryAdapter(self._http_client)
        return self._health_repo