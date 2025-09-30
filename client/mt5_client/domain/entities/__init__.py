"""
MT5 Client - Domain Entities
Entidades de domínio seguindo Clean Architecture
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


@dataclass(frozen=True)
class Symbol:
    """
    Entidade Symbol - Representa um símbolo de trading
    
    Single Responsibility: Apenas dados e lógica de negócio do símbolo
    Immutable: Frozen dataclass para garantir integridade
    """
    name: str
    description: str
    digits: int
    point: float
    currency_base: str
    currency_profit: str
    currency_margin: Optional[str] = None
    volume_min: Optional[float] = None
    volume_max: Optional[float] = None
    trade_mode: Optional[int] = None
    
    def __post_init__(self):
        """Validação de regras de negócio"""
        if not self.name:
            raise ValueError("Symbol name cannot be empty")
        if self.digits < 0:
            raise ValueError("Digits must be non-negative")
        if self.point <= 0:
            raise ValueError("Point must be positive")
    
    @property
    def is_forex(self) -> bool:
        """Verificar se é um par de moedas Forex"""
        return len(self.name) == 6 and self.name.isalpha()
    
    @property
    def precision(self) -> Decimal:
        """Obter precisão baseada nos dígitos"""
        return Decimal(10) ** (-self.digits)


@dataclass(frozen=True)
class Ticker:
    """
    Entidade Ticker - Representa uma cotação OHLCV
    
    Single Responsibility: Dados de cotação e cálculos relacionados
    """
    symbol: str
    time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    
    def __post_init__(self):
        """Validação de regras de negócio"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.high < self.low:
            raise ValueError("High must be >= Low")
        if not (self.low <= self.open <= self.high):
            raise ValueError("Open must be between Low and High")
        if not (self.low <= self.close <= self.high):
            raise ValueError("Close must be between Low and High")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
    
    @property
    def body(self) -> Decimal:
        """Corpo da vela (diferença entre close e open)"""
        return self.close - self.open
    
    @property
    def is_bullish(self) -> bool:
        """Verificar se é uma vela de alta"""
        return self.close > self.open
    
    @property
    def is_bearish(self) -> bool:
        """Verificar se é uma vela de baixa"""
        return self.close < self.open
    
    @property
    def is_doji(self) -> bool:
        """Verificar se é um doji (close = open)"""
        return self.close == self.open
    
    @property
    def range_value(self) -> Decimal:
        """Range da vela (high - low)"""
        return self.high - self.low
    
    @property
    def upper_shadow(self) -> Decimal:
        """Sombra superior"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_shadow(self) -> Decimal:
        """Sombra inferior"""
        return min(self.open, self.close) - self.low


@dataclass(frozen=True)
class SymbolPercentChange:
    """
    Entidade para variação percentual de símbolos
    
    Single Responsibility: Dados de variação percentual e análises
    """
    symbol: str
    pct_change: Decimal
    error: Optional[str] = None
    
    def __post_init__(self):
        """Validação"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Verificar se a variação é válida (sem erro)"""
        return self.error is None
    
    @property
    def is_positive(self) -> bool:
        """Verificar se é uma variação positiva"""
        return self.is_valid and self.pct_change > 0
    
    @property
    def is_negative(self) -> bool:
        """Verificar se é uma variação negativa"""
        return self.is_valid and self.pct_change < 0
    
    @property
    def is_neutral(self) -> bool:
        """Verificar se não houve variação"""
        return self.is_valid and self.pct_change == 0
    
    @property
    def trend_strength(self) -> str:
        """Classificar força da tendência"""
        if not self.is_valid:
            return "INVALID"
        
        abs_change = abs(self.pct_change)
        
        if abs_change >= 2:
            return "STRONG"
        elif abs_change >= 1:
            return "MODERATE"
        elif abs_change >= 0.5:
            return "WEAK"
        else:
            return "MINIMAL"


@dataclass(frozen=True)
class MarketData:
    """
    Entidade agregada para dados de mercado
    
    Single Responsibility: Agregar dados relacionados de um símbolo
    """
    symbol: Symbol
    latest_ticker: Optional[Ticker] = None
    tickers: Optional[List[Ticker]] = None
    percent_change: Optional[SymbolPercentChange] = None
    
    def __post_init__(self):
        """Validação de consistência"""
        if self.latest_ticker and self.latest_ticker.symbol != self.symbol.name:
            raise ValueError("Latest ticker symbol must match symbol name")
        
        if self.tickers:
            for ticker in self.tickers:
                if ticker.symbol != self.symbol.name:
                    raise ValueError("All tickers must match symbol name")
        
        if self.percent_change and self.percent_change.symbol != self.symbol.name:
            raise ValueError("Percent change symbol must match symbol name")
    
    @property
    def has_price_data(self) -> bool:
        """Verificar se tem dados de preço"""
        return self.latest_ticker is not None or (self.tickers is not None and len(self.tickers) > 0)
    
    @property
    def current_price(self) -> Optional[Decimal]:
        """Obter preço atual"""
        if self.latest_ticker:
            return self.latest_ticker.close
        elif self.tickers and len(self.tickers) > 0:
            return self.tickers[-1].close  # Último ticker
        return None
    
    def calculate_price_range(self) -> Optional[tuple[Decimal, Decimal]]:
        """Calcular range de preços (min, max) dos tickers"""
        if not self.tickers:
            return None
        
        lows = [ticker.low for ticker in self.tickers]
        highs = [ticker.high for ticker in self.tickers]
        
        return min(lows), max(highs)


@dataclass(frozen=True)
class ApiResponse:
    """
    Entidade para resposta da API
    
    Single Responsibility: Encapsular resposta da API com metadados
    """
    success: bool
    data: Optional[any] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Validação de consistência"""
        if not self.success and not self.error_message:
            raise ValueError("Failed responses must have error message")
        if self.success and self.error_message:
            raise ValueError("Successful responses should not have error message")
    
    @property
    def has_data(self) -> bool:
        """Verificar se tem dados"""
        return self.success and self.data is not None
    
    @classmethod
    def success_response(cls, data: any, timestamp: datetime = None) -> 'ApiResponse':
        """Factory method para resposta de sucesso"""
        return cls(
            success=True,
            data=data,
            timestamp=timestamp or datetime.now()
        )
    
    @classmethod
    def error_response(cls, error_message: str, timestamp: datetime = None) -> 'ApiResponse':
        """Factory method para resposta de erro"""
        return cls(
            success=False,
            error_message=error_message,
            timestamp=timestamp or datetime.now()
        )