"""
Domain interfaces following SOLID principles.
These abstractions define contracts that infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from ..entities import (
    Symbol, Ticker, Account, TradeRequest, Position, TimeFrame
)


class ISymbolRepository(ABC):
    """
    Interface for symbol data operations.
    Following Interface Segregation Principle (ISP).
    """
    
    @abstractmethod
    async def get_all_symbols(self) -> List[Symbol]:
        """Retrieve all available trading symbols."""
        pass
    
    @abstractmethod
    async def get_symbol_by_name(self, symbol_name: str) -> Optional[Symbol]:
        """Retrieve specific symbol by name."""
        pass
    
    @abstractmethod
    async def get_symbols_by_filter(self, filter_criteria: dict) -> List[Symbol]:
        """Retrieve symbols matching filter criteria."""
        pass


class IMarketDataRepository(ABC):
    """
    Interface for market data operations.
    Single Responsibility: Handle only market data.
    """
    
    @abstractmethod
    async def get_tickers_by_range(
        self,
        symbol: str,
        timeframe: TimeFrame,
        date_from: datetime,
        date_to: datetime
    ) -> List[Ticker]:
        """Retrieve ticker data for a specific date range."""
        pass
    
    @abstractmethod
    async def get_tickers_by_count(
        self,
        symbol: str,
        timeframe: TimeFrame,
        count: int
    ) -> List[Ticker]:
        """Retrieve latest N tickers for a symbol."""
        pass
    
    @abstractmethod
    async def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol."""
        pass


class IAccountRepository(ABC):
    """
    Interface for account operations.
    """
    
    @abstractmethod
    async def get_account_info(self) -> Optional[Account]:
        """Retrieve current account information."""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Retrieve all open positions."""
        pass
    
    @abstractmethod
    async def get_position_by_ticket(self, ticket: int) -> Optional[Position]:
        """Retrieve specific position by ticket."""
        pass


class ITradingService(ABC):
    """
    Interface for trading operations.
    Separated from data retrieval following SRP.
    """
    
    @abstractmethod
    async def open_position(self, trade_request: TradeRequest) -> dict:
        """Open a new trading position."""
        pass
    
    @abstractmethod
    async def close_position(self, ticket: int, volume: Optional[Decimal] = None) -> dict:
        """Close an existing position."""
        pass
    
    @abstractmethod
    async def modify_position(
        self,
        ticket: int,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None
    ) -> dict:
        """Modify stop loss and take profit of an existing position."""
        pass


class IMT5ConnectionService(ABC):
    """
    Interface for MT5 connection management.
    Single responsibility: connection lifecycle.
    """
    
    @abstractmethod
    async def initialize_connection(self) -> bool:
        """Initialize connection to MetaTrader 5."""
        pass
    
    @abstractmethod
    async def login(self, login: int, password: str, server: str) -> bool:
        """Login to MetaTrader 5 account."""
        pass
    
    @abstractmethod
    async def shutdown_connection(self) -> None:
        """Shutdown connection to MetaTrader 5."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass


class IConfigurationService(ABC):
    """
    Interface for configuration management.
    """
    
    @abstractmethod
    def get_mt5_credentials(self) -> dict:
        """Get MT5 login credentials."""
        pass
    
    @abstractmethod
    def get_api_keys(self) -> List[str]:
        """Get valid API keys for authentication."""
        pass
    
    @abstractmethod
    def get_server_config(self) -> dict:
        """Get server configuration settings."""
        pass


class IAuthenticationService(ABC):
    """
    Interface for authentication operations.
    """
    
    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """Validate if API key is authorized."""
        pass
    
    @abstractmethod
    def get_user_permissions(self, api_key: str) -> List[str]:
        """Get permissions for a specific API key."""
        pass


# Use Case Interfaces following Command Pattern
class IUseCase(ABC):
    """
    Base interface for all use cases.
    Following Command pattern for better testability.
    """
    pass


class IGetSymbolsUseCase(IUseCase):
    """Get all symbols use case interface."""
    
    @abstractmethod
    async def execute(self) -> List[Symbol]:
        pass


class IGetSymbolInfoUseCase(IUseCase):
    """Get symbol information use case interface."""
    
    @abstractmethod
    async def execute(self, symbol_name: str) -> Optional[Symbol]:
        pass


class IGetTickersUseCase(IUseCase):
    """Get ticker data use case interface."""
    
    @abstractmethod
    async def execute(
        self,
        symbol: str,
        timeframe: TimeFrame,
        date_from: datetime,
        date_to: datetime
    ) -> List[Ticker]:
        pass


class IGetTickersByCountUseCase(IUseCase):
    """Get tickers by count use case interface."""
    
    @abstractmethod
    async def execute(
        self,
        symbol: str,
        timeframe: TimeFrame,
        count: int
    ) -> List[Ticker]:
        pass


class IGetSymbolsPercentChangeUseCase(IUseCase):
    """Get symbols with percent change use case interface."""
    
    @abstractmethod
    async def execute(
        self,
        symbols: List[str],
        timeframe: TimeFrame
    ) -> List[dict]:
        pass


class IOpenPositionUseCase(IUseCase):
    """Open position use case interface."""
    
    @abstractmethod
    async def execute(self, trade_request: TradeRequest) -> dict:
        pass


class IClosePositionUseCase(IUseCase):
    """Close position use case interface."""
    
    @abstractmethod
    async def execute(self, ticket: int, volume: Optional[Decimal] = None) -> dict:
        pass