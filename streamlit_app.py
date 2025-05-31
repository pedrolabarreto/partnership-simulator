
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Partnership", layout="wide")

st.title("📈 Simulador de Partnership")
st.markdown(
    """
Ferramenta para colaboradores e sócios:
* **Calcule** o valor da sua participação.
* **Acompanhe** o saldo a pagar das parcelas.
* **Projete** o valuation da empresa com modelo em **dois estágios** (alta expansão → perpetuidade).
""",
    unsafe_allow_html=True,
)

###############################################################################
# Função utilitária ###########################################################
###############################################################################

def two_stage_valuation(fcf1: float, g1: float, years1: int, g2: float, wacc: float):
    """Enterprise Value (EV) por DCF em dois estágios (mid-year)."""
    fcfs, pv_fcfs = [], []
    for n in range(1, years1 + 1):
        fcf_n = fcf1 * (1 + g1) ** (n - 1)
        pv_n = fcf_n / (1 + wacc) ** (n - 0.5)
        fcfs.append(fcf_n)
        pv_fcfs.append(pv_n)

    fcf_last = fcfs[-1] * (1 + g1)
    tv = fcf_last * (1 + g2) / (wacc - g2)
    pv_tv = tv / (1 + wacc) ** (years1 - 0.5)

    ev = sum(pv_fcfs) + pv_tv
    return ev, fcfs, pv_fcfs, pv_tv

###############################################################################
# Sidebar – Inputs ############################################################
###############################################################################
with st.sidebar:
    st.header("📌 Dados básicos")
    valuation_input = st.number_input("Valuation atual (R$)", min_value=0.0, value=10_000_000.0, step=100_000.0, format="%.2f")
    equity_pct = st.number_input("Sua participação (%)", 0.0, 100.0, 1.0, step=0.1)
    share_value = valuation_input * equity_pct / 100

    st.header("💸 Parcelamento")
    agreed_price = st.number_input("Preço acordado pela participação (R$)", 0.0, value=share_value, step=50_000.0, format="%.2f")
    amount_paid = st.number_input("Valor já pago (R$)", 0.0, value=0.0, step=10_000.0, format="%.2f")
    balance_due = max(agreed_price - amount_paid, 0.0)

    st.header("⚙️ Projeção de Valuation")
    fcf1 = st.number_input("FCF do próximo ano (R$)", 0.0, value=1_000_000.0, step=50_000.0, format="%.2f")
    g1_pct = st.slider("Crescimento alto (%)", 0.0, 30.0, 10.0)
    years1 = st.slider("Duração do estágio alto (anos)", 1, 10, 5)
    g2_pct = st.slider("Crescimento perpetuidade (%)", 0.0, 10.0, 3.0)
    wacc_pct = st.slider("WACC (%)", 5.0, 25.0, 15.0)

###############################################################################
# Seção 1 – Participação ######################################################
###############################################################################

st.subheader("Sua participação hoje")
col1, col2, col3 = st.columns(3)
col1.metric("Valor da participação", f"R$ {share_value:,.2f}")
col2.metric("Preço acordado", f"R$ {agreed_price:,.2f}")
col3.metric("Saldo a pagar", f"R$ {balance_due:,.2f}")

###############################################################################
# Seção 2 – Valuation futuro ##################################################
###############################################################################
ev, fcfs, pv_fcfs, pv_tv = two_stage_valuation(
    fcf1,
    g1_pct / 100,
    years1,
    g2_pct / 100,
    wacc_pct / 100,
)

c1, c2 = st.columns(2)
c1.metric("Enterprise Value (EV)", f"R$ {ev:,.2f}")
c2.metric("Valor terminal (PV)", f"R$ {pv_tv:,.2f}")

proj_df = pd.DataFrame({
    "Ano (t)": list(range(1, years1 + 1)),  # inteiro garante ordem correta
    "FCL projetado": fcfs,
    "VP (mid-year)": pv_fcfs,
})
proj_df.set_index("Ano (t)", inplace=True)

st.dataframe(proj_df, use_container_width=True)

###############################################################################
# Seção 3 – Gráfico ordenado ##################################################
###############################################################################

# Série de valuations futuros (ilustrativa)
future_years = years1 + 5  # +5 anos após estágio alto
val_list = []
ev_temp = valuation_input
for n in range(1, future_years + 1):
    growth = g1_pct if n <= years1 else g2_pct
    ev_temp *= 1 + growth / 100
    val_list.append({"Ano": n, "Valuation": ev_temp})

chart_df = pd.DataFrame(val_list).set_index("Ano")

st.subheader("Valuation projetado (ilustrativo)")
st.line_chart(chart_df.sort_index())

###############################################################################
# Rodapé ######################################################################
###############################################################################

st.markdown(
    """---
📊 **Dica:** se o gráfico parecer fora de ordem, forçe recarregamento com *Shift+F5* para limpar cache.
"""
)
