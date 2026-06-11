import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# 1. Configuração da Página
st.set_page_config(page_title="Calculadora de ROI - Usina Solar", layout="wide")
st.title("☀️ Calculadora de Viabilidade - Usina Solar")
st.markdown("Simule a previsibilidade e o retorno financeiro da sua usina em tempo real.")

# 2. Barra Lateral (Inputs Interativos para você usar na feira)
st.sidebar.header("Parâmetros do Cliente")
investimento_inicial = st.sidebar.number_input("Investimento Inicial (R$)", min_value=10000, value=300000, step=10000)
retorno_realista = st.sidebar.number_input("Retorno Mensal Esperado (R$)", min_value=100, value=7000, step=100)

# Calculando a variação dos cenários (20% para cima e para baixo)
retorno_pessimista = retorno_realista * 0.8
retorno_otimista = retorno_realista * 1.2

st.sidebar.markdown("---")
st.sidebar.markdown("**Projeção dos Cenários:**")
st.sidebar.markdown(f"🔴 **Pessimista (-20%):** R$ {retorno_pessimista:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))
st.sidebar.markdown(f"🔵 **Realista (Base):** R$ {retorno_realista:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))
st.sidebar.markdown(f"🟢 **Otimista (+20%):** R$ {retorno_otimista:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))

# 3. Matemática e Eixo do Tempo (120 meses / 10 anos)
meses = np.arange(0, 121)
caixa_realista = -investimento_inicial + (retorno_realista * meses)
caixa_pessimista = -investimento_inicial + (retorno_pessimista * meses)
caixa_otimista = -investimento_inicial + (retorno_otimista * meses)

# 4. Construção do Gráfico
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(meses, caixa_otimista, label='Otimista', color='#2ca02c', linewidth=2.5)
ax.plot(meses, caixa_realista, label='Realista', color='#1f77b4', linewidth=3.5)
ax.plot(meses, caixa_pessimista, label='Pessimista', color='#d62728', linewidth=2.5, linestyle='--')

# Linha do Break-even (Ponto zero)
ax.axhline(0, color='black', linewidth=1.5, linestyle='-')

# Configurações visuais do gráfico
ax.set_title('Projeção de Retorno Financeiro Acumulado (10 Anos)', fontsize=14, fontweight='bold')
ax.set_xlabel('Tempo de Operação (Meses)', fontsize=12)
ax.set_ylabel('Saldo Financeiro Acumulado (R$)', fontsize=12)
ax.set_xticks(np.arange(0, 121, 12))
ax.grid(True, linestyle=':', alpha=0.7)
ax.legend(loc='upper left')

# Formatação do Eixo Y para Reais (R$)
formatter = ticker.FuncFormatter(lambda x, pos: f'R$ {int(x):,}'.replace(',', '.'))
ax.yaxis.set_major_formatter(formatter)

# 5. Exibindo o Gráfico no Streamlit
st.pyplot(fig)

# 6. Rodapé com Resumo
st.info(f"O **Payback Realista** (ponto em que a usina se paga) ocorre no mês **{int(investimento_inicial/retorno_realista)}**.")