import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Simulador de Investimentos: Fundo Longo Prazo, Renda Fixa e VGBL")

# === Sidebar: parâmetros de entrada ===
st.sidebar.header("Parâmetros Gerais")

# Valor inicial
valor_inicial = st.sidebar.number_input(
    "Valor inicial aplicado (R$):", 
    min_value=0.0, 
    value=10000.0, 
    step=1000.0, 
    format="%.2f"
)

# Aportes
st.sidebar.subheader("Aportes")
aporte = st.sidebar.number_input(
    "Valor do aporte periódico (R$):", 
    min_value=0.0, 
    value=1000.0, 
    step=100.0, 
    format="%.2f"
)
frequencia_aporte = st.sidebar.selectbox(
    "Frequência dos aportes:",
    ("Mensal", "Anual")
)

# Taxa de retorno anual (em %)
taxa_anual = st.sidebar.slider(
    "Taxa de retorno anual (%):", 
    min_value=0.0, 
    max_value=50.0, 
    value=8.0, 
    step=0.1
) / 100.0

# Prazo total em anos
prazo_anos = st.sidebar.number_input(
    "Prazo total (anos):", 
    min_value=1, 
    max_value=50, 
    value=10, 
    step=1
)

# Ciclo de reinvestimento para renda fixa (em anos)
st.sidebar.subheader("Renda Fixa")
ciclo_rf_anos = st.sidebar.number_input(
    "Ciclo de reinvestimento RF (anos):", 
    min_value=1, 
    max_value=10, 
    value=4, 
    step=1
)

# Botão para recalcular
if st.sidebar.button("Calcular projeções"):

    # === Preparar simulação mês a mês ===
    meses_totais = prazo_anos * 12
    # Taxa mensal equivalente (composta)
    taxa_mensal = (1 + taxa_anual) ** (1/12) - 1

    # Arrays para armazenar a evolução líquida de cada modalidade
    serie_fundo = np.zeros(meses_totais + 1)
    serie_rf = np.zeros(meses_totais + 1)
    serie_vgbl = np.zeros(meses_totais + 1)

    # 1) Fundo de Investimento (Longo Prazo) com come-cotas semestral
    portfolio_fundo = valor_inicial
    # Base que será usada para cálculo de ganho isento até o próximo come-cotas
    base_come = valor_inicial
    imposto_pago_fundo = 0.0

    # 2) Renda Fixa com tributação regressiva e reinvestimento a cada ciclo
    portfolio_rf = valor_inicial
    base_rf = valor_inicial
    imposto_pago_rf = 0.0
    meses_por_ciclo = ciclo_rf_anos * 12

    # 3) VGBL com tabela regressiva (imposto único no resgate)
    portfolio_vgbl = valor_inicial
    soma_aportes_vgbl = 0.0  # para calcular base de imposto ao final

    # === Loop mês a mês ===
    for mes in range(0, meses_totais + 1):
        # Registrar valores ao longo do tempo
        serie_fundo[mes] = portfolio_fundo
        serie_rf[mes] = portfolio_rf
        serie_vgbl[mes] = portfolio_vgbl

        if mes == meses_totais:
            break

        # --- Antes do crescimento mensal: incluir aporte, se for o mês correto ---
        # Fundo
        if frequencia_aporte == "Mensal":
            portfolio_fundo += aporte
        elif (frequencia_aporte == "Anual") and (mes % 12 == 0) and (mes > 0):
            portfolio_fundo += aporte

        # Renda Fixa
        if frequencia_aporte == "Mensal":
            portfolio_rf += aporte
        elif (frequencia_aporte == "Anual") and (mes % 12 == 0) and (mes > 0):
            portfolio_rf += aporte

        # VGBL
        if frequencia_aporte == "Mensal":
            portfolio_vgbl += aporte
            soma_aportes_vgbl += aporte
        elif (frequencia_aporte == "Anual") and (mes % 12 == 0) and (mes > 0):
            portfolio_vgbl += aporte
            soma_aportes_vgbl += aporte

        # --- Crescimento mensal ---
        portfolio_fundo *= 1 + taxa_mensal
        portfolio_rf *= 1 + taxa_mensal
        portfolio_vgbl *= 1 + taxa_mensal

        # --- Eventos de tributação ---
        # 1) Fundo: come-cotas em maio e novembro (meses 5 e 11 considerando janeiro=1)
        mes_do_ano = (mes % 12) + 1  # janeiro=1, fevereiro=2, ..., dezembro=12
        if mes_do_ano in (5, 11):
            # Ganho desde o último evento
            ganho = portfolio_fundo - base_come
            imposto = ganho * 0.15  # 15% para fundo de longo prazo
            if imposto > 0:
                portfolio_fundo -= imposto
                imposto_pago_fundo += imposto
            base_come = portfolio_fundo  # nova base para o próximo ciclo

        # 2) Renda Fixa: ao final de cada ciclo (em meses_por_ciclo)
        if (mes > 0) and (mes % meses_por_ciclo == 0):
            ganho_rf = portfolio_rf - base_rf
            # Tabela regressiva de IR (em %)
            # 0-6 meses: 22.5%, 6-12: 20%, 12-24: 17.5%, >24: 15%
            meses_held = meses_por_ciclo
            if meses_held <= 6:
                aliquota = 0.225
            elif meses_held <= 12:
                aliquota = 0.20
            elif meses_held <= 24:
                aliquota = 0.175
            else:
                aliquota = 0.15
            imposto2 = ganho_rf * aliquota
            if imposto2 > 0:
                portfolio_rf -= imposto2
                imposto_pago_rf += imposto2
            base_rf = portfolio_rf

        # 3) VGBL: nao tributa ate o final (resgate), entao nada aqui

    # --- Após o loop, cálculo final do imposto sobre VGBL ---
    # Base de imposto = ganhos totais = portfolio_vgbl - (valor_inicial + soma_aportes_vgbl)
    ganho_vgbl = portfolio_vgbl - (valor_inicial + soma_aportes_vgbl)
    # Determinar aliquota regressiva pelo prazo total (prazo_anos)
    if prazo_anos <= 2:
        aliquota_vgbl = 0.35
    elif prazo_anos <= 4:
        aliquota_vgbl = 0.30
    elif prazo_anos <= 6:
        aliquota_vgbl = 0.25
    elif prazo_anos <= 8:
        aliquota_vgbl = 0.20
    elif prazo_anos <= 10:
        aliquota_vgbl = 0.15
    else:
        aliquota_vgbl = 0.10
    imposto_pago_vgbl = ganho_vgbl * aliquota_vgbl
    valor_liquido_vgbl = portfolio_vgbl - imposto_pago_vgbl

    # O valor final de cada modalidade (ja liquido de IR):
    valor_final_fundo = serie_fundo[-1]  # fundo ja foi “zerado” nos eventos de come-cotas
    valor_final_rf = serie_rf[-1]        # RF ja foi tributado no ciclo final
    valor_final_vgbl = valor_liquido_vgbl

    # === Exibir resultados ---
    st.subheader("1) Resultados Finais")
    col1, col2, col3 = st.columns(3)
    col1.metric("Fundo (liquido)", f"R$ {valor_final_fundo:,.2f}")
    col2.metric("Renda Fixa (liquido)", f"R$ {valor_final_rf:,.2f}")
    col3.metric("VGBL (liquido)", f"R$ {valor_final_vgbl:,.2f}")

    st.subheader("2) Imposto Pago ao Longo do Período")
    col4, col5, col6 = st.columns(3)
    col4.write(f"Fundo (come-cotas): R$ {imposto_pago_fundo:,.2f}")
    col5.write(f"Renda Fixa: R$ {imposto_pago_rf:,.2f}")
    col6.write(f"VGBL (resgate): R$ {imposto_pago_vgbl:,.2f}")

    # === Montar DataFrame para o gráfico de evolução ===
    anos = np.arange(0, meses_totais + 1) / 12
    df_evolucao = pd.DataFrame({
        "Fundo (apos come-cotas)": serie_fundo,
        "Renda Fixa (apos IR em cada ciclo)": serie_rf,
        "VGBL (bruto)": serie_vgbl
    }, index=anos)

    st.subheader("3) Grafico de Evolucao do Saldo")
    st.line_chart(df_evolucao)

    st.markdown('''

**Observacoes importantes**:

- **Fundo de Investimento (Longo Prazo)**
  - Aplica-se IR de 15% sobre o ganho semestralmente (come-cotas em maio e novembro).
  - Nao ha tributacao adicional no resgate, pois o come-cotas ja antecipou o IR devido.

- **Renda Fixa**
  - A cada ciclo (definido em anos), todo o ganho acumulado desde o ultimo evento e tributado.
  - A aliquota segue a tabela regressiva de IR (maior tempo de aplicacao -> menor aliquota).
  - Apos o pagamento do IR, o montante liquido e reinvestido para o proximo ciclo.

- **VGBL**
  - Nao ha come-cotas durante a acumulacao.
  - No resgate, aplica-se uma unica aliquota de IR sobre todo o ganho acumulado, conforme o prazo total de permanencia (tabela regressiva).

- **Aportes**
  - Se escolher "Mensal", os aportes sao adicionados no inicio de cada mes.
  - Se escolher "Anual", os aportes sao adicionados no inicio de cada ano (1o mes de cada ano).

- **Taxa de Retorno**
  - A taxa anual informada no sidebar e convertida para equivalencia mensal composta.

- **Ciclo de Renda Fixa**
  - Informe em anos (ex.: 4 significa que, a cada 48 meses, ocorre a tributacao de IR sobre o ganho daquele periodo).
''')

