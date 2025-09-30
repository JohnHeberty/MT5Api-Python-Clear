"""
MetaTrader 5 adapter implementing domain interfaces.
This adapter translates between MT5 API and our domain entities.
"""
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    # Mock MT5 module for development/testing
    class MockMT5:
        SYMBOL_TRADE_MODE_DISABLED = 0
        SYMBOL_TRADE_MODE_FULL = 4
        TIMEFRAME_M1 = 1
        TIMEFRAME_M5 = 5
        TIMEFRAME_M15 = 15
        TIMEFRAME_M30 = 30
        TIMEFRAME_H1 = 16385
        TIMEFRAME_H4 = 16388
        TIMEFRAME_D1 = 16408
        TIMEFRAME_W1 = 32769
        TIMEFRAME_MN1 = 49153
        TRADE_ACTION_DEAL = 1
        ORDER_TYPE_BUY = 0
        ORDER_TYPE_SELL = 1
        ORDER_TIME_GTC = 0
        TRADE_RETCODE_DONE = 10009
        
        def initialize(self): return True
        def login(self, *args): return True
        def shutdown(self): pass
        def terminal_info(self): return {"connected": True}
        def symbols_get(self): return []
        def symbol_info(self, symbol): return None
        def copy_rates_range(self, *args): return None
        def copy_rates_from_pos(self, *args): return None
        def symbol_info_tick(self, symbol): return None
        def order_send(self, request): 
            return type('Result', (), {
                'retcode': self.TRADE_RETCODE_DONE,
                'deal': 12345,
                'order': 12345,
                'volume': 0.1,
                'price': 1.0000,
                'bid': 0.9999,
                'ask': 1.0001,
                'comment': 'Mock trade',
                'request_id': 1,
                'retcode_external': 0,
                '_asdict': lambda: {
                    'retcode': self.TRADE_RETCODE_DONE,
                    'deal': 12345,
                    'order': 12345,
                    'volume': 0.1,
                    'price': 1.0000,
                    'bid': 0.9999,
                    'ask': 1.0001,
                    'comment': 'Mock trade',
                    'request_id': 1,
                    'retcode_external': 0
                }
            })()
    
    mt5 = MockMT5()
    MT5_AVAILABLE = False

import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ...domain.interfaces import (
    ISymbolRepository,
    IMarketDataRepository,
    IAccountRepository,
    ITradingService,
    IMT5ConnectionService
)
from ...domain.entities import (
    Symbol, Ticker, Account, Position, TradeRequest,
    TradeMode, TimeFrame, OrderType
)


class MT5ConnectionAdapter(IMT5ConnectionService):
    """
    Adapter for MT5 connection management.
    Single responsibility: Handle MT5 connection lifecycle.
    """
    
    def __init__(self):
        self._is_connected = False
        self._executor = ThreadPoolExecutor(max_workers=1)
    
    async def initialize_connection(self) -> bool:
        """Initialize connection to MetaTrader 5."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self._executor, mt5.initialize)
        self._is_connected = result
        return result
    
    async def login(self, login: int, password: str, server: str) -> bool:
        """Login to MetaTrader 5 account."""
        if not self._is_connected:
            await self.initialize_connection()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            mt5.login,
            login,
            password,
            server
        )
        return result
    
    async def shutdown_connection(self) -> None:
        """Shutdown connection to MetaTrader 5."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, mt5.shutdown)
        self._is_connected = False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._is_connected and mt5.terminal_info() is not None


class MT5SymbolRepository(ISymbolRepository):
    """
    Repository for MT5 symbol operations.
    Implements symbol data retrieval from MT5.
    """
    
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    async def get_all_symbols(self) -> List[Symbol]:
        """Retrieve all available trading symbols from MT5."""
        loop = asyncio.get_event_loop()
        symbols_data = await loop.run_in_executor(self._executor, mt5.symbols_get)
        
        if symbols_data is None:
            return []
        
        symbols = []
        for symbol_data in symbols_data:
            try:
                symbol = self._convert_mt5_symbol_to_domain(symbol_data)
                symbols.append(symbol)
            except Exception as e:
                # Log error but continue processing other symbols
                print(f"Error converting symbol {getattr(symbol_data, 'name', 'unknown')}: {e}")
                continue
        
        return symbols
    
    async def get_symbol_by_name(self, symbol_name: str) -> Optional[Symbol]:
        """Retrieve specific symbol by name from MT5."""
        loop = asyncio.get_event_loop()
        symbol_data = await loop.run_in_executor(self._executor, mt5.symbol_info, symbol_name)
        
        if symbol_data is None:
            return None
        
        try:
            return self._convert_mt5_symbol_to_domain(symbol_data)
        except Exception as e:
            print(f"Error converting symbol {symbol_name}: {e}")
            return None
    
    async def get_symbols_by_filter(self, filter_criteria: dict) -> List[Symbol]:
        """Retrieve symbols matching filter criteria."""
        # Get all symbols first, then filter
        all_symbols = await self.get_all_symbols()
        
        filtered_symbols = []
        for symbol in all_symbols:
            if self._matches_criteria(symbol, filter_criteria):
                filtered_symbols.append(symbol)
        
        return filtered_symbols
    
    def _convert_mt5_symbol_to_domain(self, mt5_symbol) -> Symbol:
        """Convert MT5 symbol data to domain Symbol entity."""
        # Map MT5 trade mode to our enum
        trade_mode_mapping = {
            0: TradeMode.DISABLED,
            1: TradeMode.LONG_ONLY,
            2: TradeMode.SHORT_ONLY,
            3: TradeMode.CLOSE_ONLY,
            4: TradeMode.FULL
        }
        
        return Symbol(
            name=mt5_symbol.name,
            description=getattr(mt5_symbol, 'description', ''),
            currency_base=mt5_symbol.currency_base,
            currency_profit=mt5_symbol.currency_profit,
            currency_margin=mt5_symbol.currency_margin,
            digits=mt5_symbol.digits,
            point=Decimal(str(mt5_symbol.point)),
            volume_min=Decimal(str(mt5_symbol.volume_min)),
            volume_max=Decimal(str(mt5_symbol.volume_max)),
            volume_step=Decimal(str(mt5_symbol.volume_step)),
            trade_mode=trade_mode_mapping.get(mt5_symbol.trade_mode, TradeMode.DISABLED),
            margin_initial=Decimal(str(getattr(mt5_symbol, 'margin_initial', 0))),
            margin_maintenance=Decimal(str(getattr(mt5_symbol, 'margin_maintenance', 0)))
        )
    
    def _matches_criteria(self, symbol: Symbol, criteria: dict) -> bool:
        """Check if symbol matches filter criteria."""
        for key, value in criteria.items():
            if hasattr(symbol, key):
                if getattr(symbol, key) != value:
                    return False
        return True


class MT5MarketDataRepository(IMarketDataRepository):
    """
    Repository for MT5 market data operations.
    Handles ticker data retrieval and price information.
    """
    
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    async def get_tickers_by_range(
        self,
        symbol: str,
        timeframe: TimeFrame,
        date_from: datetime,
        date_to: datetime
    ) -> List[Ticker]:
        """Retrieve ticker data for a specific date range."""
        loop = asyncio.get_event_loop()
        
        # Convert our timeframe to MT5 timeframe
        mt5_timeframe = self._convert_timeframe_to_mt5(timeframe)
        
        rates = await loop.run_in_executor(
            self._executor,
            mt5.copy_rates_range,
            symbol,
            mt5_timeframe,
            date_from,
            date_to
        )
        
        if rates is None or len(rates) == 0:
            return []
        
        return self._convert_rates_to_tickers(rates, symbol, timeframe)
    
    async def get_tickers_by_count(
        self,
        symbol: str,
        timeframe: TimeFrame,
        count: int
    ) -> List[Ticker]:
        """Retrieve latest N tickers for a symbol."""
        loop = asyncio.get_event_loop()
        
        # Convert our timeframe to MT5 timeframe
        mt5_timeframe = self._convert_timeframe_to_mt5(timeframe)
        
        rates = await loop.run_in_executor(
            self._executor,
            mt5.copy_rates_from_pos,
            symbol,
            mt5_timeframe,
            0,
            count
        )
        
        if rates is None or len(rates) == 0:
            return []
        
        return self._convert_rates_to_tickers(rates, symbol, timeframe)
    
    async def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol."""
        loop = asyncio.get_event_loop()
        tick = await loop.run_in_executor(self._executor, mt5.symbol_info_tick, symbol)
        
        if tick is None:
            return None
        
        # Return bid price as current price
        return Decimal(str(tick.bid))
    
    def _convert_timeframe_to_mt5(self, timeframe: TimeFrame) -> int:
        """Convert our TimeFrame enum to MT5 timeframe constant."""
        timeframe_mapping = {
            TimeFrame.M1: mt5.TIMEFRAME_M1,
            TimeFrame.M5: mt5.TIMEFRAME_M5,
            TimeFrame.M15: mt5.TIMEFRAME_M15,
            TimeFrame.M30: mt5.TIMEFRAME_M30,
            TimeFrame.H1: mt5.TIMEFRAME_H1,
            TimeFrame.H4: mt5.TIMEFRAME_H4,
            TimeFrame.D1: mt5.TIMEFRAME_D1,
            TimeFrame.W1: mt5.TIMEFRAME_W1,
            TimeFrame.MN1: mt5.TIMEFRAME_MN1
        }
        return timeframe_mapping.get(timeframe, mt5.TIMEFRAME_M1)
    
    def _convert_rates_to_tickers(self, rates, symbol: str, timeframe: TimeFrame) -> List[Ticker]:
        """Convert MT5 rates array to Ticker entities."""
        tickers = []
        
        for rate in rates:
            try:
                ticker = Ticker(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=pd.to_datetime(rate['time'], unit='s'),
                    open_price=Decimal(str(rate['open'])),
                    high_price=Decimal(str(rate['high'])),
                    low_price=Decimal(str(rate['low'])),
                    close_price=Decimal(str(rate['close'])),
                    volume=int(rate['tick_volume'])
                )
                tickers.append(ticker)
            except Exception as e:
                print(f"Error converting rate data for {symbol}: {e}")
                continue
        
        return tickers


class MT5TradingService(ITradingService):
    """
    Service for MT5 trading operations.
    Handles position opening, closing, and modification.
    """
    
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1)
    
    async def open_position(self, trade_request: TradeRequest) -> dict:
        """Open a new trading position."""
        loop = asyncio.get_event_loop()
        
        # Get symbol info for price calculation
        symbol_info = await loop.run_in_executor(
            self._executor,
            mt5.symbol_info,
            trade_request.symbol
        )
        
        if symbol_info is None:
            raise ValueError(f"Symbol {trade_request.symbol} not found")
        
        # Prepare MT5 trade request
        mt5_request = self._prepare_mt5_trade_request(trade_request, symbol_info)
        
        # Execute trade
        result = await loop.run_in_executor(
            self._executor,
            mt5.order_send,
            mt5_request
        )
        
        return self._process_trade_result(result)
    
    async def close_position(self, ticket: int, volume: Optional[Decimal] = None) -> dict:
        """Close an existing position."""
        # Implementation for closing positions
        # This would require getting position info first, then creating close request
        raise NotImplementedError("Close position functionality to be implemented")
    
    async def modify_position(
        self,
        ticket: int,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None
    ) -> dict:
        """Modify stop loss and take profit of an existing position."""
        # Implementation for modifying positions
        raise NotImplementedError("Modify position functionality to be implemented")
    
    def _prepare_mt5_trade_request(self, trade_request: TradeRequest, symbol_info) -> dict:
        """Prepare MT5 trade request from domain TradeRequest."""
        # Determine price based on order type
        price = (symbol_info.ask if trade_request.order_type == OrderType.BUY 
                else symbol_info.bid)
        
        # Determine MT5 order type
        mt5_order_type = (mt5.ORDER_TYPE_BUY if trade_request.order_type == OrderType.BUY
                         else mt5.ORDER_TYPE_SELL)
        
        mt5_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": trade_request.symbol,
            "volume": float(trade_request.volume),
            "type": mt5_order_type,
            "price": price,
            "deviation": trade_request.deviation,
            "magic": trade_request.magic_number,
            "comment": trade_request.comment,
            "type_time": mt5.ORDER_TIME_GTC,
        }
        
        # Add stop loss and take profit if specified
        if trade_request.stop_loss:
            mt5_request["sl"] = float(trade_request.stop_loss)
        
        if trade_request.take_profit:
            mt5_request["tp"] = float(trade_request.take_profit)
        
        return mt5_request
    
    def _process_trade_result(self, result) -> dict:
        """Process MT5 trade result and convert to standardized format."""
        result_dict = result._asdict() if hasattr(result, '_asdict') else {}
        
        return {
            "success": result.retcode == mt5.TRADE_RETCODE_DONE,
            "retcode": result.retcode,
            "deal": result.deal,
            "order": result.order,
            "volume": result.volume,
            "price": result.price,
            "bid": result.bid,
            "ask": result.ask,
            "comment": result.comment,
            "request_id": result.request_id,
            "retcode_external": result.retcode_external
        }