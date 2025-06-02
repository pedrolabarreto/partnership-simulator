# Simulador de Investimentos

Este e um aplicativo Streamlit que projeta o patrimonio liquido acumulado em tres opcoes de investimento:
1. Fundo de investimento de longo prazo com come-cotas semestrais.
2. Titulo de renda fixa com tributacao regressiva (reinvestimento em ciclos).
3. VGBL com tabela regressiva (imposto unico no resgate).

## Como usar

1. Clone este repositorio.
2. Instale as dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```

A interface permite ajustar:
- Valor inicial aplicado.
- Valor e frequencia dos aportes (mensal ou anual).
- Taxa de retorno anual.
- Prazo total em anos.
- Ciclo de reinvestimento da renda fixa (em anos).

Clique em "Calcular projeções" no sidebar para ver:
- Valor liquido final em cada modalidade.
- Imposto pago ao longo do periodo.
- Grafico de evolucao dos saldos.
