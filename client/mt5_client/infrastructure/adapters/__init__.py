"""
MT5 Client - Infrastructure Adapters
Adaptadores para comunicação externa seguindo Clean Architecture
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import aiohttp
import json

from ..config import ApiConfig
from ...domain.entities import Symbol, Ticker, SymbolPercentChange, MarketData, ApiResponse
from ...domain.repositories import (
    ISymbolRepository, ITickerRepository, IMarketAnalysisRepository,
    IMarketDataRepository, IHealthRepository, IMT5Repository
)


class HttpClient:
    """
    Cliente HTTP para comunicação com a API
    
    Single Responsibility: Apenas comunicação HTTP
    Dependency Inversion: Interface abstrata para HTTP
    """
    
    def __init__(self, config: ApiConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Garantir que a sessão está criada"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(verify_ssl=self.config.verify_ssl)
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.config.get_headers()
            )
    
    async def close(self):
        """Fechar sessão HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fazer requisição POST"""
        await self._ensure_session()
        
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.strip('/')}"
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"POST {url} - Attempt {attempt + 1}")
                
                async with self._session.post(url, json=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    self.logger.debug(f"POST {url} - Success")
                    return result
                    
            except asyncio.TimeoutError:
                self.logger.warning(f"POST {url} - Timeout (attempt {attempt + 1})")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay)
                
            except aiohttp.ClientError as e:
                self.logger.error(f"POST {url} - Client error: {e}")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay)
        
        raise Exception(f"Failed to POST {url} after {self.config.max_retries} attempts")
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Fazer requisição GET"""
        await self._ensure_session()
        
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.strip('/')}"
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"GET {url} - Attempt {attempt + 1}")
                
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    self.logger.debug(f"GET {url} - Success")
                    return result
                    
            except asyncio.TimeoutError:
                self.logger.warning(f"GET {url} - Timeout (attempt {attempt + 1})")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay)
                
            except aiohttp.ClientError as e:
                self.logger.error(f"GET {url} - Client error: {e}")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay)
        
        raise Exception(f"Failed to GET {url} after {self.config.max_retries} attempts")


class SymbolRepositoryAdapter(ISymbolRepository):
    """
    Adaptador para repositório de símbolos
    
    Adapter Pattern: Adapta API HTTP para interface de domínio
    Single Responsibility: Apenas símbolos
    """
    
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def get_all_symbols(self) -> List[Symbol]:
        """Obter todos os símbolos"""
        try:
            response = await self.http_client.post("/GetSymbols/", {})
            
            if not response.get("OK"):
                raise Exception(f"API Error: {response.get('Error', 'Unknown error')}")
            
            symbols_data = response.get("Resposta", {}).get("symbols", [])
            
            return [self._map_to_symbol(symbol_data) for symbol_data in symbols_data]
            
        except Exception as e:
            self.logger.error(f"Error getting symbols: {e}")
            raise
    
    async def get_symbol_by_name(self, symbol_name: str) -> Optional[Symbol]:
        """Obter símbolo por nome"""
        try:
            response = await self.http_client.post("/GetSymbolInfo/", {
                "symbol": symbol_name
            })
            
            if not response.get("OK"):
                self.logger.warning(f"Symbol {symbol_name} not found")
                return None
            
            symbol_data = response.get("Resposta", {})
            return self._map_to_symbol(symbol_data)
            
        except Exception as e:
            self.logger.error(f"Error getting symbol {symbol_name}: {e}")
            raise
    
    async def search_symbols(self, pattern: str) -> List[Symbol]:
        """Buscar símbolos por padrão"""
        # Para simulação, obtemos todos e filtramos
        all_symbols = await self.get_all_symbols()
        pattern_upper = pattern.upper()
        
        return [
            symbol for symbol in all_symbols
            if pattern_upper in symbol.name.upper() or pattern_upper in symbol.description.upper()
        ]
    
    def _map_to_symbol(self, symbol_data: Dict[str, Any]) -> Symbol:
        """Mapear dados da API para entidade Symbol"""
        return Symbol(
            name=symbol_data.get("name", ""),
            description=symbol_data.get("description", ""),
            digits=symbol_data.get("digits", 5),
            point=symbol_data.get("point", 0.00001),
            currency_base=symbol_data.get("currency_base", ""),
            currency_profit=symbol_data.get("currency_profit", ""),
            currency_margin=symbol_data.get("currency_margin"),
            volume_min=symbol_data.get("volume_min"),
            volume_max=symbol_data.get("volume_max"),
            trade_mode=symbol_data.get("trade_mode")
        )


class TickerRepositoryAdapter(ITickerRepository):
    """
    Adaptador para repositório de cotações
    
    Adapter Pattern: Adapta API HTTP para interface de domínio
    Single Responsibility: Apenas cotações
    """
    
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def get_tickers_by_period(
        self, 
        symbol: str, 
        date_from: datetime, 
        date_to: datetime,
        timeframe: int = 1
    ) -> List[Ticker]:
        """Obter cotações por período"""
        try:
            response = await self.http_client.post("/GetTickers/", {
                "active": symbol,
                "dateFrom": date_from.strftime("%Y-%m-%d %H:%M:%S"),
                "dateTo": date_to.strftime("%Y-%m-%d %H:%M:%S"),
                "timeframe": timeframe
            })
            
            if not response.get("OK"):
                raise Exception(f"API Error: {response.get('Error', 'Unknown error')}")
            
            tickers_data = response.get("Resposta", {}).get("tickers", [])
            
            return [self._map_to_ticker(ticker_data, symbol) for ticker_data in tickers_data]
            
        except Exception as e:
            self.logger.error(f"Error getting tickers for {symbol}: {e}")
            raise
    
    async def get_latest_tickers(
        self, 
        symbol: str, 
        count: int = 10,
        timeframe: int = 1
    ) -> List[Ticker]:
        """Obter últimas cotações"""
        try:
            response = await self.http_client.post("/GetTickersPos/", {
                "active": symbol,
                "position": count,
                "timeframe": timeframe
            })
            
            if not response.get("OK"):
                raise Exception(f"API Error: {response.get('Error', 'Unknown error')}")
            
            tickers_data = response.get("Resposta", {}).get("tickers", [])
            
            return [self._map_to_ticker(ticker_data, symbol) for ticker_data in tickers_data]
            
        except Exception as e:
            self.logger.error(f"Error getting latest tickers for {symbol}: {e}")
            raise
    
    async def get_latest_ticker(self, symbol: str) -> Optional[Ticker]:
        """Obter última cotação"""
        tickers = await self.get_latest_tickers(symbol, count=1)
        return tickers[0] if tickers else None
    
    def _map_to_ticker(self, ticker_data: Dict[str, Any], symbol: str) -> Ticker:
        """Mapear dados da API para entidade Ticker"""
        time_str = ticker_data.get("time", "")
        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S") if time_str else datetime.now()
        
        return Ticker(
            symbol=symbol,
            time=time_obj,
            open=Decimal(str(ticker_data.get("open", 0))),
            high=Decimal(str(ticker_data.get("high", 0))),
            low=Decimal(str(ticker_data.get("low", 0))),
            close=Decimal(str(ticker_data.get("close", 0))),
            volume=ticker_data.get("volume", 0)
        )


class MarketAnalysisRepositoryAdapter(IMarketAnalysisRepository):
    """
    Adaptador para repositório de análise de mercado
    
    Single Responsibility: Apenas análises de mercado
    """
    
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def get_symbols_percent_change(
        self, 
        symbols: List[str],
        timeframe: int = 1
    ) -> List[SymbolPercentChange]:
        """Obter variação percentual de símbolos"""
        try:
            response = await self.http_client.post("/GetSymbolsPctChange/", {
                "actives": symbols,
                "timeframe": timeframe
            })
            
            if not response.get("OK"):
                raise Exception(f"API Error: {response.get('Error', 'Unknown error')}")
            
            symbols_data = response.get("Resposta", {}).get("symbols", [])
            
            return [self._map_to_percent_change(symbol_data) for symbol_data in symbols_data]
            
        except Exception as e:
            self.logger.error(f"Error getting percent changes: {e}")
            raise
    
    async def get_symbol_percent_change(
        self, 
        symbol: str,
        timeframe: int = 1
    ) -> Optional[SymbolPercentChange]:
        """Obter variação percentual de um símbolo"""
        results = await self.get_symbols_percent_change([symbol], timeframe)
        return results[0] if results else None
    
    def _map_to_percent_change(self, symbol_data: Dict[str, Any]) -> SymbolPercentChange:
        """Mapear dados da API para entidade SymbolPercentChange"""
        return SymbolPercentChange(
            symbol=symbol_data.get("symbol", ""),
            pct_change=Decimal(str(symbol_data.get("pct_change", 0))),
            error=symbol_data.get("error")
        )


class HealthRepositoryAdapter(IHealthRepository):
    """
    Adaptador para verificação de saúde da API
    
    Single Responsibility: Apenas health checks
    """
    
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def check_health(self) -> ApiResponse:
        """Verificar saúde da API"""
        try:
            response = await self.http_client.get("/health")
            
            return ApiResponse.success_response(
                data=response,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return ApiResponse.error_response(
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def get_api_info(self) -> ApiResponse:
        """Obter informações da API"""
        try:
            response = await self.http_client.get("/")
            
            return ApiResponse.success_response(
                data=response,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get API info: {e}")
            return ApiResponse.error_response(
                error_message=str(e),
                timestamp=datetime.now()
            )


class MarketDataRepositoryAdapter(IMarketDataRepository):
    """
    Adaptador agregado para dados completos de mercado
    
    Single Responsibility: Agregar dados de diferentes repositórios
    Facade Pattern: Interface simplificada para operações complexas
    """
    
    def __init__(
        self, 
        symbol_repo: ISymbolRepository,
        ticker_repo: ITickerRepository,
        analysis_repo: IMarketAnalysisRepository
    ):
        self.symbol_repo = symbol_repo
        self.ticker_repo = ticker_repo
        self.analysis_repo = analysis_repo
        self.logger = logging.getLogger(__name__)
    
    async def get_complete_market_data(self, symbol_name: str) -> Optional[MarketData]:
        """Obter dados completos de mercado"""
        try:
            # Obter símbolo
            symbol = await self.symbol_repo.get_symbol_by_name(symbol_name)
            if not symbol:
                return None
            
            # Obter dados em paralelo
            tasks = [
                self.ticker_repo.get_latest_ticker(symbol_name),
                self.ticker_repo.get_latest_tickers(symbol_name, 10),
                self.analysis_repo.get_symbol_percent_change(symbol_name)
            ]
            
            latest_ticker, tickers, percent_change = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Tratar exceções
            if isinstance(latest_ticker, Exception):
                latest_ticker = None
            if isinstance(tickers, Exception):
                tickers = None
            if isinstance(percent_change, Exception):
                percent_change = None
            
            return MarketData(
                symbol=symbol,
                latest_ticker=latest_ticker,
                tickers=tickers,
                percent_change=percent_change
            )
            
        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol_name}: {e}")
            raise
    
    async def get_multiple_market_data(self, symbol_names: List[str]) -> List[MarketData]:
        """Obter dados de múltiplos símbolos"""
        tasks = [self.get_complete_market_data(symbol) for symbol in symbol_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar apenas resultados válidos
        return [result for result in results if isinstance(result, MarketData)]