#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "[1/4] Verificando ambiente..."
if [ ! -d ".venv" ]; then
  echo "[2/4] Criando ambiente virtual..."
  python3 -m venv .venv
fi
echo "[3/4] Ativando ambiente e instalando dependencias..."
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt
echo "[4/4] Iniciando aplicativo no navegador..."
python -m streamlit run app.py
