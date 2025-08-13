@echo off
setlocal
title CRM IntelliDash - Iniciando
cd /d "%~dp0"
echo [1/4] Verificando ambiente...
if not exist .venv (
  echo [2/4] Criando ambiente virtual...
  py -3 -m venv .venv
)
echo [3/4] Ativando ambiente e instalando dependencias...
call .venv\Scripts\activate
python -m pip install --upgrade pip > nul
pip install -r requirements.txt
echo [4/4] Iniciando aplicativo no navegador...
python -m streamlit run app.py
