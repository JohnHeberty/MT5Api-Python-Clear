"""
MT5 Client - Application Use Cases
Casos de uso seguindo Clean Architecture
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..dtos import (
    GetSymbolsRequest, GetSymbolInfoRequest, GetTickersRequest,
    GetTickersPosRequest, GetSymbolsPctChangeRequest, GetMarketDataRequest,
    SearchSymbolsRequest, SymbolResponse, TickerResponse, 
    SymbolPctChangeResponse, MarketDataResponse, ApiHealthResponse
)
from ...domain.repositories import IMT5Repository


class BaseUseCase(ABC):
    """
    Classe base para casos de uso
    
    Single Responsibility: Define estrutura comum
    Dependency Inversion: Depende de abstração
    """
    
    def __init__(self, repository: IMT5Repository):
        self._repository = repository


class GetSymbolsUseCase(BaseUseCase):
    """
    Caso de uso: Obter todos os símbolos
    
    Single Responsibility: Apenas obter símbolos
    """
    
    async def execute(self, request: GetSymbolsRequest) -> List[SymbolResponse]:
        """Executar caso de uso"""
        symbols = await self._repository.symbols.get_all_symbols()
        return [SymbolResponse.from_entity(symbol) for symbol in symbols]


class GetSymbolInfoUseCase(BaseUseCase):
    """
    Caso de uso: Obter informações de um símbolo
    
    Single Responsibility: Apenas informações de símbolo
    """
    
    async def execute(self, request: GetSymbolInfoRequest) -> Optional[SymbolResponse]:
        """Executar caso de uso"""
        symbol = await self._repository.symbols.get_symbol_by_name(request.symbol)
        
        if symbol is None:
            return None
        
        return SymbolResponse.from_entity(symbol)


class SearchSymbolsUseCase(BaseUseCase):
    """
    Caso de uso: Buscar símbolos por padrão
    
    Single Responsibility: Apenas busca de símbolos
    """
    
    async def execute(self, request: SearchSymbolsRequest) -> List[SymbolResponse]:
        """Executar caso de uso"""
        symbols = await self._repository.symbols.search_symbols(request.pattern)
        
        result = [SymbolResponse.from_entity(symbol) for symbol in symbols]
        
        if request.limit:
            result = result[:request.limit]
        
        return result


class GetTickersUseCase(BaseUseCase):
    """
    Caso de uso: Obter cotações por período
    
    Single Responsibility: Apenas cotações por período
    """
    
    async def execute(self, request: GetTickersRequest) -> List[TickerResponse]:
        """Executar caso de uso"""
        tickers = await self._repository.tickers.get_tickers_by_period(
            symbol=request.symbol,
            date_from=request.date_from,
            date_to=request.date_to,
            timeframe=request.timeframe
        )
        
        return [TickerResponse.from_entity(ticker) for ticker in tickers]


class GetTickersPosUseCase(BaseUseCase):
    """
    Caso de uso: Obter últimas cotações
    
    Single Responsibility: Apenas últimas cotações
    """
    
    async def execute(self, request: GetTickersPosRequest) -> List[TickerResponse]:
        """Executar caso de uso"""
        tickers = await self._repository.tickers.get_latest_tickers(
            symbol=request.symbol,
            count=request.count,
            timeframe=request.timeframe
        )
        
        return [TickerResponse.from_entity(ticker) for ticker in tickers]


class GetSymbolsPctChangeUseCase(BaseUseCase):
    """
    Caso de uso: Obter variação percentual de símbolos
    
    Single Responsibility: Apenas variação percentual
    """
    
    async def execute(self, request: GetSymbolsPctChangeRequest) -> List[SymbolPctChangeResponse]:
        """Executar caso de uso"""
        pct_changes = await self._repository.analysis.get_symbols_percent_change(
            symbols=request.symbols,
            timeframe=request.timeframe
        )
        
        return [SymbolPctChangeResponse.from_entity(pct) for pct in pct_changes]


class GetMarketDataUseCase(BaseUseCase):
    """
    Caso de uso: Obter dados completos de mercado
    
    Single Responsibility: Agregação de dados de mercado
    Open/Closed: Extensível para novos tipos de dados
    """
    
    async def execute(self, request: GetMarketDataRequest) -> Optional[MarketDataResponse]:
        """Executar caso de uso"""
        market_data = await self._repository.market_data.get_complete_market_data(
            request.symbol
        )
        
        if market_data is None:
            return None
        
        return MarketDataResponse.from_entity(market_data)


class GetMultipleMarketDataUseCase(BaseUseCase):
    """
    Caso de uso: Obter dados de múltiplos símbolos
    
    Single Responsibility: Agregação de múltiplos símbolos
    """
    
    async def execute(self, symbols: List[str]) -> List[MarketDataResponse]:
        """Executar caso de uso"""
        market_data_list = await self._repository.market_data.get_multiple_market_data(symbols)
        
        return [MarketDataResponse.from_entity(md) for md in market_data_list]


class CheckApiHealthUseCase(BaseUseCase):
    """
    Caso de uso: Verificar saúde da API
    
    Single Responsibility: Apenas verificação de saúde
    """
    
    async def execute(self) -> ApiHealthResponse:
        """Executar caso de uso"""
        health_response = await self._repository.health.check_health()
        
        if health_response.success and health_response.data:
            data = health_response.data
            return ApiHealthResponse(
                status=data.get("status", "unknown"),
                mt5_connection=data.get("mt5_connection", "unknown"),
                mt5_available=data.get("mt5_available", False),
                timestamp=health_response.timestamp
            )
        else:
            # Retornar status de erro
            return ApiHealthResponse(
                status="error",
                mt5_connection="disconnected", 
                mt5_available=False,
                timestamp=health_response.timestamp
            )


# Facade/Aggregator Use Case para operações complexas
class MarketAnalysisUseCase(BaseUseCase):
    """
    Caso de uso avançado: Análise completa de mercado
    
    Single Responsibility: Análise agregada de mercado
    Open/Closed: Extensível para novas análises
    """
    
    async def analyze_symbols(self, symbols: List[str], timeframe: int = 1) -> dict:
        """
        Realizar análise completa de múltiplos símbolos
        
        Retorna análise agregada com:
        - Dados de mercado de todos os símbolos
        - Estatísticas gerais
        - Tendências identificadas
        """
        # Obter dados de mercado
        market_data_list = await self._repository.market_data.get_multiple_market_data(symbols)
        
        # Obter variações percentuais
        pct_changes = await self._repository.analysis.get_symbols_percent_change(
            symbols, timeframe
        )
        
        # Calcular estatísticas
        valid_changes = [pct for pct in pct_changes if pct.is_valid]
        
        if valid_changes:
            positive_count = sum(1 for pct in valid_changes if pct.is_positive)
            negative_count = sum(1 for pct in valid_changes if pct.is_negative)
            total_count = len(valid_changes)
            
            avg_change = sum(pct.pct_change for pct in valid_changes) / total_count
            
            market_sentiment = "bullish" if positive_count > total_count * 0.6 else \
                              "bearish" if negative_count > total_count * 0.6 else "neutral"
        else:
            market_sentiment = "unknown"
            avg_change = 0
            positive_count = negative_count = total_count = 0
        
        return {
            "market_data": [MarketDataResponse.from_entity(md) for md in market_data_list],
            "percent_changes": [SymbolPctChangeResponse.from_entity(pct) for pct in pct_changes],
            "statistics": {
                "total_symbols": len(symbols),
                "valid_symbols": len(valid_changes),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "average_change": float(avg_change),
                "market_sentiment": market_sentiment
            }
        }