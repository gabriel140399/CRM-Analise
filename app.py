
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json, math, io
import datetime as dt

st.set_page_config(page_title="CRM IntelliDash (No-Excel)", page_icon="📈", layout="wide")

with open("assets/theme.css","r",encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- BRANDING ----------
from pathlib import Path
import json as _json
BRAND = {"brand_name":"IntelliDash","brand_tagline":"CRM Inteligente, Sem Planilhas","primary_color":"#6C5CE7","secondary_color":"#A29BFE","accent_color":"#22c55e"}
try:
    with open("branding.json","r",encoding="utf-8") as _bf:
        BRAND.update(_json.load(_bf))
except Exception:
    pass

st.set_page_config(page_title=f"{BRAND['brand_name']} — IntelliDash", page_icon="assets/logo.svg", layout="wide")

# Header with logo and splash
c_logo, c_text = st.columns([1,3])
with c_logo:
    st.image("assets/logo.svg", use_column_width=True)
with c_text:
    st.title(f"{BRAND['brand_name']} — CRM IntelliDash")
    st.caption(BRAND.get("brand_tagline",""))

st.image("assets/splash.svg", use_column_width=True)
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ------------- Helpers -------------
def ceil_int(x):
    try:
        return int(math.ceil(float(x)))
    except:
        return 0

def fmt_money(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
    except:
        return "-"

def compute_forward(params):
    envios = params["envios"]
    freq = params["frequencia"]
    orate = params["open_rate"]
    ctr = params["ctr"]
    cvr = params["cvr"]
    ticket = params["ticket"]
    envios_periodo = envios * freq
    aberturas = envios_periodo * orate
    cliques = envios_periodo * ctr
    compras = cliques * cvr
    receita_prev = compras * ticket
    return {
        "envios_periodo": envios_periodo,
        "aberturas": aberturas,
        "cliques": cliques,
        "compras": compras,
        "receita_prev": receita_prev
    }

def compute_inverse(meta, params):
    """ Calcula o necessário em cada etapa para bater a meta (mantendo taxas). """
    ticket = params["ticket"]
    cvr = params["cvr"]
    ctr = params["ctr"]
    orate = params["open_rate"]
    freq = params["frequencia"]
    # compras necessárias e cliques/aberturas/envios necessários (por período)
    compras_need = 0 if ticket==0 else meta / ticket
    cliques_need = 0 if cvr==0 else compras_need / cvr
    envios_periodo_need = 0 if ctr==0 else cliques_need / ctr
    aberturas_need = envios_periodo_need * orate
    envios_por_disparo_need = 0 if freq==0 else envios_periodo_need / freq
    return {
        "envios_periodo_need": envios_periodo_need,
        "envios_por_disparo_need": envios_por_disparo_need,
        "aberturas_need": aberturas_need,
        "cliques_need": cliques_need,
        "compras_need": compras_need
    }

def optimize_plan(meta, base, max_multipliers=None, weights=None):
    if max_multipliers is None:
        max_multipliers = {
            "envios":[1,1.1,1.2,1.3,1.5,1.7,2.0],
            "ctr":[1,1.05,1.1,1.2,1.3],
            "cvr":[1,1.05,1.1,1.2,1.3,1.4],
            "ticket":[1,1.03,1.05,1.1,1.15,1.2]
        }
    if weights is None:
        weights = {"envios":1.0, "ctr":2.0, "cvr":2.5, "ticket":1.5}
    best = None
    base_k = compute_forward(base)
    base_rev = base_k["receita_prev"]
    for m_env in max_multipliers["envios"]:
        for m_ctr in max_multipliers["ctr"]:
            for m_cvr in max_multipliers["cvr"]:
                for m_tk in max_multipliers["ticket"]:
                    p = base.copy()
                    p["envios"] = base["envios"] * m_env
                    p["ctr"] = base["ctr"] * m_ctr
                    p["cvr"] = base["cvr"] * m_cvr
                    p["ticket"] = base["ticket"] * m_tk
                    k = compute_forward(p)
                    rev = k["receita_prev"]
                    if rev >= meta:
                        cost = (m_env-1)/0.1*weights["envios"] + (m_ctr-1)/0.1*weights["ctr"] + (m_cvr-1)/0.1*weights["cvr"] + (m_tk-1)/0.1*weights["ticket"]
                        changed = sum([m_env>1, m_ctr>1, m_cvr>1, m_tk>1])
                        cost += changed*0.3
                        if (best is None) or (cost < best["cost"]):
                            best = {"params":p,"kpi":k,"rev":rev,"cost":cost,"multipliers":{"envios":m_env,"ctr":m_ctr,"cvr":m_cvr,"ticket":m_tk},"base_rev":base_rev}
    return best

def funnel_df(kpi):
    labels = ["Envios","Aberturas","Cliques","Compras"]
    values = [ceil_int(kpi["envios_periodo"]), ceil_int(kpi["aberturas"]), ceil_int(kpi["cliques"]), ceil_int(kpi["compras"])]
    return pd.DataFrame({"Etapa":labels,"Quantidade":values})

def heuristics(params):
    tips, wins = [], []
    if params["open_rate"] < 0.18: tips.append("Open Rate < 18%: melhorar assuntos, segmentar por engajamento e aquecer domínio.")
    else: wins.append("Open Rate saudável — mantenha testes A/B de assunto.")
    if params["ctr"] < 0.015: tips.append("CTR < 1,5%: aumentar blocos de oferta e CTAs claros; produtos best-sellers acima da dobra.")
    else: wins.append("CTR ok — explore recomendação dinâmica e CTA secundário.")
    if params["cvr"] < 0.015: tips.append("CVR < 1,5%: landing específica por campanha, prova social e checkout simplificado.")
    else: wins.append("CVR consistente — testar bundles e escadas de valor.")
    if params["ticket"] < 120: tips.append("Ticket médio baixo: bundle/kit, frete grátis acima de X, cross/upsell.")
    else: wins.append("Ticket médio bom — explorar kits premium e assinaturas.")
    return tips, wins

def save_profile(params):
    return json.dumps(params, ensure_ascii=False, indent=2).encode("utf-8")

def load_profile(file_bytes):
    return json.loads(file_bytes.decode("utf-8"))

# ------------- UI -------------



with st.sidebar:
    st.markdown("### 🎛️ Presets de parâmetros")
    default_params = {
        "meta": 20000.0,
        "envios": 15000.0,
        "frequencia": 4,
        "open_rate": 0.22,
        "ctr": 0.018,
        "cvr": 0.017,
        "ticket": 180.0,
        # blocos para cálculos adicionais
        "clientes_ativos": 10000,
        "pedidos_periodo": 1800,
        "pedidos_repetidos": 420
    }
    if "params" not in st.session_state:
        st.session_state["params"] = default_params.copy()

    up = st.file_uploader("Carregar preset (.json)", type=["json"])
    if up:
        try:
            st.session_state["params"] = load_profile(up.read())
            st.success("Preset carregado!")
        except Exception as e:
            st.error(f"Erro ao carregar preset: {e}")

    st.download_button("⬇️ Baixar preset atual", data=save_profile(st.session_state["params"]), file_name="preset_crm.json", mime="application/json")

tabs = st.tabs(["🧩 Parâmetros","📊 Dashboard","🌀 Funil Inverso","🔁 Taxa de Recompra","🧠 Plano Inteligente","🧯 Detratores & Pontos Positivos"])

with tabs[0]:
    st.subheader("Parâmetros do período")
    p = st.session_state["params"]
    c1,c2,c3 = st.columns(3)
    with c1:
        p["meta"] = st.number_input("Meta de Receita (R$)", min_value=0.0, value=float(p["meta"]), step=100.0, format="%.2f")
        p["envios"] = st.number_input("Envios por disparo (base elegível)", min_value=0.0, value=float(p["envios"]), step=100.0)
    with c2:
        p["frequencia"] = st.number_input("Frequência de disparos no período", min_value=1, value=int(p["frequencia"]), step=1)
        p["ticket"] = st.number_input("Ticket médio (R$)", min_value=0.0, value=float(p["ticket"]), step=1.0, format="%.2f")
    with c3:
        p["open_rate"] = st.number_input("Open Rate (por enviado)", min_value=0.0, max_value=1.0, value=float(p["open_rate"]), step=0.01, format="%.2f")
        p["ctr"] = st.number_input("CTR (cliques por enviado)", min_value=0.0, max_value=1.0, value=float(p["ctr"]), step=0.001, format="%.3f")
        p["cvr"] = st.number_input("CVR (conversão do clique)", min_value=0.0, max_value=1.0, value=float(p["cvr"]), step=0.001, format="%.3f")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("Dados para Taxa de Recompra (opcional)")
    c4,c5,c6 = st.columns(3)
    with c4:
        p["clientes_ativos"] = st.number_input("Clientes ativos no período", min_value=0, value=int(p["clientes_ativos"]), step=10)
    with c5:
        p["pedidos_periodo"] = st.number_input("Pedidos totais no período", min_value=0, value=int(p["pedidos_periodo"]), step=10)
    with c6:
        p["pedidos_repetidos"] = st.number_input("Pedidos repetidos no período", min_value=0, value=int(p["pedidos_repetidos"]), step=10)

    st.session_state["params"] = p
    st.success("Parâmetros salvos! Veja as próximas abas.")

with tabs[1]:
    st.subheader("Dashboard")
    k = compute_forward(st.session_state["params"])
    meta = st.session_state["params"]["meta"]
    gap = max(meta - k["receita_prev"], 0)
    ating = 0 if meta==0 else k["receita_prev"]/meta
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Receita Prevista", fmt_money(k["receita_prev"]))
    m2.metric("Meta", fmt_money(meta))
    m3.metric("% Atingimento", f"{ating*100:.1f}%")
    m4.metric("Gap para Meta", fmt_money(gap))
    m5.metric("Compras Previstas", ceil_int(k["compras"]))

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1.2,1])
    with c1:
        df = funnel_df(k)
        fig = px.funnel(df, y="Etapa", x="Quantidade")
        fig.update_layout(height=430, margin=dict(t=30,b=30,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### Funil (valores inteiros ⬆️)")
        st.dataframe(df, hide_index=True, use_container_width=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    cA,cB,cC = st.columns(3)
    cA.metric("Envios no Período", ceil_int(k["envios_periodo"]))
    cB.metric("Aberturas Previstas", ceil_int(k["aberturas"]))
    cC.metric("Cliques Previstos", ceil_int(k["cliques"]))

with tabs[2]:
    st.subheader("Funil Inverso (o que é necessário para bater a meta)")
    p = st.session_state["params"]
    inv = compute_inverse(p["meta"], p)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Envios/Período necessários", ceil_int(inv["envios_periodo_need"]))
    c2.metric("Envios por disparo", ceil_int(inv["envios_por_disparo_need"]))
    c3.metric("Aberturas necessárias", ceil_int(inv["aberturas_need"]))
    c4.metric("Cliques necessários", ceil_int(inv["cliques_need"]))
    c5.metric("Compras necessárias", ceil_int(inv["compras_need"]))

with tabs[3]:
    st.subheader("Taxa de Recompra")
    p = st.session_state["params"]
    clientes = max(p["clientes_ativos"], 1)
    pedidos = p["pedidos_periodo"]
    repetidos = p["pedidos_repetidos"]
    # Exemplo de métricas
    avg_pedidos_por_cliente = pedidos / clientes
    taxa_recompra = 0 if pedidos==0 else repetidos / pedidos
    m1,m2,m3 = st.columns(3)
    m1.metric("Pedidos por Cliente (média)", f"{avg_pedidos_por_cliente:.2f}")
    m2.metric("Pedidos repetidos", ceil_int(repetidos))
    m3.metric("Taxa de Recompra", f"{taxa_recompra*100:.1f}%")

with tabs[4]:
    st.subheader("Plano Inteligente")
    p = st.session_state["params"]
    best = optimize_plan(p["meta"], p)
    base_k = compute_forward(p)
    if best is None:
        st.error("Não foi possível encontrar um plano dentro dos limites. Ajuste as taxas ou frequência.")
    else:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("#### Situação Atual")
            st.metric("Receita Prevista (Atual)", fmt_money(base_k["receita_prev"]))
            st.metric("Compras (Atual)", ceil_int(base_k["compras"]))
        with c2:
            st.markdown("#### Proposta do Plano")
            st.metric("Receita Prevista (Plano)", fmt_money(best["rev"]))
            st.metric("Compras (Plano)", ceil_int(best["kpi"]["compras"]))

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        mult = best["multipliers"]
        plan_df = pd.DataFrame({
            "Alavanca":["Envios","CTR","CVR","Ticket médio"],
            "Ação":[
                ("Aumentar em %.0f%%"%( (mult["envios"]-1)*100) if mult["envios"]>1 else "Manter"),
                ("Aumentar em %.0f%%"%( (mult["ctr"]-1)*100) if mult["ctr"]>1 else "Manter"),
                ("Aumentar em %.0f%%"%( (mult["cvr"]-1)*100) if mult["cvr"]>1 else "Manter"),
                ("Aumentar em %.0f%%"%( (mult["ticket"]-1)*100) if mult["ticket"]>1 else "Manter"),
            ],
            "De":[ceil_int(p["envios"]), f"{p['ctr']*100:.2f}%", f"{p['cvr']*100:.2f}%", fmt_money(p["ticket"])],
            "Para":[ceil_int(p["envios"]*mult["envios"]), f"{p['ctr']*mult['ctr']*100:.2f}%", f"{p['cvr']*mult['cvr']*100:.2f}%", fmt_money(p["ticket"]*mult["ticket"])]
        })
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Baixar plano (CSV)", data=plan_df.to_csv(index=False).encode("utf-8"), file_name="plano_inteligente.csv", mime="text/csv")

with tabs[5]:
    st.subheader("Detratores & Pontos Positivos")
    tips, wins = heuristics(st.session_state["params"])
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### Detratores (agir agora)")
        for t in tips:
            st.markdown(f"- {t}")
    with col2:
        st.markdown("#### Pontos Positivos (ampliar)")
        for w in wins:
            st.markdown(f"- {w}")

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.caption("Valores do funil (Envios, Aberturas, Cliques, Compras) são sempre **arredondados para cima** no dashboard.")


st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='brand-footer'><img src='assets/logo.svg'/> <span>{BRAND['brand_name']} • © {dt.datetime.now().year}</span></div>", unsafe_allow_html=True)
