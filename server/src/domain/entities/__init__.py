"""
Domain entities representing the core business objects.
Following Domain-Driven Design principles.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum


class TradeMode(Enum):
    """Trade mode enumeration for symbols."""
    DISABLED = 0
    LONG_ONLY = 1  
    SHORT_ONLY = 2
    CLOSE_ONLY = 3
    FULL = 4


class TimeFrame(Enum):
    """MetaTrader 5 timeframes."""
    M1 = 1
    M5 = 5
    M15 = 15
    M30 = 30
    H1 = 16385
    H4 = 16388
    D1 = 16408
    W1 = 32769
    MN1 = 49153


class OrderType(Enum):
    """Order types for trading operations."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Symbol:
    """
    Symbol entity representing a tradable instrument.
    Immutable to ensure data integrity.
    """
    name: str
    description: str
    currency_base: str
    currency_profit: str
    currency_margin: str
    digits: int
    point: Decimal
    volume_min: Decimal
    volume_max: Decimal
    volume_step: Decimal
    trade_mode: TradeMode
    margin_initial: Decimal
    margin_maintenance: Decimal
    
    def __post_init__(self):
        """Validate symbol data integrity."""
        if not self.name:
            raise ValueError("Symbol name cannot be empty")
        if self.digits < 0:
            raise ValueError("Digits must be non-negative")
        if self.volume_min <= 0:
            raise ValueError("Minimum volume must be positive")
        if self.volume_max < self.volume_min:
            raise ValueError("Maximum volume must be greater than minimum volume")


@dataclass(frozen=True) 
class Ticker:
    """
    Ticker entity representing market data for a specific time period.
    Contains OHLC data with validation.
    """
    symbol: str
    timeframe: TimeFrame
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    
    def __post_init__(self):
        """Validate ticker data integrity."""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.high_price < max(self.open_price, self.close_price):
            raise ValueError("High price must be >= open and close prices")
        if self.low_price > min(self.open_price, self.close_price):
            raise ValueError("Low price must be <= open and close prices")
        if self.volume < 0:
            raise ValueError("Volume must be non-negative")
    
    def get_price_change_percent(self) -> Decimal:
        """Calculate price change percentage from open to close."""
        if self.open_price == 0:
            return Decimal('0')
        return ((self.close_price - self.open_price) / self.open_price) * 100


@dataclass(frozen=True)
class Account:
    """
    Account entity representing trading account information.
    Contains account details and trading permissions.
    """
    login: int
    name: str
    server: str
    currency: str
    balance: Decimal
    equity: Decimal
    margin: Decimal
    margin_free: Decimal
    leverage: int
    trade_allowed: bool
    trade_mode: TradeMode
    
    def __post_init__(self):
        """Validate account data."""
        if self.login <= 0:
            raise ValueError("Login must be positive")
        if not self.name:
            raise ValueError("Account name cannot be empty")
        if self.leverage <= 0:
            raise ValueError("Leverage must be positive")
    
    def is_margin_sufficient(self, required_margin: Decimal) -> bool:
        """Check if account has sufficient free margin for a trade."""
        return self.margin_free >= required_margin
    
    def get_margin_level_percent(self) -> Optional[Decimal]:
        """Calculate margin level percentage."""
        if self.margin == 0:
            return None
        return (self.equity / self.margin) * 100


@dataclass
class TradeRequest:
    """
    Trade request entity for opening/closing positions.
    Mutable to allow modifications before execution.
    """
    symbol: str
    volume: Decimal
    order_type: OrderType
    price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    deviation: int = 20
    comment: str = ""
    magic_number: int = 234000
    
    def validate(self) -> None:
        """Validate trade request parameters."""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.volume <= 0:
            raise ValueError("Volume must be positive")
        if self.deviation < 0:
            raise ValueError("Deviation must be non-negative")
        
        # Additional validations for stop loss and take profit
        if self.price and self.stop_loss and self.take_profit:
            if self.order_type == OrderType.BUY:
                if self.stop_loss >= self.price:
                    raise ValueError("Stop loss must be below entry price for BUY orders")
                if self.take_profit <= self.price:
                    raise ValueError("Take profit must be above entry price for BUY orders")
            elif self.order_type == OrderType.SELL:
                if self.stop_loss <= self.price:
                    raise ValueError("Stop loss must be above entry price for SELL orders")
                if self.take_profit >= self.price:
                    raise ValueError("Take profit must be below entry price for SELL orders")


@dataclass(frozen=True)
class Position:
    """
    Position entity representing an open trading position.
    """
    ticket: int
    symbol: str
    order_type: OrderType
    volume: Decimal
    open_price: Decimal
    current_price: Decimal
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    profit: Decimal
    swap: Decimal
    commission: Decimal
    open_time: datetime
    comment: str
    magic_number: int
    
    def __post_init__(self):
        """Validate position data."""
        if self.ticket <= 0:
            raise ValueError("Ticket must be positive")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.volume <= 0:
            raise ValueError("Volume must be positive")
    
    def get_unrealized_profit(self) -> Decimal:
        """Calculate total unrealized profit including swap and commission."""
        return self.profit + self.swap + self.commission
    
    def get_profit_in_points(self, point_value: Decimal) -> Decimal:
        """Calculate profit in points."""
        if point_value == 0:
            return Decimal('0')
        price_diff = (
            self.current_price - self.open_price 
            if self.order_type == OrderType.BUY 
            else self.open_price - self.current_price
        )
        return price_diff / point_value