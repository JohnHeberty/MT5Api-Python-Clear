# 🔐 Sistema de Autenticação Flexível - MT5 Trading API

## 📋 Como Funciona

A API agora possui **autenticação condicional** baseada na configuração das `API_KEYS`:

### ✅ **Quando API_KEYS tem valores**
```env
API_KEYS=cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4
```
- 🔒 **Autenticação OBRIGATÓRIA** para endpoints da API
- ❌ Requisições sem header `AcessKey` são **rejeitadas** (401)
- ✅ Apenas chaves válidas são aceitas

### 🆓 **Quando API_KEYS está vazia**
```env
API_KEYS=
# ou
# API_KEYS=
```
- 🔓 **Autenticação OPCIONAL** para endpoints da API
- ✅ Requisições sem header `AcessKey` são **aceitas**
- ✅ Headers de API key são **ignorados** se fornecidos

## 🎯 Endpoints Sempre Públicos
Independente da configuração de `API_KEYS`:
- `GET /` - Página inicial
- `GET /health` - Status da API
- `GET /auth-info` - Informações de autenticação

## 📚 Documentação Sempre Protegida
A documentação **sempre** requer BasicAuth:
- `GET /docs` - Swagger UI (homelab/john.1998)
- `GET /redoc` - ReDoc (homelab/john.1998)
- `GET /openapi.json` - Schema OpenAPI (homelab/john.1998)

## ⚙️ Configuração

### Arquivo `.env`
```env
# Para ATIVAR autenticação (produção recomendada)
API_KEYS=cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4

# Para DESATIVAR autenticação (desenvolvimento/teste)
API_KEYS=

# Documentação sempre protegida
DOCS_USERNAME=homelab
DOCS_PASSWORD=john.1998
```

## 🧪 Como Testar

### 1. **Verificar Status Atual**
```bash
curl http://localhost:8000/auth-info
```

**Resposta com auth ativada:**
```json
{
    "api_authentication": {
        "enabled": true,
        "status": "ATIVADA - API Keys configuradas",
        "configured_keys": 1
    }
}
```

**Resposta com auth desativada:**
```json
{
    "api_authentication": {
        "enabled": false,
        "status": "DESATIVADA - Nenhuma API Key configurada",
        "configured_keys": 0
    }
}
```

### 2. **Testar Endpoints da API**

**Com autenticação ativada:**
```bash
# ❌ Falha sem header
curl -X POST http://localhost:8000/GetSymbols/

# ✅ Sucesso com header válido
curl -X POST http://localhost:8000/GetSymbols/ \
     -H "AcessKey: cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4"
```

**Com autenticação desativada:**
```bash
# ✅ Sucesso sem header
curl -X POST http://localhost:8000/GetSymbols/

# ✅ Sucesso com header (ignorado)
curl -X POST http://localhost:8000/GetSymbols/ \
     -H "AcessKey: qualquer-coisa"
```

## 💻 Exemplos de Código

### Python com autenticação ativada
```python
import requests

headers = {
    'AcessKey': 'cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4',
    'Content-Type': 'application/json'
}

response = requests.post('http://localhost:8000/GetSymbols/', headers=headers)
```

### Python com autenticação desativada
```python
import requests

# Headers opcionais quando auth desativada
response = requests.post('http://localhost:8000/GetSymbols/')
```

### JavaScript/Fetch
```javascript
// Com autenticação ativada
const headers = {
    'AcessKey': 'cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4',
    'Content-Type': 'application/json'
};

fetch('http://localhost:8000/GetSymbols/', {
    method: 'POST',
    headers: headers
});

// Com autenticação desativada
fetch('http://localhost:8000/GetSymbols/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
});
```

## 🔄 Alternar Modos

### **Ativar Autenticação** (Produção)
1. Editar `server/.env`:
   ```env
   API_KEYS=cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4
   ```
2. Reiniciar servidor
3. ✅ Endpoints requerem API key

### **Desativar Autenticação** (Desenvolvimento)
1. Editar `server/.env`:
   ```env
   API_KEYS=
   ```
2. Reiniciar servidor
3. ✅ Endpoints funcionam sem API key

## 🛡️ Recomendações de Segurança

### 🏭 **Produção**
- ✅ **SEMPRE** configurar `API_KEYS` com valores seguros
- ✅ Usar HTTPS em domínio público
- ✅ Alterar credenciais BasicAuth padrão
- ✅ Restringir acesso por IP se possível

### 🧪 **Desenvolvimento/Teste**
- ✅ Deixar `API_KEYS` vazia para testes simples
- ⚠️ **NUNCA** subir em produção sem API keys
- ✅ Usar localhost apenas

## 📊 Logs e Monitoramento

### Mensagens no Console
```bash
# Auth ativada
🔑 API Endpoints requerem header: AcessKey ou Authorization

# Auth desativada
🔓 API Endpoints: Autenticação desabilitada (API_KEYS vazia)
```

### Headers de Resposta
- `X-Process-Time`: Tempo de processamento
- Status codes apropriados (200, 401, etc.)

## 🆘 Troubleshooting

### **Problema**: Endpoints retornam 401 mesmo com auth desativada
**Solução**: 
1. Verificar `.env`: `API_KEYS=` (deve estar vazia)
2. Reiniciar servidor completamente
3. Verificar `/auth-info` para confirmar status

### **Problema**: API funciona sem key mesmo com auth ativada  
**Solução**:
1. Verificar `.env`: `API_KEYS=sua-chave` (deve ter valor)
2. Reiniciar servidor
3. Verificar `/auth-info` para confirmar status

### **Problema**: Documentação não carrega
**Solução**: BasicAuth sempre ativo - usar homelab/john.1998

---

✅ **Sistema flexível: Desenvolvimento sem friction, Produção com segurança!**