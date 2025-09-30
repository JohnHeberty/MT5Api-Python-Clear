@echo off
REM Script único para configurar e executar a MT5 Trading API

echo ========================================
echo    MT5 Trading API - Setup e Start
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não está instalado ou não está no PATH
    echo Por favor, instale o Python primeiro
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Criar ambiente virtual se não existir
if not exist venv (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
)

echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo 📋 Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1

echo 📦 Instalando dependências...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    echo Tentando instalar pacotes essenciais individualmente...
    pip install fastapi uvicorn pydantic python-dotenv pandas
    pip install MetaTrader5
)

REM Verificar se .env existe
if not exist .env (
    echo ⚠️ Arquivo .env não encontrado
    if exist .env.example (
        echo 📋 Copiando .env.example para .env...
        copy .env.example .env >nul
        echo ⚠️ Configure suas credenciais no arquivo .env
        echo.
    )
)

echo.
echo ========================================
echo 🚀 Iniciando MT5 Trading API...
echo 📚 Documentação: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo ⚡ Pressione Ctrl+C para parar o servidor
echo ========================================
echo.

python app.py

pause