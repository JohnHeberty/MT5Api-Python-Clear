# MT5 Trading Client

Cliente Python para consumir MT5 Trading API de outras máquinas. Implementado com Clean Architecture para máxima flexibilidade e manutenibilidade.

## 🚀 Características

- **Clean Architecture**: Separação clara de responsabilidades
- **Interface Async/Await**: Performance otimizada para I/O
- **Interface Síncrona**: Para scripts simples
- **Retry Automático**: Tratamento robusto de falhas de rede
- **Configuração Flexível**: Via parâmetros ou variáveis ambiente
- **Type Hints Completas**: Suporte completo ao IntelliSense
- **SOLID Principles**: Código extensível e testável

## 📦 Instalação

### Instalação Local
```bash
cd client
pip install -r requirements.txt
pip install -e .
```

### Instalação via Código
```python
# Copiar pasta mt5_client para seu projeto
# Instalar dependências: pip install aiohttp numpy python-dotenv
```

## 🔧 Uso

### Interface Async (Recomendado)

```python
import asyncio
from mt5_client import MT5TradingClient

async def main():
    # Criar cliente
    client = MT5TradingClient(
        api_url="http://servidor-mt5:8000",
        api_key="sua-chave-aqui"  # opcional
    )
    
    async with client:
        # Verificar saúde da API
        health = await client.check_health()
        print(f"Status: {health.status}")
        
        # Obter símbolos disponíveis
        symbols = await client.get_symbols()
        print(f"Símbolos: {len(symbols)}")
        
        # Dados de um símbolo específico
        eurusd = await client.get_market_data("EURUSD")
        if eurusd:
            print(f"EURUSD: {eurusd.current_price}")
        
        # Preços atuais de múltiplos símbolos
        prices = await client.get_current_prices(["EURUSD", "GBPUSD", "USDJPY"])
        print("Preços atuais:", prices)
        
        # Variações diárias
        changes = await client.get_daily_changes(["EURUSD", "GBPUSD"])
        print("Variações:", changes)
        
        # Cotações históricas
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        tickers = await client.get_tickers(
            symbol="EURUSD",
            date_from=start_date,
            date_to=end_date,
            timeframe=16385  # H1
        )
        print(f"Cotações H1: {len(tickers)}")

# Executar
asyncio.run(main())
```

### Interface Síncrona (Scripts Simples)

```python
from mt5_client import SimpleMT5Client

# Usar cliente simples
with SimpleMT5Client("http://servidor-mt5:8000") as client:
    # Verificar conexão
    health = client.check_health()
    print(f"API Status: {health.status}")
    
    # Obter símbolos
    symbols = client.get_symbols()
    print(f"Total de símbolos: {len(symbols)}")
    
    # Preços atuais
    prices = client.get_current_prices(["EURUSD", "GBPUSD"])
    for symbol, price in prices.items():
        print(f"{symbol}: {price}")
    
    # Variações do dia
    changes = client.get_daily_changes(["EURUSD", "GBPUSD"])
    for symbol, change in changes.items():
        print(f"{symbol}: {change:+.2f}%")
```

### Factory Functions

```python
from mt5_client import create_client, create_simple_client

# Cliente async
async_client = create_client(
    api_url="http://servidor-mt5:8000",
    timeout=60,
    max_retries=5
)

# Cliente síncrono  
sync_client = create_simple_client("http://servidor-mt5:8000")
```

## ⚙️ Configuração

### Via Parâmetros
```python
client = MT5TradingClient(
    api_url="http://servidor-mt5:8000",
    api_key="sua-chave",
    timeout=30,
    max_retries=3,
    log_level="INFO"
)
```

### Via Variáveis de Ambiente
```python
# Criar arquivo .env
MT5_API_URL=http://servidor-mt5:8000
MT5_API_KEY=sua-chave-aqui
MT5_TIMEOUT=30
MT5_MAX_RETRIES=3
MT5_LOG_LEVEL=INFO

# No código
client = MT5TradingClient()  # Carrega automaticamente do .env
```

## 📊 Timeframes Suportados

| Timeframe | Código | Descrição |
|-----------|--------|-----------|
| M1        | 1      | 1 minuto  |
| M5        | 5      | 5 minutos |
| M15       | 15     | 15 minutos |
| M30       | 30     | 30 minutos |
| H1        | 16385  | 1 hora    |
| H4        | 16388  | 4 horas   |
| D1        | 16408  | 1 dia     |

## 🔍 Métodos Disponíveis

### Informações de Símbolos
- `get_symbols()` - Todos os símbolos
- `get_symbol_info(symbol)` - Info de símbolo específico  
- `search_symbols(pattern)` - Buscar por padrão
- `get_forex_pairs()` - Apenas pares Forex
- `get_major_pairs()` - Principais pares (EUR/USD, etc.)

### Dados de Mercado
- `get_market_data(symbol)` - Dados completos de um símbolo
- `get_multiple_market_data(symbols)` - Dados de múltiplos símbolos
- `get_current_prices(symbols)` - Preços atuais
- `get_daily_changes(symbols)` - Variações do dia

### Cotações Históricas
- `get_tickers(symbol, date_from, date_to, timeframe)` - Por período
- `get_latest_tickers(symbol, count, timeframe)` - Últimas N cotações

### Análises
- `get_symbols_percent_change(symbols, timeframe)` - Variações percentuais
- `analyze_market(symbols, timeframe)` - Análise completa

### Utilitários
- `check_health()` - Status da API

## 🛠️ Desenvolvimento

```bash
# Clonar e configurar
cd client

# Instalar dependências
pip install -r requirements.txt
pip install -e .

# Instalar dependências de desenvolvimento
pip install pytest pytest-asyncio black flake8 mypy

# Executar testes
pytest

# Formatação de código
black mt5_client/

# Linting
flake8 mt5_client/
```

## 📁 Estrutura do Projeto

```
client/
├── mt5_client/                 # Pacote principal
│   ├── __init__.py            # Interface pública
│   ├── domain/                # Camada de domínio
│   │   ├── entities/          # Entidades de negócio
│   │   ├── repositories/      # Interfaces de repositório
│   │   └── exceptions.py      # Exceções de domínio
│   ├── application/           # Camada de aplicação
│   │   ├── use_cases/         # Casos de uso
│   │   └── dtos/             # Objetos de transferência
│   ├── infrastructure/        # Camada de infraestrutura  
│   │   ├── adapters/          # Adaptadores HTTP
│   │   ├── config.py          # Configurações
│   │   └── __init__.py        # MT5Repository
│   └── presentation/          # Camada de apresentação
│       └── __init__.py        # MT5TradingClient
├── setup.py                   # Configuração de instalação
├── requirements.txt           # Dependências
└── README.md                  # Esta documentação
```

## 🌐 Exemplos de Uso em Produção

### Script de Monitoramento
```python
import asyncio
from datetime import datetime
from mt5_client import MT5TradingClient

async def monitor_pairs():
    client = MT5TradingClient("http://servidor-mt5:8000")
    
    major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
    
    async with client:
        while True:
            try:
                prices = await client.get_current_prices(major_pairs)
                changes = await client.get_daily_changes(major_pairs)
                
                print(f"\n[{datetime.now()}] Monitoramento de Pares:")
                for pair in major_pairs:
                    price = prices.get(pair, "N/A")
                    change = changes.get(pair, 0)
                    status = "🔴" if change < -0.5 else "🟢" if change > 0.5 else "⚪"
                    print(f"{status} {pair}: {price} ({change:+.2f}%)")
                
                await asyncio.sleep(30)  # Atualizar a cada 30s
                
            except Exception as e:
                print(f"Erro: {e}")
                await asyncio.sleep(60)

asyncio.run(monitor_pairs())
```

### Análise de Volatilidade
```python
from mt5_client import SimpleMT5Client
from datetime import datetime, timedelta

with SimpleMT5Client("http://servidor-mt5:8000") as client:
    symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    
    # Obter dados da última semana
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    for symbol in symbols:
        # Dados H1 da semana
        tickers = client.get_tickers(symbol, start_date, end_date, 16385)
        
        if tickers:
            prices = [t.close for t in tickers]
            volatility = (max(prices) - min(prices)) / min(prices) * 100
            print(f"{symbol}: Volatilidade semanal {volatility:.2f}%")
```

## 🔒 Segurança

- Use HTTPS em produção
- Mantenha a API key segura
- Configure timeout adequado
- Use retry com backoff
- Monitore logs para detectar problemas

## 📞 Suporte

Para dúvidas sobre uso do cliente, consulte a documentação da API do servidor ou os exemplos incluídos.