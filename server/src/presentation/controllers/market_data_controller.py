"""
FastAPI controllers following Single Responsibility Principle.
Each controller handles a specific domain of operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional

from ...application.use_cases import (
    GetSymbolsUseCase,
    GetSymbolInfoUseCase,
    GetTickersUseCase,
    GetTickersByCountUseCase,
    GetSymbolsPercentChangeUseCase
)
from ...application.dtos import (
    ApiResponse,
    SymbolResponseModel,
    TickerResponseModel,
    SymbolPercentChangeModel,
    GetSymbolInfoRequest,
    GetTickersRequest,
    GetTickersByCountRequest,
    GetSymbolsPercentChangeRequest
)
from ...domain.entities import TimeFrame


class MarketDataController:
    """
    Controller for market data operations.
    Single responsibility: Handle market data HTTP endpoints.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/market-data", tags=["Market Data"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up all market data routes."""
        
        @self.router.post(
            "/symbols",
            response_model=ApiResponse,
            summary="Get All Symbols",
            description="Retrieve all available trading symbols with their information",
            responses={
                200: {"description": "Symbols retrieved successfully"},
                401: {"description": "Unauthorized - Invalid API key"},
                500: {"description": "Internal server error"}
            }
        )
        async def get_symbols(
            get_symbols_use_case = Depends(lambda: None)  # Temporarily disable dependency
        ):
            """Get all available trading symbols."""
            try:
                symbols = await get_symbols_use_case.execute()
                
                # Convert domain entities to response models
                symbol_models = [
                    SymbolResponseModel.model_validate(symbol) 
                    for symbol in symbols
                ]
                
                return ApiResponse(
                    ok=True,
                    data={
                        "symbols": symbol_models,
                        "count": len(symbol_models)
                    }
                )
            
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve symbols: {str(e)}"
                )
        
        @self.router.post(
            "/symbol-info",
            response_model=ApiResponse,
            summary="Get Symbol Information",
            description="Retrieve detailed information for a specific trading symbol",
            responses={
                200: {"description": "Symbol information retrieved successfully"},
                400: {"description": "Invalid request parameters"},
                404: {"description": "Symbol not found"},
                401: {"description": "Unauthorized - Invalid API key"},
                500: {"description": "Internal server error"}
            }
        )
        async def get_symbol_info(
            request: GetSymbolInfoRequest,
            get_symbol_info_use_case: GetSymbolInfoUseCase = Depends()
        ):
            """Get information for a specific symbol."""
            try:
                symbol = await get_symbol_info_use_case.execute(request.active)
                
                if symbol is None:
                    return ApiResponse(
                        ok=False,
                        error=f"Symbol '{request.active}' not found"
                    )
                
                symbol_model = SymbolResponseModel.model_validate(symbol)
                
                return ApiResponse(
                    ok=True,
                    data=symbol_model
                )
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve symbol info: {str(e)}"
                )
        
        @self.router.post(
            "/tickers",
            response_model=ApiResponse,
            summary="Get Ticker Data by Date Range",
            description="Retrieve historical ticker/candlestick data for a symbol within a date range",
            responses={
                200: {"description": "Ticker data retrieved successfully"},
                400: {"description": "Invalid request parameters"},
                401: {"description": "Unauthorized - Invalid API key"},
                500: {"description": "Internal server error"}
            }
        )
        async def get_tickers(
            request: GetTickersRequest,
            get_tickers_use_case: GetTickersUseCase = Depends()
        ):
            """Get ticker data for a specific date range."""
            try:
                from datetime import datetime
                
                date_from = datetime.strptime(request.date_from, "%Y-%m-%d %H:%M:%S")
                date_to = datetime.strptime(request.date_to, "%Y-%m-%d %H:%M:%S")
                
                # Convert timeframe integer to enum
                timeframe = TimeFrame(request.timeframe)
                
                tickers = await get_tickers_use_case.execute(
                    request.active,
                    timeframe,
                    date_from,
                    date_to
                )
                
                # Convert domain entities to response models
                ticker_models = []
                for ticker in tickers:
                    ticker_model = TickerResponseModel.model_validate(ticker)
                    ticker_model.price_change_percent = ticker.get_price_change_percent()
                    ticker_models.append(ticker_model)
                
                return ApiResponse(
                    ok=True,
                    data={
                        "tickers": ticker_models,
                        "count": len(ticker_models),
                        "symbol": request.active,
                        "timeframe": request.timeframe,
                        "date_from": request.date_from,
                        "date_to": request.date_to
                    }
                )
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve ticker data: {str(e)}"
                )
        
        @self.router.post(
            "/tickers-by-count",
            response_model=ApiResponse,
            summary="Get Latest Ticker Data",
            description="Retrieve the latest N ticker/candlestick data points for a symbol",
            responses={
                200: {"description": "Ticker data retrieved successfully"},
                400: {"description": "Invalid request parameters"},
                401: {"description": "Unauthorized - Invalid API key"},
                500: {"description": "Internal server error"}
            }
        )
        async def get_tickers_by_count(
            request: GetTickersByCountRequest,
            get_tickers_by_count_use_case: GetTickersByCountUseCase = Depends()
        ):
            """Get the latest N ticker data points."""
            try:
                # Convert timeframe integer to enum
                timeframe = TimeFrame(request.timeframe)
                
                tickers = await get_tickers_by_count_use_case.execute(
                    request.active,
                    timeframe,
                    request.position
                )
                
                # Convert domain entities to response models
                ticker_models = []
                for ticker in tickers:
                    ticker_model = TickerResponseModel.model_validate(ticker)
                    ticker_model.price_change_percent = ticker.get_price_change_percent()
                    ticker_models.append(ticker_model)
                
                return ApiResponse(
                    ok=True,
                    data={
                        "tickers": ticker_models,
                        "count": len(ticker_models),
                        "symbol": request.active,
                        "timeframe": request.timeframe,
                        "requested_count": request.position
                    }
                )
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve ticker data: {str(e)}"
                )
        
        @self.router.post(
            "/symbols-percent-change",
            response_model=ApiResponse,
            summary="Get Symbols with Percent Change",
            description="Calculate and retrieve percentage change for multiple symbols",
            responses={
                200: {"description": "Symbols percent change calculated successfully"},
                400: {"description": "Invalid request parameters"},
                401: {"description": "Unauthorized - Invalid API key"},
                500: {"description": "Internal server error"}
            }
        )
        async def get_symbols_percent_change(
            request: GetSymbolsPercentChangeRequest,
            get_symbols_pct_change_use_case: GetSymbolsPercentChangeUseCase = Depends()
        ):
            """Get percentage change for multiple symbols."""
            try:
                # Convert timeframe integer to enum
                timeframe = TimeFrame(request.timeframe)
                
                results = await get_symbols_pct_change_use_case.execute(
                    request.actives,
                    timeframe
                )
                
                # Convert results to response models
                symbol_changes = []
                for result in results:
                    symbol_change = SymbolPercentChangeModel(**result)
                    symbol_changes.append(symbol_change)
                
                return ApiResponse(
                    ok=True,
                    data={
                        "symbols": symbol_changes,
                        "count": len(symbol_changes),
                        "timeframe": request.timeframe
                    }
                )
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to calculate percent changes: {str(e)}"
                )