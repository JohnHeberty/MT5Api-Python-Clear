# 📚 MT5 Trading API - Exemplos SOLID

Esta pasta contém exemplos completos de uso da MT5 Trading API, implementados seguindo rigorosamente os **princípios SOLID**.

## 🎯 **Estrutura dos Exemplos**

### **📁 Arquivos Principais:**

```
example/
├── base.py                           # 🏗️ Classes base (SOLID)
├── config.py                        # ⚙️ Configurações
├── run_all_examples.py              # 🚀 Executar todos
├── get_symbols_example.py           # 📊 GetSymbols
├── get_symbol_info_example.py       # 🔍 GetSymbolInfo
├── get_tickers_example.py           # 📈 GetTickers
├── get_tickers_pos_example.py       # 📉 GetTickersPos
├── get_symbols_pct_change_example.py # 📊 GetSymbolsPctChange
└── README.md                        # 📚 Este arquivo
```

## 🏗️ **Princípios SOLID Aplicados**

### **🎯 Single Responsibility Principle (SRP)**
- **`ApiConfig`**: Responsável apenas pela configuração
- **`ApiClient`**: Responsável apenas pela comunicação HTTP  
- **`BaseExample`**: Responsável apenas pela estrutura base de exemplos
- **Cada exemplo`**: Demonstra apenas um endpoint específico

### **🔓 Open/Closed Principle (OCP)**
- **Classes extensíveis**: Novos exemplos podem ser adicionados sem modificar código existente
- **`MultiSymbolInfoExample`**: Estende funcionalidade sem modificar `GetSymbolInfoExample`
- **`MarketSentimentExample`**: Estende `GetSymbolsPctChangeExample` para análise avançada

### **🔄 Liskov Substitution Principle (LSP)**
- **Todas as subclasses** de `BaseExample` são intercambiáveis
- **`ExampleRunner`** funciona com qualquer implementação de `BaseExample`
- **Polimorfismo perfeito** em `format_response()` e `execute()`

### **🔌 Interface Segregation Principle (ISP)**
- **`ApiKeyRequiredMixin`**: Interface específica para autenticação
- **Interfaces pequenas**: Cada classe implementa apenas o que precisa
- **Métodos focados**: `execute()`, `get_description()`, `format_response()`

### **⚡ Dependency Inversion Principle (DIP)**
- **Exemplos dependem de abstrações**: `ApiClient` (não implementação concreta)
- **Injeção de dependência**: `ApiClient` injetado nos construtores
- **Factory Pattern**: `create_all_examples()` centraliza criação

## 🚀 **Como Executar**

### **📋 Pré-requisitos:**
```bash
# Instalar dependências
pip install requests

# Verificar se a API está rodando
curl http://localhost:8000/health
```

### **⚙️ Configuração:**
1. **Edite `config.py`** para configurar sua API key
2. **Verifique URL da API** (padrão: http://localhost:8000)

### **🎯 Execução:**

#### **1. Executar todos os exemplos:**
```bash
cd example
python run_all_examples.py
```

#### **2. Executar exemplo específico:**
```bash
# GetSymbols
python get_symbols_example.py

# GetSymbolInfo
python get_symbol_info_example.py

# GetTickers  
python get_tickers_example.py

# GetTickersPos
python get_tickers_pos_example.py

# GetSymbolsPctChange
python get_symbols_pct_change_example.py
```

## 📊 **Descrição dos Exemplos**

### **🔍 GetSymbols (`get_symbols_example.py`)**
- **Objetivo**: Listar todos os símbolos disponíveis
- **Demonstra**: SRP, formatação customizada
- **Retorna**: Lista completa com detalhes dos símbolos

### **📊 GetSymbolInfo (`get_symbol_info_example.py`)**
- **Objetivo**: Informações detalhadas de símbolos
- **Exemplos**: Símbolo único + múltiplos símbolos
- **Demonstra**: OCP (extensibilidade), LSP (substituição)

### **📈 GetTickers (`get_tickers_example.py`)**
- **Objetivo**: Cotações históricas por período
- **Exemplos**: Período específico + comparação de timeframes
- **Demonstra**: DIP (injeção), análise estatística

### **📉 GetTickersPos (`get_tickers_pos_example.py`)**
- **Objetivo**: Últimas N cotações
- **Exemplos**: Cotações detalhadas + múltiplos símbolos
- **Demonstra**: ISP (interfaces), formatação rica

### **📊 GetSymbolsPctChange (`get_symbols_pct_change_example.py`)**
- **Objetivo**: Variação percentual de símbolos
- **Exemplos**: Variação simples + análise de sentimento
- **Demonstra**: Todos os princípios SOLID

## 🎨 **Padrões de Projeto Utilizados**

### **🏭 Factory Pattern**
- **`create_all_examples()`**: Centraliza criação de exemplos
- **Facilita manutenção** e adição de novos exemplos

### **🎭 Strategy Pattern**
- **`format_response()`**: Diferentes estratégias de formatação
- **Cada exemplo** tem sua própria estratégia de exibição

### **🔌 Dependency Injection**
- **Construtores recebem dependências** (`ApiClient`)
- **Facilita testes** e reutilização

### **📦 Mixin Pattern**
- **`ApiKeyRequiredMixin`**: Funcionalidade reutilizável
- **Composição ao invés de herança** complexa

## 🧪 **Estrutura de Testes (Conceitual)**

### **Como testar seguindo SOLID:**

```python
# Mock do ApiClient para testes
class MockApiClient(ApiClient):
    def post(self, endpoint, data):
        return {"OK": True, "Resposta": {"mock": "data"}}

# Teste de exemplo
def test_get_symbols():
    mock_client = MockApiClient(ApiConfig("", ""))
    example = GetSymbolsExample(mock_client)
    result = example.execute()
    assert result["OK"] == True
```

## 🔧 **Extensibilidade**

### **Para adicionar novos exemplos:**

1. **Herde de `BaseExample`**:
```python
class MeuNovoExample(BaseExample):
    def execute(self):
        # Sua implementação
    
    def get_description(self):
        return "Meu novo endpoint"
```

2. **Use mixins se necessário**:
```python
class MeuNovoExample(BaseExample, ApiKeyRequiredMixin):
    # Automaticamente valida API key
```

3. **Adicione ao factory**:
```python
def create_all_examples(client):
    return [
        # ... exemplos existentes
        MeuNovoExample(client)
    ]
```

## 📈 **Benefícios da Arquitetura SOLID**

### **✅ Manutenibilidade**
- **Mudanças isoladas**: Alterar um exemplo não afeta outros
- **Código claro**: Cada classe tem responsabilidade única

### **✅ Testabilidade** 
- **Injeção de dependência**: Facilita mocks
- **Interfaces pequenas**: Testes focados

### **✅ Extensibilidade**
- **Novos exemplos**: Fácil adição sem modificar código existente
- **Novas funcionalidades**: Mixins e herança

### **✅ Reutilização**
- **Classes base**: Reutilizáveis para novos endpoints
- **Padrões consistentes**: Formatação e estrutura

## 🎯 **Próximos Passos**

1. **Configure sua API key** em `config.py`
2. **Execute `run_all_examples.py`** para ver todos funcionando
3. **Explore exemplos individuais** para entender cada endpoint
4. **Crie seus próprios exemplos** seguindo os padrões SOLID

---

**🏗️ Arquitetura SOLID + 🚀 Performance + 📚 Documentação = Código Profissional! ✨**