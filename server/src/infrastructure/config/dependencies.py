"""
Dependency Injection container using FastAPI Depends.
Implements Dependency Inversion Principle for clean dependency management.
"""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from ...domain.interfaces import (
    ISymbolRepository,
    IMarketDataRepository,
    ITradingService,
    IMT5ConnectionService,
    IConfigurationService,
    IAuthenticationService,
    IGetSymbolsUseCase,
    IGetSymbolInfoUseCase,
    IGetTickersUseCase,
    IGetTickersByCountUseCase,
    IGetSymbolsPercentChangeUseCase,
    IOpenPositionUseCase,
    IClosePositionUseCase
)

from ...infrastructure.adapters import (
    MT5ConnectionAdapter,
    MT5SymbolRepository,
    MT5MarketDataRepository,
    MT5TradingService,
    EnvironmentConfigurationService,
    SimpleAuthenticationService
)

from ...application.use_cases import (
    GetSymbolsUseCase,
    GetSymbolInfoUseCase,
    GetTickersUseCase,
    GetTickersByCountUseCase,
    GetSymbolsPercentChangeUseCase,
    OpenPositionUseCase,
    ClosePositionUseCase
)


# Configuration Services
@lru_cache()
def get_configuration_service() -> IConfigurationService:
    """
    Get configuration service instance.
    Singleton pattern using lru_cache.
    """
    return EnvironmentConfigurationService()


def get_authentication_service(
    config_service: Annotated[IConfigurationService, Depends(get_configuration_service)]
) -> IAuthenticationService:
    """Get authentication service instance."""
    return SimpleAuthenticationService(config_service)


# Infrastructure Services  
@lru_cache()
def get_mt5_connection_service() -> IMT5ConnectionService:
    """
    Get MT5 connection service instance.
    Singleton to maintain connection state.
    """
    return MT5ConnectionAdapter()


def get_symbol_repository(
    connection_service: Annotated[IMT5ConnectionService, Depends(get_mt5_connection_service)]
) -> ISymbolRepository:
    """Get symbol repository instance."""
    return MT5SymbolRepository()


def get_market_data_repository(
    connection_service: Annotated[IMT5ConnectionService, Depends(get_mt5_connection_service)]
) -> IMarketDataRepository:
    """Get market data repository instance.""" 
    return MT5MarketDataRepository()


def get_trading_service(
    connection_service: Annotated[IMT5ConnectionService, Depends(get_mt5_connection_service)]
) -> ITradingService:
    """Get trading service instance."""
    return MT5TradingService()


# Use Cases
def get_symbols_use_case(
    symbol_repository: Annotated[ISymbolRepository, Depends(get_symbol_repository)]
) -> IGetSymbolsUseCase:
    """Get symbols use case instance."""
    return GetSymbolsUseCase(symbol_repository)


def get_symbol_info_use_case(
    symbol_repository: Annotated[ISymbolRepository, Depends(get_symbol_repository)]
) -> IGetSymbolInfoUseCase:
    """Get symbol info use case instance."""
    return GetSymbolInfoUseCase(symbol_repository)


def get_tickers_use_case(
    market_data_repository: Annotated[IMarketDataRepository, Depends(get_market_data_repository)]
) -> IGetTickersUseCase:
    """Get tickers use case instance."""
    return GetTickersUseCase(market_data_repository)


def get_tickers_by_count_use_case(
    market_data_repository: Annotated[IMarketDataRepository, Depends(get_market_data_repository)]
) -> IGetTickersByCountUseCase:
    """Get tickers by count use case instance."""
    return GetTickersByCountUseCase(market_data_repository)


def get_symbols_percent_change_use_case(
    symbol_repository: Annotated[ISymbolRepository, Depends(get_symbol_repository)],
    market_data_repository: Annotated[IMarketDataRepository, Depends(get_market_data_repository)]
) -> IGetSymbolsPercentChangeUseCase:
    """Get symbols percent change use case instance."""
    return GetSymbolsPercentChangeUseCase(symbol_repository, market_data_repository)


def get_open_position_use_case(
    trading_service: Annotated[ITradingService, Depends(get_trading_service)]
) -> IOpenPositionUseCase:
    """Get open position use case instance."""
    return OpenPositionUseCase(trading_service)


def get_close_position_use_case(
    trading_service: Annotated[ITradingService, Depends(get_trading_service)]
) -> IClosePositionUseCase:
    """Get close position use case instance."""
    return ClosePositionUseCase(trading_service)


# Convenience type aliases for dependency injection
ConfigurationServiceDep = Annotated[IConfigurationService, Depends(get_configuration_service)]
AuthenticationServiceDep = Annotated[IAuthenticationService, Depends(get_authentication_service)]
MT5ConnectionServiceDep = Annotated[IMT5ConnectionService, Depends(get_mt5_connection_service)]

SymbolRepositoryDep = Annotated[ISymbolRepository, Depends(get_symbol_repository)]
MarketDataRepositoryDep = Annotated[IMarketDataRepository, Depends(get_market_data_repository)]
TradingServiceDep = Annotated[ITradingService, Depends(get_trading_service)]

GetSymbolsUseCaseDep = Annotated[IGetSymbolsUseCase, Depends(get_symbols_use_case)]
GetSymbolInfoUseCaseDep = Annotated[IGetSymbolInfoUseCase, Depends(get_symbol_info_use_case)]
GetTickersUseCaseDep = Annotated[IGetTickersUseCase, Depends(get_tickers_use_case)]
GetTickersByCountUseCaseDep = Annotated[IGetTickersByCountUseCase, Depends(get_tickers_by_count_use_case)]
GetSymbolsPercentChangeUseCaseDep = Annotated[IGetSymbolsPercentChangeUseCase, Depends(get_symbols_percent_change_use_case)]
OpenPositionUseCaseDep = Annotated[IOpenPositionUseCase, Depends(get_open_position_use_case)]
ClosePositionUseCaseDep = Annotated[IClosePositionUseCase, Depends(get_close_position_use_case)]