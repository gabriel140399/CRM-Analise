# GR-CRM IntelliDash

Simulador de funil de CRM para planejar campanhas de e-mail com base em metas de receita. Em vez de montar planilhas, você informa base, frequência e taxas do funil e o app mostra se a meta fecha, o que falta e quais alavancas mexer.

## Funcionalidades

- **Dashboard:** receita prevista, % de atingimento da meta, gap e funil completo (envios, aberturas, cliques, compras)
- **Funil inverso:** quantos envios, aberturas, cliques e compras são necessários para bater a meta
- **Taxa de recompra:** pedidos por cliente e percentual de pedidos repetidos
- **Plano inteligente:** busca a combinação de menor esforço entre volume de envios, CTR, CVR e ticket médio para atingir a meta, com exportação em CSV
- **Detratores e pontos positivos:** diagnóstico automático com recomendações práticas a partir de benchmarks de open rate, CTR, CVR e ticket
- **Presets:** salve e carregue cenários em JSON

## Tecnologias

Python · Streamlit · pandas · NumPy · Plotly

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Também há atalhos de inicialização para Windows (`START_IntelliDash_Windows.bat`), macOS (`START_IntelliDash_macOS.command`) e Linux (`start_intellidash_linux.sh`). Veja o `HOSTING_GUIDE.md` para publicar online.

## Personalização

As cores e o nome da marca podem ser alterados no arquivo `branding.json`.

---

Feito por [Gabriel Ribeiro](https://www.linkedin.com/in/gabriel-ribeiro-crm), CRM Specialist.
