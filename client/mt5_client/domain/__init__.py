"""
MT5 Client - Domain Package
Camada de domínio seguindo Clean Architecture
"""

# Importações principais para facilitar uso
from .entities import (
    Symbol,
    Ticker, 
    SymbolPercentChange,
    MarketData,
    ApiResponse
)

from .repositories import (
    ISymbolRepository,
    ITickerRepository,
    IMarketAnalysisRepository,
    IMarketDataRepository,
    IHealthRepository,
    IMT5Repository
)

__all__ = [
    # Entities
    "Symbol",
    "Ticker",
    "SymbolPercentChange", 
    "MarketData",
    "ApiResponse",
    
    # Repository Interfaces
    "ISymbolRepository",
    "ITickerRepository", 
    "IMarketAnalysisRepository",
    "IMarketDataRepository",
    "IHealthRepository",
    "IMT5Repository"
]