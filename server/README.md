# 🚀 MT5 Trading API Server

Servidor de API para MetaTrader 5 com FastAPI, otimizada para performance e **segura para produção**.

## 🔐 Sistema de Autenticação Dupla

### 📚 Documentação (BasicAuth)
- **URL**: `http://localhost:8000/docs`
- **Usuário**: `homelab`  
- **Senha**: `john.1998`
- **Proteção**: Acesso ao Swagger UI e ReDoc

### 🔑 API Endpoints (API Key)
- **Header**: `AcessKey` ou `Authorization`
- **Chave padrão**: `cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4`
- **Proteção**: Todos os endpoints da API

## ✨ **EXECUÇÃO SUPER SIMPLES**

### **Um único comando para tudo:**

```bash
start_server.bat
```

**Isso fará:**
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências  
- ✅ Conectar ao MetaTrader 5
- ✅ Iniciar servidor na porta 8000
- ✅ Abrir documentação automática

### 🌐 **Acesso Imediato**
- **API Principal**: http://localhost:8000
- **Documentação Interativa**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 🏗️ **Arquitetura Clean + SOLID**

Este projeto implementa **Clean Architecture** com princípios **SOLID**:

- **🔄 Clean Architecture**: Separação clara entre camadas
- **🎯 SOLID Principles**: Cada classe tem responsabilidade única  
- **📊 Auto Documentação**: OpenAPI/Swagger completo
- **🔐 Autenticação**: Middleware de segurança robusto
- **⚡ MetaTrader5**: Integração real e funcional
- **🛡️ Error Handling**: Tratamento global de exceções
- **🎨 Performance**: Async/await otimizado

### 📁 **Estrutura Simplificada**

```
OLD_MT5Api/
├── app.py              # ← ARQUIVO PRINCIPAL (tudo integrado)
├── start.bat           # ← SCRIPT DE EXECUÇÃO ÚNICA
├── requirements.txt    # ← DEPENDÊNCIAS (arquivo único)
├── .env                # ← SUAS CREDENCIAIS MT5
├── src/                # ← Clean Architecture (preservada)
└── old/                # ← Código legado (backup)
```

### � **Configuração Rápida**

1. **Configure suas credenciais no `.env`:**
```env
USERCLEAR=seu_login_mt5
PASSCLEAR=sua_senha_mt5
```

2. **Execute:**
```bash
start.bat
```

**PRONTO!** ✅

### 📖 Documentação da API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### 🔑 Autenticação

Todas as rotas protegidas requerem uma chave API no header:

```bash
curl -H "AcessKey: sua-chave-api-aqui" \
     -X POST http://localhost:8000/api/v1/market-data/symbols
```

### 📊 Endpoints Principais

#### Market Data
- `POST /api/v1/market-data/symbols` - Listar todos os símbolos
- `POST /api/v1/market-data/symbol-info` - Informações de um símbolo
- `POST /api/v1/market-data/tickers` - Dados históricos por período
- `POST /api/v1/market-data/tickers-by-count` - Últimas N velas
- `POST /api/v1/market-data/symbols-percent-change` - Variação percentual

#### Trading
- `POST /api/v1/trading/open-position` - Abrir posição
- `POST /api/v1/trading/close-position` - Fechar posição
- `GET /api/v1/trading/positions` - Listar posições abertas

### 🛠️ Princípios SOLID Implementados

#### Single Responsibility Principle (SRP)
- Cada use case tem uma única responsabilidade
- Controllers separados por domínio (MarketData, Trading)
- Middleware específico para cada preocupação (Auth, CORS, Logging)

#### Open/Closed Principle (OCP)
- Interfaces permitem extensão sem modificação
- Novos adaptadores podem ser adicionados facilmente

#### Liskov Substitution Principle (LSP)
- Todas as implementações respeitam os contratos das interfaces
- Adaptadores são intercambiáveis

#### Interface Segregation Principle (ISP)
- Interfaces pequenas e específicas (ISymbolRepository, IMarketDataRepository)
- Clientes dependem apenas do que precisam

#### Dependency Inversion Principle (DIP)
- Classes de alto nível não dependem de implementações
- Container de DI gerencia todas as dependências

### 🔧 Configuração

As configurações são gerenciadas através de variáveis de ambiente:

```env
# MT5 Credentials
USERCLEAR=1001585107
PASSCLEAR=mn9xyQw@
MT5_SERVER=ClearInvestimentos-CLEAR

# API Configuration
API_KEYS=sua-chave-api-1,sua-chave-api-2
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

### 🧪 Testes

```bash
# Executar testes unitários
pytest tests/

# Executar com cobertura
pytest --cov=src tests/
```

### 🐳 Docker

```bash
# Construir imagem
docker build -t mt5-api .

# Executar container
docker run -p 8000:8000 --env-file .env mt5-api
```

### 📈 Performance

- **Async/Await**: Operações não-bloqueantes
- **Connection Pooling**: Reutilização de conexões MT5
- **Request Timeout**: Proteção contra operações lentas
- **Memory Management**: Uso eficiente de recursos

### 🔒 Segurança

- **API Key Authentication**: Autenticação baseada em chave
- **CORS Policy**: Política de origem configurável
- **Security Headers**: Headers de segurança automáticos
- **Input Validation**: Validação rigorosa com Pydantic
- **Error Sanitization**: Sanitização de erros sensíveis

### 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

### 🆘 Suporte

Para suporte técnico ou dúvidas:
- 📧 Email: support@mt5api.com
- 📚 Documentação: `/docs`
- 🐛 Issues: GitHub Issues