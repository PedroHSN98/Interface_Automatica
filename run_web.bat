@echo off
title AutoHub Pro - Interface Web
cd /d "%~dp0"

echo ================================================
echo   AutoHub Pro - Interface Web
echo ================================================
echo.

:: Ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Ambiente virtual ativado.
) else (
    echo [AVISO] Ambiente virtual nao encontrado.
    echo         Execute primeiro:
    echo           python -m venv .venv
    echo           .venv\Scripts\pip install -r requirements.txt
    echo.
)

:: Instala Flask se nao estiver instalado
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Instalando Flask...
    pip install flask -q
)

echo.
echo [INFO] Iniciando servidor...
echo [INFO] Acesse: http://localhost:5000
echo [INFO] Ctrl+C para encerrar
echo.

python web\server.py
pause
