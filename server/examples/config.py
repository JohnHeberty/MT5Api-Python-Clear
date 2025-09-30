"""
Configuração para os exemplos da MT5 API
"""

# Configurações da API
API_BASE_URL = "http://localhost:8000"

# API Key - Configure com sua chave
# Para obter acesso, use uma das chaves válidas ou configure no .env
API_KEY = "cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4"

# Símbolos para testes
TEST_SYMBOLS = [
    "EURUSD",
    "USDJPY", 
    "GBPUSD",
    "AUDUSD",
    "USDCHF"
]

# Timeframes disponíveis
TIMEFRAMES = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 16385,
    "H4": 16388,
    "D1": 16408
}

# Configurações de exemplo
DEFAULT_SYMBOL = "EURUSD"
DEFAULT_TIMEFRAME = 1  # M1
DEFAULT_COUNT = 10
DEFAULT_DATE_FROM = "2024-01-01 00:00:00"
DEFAULT_DATE_TO = "2024-01-01 23:59:59"