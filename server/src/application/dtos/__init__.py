"""
Data Transfer Objects (DTOs) using Pydantic for automatic validation.
These models define the API contract and provide automatic validation and documentation.
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum


# Response Models
class ApiResponse(BaseModel):
    """Base response model for all API endpoints."""
    ok: bool = Field(description="Indicates if the operation was successful")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if operation failed")
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    )


class SymbolResponseModel(BaseModel):
    """Response model for symbol information."""
    name: str = Field(description="Symbol name")
    description: str = Field(description="Symbol description")
    currency_base: str = Field(description="Base currency")
    currency_profit: str = Field(description="Profit currency")
    currency_margin: str = Field(description="Margin currency")
    digits: int = Field(description="Number of decimal places")
    point: Decimal = Field(description="Point size")
    volume_min: Decimal = Field(description="Minimum volume")
    volume_max: Decimal = Field(description="Maximum volume")
    volume_step: Decimal = Field(description="Volume step")
    trade_mode: int = Field(description="Trade mode (0=disabled, 4=full)")
    margin_initial: Decimal = Field(description="Initial margin requirement")
    margin_maintenance: Decimal = Field(description="Maintenance margin requirement")
    
    model_config = ConfigDict(from_attributes=True)


class TickerResponseModel(BaseModel):
    """Response model for ticker/candlestick data."""
    symbol: str = Field(description="Symbol name")
    timeframe: int = Field(description="Timeframe")
    timestamp: datetime = Field(description="Candlestick timestamp")
    open_price: Decimal = Field(description="Opening price")
    high_price: Decimal = Field(description="Highest price")
    low_price: Decimal = Field(description="Lowest price") 
    close_price: Decimal = Field(description="Closing price")
    volume: int = Field(description="Volume")
    price_change_percent: Optional[Decimal] = Field(default=None, description="Price change percentage")
    
    model_config = ConfigDict(from_attributes=True)


class SymbolPercentChangeModel(BaseModel):
    """Model for symbol with percentage change information."""
    symbol: str = Field(description="Symbol name")
    pct_change: float = Field(description="Percentage change")
    symbol_info: Optional[SymbolResponseModel] = Field(default=None, description="Symbol information")
    error: Optional[str] = Field(default=None, description="Error message if calculation failed")


class PositionResponseModel(BaseModel):
    """Response model for trading positions."""
    ticket: int = Field(description="Position ticket number")
    symbol: str = Field(description="Symbol name")
    order_type: str = Field(description="Order type (BUY/SELL)")
    volume: Decimal = Field(description="Position volume")
    open_price: Decimal = Field(description="Opening price")
    current_price: Decimal = Field(description="Current price")
    stop_loss: Optional[Decimal] = Field(default=None, description="Stop loss price")
    take_profit: Optional[Decimal] = Field(default=None, description="Take profit price")
    profit: Decimal = Field(description="Current profit/loss")
    swap: Decimal = Field(description="Swap amount")
    commission: Decimal = Field(description="Commission amount")
    open_time: datetime = Field(description="Position opening time")
    comment: str = Field(description="Position comment")
    magic_number: int = Field(description="Magic number")
    
    model_config = ConfigDict(from_attributes=True)


# Request Models
class GetSymbolInfoRequest(BaseModel):
    """Request model for getting symbol information."""
    active: str = Field(description="Symbol name to get information for", min_length=1, max_length=20)
    
    @validator('active')
    def validate_symbol_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Symbol name cannot be empty')
        return v.strip().upper()


class GetTickersRequest(BaseModel):
    """Request model for getting ticker data by date range."""
    active: str = Field(description="Symbol name", min_length=1, max_length=20)
    date_from: str = Field(description="Start date in format 'YYYY-MM-DD HH:MM:SS'")
    date_to: str = Field(description="End date in format 'YYYY-MM-DD HH:MM:SS'")
    timeframe: int = Field(description="Timeframe (1=M1, 5=M5, 16385=H1, etc.)")
    
    @validator('active')
    def validate_symbol_name(cls, v):
        return v.strip().upper()
    
    @validator('date_from', 'date_to')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError('Date must be in format YYYY-MM-DD HH:MM:SS')
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = [1, 5, 15, 30, 16385, 16388, 16408, 32769, 49153]
        if v not in valid_timeframes:
            raise ValueError(f'Invalid timeframe. Valid values: {valid_timeframes}')
        return v


class GetTickersByCountRequest(BaseModel):
    """Request model for getting ticker data by count."""
    active: str = Field(description="Symbol name", min_length=1, max_length=20)
    position: int = Field(description="Number of candles to retrieve", gt=0, le=1000)
    timeframe: int = Field(description="Timeframe (1=M1, 5=M5, 16385=H1, etc.)")
    
    @validator('active')
    def validate_symbol_name(cls, v):
        return v.strip().upper()
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = [1, 5, 15, 30, 16385, 16388, 16408, 32769, 49153]
        if v not in valid_timeframes:
            raise ValueError(f'Invalid timeframe. Valid values: {valid_timeframes}')
        return v


class GetSymbolsPercentChangeRequest(BaseModel):
    """Request model for getting symbols with percentage change."""
    actives: List[str] = Field(description="List of symbol names", min_items=1, max_items=1000)
    timeframe: int = Field(description="Timeframe for calculation")
    
    @validator('actives')
    def validate_symbol_list(cls, v):
        if not v:
            raise ValueError('Symbol list cannot be empty')
        return [symbol.strip().upper() for symbol in v if symbol.strip()]
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = [1, 5, 15, 30, 16385, 16388, 16408, 32769, 49153]
        if v not in valid_timeframes:
            raise ValueError(f'Invalid timeframe. Valid values: {valid_timeframes}')
        return v


class OrderTypeEnum(str, Enum):
    """Order type enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class TradeRequestModel(BaseModel):
    """Request model for opening trading positions."""
    symbol: str = Field(description="Symbol to trade", min_length=1, max_length=20)
    volume: Decimal = Field(description="Volume to trade", gt=0)
    order_type: OrderTypeEnum = Field(description="Order type (BUY or SELL)")
    price: Optional[Decimal] = Field(default=None, description="Entry price (if None, market price will be used)")
    stop_loss: Optional[Decimal] = Field(default=None, description="Stop loss price")
    take_profit: Optional[Decimal] = Field(default=None, description="Take profit price")
    deviation: int = Field(default=20, description="Price deviation in points", ge=0, le=100)
    comment: str = Field(default="", description="Trade comment", max_length=100)
    magic_number: int = Field(default=234000, description="Magic number for trade identification")
    
    @validator('symbol')
    def validate_symbol_name(cls, v):
        return v.strip().upper()
    
    @validator('volume')
    def validate_volume(cls, v):
        if v <= 0:
            raise ValueError('Volume must be positive')
        return v


class ClosePositionRequest(BaseModel):
    """Request model for closing trading positions."""
    ticket: int = Field(description="Position ticket to close", gt=0)
    volume: Optional[Decimal] = Field(default=None, description="Volume to close (if None, closes entire position)")
    
    @validator('volume')
    def validate_volume(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Volume must be positive if specified')
        return v


class TradeResultModel(BaseModel):
    """Response model for trading operations."""
    success: bool = Field(description="Whether the trade was successful")
    retcode: int = Field(description="Return code from MT5")
    deal: Optional[int] = Field(default=None, description="Deal ticket number")
    order: Optional[int] = Field(default=None, description="Order ticket number")
    volume: Optional[Decimal] = Field(default=None, description="Executed volume")
    price: Optional[Decimal] = Field(default=None, description="Execution price")
    bid: Optional[Decimal] = Field(default=None, description="Current bid price")
    ask: Optional[Decimal] = Field(default=None, description="Current ask price")
    comment: Optional[str] = Field(default=None, description="Broker comment")
    request_id: Optional[int] = Field(default=None, description="Request ID")


# Error Models
class ValidationErrorModel(BaseModel):
    """Model for validation errors."""
    field: str = Field(description="Field that caused the error")
    message: str = Field(description="Error message")
    value: Any = Field(description="Invalid value")


class ErrorResponseModel(BaseModel):
    """Error response model."""
    ok: bool = False
    error: str = Field(description="Error message")
    details: Optional[List[ValidationErrorModel]] = Field(default=None, description="Validation error details")
    error_code: Optional[str] = Field(default=None, description="Error code for programmatic handling")