"""
Use cases implementing business logic.
Each use case has a single responsibility following SRP.
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from ...domain.interfaces import (
    IGetSymbolsUseCase,
    IGetSymbolInfoUseCase, 
    IGetTickersUseCase,
    IGetTickersByCountUseCase,
    IGetSymbolsPercentChangeUseCase,
    IOpenPositionUseCase,
    IClosePositionUseCase,
    ISymbolRepository,
    IMarketDataRepository,
    ITradingService
)
from ...domain.entities import Symbol, Ticker, TradeRequest, TimeFrame


class GetSymbolsUseCase(IGetSymbolsUseCase):
    """
    Use case for retrieving all available trading symbols.
    Single responsibility: Get symbols data.
    """
    
    def __init__(self, symbol_repository: ISymbolRepository):
        self._symbol_repository = symbol_repository
    
    async def execute(self) -> List[Symbol]:
        """Execute the get symbols use case."""
        try:
            symbols = await self._symbol_repository.get_all_symbols()
            return symbols
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve symbols: {str(e)}")


class GetSymbolInfoUseCase(IGetSymbolInfoUseCase):
    """
    Use case for retrieving information about a specific symbol.
    Single responsibility: Get symbol information.
    """
    
    def __init__(self, symbol_repository: ISymbolRepository):
        self._symbol_repository = symbol_repository
    
    async def execute(self, symbol_name: str) -> Optional[Symbol]:
        """Execute the get symbol info use case."""
        if not symbol_name or not symbol_name.strip():
            raise ValueError("Symbol name cannot be empty")
        
        try:
            symbol = await self._symbol_repository.get_symbol_by_name(symbol_name.strip().upper())
            return symbol
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve symbol info for {symbol_name}: {str(e)}")


class GetTickersUseCase(IGetTickersUseCase):
    """
    Use case for retrieving ticker data within a date range.
    Single responsibility: Get historical ticker data.
    """
    
    def __init__(self, market_data_repository: IMarketDataRepository):
        self._market_data_repository = market_data_repository
    
    async def execute(
        self,
        symbol: str,
        timeframe: TimeFrame,
        date_from: datetime,
        date_to: datetime
    ) -> List[Ticker]:
        """Execute the get tickers use case."""
        # Validate input parameters
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        if date_from >= date_to:
            raise ValueError("Date from must be before date to")
        
        try:
            tickers = await self._market_data_repository.get_tickers_by_range(
                symbol.strip().upper(),
                timeframe,
                date_from,
                date_to
            )
            return tickers
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve tickers for {symbol}: {str(e)}")


class GetTickersByCountUseCase(IGetTickersByCountUseCase):
    """
    Use case for retrieving the latest N ticker data points.
    Single responsibility: Get recent ticker data.
    """
    
    def __init__(self, market_data_repository: IMarketDataRepository):
        self._market_data_repository = market_data_repository
    
    async def execute(
        self,
        symbol: str,
        timeframe: TimeFrame,
        count: int
    ) -> List[Ticker]:
        """Execute the get tickers by count use case."""
        # Validate input parameters
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        if count <= 0:
            raise ValueError("Count must be positive")
        
        if count > 1000:
            raise ValueError("Count cannot exceed 1000 for performance reasons")
        
        try:
            tickers = await self._market_data_repository.get_tickers_by_count(
                symbol.strip().upper(),
                timeframe,
                count
            )
            return tickers
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve tickers for {symbol}: {str(e)}")


class GetSymbolsPercentChangeUseCase(IGetSymbolsPercentChangeUseCase):
    """
    Use case for calculating percent change for multiple symbols.
    Single responsibility: Calculate price change percentages.
    """
    
    def __init__(
        self,
        symbol_repository: ISymbolRepository,
        market_data_repository: IMarketDataRepository
    ):
        self._symbol_repository = symbol_repository
        self._market_data_repository = market_data_repository
    
    async def execute(
        self,
        symbols: List[str],
        timeframe: TimeFrame
    ) -> List[dict]:
        """Execute the get symbols percent change use case."""
        if not symbols:
            raise ValueError("Symbols list cannot be empty")
        
        if len(symbols) > 1000:
            raise ValueError("Cannot process more than 1000 symbols for performance reasons")
        
        results = []
        
        try:
            # Get symbol information
            all_symbols = await self._symbol_repository.get_all_symbols()
            symbol_dict = {s.name: s for s in all_symbols}
            
            for symbol_name in symbols:
                symbol_name = symbol_name.strip().upper()
                
                if symbol_name not in symbol_dict:
                    results.append({
                        "symbol": symbol_name,
                        "pct_change": 0.0,
                        "error": "Symbol not found"
                    })
                    continue
                
                try:
                    # Get last 2 tickers to calculate percentage change
                    tickers = await self._market_data_repository.get_tickers_by_count(
                        symbol_name,
                        timeframe,
                        2
                    )
                    
                    if len(tickers) >= 2:
                        # Calculate percentage change from previous close to current close
                        previous_close = tickers[0].close_price
                        current_close = tickers[1].close_price
                        
                        if previous_close > 0:
                            pct_change = float(((current_close - previous_close) / previous_close) * 100)
                        else:
                            pct_change = 0.0
                    else:
                        pct_change = 0.0
                    
                    results.append({
                        "symbol": symbol_name,
                        "pct_change": round(pct_change, 4),
                        "symbol_info": symbol_dict[symbol_name]
                    })
                    
                except Exception as e:
                    results.append({
                        "symbol": symbol_name,
                        "pct_change": 0.0,
                        "error": f"Failed to calculate change: {str(e)}"
                    })
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to calculate percent changes: {str(e)}")


class OpenPositionUseCase(IOpenPositionUseCase):
    """
    Use case for opening a new trading position.
    Single responsibility: Open trading positions.
    """
    
    def __init__(self, trading_service: ITradingService):
        self._trading_service = trading_service
    
    async def execute(self, trade_request: TradeRequest) -> dict:
        """Execute the open position use case."""
        try:
            # Validate trade request
            trade_request.validate()
            
            # Execute the trade
            result = await self._trading_service.open_position(trade_request)
            return result
            
        except ValueError as e:
            raise ValueError(f"Invalid trade request: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to open position: {str(e)}")


class ClosePositionUseCase(IClosePositionUseCase):
    """
    Use case for closing an existing trading position.
    Single responsibility: Close trading positions.
    """
    
    def __init__(self, trading_service: ITradingService):
        self._trading_service = trading_service
    
    async def execute(self, ticket: int, volume: Optional[Decimal] = None) -> dict:
        """Execute the close position use case."""
        if ticket <= 0:
            raise ValueError("Ticket must be positive")
        
        if volume is not None and volume <= 0:
            raise ValueError("Volume must be positive if specified")
        
        try:
            result = await self._trading_service.close_position(ticket, volume)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to close position {ticket}: {str(e)}")