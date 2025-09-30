"""
MT5 Trading Client Library

Cliente Python para consumir MT5 Trading API de outras máquinas.
Implementa Clean Architecture com interface simples e flexível.

Exemplo de uso básico:
```python
from mt5_client import MT5TradingClient

# Usar com async/await
async def main():
    client = MT5TradingClient("http://servidor-mt5:8000")
    
    async with client:
        # Verificar saúde da API
        health = await client.check_health()
        print(f"API Status: {health.status}")
        
        # Obter símbolos
        symbols = await client.get_symbols()
        print(f"Símbolos disponíveis: {len(symbols)}")
        
        # Dados de mercado
        eurusd = await client.get_market_data("EURUSD")
        if eurusd:
            print(f"EURUSD: {eurusd.current_price}")

# Usar de forma simples (síncrono)
from mt5_client import SimpleMT5Client

with SimpleMT5Client("http://servidor-mt5:8000") as client:
    symbols = client.get_symbols()
    prices = client.get_current_prices(["EURUSD", "GBPUSD"])
    print(prices)
```

Funcionalidades principais:
- Consulta de símbolos e informações de mercado
- Obtenção de cotações históricas e atuais
- Análise de variação percentual
- Análise completa de mercado
- Interface async/await e síncrona
- Retry automático e tratamento de erros
- Configuração flexível via parâmetros ou variáveis ambiente
"""

# Importações principais
from .presentation import (
    MT5TradingClient,
    SimpleMT5Client, 
    create_client,
    create_simple_client
)

# DTOs para uso externo
from .application.dtos import (
    SymbolResponse,
    TickerResponse, 
    SymbolPctChangeResponse,
    MarketDataResponse,
    ApiHealthResponse
)

# Exceções públicas
from .domain.exceptions import (
    MT5ClientError,
    ConnectionError,
    AuthenticationError,
    ValidationError,
    ApiError
)

# Metadados
__version__ = "1.0.0"
__author__ = "MT5 Trading API Client"
__description__ = "Cliente Python para MT5 Trading API com Clean Architecture"

# Interface principal simplificada
__all__ = [
    # Classes principais
    "MT5TradingClient",
    "SimpleMT5Client",
    
    # Factory functions
    "create_client", 
    "create_simple_client",
    
    # DTOs
    "SymbolResponse",
    "TickerResponse",
    "SymbolPctChangeResponse", 
    "MarketDataResponse",
    "ApiHealthResponse",
    
    # Exceções
    "MT5ClientError",
    "ConnectionError",
    "AuthenticationError", 
    "ValidationError",
    "ApiError"
]