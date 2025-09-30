"""
MT5 Client - Application Layer
Camada de aplicação seguindo Clean Architecture
"""

# DTOs
from .dtos import (
    GetSymbolsRequest,
    GetSymbolInfoRequest, 
    GetTickersRequest,
    GetTickersPosRequest,
    GetSymbolsPctChangeRequest,
    GetMarketDataRequest,
    SearchSymbolsRequest,
    SymbolResponse,
    TickerResponse,
    SymbolPctChangeResponse, 
    MarketDataResponse,
    ApiHealthResponse,
    GenericResponse
)

# Use Cases  
from .use_cases import (
    BaseUseCase,
    GetSymbolsUseCase,
    GetSymbolInfoUseCase,
    SearchSymbolsUseCase,
    GetTickersUseCase,
    GetTickersPosUseCase,
    GetSymbolsPctChangeUseCase,
    GetMarketDataUseCase,
    GetMultipleMarketDataUseCase,
    CheckApiHealthUseCase,
    MarketAnalysisUseCase
)

__all__ = [
    # DTOs
    "GetSymbolsRequest",
    "GetSymbolInfoRequest",
    "GetTickersRequest", 
    "GetTickersPosRequest",
    "GetSymbolsPctChangeRequest",
    "GetMarketDataRequest",
    "SearchSymbolsRequest",
    "SymbolResponse",
    "TickerResponse",
    "SymbolPctChangeResponse",
    "MarketDataResponse", 
    "ApiHealthResponse",
    "GenericResponse",
    
    # Use Cases
    "BaseUseCase",
    "GetSymbolsUseCase",
    "GetSymbolInfoUseCase", 
    "SearchSymbolsUseCase",
    "GetTickersUseCase",
    "GetTickersPosUseCase",
    "GetSymbolsPctChangeUseCase",
    "GetMarketDataUseCase",
    "GetMultipleMarketDataUseCase",
    "CheckApiHealthUseCase",
    "MarketAnalysisUseCase"
]