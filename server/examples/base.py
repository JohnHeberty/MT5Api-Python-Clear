"""
MT5 API Examples - Base Classes
Implementação seguindo princípios SOLID
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import json
from datetime import datetime

# Single Responsibility Principle - Cada classe tem uma responsabilidade única
class ApiConfig:
    """Responsável pela configuração da API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "AcessKey": api_key
        }

class ApiClient:
    """Responsável pela comunicação HTTP com a API"""
    
    def __init__(self, config: ApiConfig):
        self.config = config
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fazer requisição POST para a API"""
        url = f"{self.config.base_url}/{endpoint.strip('/')}"
        
        try:
            response = requests.post(
                url,
                json=data,
                headers=self.config.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"OK": False, "Error": str(e)}
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """Fazer requisição GET para a API"""
        url = f"{self.config.base_url}/{endpoint.strip('/')}"
        
        try:
            response = requests.get(
                url,
                headers=self.config.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"OK": False, "Error": str(e)}

# Open/Closed Principle - Aberto para extensão, fechado para modificação
class BaseExample(ABC):
    """Classe base abstrata para todos os exemplos"""
    
    def __init__(self, client: ApiClient):
        self.client = client
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Executar o exemplo - deve ser implementado pelas subclasses"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Obter descrição do exemplo"""
        pass
    
    def format_response(self, response: Dict[str, Any]) -> str:
        """Formatar resposta de forma legível"""
        if response.get("OK"):
            return f"✅ Sucesso: {json.dumps(response.get('Resposta', {}), indent=2, ensure_ascii=False)}"
        else:
            return f"❌ Erro: {response.get('Error', 'Erro desconhecido')}"
    
    def run(self) -> None:
        """Executar exemplo e exibir resultado"""
        print(f"\n🚀 {self.get_description()}")
        print("=" * 50)
        
        try:
            result = self.execute()
            print(self.format_response(result))
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")

# Liskov Substitution Principle - Subclasses devem ser substituíveis pela classe base
class HealthCheckExample(BaseExample):
    """Exemplo básico de health check (sem autenticação)"""
    
    def execute(self) -> Dict[str, Any]:
        return self.client.get("/health")
    
    def get_description(self) -> str:
        return "Health Check - Verificar status da API"

# Interface Segregation Principle - Interfaces específicas são melhores que genéricas
class ApiKeyRequiredMixin:
    """Mixin para exemplos que requerem API key"""
    
    def validate_api_key(self) -> bool:
        """Validar se API key está configurada"""
        return bool(self.client.config.api_key)
    
    def run(self) -> None:
        """Override para verificar API key antes de executar"""
        if not self.validate_api_key():
            print("⚠️  API Key não configurada. Configure API_KEY no arquivo config.py")
            return
        super().run()

# Dependency Inversion Principle - Depender de abstrações, não de implementações concretas
class ExampleRunner:
    """Responsável por executar exemplos"""
    
    def __init__(self, examples: list[BaseExample]):
        self.examples = examples
    
    def run_all(self) -> None:
        """Executar todos os exemplos"""
        print("🎯 Executando todos os exemplos da MT5 API")
        print("=" * 60)
        
        for example in self.examples:
            example.run()
            print("\n" + "-" * 50)
    
    def run_single(self, index: int) -> None:
        """Executar um exemplo específico"""
        if 0 <= index < len(self.examples):
            self.examples[index].run()
        else:
            print(f"❌ Índice inválido. Use 0-{len(self.examples)-1}")
    
    def list_examples(self) -> None:
        """Listar todos os exemplos disponíveis"""
        print("📋 Exemplos disponíveis:")
        for i, example in enumerate(self.examples):
            print(f"  {i}: {example.get_description()}")