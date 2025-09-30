"""
Exceções do domínio MT5 Client
"""


class MT5ClientError(Exception):
    """Exceção base para erros do cliente MT5"""
    pass


class ConnectionError(MT5ClientError):
    """Erro de conexão com a API"""
    pass


class AuthenticationError(MT5ClientError):
    """Erro de autenticação"""
    pass


class ValidationError(MT5ClientError):
    """Erro de validação de dados"""
    pass


class ApiError(MT5ClientError):
    """Erro genérico da API"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response