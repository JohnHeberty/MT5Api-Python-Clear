# 🚀 Meta Trader 5 API - Client & Server

Sistema completo de trading com MetaTrader 5, implementado com **Clean Architecture** e **SOLID Principles**. Inclui servidor FastAPI e cliente Python para consumo em outras máquinas.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![MetaTrader5](https://img.shields.io/badge/MetaTrader5-5.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Índice

- [📖 Visão Geral](#-visão-geral)
- [🏗️ Arquitetura](#️-arquitetura)
- [⚡ Quick Start](#-quick-start)
- [🖥️ Parte 1: Servidor (API)](#️-parte-1-servidor-api)
- [💻 Parte 2: Cliente (Consumer)](#-parte-2-cliente-consumer)
- [🔧 Configurações Avançadas](#-configurações-avançadas)
- [📊 Exemplos de Uso](#-exemplos-de-uso)
- [🛡️ Segurança](#️-segurança)
- [🐛 Troubleshooting](#-troubleshooting)

---

## 📖 Visão Geral

Este projeto oferece uma **API REST completa** para MetaTrader 5 com:

### 🎯 **Recursos Principais**
- 📊 **API Server**: Servidor FastAPI com integração MT5 real
- 💻 **Client Library**: Cliente Python para consumo remoto
- 🔐 **Autenticação Dupla**: BasicAuth (docs) + API Keys (endpoints)
- 📚 **Documentação Interativa**: Swagger UI + ReDoc
- ⚡ **Performance Otimizada**: numpy + async/await
- 🏗️ **Clean Architecture**: Separação clara de responsabilidades

### 🛠️ **Tecnologias**
- **Backend**: FastAPI + Uvicorn + MetaTrader5
- **Frontend**: Swagger UI + ReDoc (documentação)
- **Client**: aiohttp + Clean Architecture
- **Data**: numpy (performance otimizada)
- **Security**: HTTPBasic + API Keys

---

## 🏗️ Arquitetura

```
MT5 Trading System
├── 🖥️  SERVER (FastAPI)          ← Servidor principal
│   ├── MetaTrader5 Integration   ← Conexão real com MT5
│   ├── REST API Endpoints        ← Endpoints para trading
│   ├── BasicAuth Documentation   ← Docs protegidas
│   └── API Key Authentication    ← Endpoints protegidos
│
└── 💻 CLIENT (Python Library)    ← Cliente para outras máquinas
    ├── Clean Architecture        ← Domain/App/Infrastructure
    ├── Async/Sync Interface      ← Flexibilidade de uso
    ├── Type Hints Complete       ← IntelliSense completo
    └── Error Handling Robust     ← Retry automático + logging
```

---

## ⚡ Quick Start

### 🚀 **Inicialização Rápida (5 minutos)**

```bash
# 1️⃣ Clone/baixe o projeto
cd OLD_MT5Api

# 2️⃣ Inicie o servidor (PRIMEIRO)
cd server
./start.bat                    # Windows - Setup automático
# OU
python app.py                  # Direto (se deps instaladas)

# 3️⃣ Configure o cliente (SEGUNDO) - Em outro terminal
cd ../client
pip install -r requirements.txt
python examples/exemplo_basico.py
```

**🎉 Pronto!** Servidor na porta 8000, cliente conectado e funcionando!

---

## 🖥️ Parte 1: Servidor (API)

O servidor é o **coração do sistema** - conecta com MetaTrader 5 e expõe API REST.

### 📂 Estrutura do Servidor

```
server/
├── app.py                 # 🎯 Arquivo principal (tudo integrado)
├── start.bat             # 🚀 Script de inicialização automática
├── requirements.txt      # 📦 Dependências do servidor
├── .env                  # 🔐 Suas credenciais (não committar)
├── .env.example          # 📋 Template de configuração
└── examples/             # 📚 Exemplos de uso da API
```

### 🚀 **1. Instalação e Configuração**

#### **Método 1: Automático (Recomendado)**
```bash
cd server
./start.bat
```

#### **Método 2: Manual**
```bash
cd server

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências  
pip install -r requirements.txt

# Configurar credenciais
cp .env.example .env
# Editar .env com suas credenciais MT5
```

### ⚙️ **2. Configuração do .env**

```bash
# =============================================================================
# MetaTrader 5 Credentials (OBRIGATÓRIO)
# =============================================================================
USERCLEAR=1001585100                    # Seu login MT5
PASSCLEAR=sua_senha_mt5                 # Sua senha MT5
MT5_SERVER=ClearInvestimentos-CLEAR     # Servidor da corretora

# =============================================================================
# API Security (Autenticação dupla)
# =============================================================================
# BasicAuth para documentação (/docs)
DOCS_USERNAME=homelab                   # Usuário para acessar docs
DOCS_PASSWORD=homelab123                # Senha para acessar docs

# API Keys para endpoints (separadas por vírgula)
API_KEYS=cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4

# =============================================================================
# Server Configuration
# =============================================================================
HOST=0.0.0.0                           # IP do servidor
PORT=8000                              # Porta do servidor
LOG_LEVEL=info                         # Nível de log
```

### 🚀 **3. Executar o Servidor**

```bash
cd server

# Opção 1: Script automático
./start.bat

# Opção 2: Direto com Python
python app.py

# Opção 3: Com uvicorn  
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 📊 **4. Verificar se Funcionou**

```bash
# ✅ Verificações básicas
curl http://localhost:8000/health        # Health check
curl http://localhost:8000/              # Info da API

# 📚 Acessar documentação (BasicAuth requerido)
# http://localhost:8000/docs
# Usuário: homelab
# Senha: homelab123
```

### 🔍 **5. Logs do Servidor**

```
✅ MetaTrader5 disponível
🚀 Iniciando MT5 Trading API...
✅ MT5 inicializado com sucesso  
✅ Login realizado: 1001585100
📊 Conta: SEU NOME
💰 Saldo: 10000.00
🔢 Alavancagem: 100x
🌟 API pronta para uso!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 📚 **6. Acessos do Servidor**

| Recurso | URL | Autenticação |
|---------|-----|--------------|
| **API Info** | `http://localhost:8000/` | ❌ Pública |
| **Health Check** | `http://localhost:8000/health` | ❌ Pública |
| **Documentação** | `http://localhost:8000/docs` | ✅ BasicAuth (homelab/homelab123) |
| **API Endpoints** | `http://localhost:8000/GetSymbols/` | ✅ API Key (AcessKey header) |

---

## 💻 Parte 2: Cliente (Consumer)

O cliente permite consumir a API de **outras máquinas** com interface clean e typehints.

### 📂 Estrutura do Cliente

```
client/
├── mt5_client/             # 📦 Pacote principal 
│   ├── domain/             # 🎯 Entidades e regras de negócio
│   ├── application/        # 📋 Casos de uso
│   ├── infrastructure/     # 🔧 HTTP adapters & config
│   └── presentation/       # 🖥️ Interface pública
├── examples/               # 📚 Exemplos práticos
├── requirements.txt        # 📦 Dependências do cliente
└── setup.py                # ⚙️ Instalação como pacote
```

### 🚀 **1. Instalação do Cliente**

```bash
cd client

# Instalar dependências
pip install -r requirements.txt

# Opção: Instalar como pacote editável
pip install -e .
```

### ⚙️ **2. Configuração do Cliente**

#### **Método 1: Via código**
```python
from mt5_client import MT5TradingClient

client = MT5TradingClient(
    api_url="http://localhost:8000",  # URL do servidor
    api_key="cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4",
    timeout=30
)
```

#### **Método 2: Via .env (cliente)**
```bash
# Criar .env no diretório client/
echo "MT5_API_URL=http://localhost:8000" > .env
echo "MT5_API_KEY=cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4" >> .env
```

### 🚀 **3. Executar o Cliente**

#### **Exemplo Básico**
```bash
cd client
python examples/exemplo_basico.py
```

#### **Exemplo com Análise**
```bash
python examples/exemplo_analise_mercado.py
```

#### **Menu Interativo**
```bash
python examples/executar_exemplos.py
```

### 💡 **4. Uso Programático**

#### **Interface Assíncrona (Recomendada)**
```python
import asyncio
from mt5_client import MT5TradingClient

async def main():
    # Criar cliente
    client = MT5TradingClient(
        api_url="http://servidor-mt5:8000",
        api_key="sua-api-key-aqui"
    )
    
    async with client:
        # Verificar conexão
        health = await client.check_health()
        print(f"Status: {health.status}")
        
        # Obter símbolos
        symbols = await client.get_symbols()
        print(f"Símbolos: {len(symbols)}")
        
        # Dados de mercado
        eurusd_data = await client.get_market_data("EURUSD")
        print(f"EURUSD: {eurusd_data.current_price}")

# Executar
asyncio.run(main())
```

#### **Interface Síncrona (Simples)**
```python
from mt5_client import SimpleMT5Client, create_simple_client

# Método 1: Classe direta
client = SimpleMT5Client("http://localhost:8000")
symbols = client.get_symbols()
print(f"Símbolos disponíveis: {len(symbols)}")

# Método 2: Factory function
with create_simple_client() as client:  # Usa .env automaticamente
    health = client.check_health()
    print(f"API Status: {health.status}")
```

### 📊 **5. Casos de Uso Completos**

#### **Trading Completo**
```python
async def exemplo_trading_completo():
    client = MT5TradingClient(api_url="http://localhost:8000")
    
    async with client:
        # 1. Verificar saúde
        health = await client.check_health()
        if not health.mt5_connected:
            print("❌ MT5 não conectado!")
            return
            
        # 2. Análise de mercado
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        analysis = await client.analyze_multiple_markets(symbols)
        
        for symbol_data in analysis:
            print(f"{symbol_data.symbol}: {symbol_data.trend_analysis}")
            
        # 3. Obter dados históricos
        eurusd_history = await client.get_tickers(
            symbol="EURUSD",
            date_from="2024-01-01 00:00:00",
            date_to="2024-01-31 23:59:59", 
            timeframe=1  # M1
        )
        
        print(f"Histórico EURUSD: {len(eurusd_history)} barras")
```

#### **Monitoramento em Tempo Real**
```python
async def monitorar_mercado():
    client = MT5TradingClient(api_url="http://localhost:8000")
    
    async with client:
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        
        while True:
            # Obter variação percentual
            changes = await client.get_symbols_pct_change(symbols)
            
            for change in changes:
                status = "📈" if change.pct_change > 0 else "📉"
                print(f"{status} {change.symbol}: {change.pct_change:.4f}%")
            
            await asyncio.sleep(10)  # Atualizar a cada 10s
```

---

## 🔧 Configurações Avançadas

### 🔐 **Segurança em Produção**

#### **Servidor**
```bash
# .env para produção
DOCS_USERNAME=seu_usuario_seguro
DOCS_PASSWORD=senha_super_segura_123!
API_KEYS=chave-super-longa-e-criptografada-xyz123,segunda-chave-para-backup

# Configurações SSL
FORCE_HTTPS=true
SECURE_COOKIES=true
ENVIRONMENT=production
```

#### **Cliente**
```python
# Para produção com HTTPS
client = MT5TradingClient(
    api_url="https://seu-servidor-mt5.com:8443",
    api_key="chave-super-segura-aqui",
    timeout=60,  # Timeout maior para produção
    max_retries=5,  # Mais tentativas
    ssl_verify=True  # Verificar certificados SSL
)
```

### ⚡ **Performance**

#### **Configurações do Servidor**
```bash
# Para alta performance
LOG_LEVEL=warning  # Menos logs
HOST=0.0.0.0
PORT=8000

# Usar com gunicorn para produção
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### **Configurações do Cliente**
```python
# Cliente otimizado
client = MT5TradingClient(
    api_url="http://localhost:8000",
    timeout=10,          # Timeout menor
    max_retries=3,       # Menos tentativas
    connection_pool=20,  # Pool de conexões
    log_level="WARNING"  # Menos logs
)
```

### 🌐 **Rede e Deploy**

#### **Docker (Servidor)**
```dockerfile
# Dockerfile para o servidor
FROM python:3.11-slim

WORKDIR /app
COPY server/ .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "app.py"]
```

#### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  mt5-api:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - USERCLEAR=${USERCLEAR}
      - PASSCLEAR=${PASSCLEAR}
    volumes:
      - ./server/.env:/app/.env
```

---

## 📊 Exemplos de Uso

### 🎯 **Cenários Reais**

#### **1. Bot de Trading Simples**
```python
# bot_trading.py
import asyncio
from mt5_client import MT5TradingClient

class TradingBot:
    def __init__(self):
        self.client = MT5TradingClient("http://localhost:8000")
    
    async def run(self):
        async with self.client:
            while True:
                # Analisar mercado
                eurusd = await self.client.get_market_data("EURUSD")
                
                # Estratégia simples
                if eurusd.trend == "bullish":
                    print("📈 Sinal de compra para EURUSD")
                elif eurusd.trend == "bearish":  
                    print("📉 Sinal de venda para EURUSD")
                
                await asyncio.sleep(60)  # Verificar a cada minuto

# Executar bot
bot = TradingBot()
asyncio.run(bot.run())
```

#### **2. Dashboard de Monitoramento**
```python
# dashboard.py
import asyncio
from mt5_client import MT5TradingClient

async def dashboard():
    client = MT5TradingClient("http://localhost:8000")
    
    async with client:
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
        
        print("📊 DASHBOARD MT5 TRADING")
        print("=" * 50)
        
        while True:
            # Limpar tela (Windows)
            import os
            os.system('cls')
            
            # Header
            print("📊 MT5 TRADING DASHBOARD")
            print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            
            # Dados de mercado
            for symbol in symbols:
                data = await client.get_market_data(symbol)
                change = await client.get_symbol_pct_change([symbol])
                
                trend_icon = "📈" if change[0].pct_change > 0 else "📉"
                print(f"{trend_icon} {symbol}: {data.current_price:.5f} ({change[0].pct_change:+.2f}%)")
            
            await asyncio.sleep(5)

asyncio.run(dashboard())
```

#### **3. Análise Técnica Avançada**
```python
# analise_tecnica.py
from mt5_client import MT5TradingClient
import numpy as np

async def analise_avancada():
    client = MT5TradingClient("http://localhost:8000")
    
    async with client:
        # Obter dados históricos
        tickers = await client.get_tickers(
            symbol="EURUSD",
            date_from="2024-01-01 00:00:00",
            date_to="2024-12-31 23:59:59",
            timeframe=16385  # H1
        )
        
        # Extrair preços de fechamento
        closes = np.array([t.close for t in tickers])
        
        # Calcular médias móveis
        sma_20 = np.convolve(closes, np.ones(20)/20, mode='valid')
        sma_50 = np.convolve(closes, np.ones(50)/50, mode='valid')
        
        # Verificar cruzamento
        if len(sma_20) > 0 and len(sma_50) > 0:
            if sma_20[-1] > sma_50[-1]:
                print("📈 SMA 20 acima da SMA 50 - Tendência de alta")
            else:
                print("📉 SMA 20 abaixo da SMA 50 - Tendência de baixa")

asyncio.run(analise_avancada())
```

---

## 🛡️ Segurança

### 🔐 **Sistema de Autenticação Dupla**

#### **1. BasicAuth para Documentação**
- **URL**: `/docs`, `/redoc`, `/openapi.json`
- **Credenciais**: Configuráveis via `.env`
- **Padrão**: `homelab` / `homelab123`
- **Uso**: Proteger documentação Swagger/ReDoc

#### **2. API Keys para Endpoints**  
- **Header**: `AcessKey` ou `Authorization`
- **Formato**: String longa criptografada
- **Configuração**: Via `.env` (múltiplas chaves suportadas)
- **Uso**: Proteger todos os endpoints da API

### 🛡️ **Práticas de Segurança**

```bash
# ✅ FAZER
- Alterar credenciais padrão antes do deploy
- Usar HTTPS em produção
- Rotacionar API keys periodicamente  
- Monitorar logs de acesso
- Implementar rate limiting

# ❌ NÃO FAZER
- Committar arquivo .env no git
- Usar credenciais padrão em produção
- Expor API sem autenticação
- Usar HTTP em produção
- Compartilhar API keys por e-mail
```

### 🔒 **Configuração Segura**

```bash
# .env para produção
DOCS_USERNAME=admin_$(date +%s)        # Username único
DOCS_PASSWORD=$(openssl rand -base64 32)  # Senha aleatória  
API_KEYS=$(openssl rand -hex 64),$(openssl rand -hex 64)  # Chaves aleatórias

# Configurações SSL
FORCE_HTTPS=true
SECURE_COOKIES=true
ENVIRONMENT=production

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

---

## 🐛 Troubleshooting

### ❌ **Problemas Comuns**

#### **1. Servidor não inicia**
```bash
# Sintomas
❌ Erro: Python não está instalado
❌ ModuleNotFoundError: No module named 'MetaTrader5'
❌ Connection refused on port 8000

# Soluções
✅ Instalar Python 3.8+
✅ pip install -r requirements.txt
✅ Verificar se porta 8000 está livre
✅ Executar start.bat como administrador
```

#### **2. MT5 não conecta**
```bash  
# Sintomas
❌ Falha ao inicializar MT5
❌ Falha no login MT5
❌ MT5 não está conectado no servidor

# Soluções  
✅ Verificar se MT5 está instalado
✅ Confirmar credenciais no .env
✅ Testar login manual no MT5
✅ Verificar se servidor da corretora está online
```

#### **3. Cliente não conecta**
```bash
# Sintomas
❌ Connection timeout
❌ API key inválida
❌ 401 Unauthorized

# Soluções
✅ Verificar URL do servidor (http://ip:porta)
✅ Confirmar API key no cliente
✅ Testar health check: curl http://localhost:8000/health
✅ Verificar firewall/rede entre client e server
```

#### **4. Documentação não carrega**
```bash
# Sintomas
❌ 401 Unauthorized no /docs
❌ Prompt de login não aparece
❌ Credenciais não funcionam

# Soluções
✅ Usar credenciais: homelab / homelab123
✅ Limpar cache do browser
✅ Tentar modo incógnito
✅ Verificar DOCS_USERNAME e DOCS_PASSWORD no .env
```

### 🔧 **Diagnósticos**

#### **Verificar Servidor**
```bash
# Testar componentes
curl http://localhost:8000/health                    # API básica
curl http://localhost:8000/                          # Info geral

# Com autenticação
curl -H "AcessKey: sua-chave" http://localhost:8000/GetSymbols/

# Logs detalhados
python app.py --log-level debug
```

#### **Verificar Cliente**
```python
# Teste de conectividade
import asyncio
from mt5_client import MT5TradingClient

async def test():
    client = MT5TradingClient("http://localhost:8000")
    
    try:
        async with client:
            health = await client.check_health()
            print(f"✅ Conexão OK: {health.status}")
    except Exception as e:
        print(f"❌ Erro: {e}")

asyncio.run(test())
```

### 📞 **Suporte e Logs**

#### **Logs do Servidor**
```bash
# Localização dos logs
server/logs/app.log              # Logs da aplicação
server/logs/mt5.log              # Logs do MetaTrader5
server/logs/access.log           # Logs de acesso HTTP

# Visualizar logs em tempo real
tail -f server/logs/app.log
```

#### **Logs do Cliente**
```python
# Ativar debug no cliente
import logging
logging.basicConfig(level=logging.DEBUG)

client = MT5TradingClient(
    api_url="http://localhost:8000",
    log_level="DEBUG"  # Logs detalhados
)
```

#### **Contatos**
- 🐛 **Issues**: Reportar problemas técnicos
- 📚 **Documentação**: Consultar READMEs específicos
- 💡 **Melhorias**: Sugestões e feedback

---

## 📝 Resumo de Comandos

### 🖥️ **Servidor**
```bash
cd server
./start.bat                     # Iniciar servidor (automático)
python app.py                   # Iniciar servidor (manual)
curl http://localhost:8000/health  # Testar servidor
```

### 💻 **Cliente** 
```bash
cd client
pip install -r requirements.txt  # Instalar deps
python examples/exemplo_basico.py  # Testar cliente
python examples/executar_exemplos.py  # Menu interativo
```

### 🔧 **Configuração**
```bash
# Servidor
cp server/.env.example server/.env  # Configurar servidor
# Editar server/.env com suas credenciais

# Cliente (opcional)
echo "MT5_API_URL=http://localhost:8000" > client/.env
echo "MT5_API_KEY=sua-chave" >> client/.env
```

---

## 🎉 Conclusão

Este projeto oferece uma **solução completa de trading** com MetaTrader 5:

- ✅ **Servidor robusto** com autenticação dupla
- ✅ **Cliente flexível** com Clean Architecture  
- ✅ **Documentação completa** e exemplos práticos
- ✅ **Segurança em produção** e performance otimizada

**🚀 Comece agora:** Execute `server/start.bat` e `client/examples/exemplo_basico.py`

---

**📄 Licença:** MIT  
**🐍 Versão Python:** 3.8+  
**📊 MetaTrader:** 5.0+  
**⚡ FastAPI:** 0.100+  
