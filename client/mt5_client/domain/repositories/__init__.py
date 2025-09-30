"""
MT5 Client - Domain Repositories
Interfaces para acesso a dados seguindo Clean Architecture
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities import Symbol, Ticker, SymbolPercentChange, MarketData, ApiResponse


class ISymbolRepository(ABC):
    """
    Interface para repositório de símbolos
    
    Interface Segregation: Interface específica para símbolos
    Dependency Inversion: Define contrato abstrato
    """
    
    @abstractmethod
    async def get_all_symbols(self) -> List[Symbol]:
        """Obter todos os símbolos disponíveis"""
        pass
    
    @abstractmethod
    async def get_symbol_by_name(self, symbol_name: str) -> Optional[Symbol]:
        """Obter símbolo específico por nome"""
        pass
    
    @abstractmethod
    async def search_symbols(self, pattern: str) -> List[Symbol]:
        """Buscar símbolos por padrão"""
        pass


class ITickerRepository(ABC):
    """
    Interface para repositório de cotações
    
    Interface Segregation: Interface específica para tickers
    """
    
    @abstractmethod
    async def get_tickers_by_period(
        self, 
        symbol: str, 
        date_from: datetime, 
        date_to: datetime,
        timeframe: int = 1
    ) -> List[Ticker]:
        """Obter cotações por período específico"""
        pass
    
    @abstractmethod
    async def get_latest_tickers(
        self, 
        symbol: str, 
        count: int = 10,
        timeframe: int = 1
    ) -> List[Ticker]:
        """Obter últimas N cotações"""
        pass
    
    @abstractmethod
    async def get_latest_ticker(self, symbol: str) -> Optional[Ticker]:
        """Obter última cotação de um símbolo"""
        pass


class IMarketAnalysisRepository(ABC):
    """
    Interface para repositório de análise de mercado
    
    Interface Segregation: Interface específica para análises
    """
    
    @abstractmethod
    async def get_symbols_percent_change(
        self, 
        symbols: List[str],
        timeframe: int = 1
    ) -> List[SymbolPercentChange]:
        """Obter variação percentual de múltiplos símbolos"""
        pass
    
    @abstractmethod
    async def get_symbol_percent_change(
        self, 
        symbol: str,
        timeframe: int = 1
    ) -> Optional[SymbolPercentChange]:
        """Obter variação percentual de um símbolo"""
        pass


class IMarketDataRepository(ABC):
    """
    Interface para repositório agregado de dados de mercado
    
    Interface Segregation: Interface para dados completos
    Dependency Inversion: Abstração de alto nível
    """
    
    @abstractmethod
    async def get_complete_market_data(self, symbol_name: str) -> Optional[MarketData]:
        """Obter dados completos de mercado para um símbolo"""
        pass
    
    @abstractmethod
    async def get_multiple_market_data(self, symbol_names: List[str]) -> List[MarketData]:
        """Obter dados de mercado para múltiplos símbolos"""
        pass


class IHealthRepository(ABC):
    """
    Interface para verificação de saúde da API
    
    Interface Segregation: Interface específica para health checks
    """
    
    @abstractmethod
    async def check_health(self) -> ApiResponse:
        """Verificar saúde da API"""
        pass
    
    @abstractmethod
    async def get_api_info(self) -> ApiResponse:
        """Obter informações da API"""
        pass


# Agregação de repositórios seguindo Interface Segregation
class IMT5Repository(ABC):
    """
    Interface agregada para todos os repositórios MT5
    
    Dependency Inversion: Abstração de alto nível
    Interface Segregation: Composta por interfaces menores
    """
    
    @property
    @abstractmethod
    def symbols(self) -> ISymbolRepository:
        """Acesso ao repositório de símbolos"""
        pass
    
    @property
    @abstractmethod
    def tickers(self) -> ITickerRepository:
        """Acesso ao repositório de cotações"""
        pass
    
    @property
    @abstractmethod
    def analysis(self) -> IMarketAnalysisRepository:
        """Acesso ao repositório de análises"""
        pass
    
    @property
    @abstractmethod
    def market_data(self) -> IMarketDataRepository:
        """Acesso ao repositório de dados de mercado"""
        pass
    
    @property
    @abstractmethod
    def health(self) -> IHealthRepository:
        """Acesso ao repositório de saúde"""
        pass