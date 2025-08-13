
# Publicar na Internet (Gratuito)

> Duas opções fáceis e grátis para mostrar aos seus clientes: **Streamlit Community Cloud** ou **Hugging Face Spaces**.

## Opção A) Streamlit Community Cloud (recomendado)
1. Crie um repositório **GitHub** e envie todos os arquivos desta pasta.
2. Acesse: https://share.streamlit.io/
3. Clique em **'New app'** → selecione seu repositório e o arquivo principal `app.py`.
4. Clique em **Deploy**. Pronto! O link público aparece na direita (compartilhe com seus clientes).

**Dicas**  
- Se precisar de segredos (APIs etc.), use **'Manage app' → 'Settings' → 'Secrets'**.  
- Logs em **'Manage app' → 'Logs'**.

## Opção B) Hugging Face Spaces (Streamlit)
1. Crie uma conta em: https://huggingface.co/
2. Clique em **'Create new Space'** → Template **Streamlit**.
3. Envie os arquivos pelo Git (ou arraste na UI web): `app.py`, `requirements.txt`, pasta `assets/`, `branding.json` etc.
4. Aguarde o build automático → o Space ficará **online** com URL pública.

**Requisitos**  
- `app.py` na raiz do repositório.  
- `requirements.txt` com as dependências.  
- Pastas `assets/` e arquivos de branding devem estar versionados.

## Personalização de Marca
- Edite `branding.json`:
```json
{
  "brand_name": "Seu Estúdio",
  "brand_tagline": "Slogan aqui",
  "primary_color": "#6C5CE7",
  "secondary_color": "#A29BFE",
  "accent_color": "#22c55e"
}
```
- Substitua `assets/logo.svg` e `assets/splash.svg` pelos seus (mesmo nome de arquivo).

## Estrutura de Arquivos
```
app.py
requirements.txt
branding.json
assets/
  ├─ theme.css
  ├─ logo.svg
  └─ splash.svg
ONECLICK_README.md
START_IntelliDash_Windows.bat
START_IntelliDash_macOS.command
start_intellidash_linux.sh
```

> Para demonstração online **não** é necessário usar os scripts de 1‑clique; eles são úteis apenas se quiser rodar localmente.
