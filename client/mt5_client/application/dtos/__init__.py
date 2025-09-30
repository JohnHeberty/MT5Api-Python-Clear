"""
MT5 Client - Application DTOs
Data Transfer Objects para comunicação entre camadas
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class GetSymbolsRequest:
    """DTO para requisição de símbolos"""
    pass  # Não precisa de parâmetros


@dataclass
class GetSymbolInfoRequest:
    """DTO para requisição de informação de símbolo"""
    symbol: str


@dataclass
class GetTickersRequest:
    """DTO para requisição de cotações por período"""
    symbol: str
    date_from: datetime
    date_to: datetime
    timeframe: int = 1


@dataclass
class GetTickersPosRequest:
    """DTO para requisição de últimas cotações"""
    symbol: str
    count: int = 10
    timeframe: int = 1


@dataclass
class GetSymbolsPctChangeRequest:
    """DTO para requisição de variação percentual"""
    symbols: List[str]
    timeframe: int = 1


@dataclass
class GetMarketDataRequest:
    """DTO para requisição de dados completos de mercado"""
    symbol: str
    include_tickers: bool = True
    tickers_count: int = 10
    include_percent_change: bool = True
    timeframe: int = 1


@dataclass
class SearchSymbolsRequest:
    """DTO para busca de símbolos"""
    pattern: str
    limit: Optional[int] = None


# Response DTOs
@dataclass
class SymbolResponse:
    """DTO para resposta de símbolo"""
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
    
    @classmethod
    def from_entity(cls, symbol) -> 'SymbolResponse':
        """Converter entidade Symbol para DTO"""
        return cls(
            name=symbol.name,
            description=symbol.description,
            digits=symbol.digits,
            point=symbol.point,
            currency_base=symbol.currency_base,
            currency_profit=symbol.currency_profit,
            currency_margin=symbol.currency_margin,
            volume_min=symbol.volume_min,
            volume_max=symbol.volume_max,
            trade_mode=symbol.trade_mode
        )


@dataclass
class TickerResponse:
    """DTO para resposta de cotação"""
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    # Propriedades calculadas
    body: Optional[float] = None
    is_bullish: Optional[bool] = None
    range_value: Optional[float] = None
    
    @classmethod
    def from_entity(cls, ticker) -> 'TickerResponse':
        """Converter entidade Ticker para DTO"""
        return cls(
            symbol=ticker.symbol,
            time=ticker.time,
            open=float(ticker.open),
            high=float(ticker.high),
            low=float(ticker.low),
            close=float(ticker.close),
            volume=ticker.volume,
            body=float(ticker.body),
            is_bullish=ticker.is_bullish,
            range_value=float(ticker.range_value)
        )


@dataclass
class SymbolPctChangeResponse:
    """DTO para resposta de variação percentual"""
    symbol: str
    pct_change: float
    error: Optional[str] = None
    trend_strength: Optional[str] = None
    
    @classmethod
    def from_entity(cls, pct_change) -> 'SymbolPctChangeResponse':
        """Converter entidade SymbolPercentChange para DTO"""
        return cls(
            symbol=pct_change.symbol,
            pct_change=float(pct_change.pct_change),
            error=pct_change.error,
            trend_strength=pct_change.trend_strength
        )


@dataclass
class MarketDataResponse:
    """DTO para resposta de dados de mercado"""
    symbol: SymbolResponse
    latest_ticker: Optional[TickerResponse] = None
    tickers: Optional[List[TickerResponse]] = None
    percent_change: Optional[SymbolPctChangeResponse] = None
    current_price: Optional[float] = None
    price_range: Optional[tuple[float, float]] = None
    
    @classmethod
    def from_entity(cls, market_data) -> 'MarketDataResponse':
        """Converter entidade MarketData para DTO"""
        tickers_dto = None
        if market_data.tickers:
            tickers_dto = [TickerResponse.from_entity(t) for t in market_data.tickers]
        
        latest_ticker_dto = None
        if market_data.latest_ticker:
            latest_ticker_dto = TickerResponse.from_entity(market_data.latest_ticker)
        
        percent_change_dto = None
        if market_data.percent_change:
            percent_change_dto = SymbolPctChangeResponse.from_entity(market_data.percent_change)
        
        price_range = market_data.calculate_price_range()
        if price_range:
            price_range = (float(price_range[0]), float(price_range[1]))
        
        return cls(
            symbol=SymbolResponse.from_entity(market_data.symbol),
            latest_ticker=latest_ticker_dto,
            tickers=tickers_dto,
            percent_change=percent_change_dto,
            current_price=float(market_data.current_price) if market_data.current_price else None,
            price_range=price_range
        )


@dataclass
class ApiHealthResponse:
    """DTO para resposta de saúde da API"""
    status: str
    mt5_connection: str
    mt5_available: bool
    timestamp: datetime


@dataclass
class GenericResponse:
    """DTO genérico para respostas"""
    success: bool
    data: Optional[any] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None