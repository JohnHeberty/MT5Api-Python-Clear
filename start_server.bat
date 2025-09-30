@echo off
REM =================================================================
REM MT5 Trading API Server - Script de Inicialização
REM =================================================================

echo 🚀 MT5 Trading API Server - Inicializando...
echo =============================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python não encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Ir para o diretório do servidor
cd /d "%~dp0server"

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo 📦 Criando ambiente virtual Python...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado com sucesso
)

REM Ativar ambiente virtual
echo 🔌 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo 📈 Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências
echo 📦 Instalando dependências...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

REM Verificar se MetaTrader5 está disponível
echo 🔍 Verificando MetaTrader5...
python -c "import MetaTrader5; print('✅ MetaTrader5 OK')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚠️ MetaTrader5 não disponível - servidor rodará em modo simulação
)

REM Verificar se arquivo .env existe
if not exist ".env" (
    echo ⚠️ Arquivo .env não encontrado! Usando configuração padrão.
    echo 💡 Crie um arquivo .env com suas credenciais MT5 para produção.
)

echo.
echo 🌟 Tudo pronto! Iniciando servidor MT5 API...
echo =============================================
echo 📚 Documentação: http://localhost:8000/docs
echo � Acesso Docs  : homelab / john.1998  
echo �🔍 Health Check : http://localhost:8000/health
echo 🔑 Auth Info    : http://localhost:8000/auth-info
echo 💡 API Endpoints: Requerem header AcessKey ou Authorization
echo ⚡ Pressione Ctrl+C para parar o servidor
echo =============================================
echo.

REM Iniciar servidor
python app.py

REM Pausar se houver erro
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Servidor encerrado com erro: %ERRORLEVEL%
    pause
)

echo.
echo 👋 Servidor MT5 API encerrado.
pause