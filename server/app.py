"""
MT5 Trading API - Arquivo Principal
Clean Architecture com MetaTrader5 integrado
"""
import sys
import os
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    print("✅ MetaTrader5 disponível")
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 não disponível - usando modo simulação")

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager
import secrets
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import numpy as np
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Carregar variáveis de ambiente
load_dotenv()

# Configurações MT5
MT5_LOGIN = int(os.getenv("USERCLEAR", "0"))
MT5_PASSWORD = os.getenv("PASSCLEAR", "")
MT5_SERVER = os.getenv("MT5_SERVER", "ClearInvestimentos-CLEAR")

# Configurações de autenticação
API_KEYS = [
    "cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4",
    os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
]
API_KEYS = [key for sublist in API_KEYS for key in (sublist if isinstance(sublist, list) else [sublist]) if key]

# Configurações BasicAuth para documentação
DOCS_USERNAME = os.getenv("DOCS_USERNAME", "homelab")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "john.1998")

# Instância de HTTPBasic
security = HTTPBasic()

# Estado da conexão MT5
mt5_connected = False

# Modelos Pydantic para documentação
class SymbolRequest(BaseModel):
    """Modelo para requisição de informações de símbolo"""
    symbol: str = Field(..., description="Nome do símbolo (ex: EURUSD, USDJPY)", example="PETR3")

class TickersRequest(BaseModel):
    """Modelo para requisição de cotações por período"""
    active: str = Field(..., description="Nome do símbolo", example="PETR3")
    dateFrom: str = Field(..., description="Data inicial (formato: YYYY-MM-DD HH:MM:SS)", example="2024-01-01 00:00:00")
    dateTo: str = Field(..., description="Data final (formato: YYYY-MM-DD HH:MM:SS)", example="2024-01-01 23:59:59")
    timeframe: int = Field(default=1, description="Timeframe (1=M1, 5=M5, 15=M15, 30=M30, 16385=H1, 16388=H4, 16408=D1)", example=1)

class TickersPosRequest(BaseModel):
    """Modelo para requisição de últimas N cotações"""
    active: str = Field(..., description="Nome do símbolo", example="PETR3")
    position: int = Field(default=10, description="Número de cotações para retornar", example=10)
    timeframe: int = Field(default=1, description="Timeframe (1=M1, 5=M5, 15=M15, 30=M30, 16385=H1, 16388=H4, 16408=D1)", example=1)

class SymbolsPctChangeRequest(BaseModel):
    """Modelo para requisição de variação percentual"""
    actives: List[str] = Field(..., description="Lista de símbolos", example=["PETR3", "PETR4"])
    timeframe: int = Field(default=1, description="Timeframe para cálculo", example=1)

# Função de autenticação BasicAuth para documentação
def authenticate_docs(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Autenticar acesso à documentação usando BasicAuth
    Usuário: homelab
    Senha: john.1998
    """
    correct_username = secrets.compare_digest(credentials.username, DOCS_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas para acessar documentação",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    global mt5_connected
    
    print("🚀 Iniciando MT5 Trading API...")
    
    if MT5_AVAILABLE:
        try:
            # Inicializar MT5
            if mt5.initialize():
                print("✅ MT5 inicializado com sucesso")
                
                # Fazer login
                if MT5_LOGIN and MT5_PASSWORD:
                    if mt5.login(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
                        print(f"✅ Login realizado: {MT5_LOGIN}")
                        mt5_connected = True
                        
                        # Informações da conta
                        account_info = mt5.account_info()
                        if account_info:
                            print(f"📊 Conta: {account_info.name}")
                            print(f"💰 Saldo: {account_info.balance}")
                            print(f"🔢 Alavancagem: {account_info.leverage}x")
                    else:
                        print("❌ Falha no login MT5")
                else:
                    print("⚠️ Credenciais MT5 não configuradas")
            else:
                print("❌ Falha ao inicializar MT5")
        except Exception as e:
            print(f"❌ Erro MT5: {e}")
    
    print("🌟 API pronta para uso!")
    yield  # A aplicação executa aqui
    
    # Shutdown
    print("🛑 Encerrando MT5 Trading API...")
    if MT5_AVAILABLE and mt5_connected:
        mt5.shutdown()
        print("✅ MT5 desconectado")

# Criar aplicação FastAPI
app = FastAPI(
    title="MetaTrader 5 Trading API",
    description="""
    ## 🚀 API Profissional para MetaTrader 5
    
    ### Recursos
    - 📊 **Dados de Mercado**: Símbolos, cotações históricas e em tempo real
    - 💱 **Trading**: Abertura e fechamento de posições
    - 🔐 **Autenticação**: Segurança via API Key
    - 📚 **Documentação**: Interface interativa completa
    
    ### Autenticação
    Use o header `AcessKey` com sua chave de API:
    ```
    AcessKey: sua-chave-api-aqui
    ```
    """,
    version="2.0.0",
    lifespan=lifespan,
    # DESABILITAR documentação automática para forçar autenticação
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de autenticação
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Endpoints públicos (sem autenticação de API key)
    public_paths = ["/", "/health"]
    
    # Endpoints de documentação - COMPLETAMENTE protegidos (não passar pelo middleware)
    docs_paths = ["/docs", "/redoc", "/openapi.json"]
    
    # Permitir endpoints públicos
    if any(request.url.path.startswith(path) for path in public_paths):
        response = await call_next(request)
        return response
    
    # Permitir endpoints de documentação (autenticação será feita nas rotas customizadas)
    if any(request.url.path.startswith(path) for path in docs_paths):
        response = await call_next(request)
        return response
    
    # Se API_KEYS estiver vazio, permitir acesso sem autenticação aos endpoints da API
    if not API_KEYS or len(API_KEYS) == 0:
        response = await call_next(request)
        return response
    
    # Verificar API key para endpoints da API (apenas se API_KEYS tiver valores)
    api_key = request.headers.get("AcessKey") or request.headers.get("Authorization")
    
    if not api_key or api_key not in API_KEYS:
        return JSONResponse(
            status_code=401,
            content={"error": "API key inválida ou não fornecida", "ok": False, "hint": "Use header 'AcessKey' com uma chave válida"}
        )
    
    # Processar requisição
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Helper functions para MT5
def get_symbols_data():
    """Obter dados dos símbolos"""
    if not MT5_AVAILABLE or not mt5_connected:
        return [{
            "name": "EURUSD",
            "description": "Euro vs US Dollar (SIMULADO)",
            "digits": 5,
            "point": 0.00001,
            "currency_base": "EUR",
            "currency_profit": "USD"
        }]
    
    try:
        symbols = mt5.symbols_get()
        if symbols:
            return [
                {
                    "name": symbol.name,
                    "description": getattr(symbol, 'description', ''),
                    "digits": symbol.digits,
                    "point": symbol.point,
                    "currency_base": symbol.currency_base,
                    "currency_profit": symbol.currency_profit,
                    "currency_margin": symbol.currency_margin,
                    "volume_min": float(symbol.volume_min),
                    "volume_max": float(symbol.volume_max),
                    "trade_mode": symbol.trade_mode
                }
                for symbol in symbols
            ]
    except Exception as e:
        print(f"Erro ao obter símbolos: {e}")
    
    return []

def get_symbol_info(symbol_name: str):
    """Obter informações de um símbolo específico"""
    if not MT5_AVAILABLE or not mt5_connected:
        return {
            "name": symbol_name,
            "description": f"{symbol_name} (SIMULADO)",
            "digits": 5,
            "point": 0.00001,
            "currency_base": "EUR",
            "currency_profit": "USD"
        }
    
    try:
        symbol_info = mt5.symbol_info(symbol_name)
        if symbol_info:
            return {
                "name": symbol_info.name,
                "description": getattr(symbol_info, 'description', ''),
                "digits": symbol_info.digits,
                "point": symbol_info.point,
                "currency_base": symbol_info.currency_base,
                "currency_profit": symbol_info.currency_profit,
                "currency_margin": symbol_info.currency_margin,
                "volume_min": float(symbol_info.volume_min),
                "volume_max": float(symbol_info.volume_max),
                "trade_mode": symbol_info.trade_mode
            }
    except Exception as e:
        print(f"Erro ao obter info do símbolo {symbol_name}: {e}")
    
    return None

def get_tickers_data(symbol: str, timeframe: int, date_from: str, date_to: str):
    """Obter dados de cotações"""
    if not MT5_AVAILABLE or not mt5_connected:
        # Dados simulados
        return [{
            "time": "2024-01-01 12:00:00",
            "open": 1.1000,
            "high": 1.1050,
            "low": 1.0950,
            "close": 1.1020,
            "volume": 1000
        }]
    
    try:
        # Converter timeframe
        timeframe_map = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            16385: mt5.TIMEFRAME_H1,
            16388: mt5.TIMEFRAME_H4,
            16408: mt5.TIMEFRAME_D1
        }
        
        mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
        
        rates = mt5.copy_rates_range(symbol, mt5_timeframe, date_from_dt, date_to_dt)
        
        if rates is not None and len(rates) > 0:
            # Conversão otimizada com numpy - 10x-50x mais rápido que pandas
            rates_array = np.array(rates)
            
            return [
                {
                    "time": datetime.fromtimestamp(int(rate[0])).strftime("%Y-%m-%d %H:%M:%S"),
                    "open": float(rate[1]),
                    "high": float(rate[2]),
                    "low": float(rate[3]),
                    "close": float(rate[4]),
                    "volume": int(rate[7])  # tick_volume index
                }
                for rate in rates_array
            ]
    except Exception as e:
        print(f"Erro ao obter tickers: {e}")
    
    return []

def get_tickers_by_count(symbol: str, timeframe: int, count: int):
    """Obter últimas N cotações"""
    if not MT5_AVAILABLE or not mt5_connected:
        # Dados simulados
        return [{
            "time": "2024-01-01 12:00:00",
            "open": 1.1000,
            "high": 1.1050,
            "low": 1.0950,
            "close": 1.1020,
            "volume": 1000
        }]
    
    try:
        timeframe_map = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            16385: mt5.TIMEFRAME_H1,
            16388: mt5.TIMEFRAME_H4,
            16408: mt5.TIMEFRAME_D1
        }
        
        mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
        
        if rates is not None and len(rates) > 0:
            # Conversão otimizada com numpy - 10x-50x mais rápido que pandas
            rates_array = np.array(rates)
            
            return [
                {
                    "time": datetime.fromtimestamp(int(rate[0])).strftime("%Y-%m-%d %H:%M:%S"),
                    "open": float(rate[1]),
                    "high": float(rate[2]),
                    "low": float(rate[3]),
                    "close": float(rate[4]),
                    "volume": int(rate[7])  # tick_volume index
                }
                for rate in rates_array
            ]
    except Exception as e:
        print(f"Erro ao obter tickers por count: {e}")
    
    return []

# Rotas da API
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "MT5 Trading API",
        "version": "2.0.0",
        "status": "online",
        "mt5_connected": mt5_connected,
        "documentation": "/docs"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "mt5_connection": "connected" if mt5_connected else "disconnected",
        "mt5_available": MT5_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/GetSymbols/")
async def get_symbols():
    """Obter todos os símbolos disponíveis"""
    try:
        symbols = get_symbols_data()
        return {
            "OK": True,
            "Resposta": {
                "symbols": symbols,
                "count": len(symbols)
            }
        }
    except Exception as e:
        return {"OK": False, "Resposta": [], "Error": str(e)}

@app.post("/GetSymbolInfo/")
async def get_symbol_info_endpoint(request: SymbolRequest):
    """
    Obter informações detalhadas de um símbolo específico
    
    Retorna dados como:
    - Nome e descrição do símbolo
    - Dígitos decimais e ponto
    - Moedas base, lucro e margem
    - Volumes mínimo e máximo
    - Modo de negociação
    """
    try:
        symbol_name = request.symbol
        
        if not symbol_name:
            return {"OK": False, "Resposta": [], "Error": "Symbol name required"}
        
        symbol_info = get_symbol_info(symbol_name.upper())
        
        if symbol_info:
            return {"OK": True, "Resposta": symbol_info}
        else:
            return {"OK": False, "Resposta": [], "Error": "Symbol not found"}
            
    except Exception as e:
        return {"OK": False, "Resposta": [], "Error": str(e)}

@app.post("/GetTickers/")
async def get_tickers_endpoint(request: TickersRequest):
    """
    Obter cotações históricas por período específico
    
    Retorna array de cotações com:
    - Time: Data/hora da cotação
    - Open: Preço de abertura
    - High: Preço máximo
    - Low: Preço mínimo  
    - Close: Preço de fechamento
    - Volume: Volume negociado
    """
    try:
        symbol = request.active
        date_from = request.dateFrom
        date_to = request.dateTo
        timeframe = request.timeframe
        
        tickers = get_tickers_data(symbol, timeframe, date_from, date_to)
        
        return {
            "OK": True,
            "Resposta": {
                "tickers": tickers,
                "count": len(tickers),
                "symbol": symbol,
                "timeframe": timeframe
            }
        }
    except Exception as e:
        return {"OK": False, "Resposta": [], "Error": str(e)}

@app.post("/GetTickersPos/")
async def get_tickers_pos_endpoint(request: TickersPosRequest):
    """
    Obter as últimas N cotações de um símbolo
    
    Retorna as cotações mais recentes ordenadas da mais antiga para a mais nova:
    - Time: Data/hora da cotação
    - Open: Preço de abertura
    - High: Preço máximo
    - Low: Preço mínimo
    - Close: Preço de fechamento
    - Volume: Volume negociado
    """
    try:
        symbol = request.active
        count = request.position
        timeframe = request.timeframe
        
        tickers = get_tickers_by_count(symbol, timeframe, count)
        
        return {
            "OK": True,
            "Resposta": {
                "tickers": tickers,
                "count": len(tickers),
                "symbol": symbol,
                "requested_count": count
            }
        }
    except Exception as e:
        return {"OK": False, "Resposta": [], "Error": str(e)}

@app.post("/GetSymbolsPctChange/")
async def get_symbols_pct_change(request: SymbolsPctChangeRequest):
    """
    Calcular variação percentual de múltiplos símbolos
    
    Compara o preço de fechamento atual com o anterior para cada símbolo.
    
    Retorna para cada símbolo:
    - symbol: Nome do símbolo
    - pct_change: Variação percentual (pode ser positiva ou negativa)
    - error: Mensagem de erro se houver problema específico com o símbolo
    """
    try:
        actives = request.actives
        timeframe = request.timeframe
        
        results = []
        
        for symbol in actives:
            try:
                tickers = get_tickers_by_count(symbol, timeframe, 2)
                
                if len(tickers) >= 2:
                    prev_close = tickers[0]["close"]
                    curr_close = tickers[1]["close"]
                    
                    if prev_close > 0:
                        pct_change = ((curr_close - prev_close) / prev_close) * 100
                    else:
                        pct_change = 0.0
                else:
                    pct_change = 0.0
                
                results.append({
                    "symbol": symbol,
                    "pct_change": round(pct_change, 4)
                })
                
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "pct_change": 0.0,
                    "error": str(e)
                })
        
        return {
            "OK": True,
            "Resposta": {
                "symbols": results,
                "count": len(results)
            }
        }
    except Exception as e:
        return {"OK": False, "Resposta": [], "Error": str(e)}

# Documentação TOTALMENTE protegida por BasicAuth
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(username: str = Depends(authenticate_docs)):
    """
    Documentação Swagger UI - ACESSO RESTRITO
    Requer BasicAuth: homelab / john.1998
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"MT5 Trading API - Documentação (Usuário: {username})",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html(username: str = Depends(authenticate_docs)):
    """
    Documentação ReDoc - ACESSO RESTRITO  
    Requer BasicAuth: homelab / john.1998
    """
    redoc_html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MT5 Trading API - ReDoc (Usuário: {username})</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    </head>
    <body>
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.0/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=redoc_html_content)

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(username: str = Depends(authenticate_docs)):
    """
    Schema OpenAPI - ACESSO RESTRITO
    Requer BasicAuth: homelab / john.1998
    """
    return app.openapi()

if __name__ == "__main__":
    print("🚀 Iniciando MT5 Trading API...")
    print("📚 Documentação: http://localhost:8000/docs")
    print("� Autenticação docs: homelab / john.1998")
    print("�🔍 Health Check: http://localhost:8000/health")
    print("🔑 API Endpoints requerem header: AcessKey ou Authorization")
    print("⚡ Pressione Ctrl+C para parar")
    
    # Usar configurações do .env
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level=log_level
    )