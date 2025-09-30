"""
MT5 Trading Client - Interface Pública
Cliente Python para consumir MT5 Trading API de outras máquinas
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..infrastructure import MT5Repository
from ..infrastructure.config import ApiConfig, LoggingConfig
from ..application import (
    GetSymbolsUseCase, GetSymbolInfoUseCase, SearchSymbolsUseCase,
    GetTickersUseCase, GetTickersPosUseCase, GetSymbolsPctChangeUseCase,
    GetMarketDataUseCase, GetMultipleMarketDataUseCase, CheckApiHealthUseCase,
    MarketAnalysisUseCase
)
from ..application.dtos import (
    GetSymbolsRequest, GetSymbolInfoRequest, SearchSymbolsRequest,
    GetTickersRequest, GetTickersPosRequest, GetSymbolsPctChangeRequest,
    GetMarketDataRequest, SymbolResponse, TickerResponse,
    SymbolPctChangeResponse, MarketDataResponse, ApiHealthResponse
)


class MT5TradingClient:
    """
    Cliente principal para MT5 Trading API
    
    Facade Pattern: Interface simplificada para toda a API
    Single Responsibility: Ponto de entrada único para o cliente
    Dependency Inversion: Usa abstrações internas
    
    Exemplo de uso:
    ```python
    from mt5_client import MT5TradingClient
    
    # Configurar cliente
    client = MT5TradingClient(
        api_url="http://servidor-mt5:8000",
        api_key="sua-chave-aqui"
    )
    
    # Usar cliente
    async with client:
        symbols = await client.get_symbols()
        eurusd_data = await client.get_market_data("EURUSD")
    ```
    """
    
    def __init__(
        self, 
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        log_level: str = "INFO"
    ):
        """
        Inicializar cliente MT5
        
        Args:
            api_url: URL base da API MT5
            api_key: Chave de API para autenticação  
            timeout: Timeout para requisições (segundos)
            max_retries: Número máximo de tentativas
            log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        """
        # Configurar logging
        logging_config = LoggingConfig(level=log_level)
        logging.basicConfig(level=logging_config.level, format=logging_config.format)
        
        self.logger = logging.getLogger(__name__)
        
        # Configurar API
        self.config = ApiConfig(
            base_url=api_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Repositório e use cases
        self._repository: Optional[MT5Repository] = None
        self._use_cases: Dict[str, Any] = {}
        
        self.logger.info(f"MT5 Client initialized for {api_url}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _initialize(self):
        """Inicializar repositório e use cases"""
        if self._repository is None:
            self._repository = MT5Repository(self.config)
            await self._repository.__aenter__()
            
            # Inicializar use cases
            self._use_cases = {
                'get_symbols': GetSymbolsUseCase(self._repository),
                'get_symbol_info': GetSymbolInfoUseCase(self._repository),
                'search_symbols': SearchSymbolsUseCase(self._repository),
                'get_tickers': GetTickersUseCase(self._repository),
                'get_tickers_pos': GetTickersPosUseCase(self._repository),
                'get_symbols_pct_change': GetSymbolsPctChangeUseCase(self._repository),
                'get_market_data': GetMarketDataUseCase(self._repository),
                'get_multiple_market_data': GetMultipleMarketDataUseCase(self._repository),
                'check_health': CheckApiHealthUseCase(self._repository),
                'market_analysis': MarketAnalysisUseCase(self._repository)
            }
            
            self.logger.info("MT5 Client initialized successfully")
    
    async def close(self):
        """Fechar recursos do cliente"""
        if self._repository:
            await self._repository.close()
            self._repository = None
        
        self._use_cases.clear()
        self.logger.info("MT5 Client closed")
    
    # Métodos públicos da API
    
    async def check_health(self) -> ApiHealthResponse:
        """
        Verificar saúde da API MT5
        
        Returns:
            Status de saúde da API e conexão MT5
        """
        await self._initialize()
        return await self._use_cases['check_health'].execute()
    
    async def get_symbols(self) -> List[SymbolResponse]:
        """
        Obter todos os símbolos disponíveis
        
        Returns:
            Lista de símbolos com informações detalhadas
        """
        await self._initialize()
        request = GetSymbolsRequest()
        return await self._use_cases['get_symbols'].execute(request)
    
    async def get_symbol_info(self, symbol: str) -> Optional[SymbolResponse]:
        """
        Obter informações detalhadas de um símbolo
        
        Args:
            symbol: Nome do símbolo (ex: "EURUSD")
            
        Returns:
            Informações do símbolo ou None se não encontrado
        """
        await self._initialize()
        request = GetSymbolInfoRequest(symbol=symbol)
        return await self._use_cases['get_symbol_info'].execute(request)
    
    async def search_symbols(self, pattern: str, limit: Optional[int] = None) -> List[SymbolResponse]:
        """
        Buscar símbolos por padrão
        
        Args:
            pattern: Padrão de busca (nome ou descrição)
            limit: Limite de resultados
            
        Returns:
            Lista de símbolos que correspondem ao padrão
        """
        await self._initialize()
        request = SearchSymbolsRequest(pattern=pattern, limit=limit)
        return await self._use_cases['search_symbols'].execute(request)
    
    async def get_tickers(
        self,
        symbol: str,
        date_from: datetime,
        date_to: datetime,
        timeframe: int = 1
    ) -> List[TickerResponse]:
        """
        Obter cotações por período específico
        
        Args:
            symbol: Nome do símbolo
            date_from: Data inicial
            date_to: Data final
            timeframe: Timeframe (1=M1, 5=M5, 15=M15, 30=M30, 16385=H1, 16388=H4, 16408=D1)
            
        Returns:
            Lista de cotações OHLCV
        """
        await self._initialize()
        request = GetTickersRequest(
            symbol=symbol,
            date_from=date_from,
            date_to=date_to,
            timeframe=timeframe
        )
        return await self._use_cases['get_tickers'].execute(request)
    
    async def get_latest_tickers(
        self,
        symbol: str,
        count: int = 10,
        timeframe: int = 1
    ) -> List[TickerResponse]:
        """
        Obter últimas N cotações
        
        Args:
            symbol: Nome do símbolo
            count: Número de cotações
            timeframe: Timeframe
            
        Returns:
            Lista das últimas cotações
        """
        await self._initialize()
        request = GetTickersPosRequest(
            symbol=symbol,
            count=count,
            timeframe=timeframe
        )
        return await self._use_cases['get_tickers_pos'].execute(request)
    
    async def get_symbols_percent_change(
        self,
        symbols: List[str],
        timeframe: int = 1
    ) -> List[SymbolPctChangeResponse]:
        """
        Obter variação percentual de múltiplos símbolos
        
        Args:
            symbols: Lista de símbolos
            timeframe: Timeframe para cálculo
            
        Returns:
            Lista de variações percentuais
        """
        await self._initialize()
        request = GetSymbolsPctChangeRequest(symbols=symbols, timeframe=timeframe)
        return await self._use_cases['get_symbols_pct_change'].execute(request)
    
    async def get_market_data(self, symbol: str) -> Optional[MarketDataResponse]:
        """
        Obter dados completos de mercado para um símbolo
        
        Args:
            symbol: Nome do símbolo
            
        Returns:
            Dados completos incluindo símbolo, cotações e variação percentual
        """
        await self._initialize()
        request = GetMarketDataRequest(symbol=symbol)
        return await self._use_cases['get_market_data'].execute(request)
    
    async def get_multiple_market_data(self, symbols: List[str]) -> List[MarketDataResponse]:
        """
        Obter dados de mercado para múltiplos símbolos
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Lista de dados de mercado
        """
        await self._initialize()
        return await self._use_cases['get_multiple_market_data'].execute(symbols)
    
    async def analyze_market(self, symbols: List[str], timeframe: int = 1) -> Dict[str, Any]:
        """
        Realizar análise completa de mercado
        
        Args:
            symbols: Lista de símbolos para análise
            timeframe: Timeframe para análise
            
        Returns:
            Análise completa com dados, estatísticas e sentimento
        """
        await self._initialize()
        return await self._use_cases['market_analysis'].analyze_symbols(symbols, timeframe)
    
    # Métodos de conveniência
    
    async def get_forex_pairs(self) -> List[SymbolResponse]:
        """Obter apenas pares de moedas Forex"""
        symbols = await self.get_symbols()
        return [symbol for symbol in symbols if len(symbol.name) == 6 and symbol.name.isalpha()]
    
    async def get_major_pairs(self) -> List[SymbolResponse]:
        """Obter principais pares de moedas"""
        major_pairs = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCHF", "NZDUSD", "USDCAD"]
        symbols = await self.get_symbols()
        return [symbol for symbol in symbols if symbol.name in major_pairs]
    
    async def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obter preços atuais de múltiplos símbolos
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Dicionário {símbolo: preço_atual}
        """
        market_data_list = await self.get_multiple_market_data(symbols)
        
        prices = {}
        for market_data in market_data_list:
            if market_data.current_price:
                prices[market_data.symbol.name] = market_data.current_price
        
        return prices
    
    async def get_daily_changes(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obter variações diárias de símbolos
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Dicionário {símbolo: variação_percentual}
        """
        changes = await self.get_symbols_percent_change(symbols, timeframe=16408)  # D1
        
        return {
            change.symbol: change.pct_change
            for change in changes
            if change.error is None
        }


# Classe utilitária para uso sem async
class SimpleMT5Client:
    """
    Cliente simplificado para uso sem async/await
    
    Wrapper síncrono para MT5TradingClient
    Facilita uso em scripts simples
    """
    
    def __init__(self, **kwargs):
        self.client = MT5TradingClient(**kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Fechar em loop novo se necessário
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(self.client.close())
    
    def _run_async(self, coro):
        """Executar corrotina de forma síncrona"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def get_symbols(self):
        return self._run_async(self.client.get_symbols())
    
    def get_symbol_info(self, symbol: str):
        return self._run_async(self.client.get_symbol_info(symbol))
    
    def get_current_prices(self, symbols: List[str]):
        return self._run_async(self.client.get_current_prices(symbols))
    
    def get_daily_changes(self, symbols: List[str]):
        return self._run_async(self.client.get_daily_changes(symbols))
    
    def check_health(self):
        return self._run_async(self.client.check_health())


# Factory functions para facilitar criação
def create_client(api_url: str, api_key: str = None, **kwargs) -> MT5TradingClient:
    """
    Factory function para criar cliente MT5
    
    Args:
        api_url: URL da API MT5
        api_key: Chave de autenticação
        **kwargs: Outras configurações
        
    Returns:
        Cliente MT5 configurado
    """
    return MT5TradingClient(api_url=api_url, api_key=api_key, **kwargs)


def create_simple_client(api_url: str, api_key: str = None, **kwargs) -> SimpleMT5Client:
    """
    Factory function para criar cliente simples
    
    Args:
        api_url: URL da API MT5
        api_key: Chave de autenticação
        **kwargs: Outras configurações
        
    Returns:
        Cliente MT5 simples (síncrono)
    """
    return SimpleMT5Client(api_url=api_url, api_key=api_key, **kwargs)