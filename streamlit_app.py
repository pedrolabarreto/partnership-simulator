
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Simulador de Partnership", layout="wide")

st.title("📈 Simulador de Partnership")
st.markdown("""
Ferramenta para colaboradores e sócios:
* **Calcule** o valor da sua participação.
* **Acompanhe** o saldo a pagar das parcelas.
* **Projete** o valuation da empresa com modelo em **dois estágios** (alta expansão + perpetuidade).
""")

###############################################################################
# Funções utilitárias #########################################################
###############################################################################

def two_stage_valuation(fcf1: float, g1: float, years1: int, g2: float, wacc: float):
    """Calcula Enterprise Value (EV) por DCF em dois estágios.

    Args:
        fcf1 (float): FCF do próximo ano (t=1).
        g1 (float): crescimento anual no 1.º estágio (0-1).
        years1 (int): duração do 1.º estágio.
        g2 (float): crescimento perpétuo (0-1).
        wacc (float): taxa de desconto (0-1).

    Returns:
        ev (float): enterprise value.
        fcfs (list[float]): lista de FCFs projetados t=1..years1.
        pv_fcfs (list[float]): valores presentes mid-year desses FCFs.
    """
    fcfs, pv_fcfs = [], []
    for n in range(1, years1 + 1):
        fcf_n = fcf1 * ((1 + g1) ** (n - 1))
        pv_n = fcf_n / ((1 + wacc) ** (n - 0.5))  # mid-year discounting
        fcfs.append(fcf_n)
        pv_fcfs.append(pv_n)

    # FCF ao final do primeiro estágio
    fcf_last = fcfs[-1] * (1 + g1)
    # Valor terminal
    tv = fcf_last * (1 + g2) / (wacc - g2)
    pv_tv = tv / ((1 + wacc) ** (years1 - 0.5))

    ev = sum(pv_fcfs) + pv_tv
    return ev, fcfs, pv_fcfs, pv_tv

###############################################################################
# Sidebar – Inputs básicos ####################################################
###############################################################################
with st.sidebar:
    st.header("📌 Dados básicos")
    valuation_input = st.number_input(
        "Valuation atual (R$)", min_value=0.0, value=10_000_000.0, step=100_000.0, format="%.2f"
    )
    equity_pct = st.number_input(
        "Sua participação (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1
    )
    share_value = valuation_input * equity_pct / 100

    st.header("💸 Parcelamento")
    agreed_price = st.number_input(
        "Preço acordado pela participação (R$)", min_value=0.0, value=share_value, step=50_000.0, format="%.2f"
    )
    amount_paid = st.number_input(
        "Valor já pago (R$)", min_value=0.0, value=0.0, step=10_000.0, format="%.2f"
    )
    balance_due = max(agreed_price - amount_paid, 0)

    st.header("⚙️ Projeção de Valuation")
    fcf1 = st.number_input(
        "FCF do próximo ano (R$)", min_value=0.0, value=1_000_000.0, step=50_000.0, format="%.2f"
    )
    g1_pct = st.slider("Crescimento alto (%)", 0.0, 30.0, 10.0)
    years1 = st.slider("Duração estágio alto (anos)", 1, 10, 5)
    g2_pct = st.slider("Crescimento perpetuidade (%)", 0.0, 10.0, 3.0)
    wacc_pct = st.slider("WACC (%)", 5.0, 25.0, 15.0)

###############################################################################
# Seção 1 – Resultado da participação #########################################
###############################################################################

st.subheader("Sua participação hoje")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Valor da participação", f"R$ {share_value:,.2f}")
col_b.metric("Total acordado a pagar", f"R$ {agreed_price:,.2f}")
col_c.metric("Saldo a pagar", f"R$ {balance_due:,.2f}")

###############################################################################
# Seção 2 – Projeção de valuation #############################################
###############################################################################
ev, fcfs, pv_fcfs, pv_tv = two_stage_valuation(
    fcf1=fcf1,
    g1=g1_pct / 100,
    years1=years1,
    g2=g2_pct / 100,
    wacc=wacc_pct / 100,
)

col1, col2 = st.columns(2)
col1.metric("Enterprise Value (EV)", f"R$ {ev:,.2f}")
col2.metric("Valor terminal (PV)", f"R$ {pv_tv:,.2f}")

# Tabela de FCFs e PVs
projection_df = pd.DataFrame({
    "Ano": [f"t+{i}" for i in range(1, years1 + 1)],
    "FCL projetado": fcfs,
    "VP (mid-year)": pv_fcfs,
})
st.dataframe(projection_df, use_container_width=True)

###############################################################################
# Seção 3 – Gráfico do valuation futuro #######################################
###############################################################################

# Gerar série de valuations futuros assumindo que EV cresce a mesma taxa do estágio 1 até anos1, depois g2
val_series = []
ev_curr = valuation_input
for n in range(1, years1 + 6):  # +5 anos além do estágio para ilustrar
    if n <= years1:
        ev_curr *= 1 + g1_pct / 100
    else:
        ev_curr *= 1 + g2_pct / 100
    val_series.append({"Ano": f"{n}", "Valuation": ev_curr})

chart_df = pd.DataFrame(val_series).set_index("Ano")
st.subheader("Valuation projetado (ilustrativo)")
if not chart_df.empty:
    st.line_chart(chart_df)

###############################################################################
# Rodapé ######################################################################
###############################################################################

st.markdown("""---
🔎 **Como funciona o cálculo em dois estágios?**

1. Descontamos os FCFs projetados com crescimento **g₁** e mid-year convention.
2. Calculamos o **valor terminal** usando **g∞**.
3. Somamos tudo → **EV**. Para chegar ao valor da cota, basta multiplicar pelo % de participação.

A matemática completa segue as mesmas premissas usadas no modelo corporativo revisado.
""")
