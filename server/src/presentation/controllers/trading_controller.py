"""
Trading controller for handling trading operations.
Follows Single Responsibility Principle for trade-related endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ...application.use_cases import (
    OpenPositionUseCase,
    ClosePositionUseCase
)
from ...application.dtos import (
    ApiResponse,
    TradeRequestModel,
    ClosePositionRequest,
    TradeResultModel
)
from ...domain.entities import TradeRequest, OrderType
from decimal import Decimal


class TradingController:
    """
    Controller for trading operations.
    Single responsibility: Handle trading HTTP endpoints.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/trading", tags=["Trading"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up all trading routes."""
        
        @self.router.post(
            "/open-position",
            response_model=ApiResponse,
            summary="Open Trading Position",
            description="Open a new BUY or SELL position for a trading symbol",
            responses={
                200: {"description": "Position opened successfully"},
                400: {"description": "Invalid trade request parameters"},
                401: {"description": "Unauthorized - Invalid API key"},
                403: {"description": "Insufficient permissions or margin"},
                500: {"description": "Internal server error"}
            }
        )
        async def open_position(
            request: TradeRequestModel,
            open_position_use_case: OpenPositionUseCase = Depends()
        ):
            """Open a new trading position."""
            try:
                # Convert DTO to domain entity
                trade_request = TradeRequest(
                    symbol=request.symbol,
                    volume=request.volume,
                    order_type=OrderType(request.order_type.value),
                    price=request.price,
                    stop_loss=request.stop_loss,
                    take_profit=request.take_profit,
                    deviation=request.deviation,
                    comment=request.comment,
                    magic_number=request.magic_number
                )
                
                # Execute the trade
                result = await open_position_use_case.execute(trade_request)
                
                # Convert result to response model
                trade_result = TradeResultModel(**result)
                
                return ApiResponse(
                    ok=True,
                    data=trade_result
                )
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except PermissionError as e:
                raise HTTPException(status_code=403, detail=str(e))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to open position: {str(e)}"
                )
        
        @self.router.post(
            "/close-position",
            response_model=ApiResponse,
            summary="Close Trading Position",
            description="Close an existing trading position by ticket number",
            responses={
                200: {"description": "Position closed successfully"},
                400: {"description": "Invalid request parameters"},
                401: {"description": "Unauthorized - Invalid API key"},
                404: {"description": "Position not found"},
                500: {"description": "Internal server error"}
            }
        )
        async def close_position(
            request: ClosePositionRequest,
            close_position_use_case: ClosePositionUseCase = Depends()
        ):
            """Close an existing trading position."""
            try:
                # Execute the close operation
                result = await close_position_use_case.execute(
                    request.ticket,
                    request.volume
                )
                
                # Convert result to response model
                trade_result = TradeResultModel(**result)
                
                return ApiResponse(
                    ok=True,
                    data=trade_result
                )
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=f"Position {request.ticket} not found")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to close position: {str(e)}"
                )
        
        # Placeholder for future trading endpoints
        @self.router.get(
            "/positions",
            response_model=ApiResponse,
            summary="Get Open Positions",
            description="Retrieve all open trading positions",
            responses={
                200: {"description": "Positions retrieved successfully"},
                401: {"description": "Unauthorized - Invalid API key"},
                500: {"description": "Internal server error"}
            }
        )
        async def get_positions():
            """Get all open positions (placeholder for future implementation)."""
            return ApiResponse(
                ok=True,
                data={
                    "positions": [],
                    "message": "Position retrieval functionality to be implemented"
                }
            )
        
        @self.router.post(
            "/modify-position",
            response_model=ApiResponse,
            summary="Modify Position Stop Loss and Take Profit",
            description="Modify stop loss and take profit levels of an existing position",
            responses={
                200: {"description": "Position modified successfully"},
                400: {"description": "Invalid request parameters"},
                401: {"description": "Unauthorized - Invalid API key"},
                404: {"description": "Position not found"},
                500: {"description": "Internal server error"}
            }
        )
        async def modify_position():
            """Modify position (placeholder for future implementation)."""
            return ApiResponse(
                ok=True,
                data={
                    "message": "Position modification functionality to be implemented"
                }
            )