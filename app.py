import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

# 1. Configurar página em modo super-largo (Fullscreen)
st.set_page_config(page_title="Terminal Solar PRO", layout="wide", initial_sidebar_state="expanded")

# 2. DECLARAÇÃO DE FUNÇÕES CRÍTICAS NO TOPO (Estabilidade absoluta)
def formato_real(valor):
    """Garante a formatação padrão BRL estrita: R$ 240.000,00"""
    try:
        return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    except:
        return "R$ 0,00"

def render_metric_card(label, value, color_class):
    """Renderiza os blocos de métricas superiores com visual TradingView"""
    st.markdown(f"""
        <div style="background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; padding: 15px; text-align: center;">
            <div style="color: #787b86; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
            <div class="{color_class}" style="font-size: 2rem; font-weight: bold; margin-top: 5px;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# 3. CSS Avançado para Interface Escura de Alta Performance
st.markdown("""
    <style>
    .block-container { padding: 80px 15px 0px 15px !important; max-width: 99% !important; margin: 0 auto !important; }
    header[data-testid="stHeader"] { 
        background-color: #0c0f16 !important; 
        height: 50px !important;
    } 
    footer { visibility: hidden !important; }
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; }
    
    .market-header-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 12px;
        width: 100%;
    }
    .market-card {
        flex: 1;
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 4px;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .market-label {
        color: #787b86;
        font-size: 0.72rem;
        font-weight: bold;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .market-value {
        color: #cbd5e1;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    .command-bar {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 15px;
        font-size: 0.75rem;
        color: #787b86;
        margin-bottom: 15px;
    }
    .panel-title-bar {
        background-color: #131722;
        color: #787b86;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid #2a2e39;
        border-bottom: none;
        border-radius: 4px 4px 0 0;
        padding: 6px 12px;
    }
    .neon-green { color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }
    .neon-blue { color: #3b82f6; text-shadow: 0 0 10px rgba(59, 130, 246, 0.3); }
    .neon-purple { color: #ff9f43; text-shadow: 0 0 10px rgba(255, 159, 67, 0.3); }
    </style>
""", unsafe_allow_html=True)

# 4. CABEÇALHO PROPRIETÁRIO SANTO HOUSE
st.markdown("""
    <div class="market-header-container">
        <div class="market-card">
            <div class="market-label">💵 DÓLAR COMERCIAL</div>
            <div class="market-value">5,1783 <span style="color: #f43f5e; font-size: 0.75rem; margin-left: 5px;">-0,28% ▼</span></div>
        </div>
        <div class="market-card">
            <div class="market-label">☀️ SOLAR INDEX GLOBAL (TAN)</div>
            <div class="market-value">61,02 USD <span style="color: #f43f5e; font-size: 0.75rem; margin-left: 5px;">-4,03% ▼</span></div>
        </div>
        <div class="market-card">
            <div class="market-label">⚡ NEXTERA ENERGY (NEE)</div>
            <div class="market-value">84,42 USD <span style="color: #10b981; font-size: 0.75rem; margin-left: 5px;">+0,49% ▲</span></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- BARRA DE COMANDO INTEGRADA ---
fuso_brasil = timezone(timedelta(hours=-3))
st.markdown("""
    <div class="command-bar">
        <div>❖ SANTO HOUSE SOLAR TERMINAL v4.7 // FULL DYNAMIC ENGINE</div>
        <div>SYS TIME: <b>{}</b></div>
        <div style="color: #10b981; font-weight: bold; letter-spacing: 1px;">● CORE SYSTEM ONLINE</div>
    </div>
""".format(datetime.now(fuso_brasil).strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)

# 5. Painel Lateral (Configuração de Inputs)
try:
    side_col1, side_col2, side_col3 = st.sidebar.columns([1, 4, 1])
    with side_col2:
        st.image("logo.jpg", use_container_width=True)
except:
    st.sidebar.markdown("<div style='text-align:center; color:#ff4b4b; font-size:0.8rem; margin-bottom:10px;'>⚠️ Faça upload do arquivo logo.jpg no GitHub</div>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='color:#3b82f6; text-align:center; margin-top:5px;'>⚙️ MODELAGEM FINANCEIRA</h3>", unsafe_allow_html=True)

perfil = st.sidebar.selectbox(
    "Perfil do Investidor", 
    ["Conservador Escalável", "Agressivo Bimestral", "Customizado"]
)

aporte_inicial = st.sidebar.number_input("Aporte Inicial Quitado (R$)", value=240000, step=10000)
st.sidebar.markdown(f"<div style='color: #10b981; font-size: 0.8rem; margin-top: -12px; margin-bottom: 12px;'>➔ Validação: <b>{formato_real(aporte_inicial)}</b></div>", unsafe_allow_html=True)

faturamento_por_usina = st.sidebar.number_input("Faturamento Mensal Inicial por Usina (R$)", value=6000, step=500)
st.sidebar.markdown(f"<div style='color: #10b981; font-size: 0.8rem; margin-top: -12px; margin-bottom: 12px;'>➔ Validação: <b>{formato_real(faturamento_por_usina)}</b></div>", unsafe_allow_html=True)

custo_parcela_banco = st.sidebar.number_input("Parcela do Financiamento Solar (R$)", value=5000, step=500)
st.sidebar.markdown(f"<div style='color: #e11d48; font-size: 0.8rem; margin-top: -12px; margin-bottom: 12px;'>➔ Validação: <b>{formato_real(custo_parcela_banco)}</b></div>", unsafe_allow_html=True)

# Seletor Dinâmico de Bandeiras Tarifárias da ANEEL
st.sidebar.markdown("---")
bandeira_aneel = st.sidebar.selectbox(
    "Bandeira Tarifária Ativa (ANEEL)",
    ["Verde (Tarifa Normal)", "Amarela (+ Extra)", "Vermelha P1 (Escassez)", "Vermelha P2 (Crise Máxima)"]
)

# Slider para definir a taxa de reajuste inflacionário anual homologado da energia
reajuste_anual_pct = st.sidebar.slider("Reajuste Anual da Energia / IPCA (%)", 0.0, 15.0, 5.0, step=0.5) / 100.0

# Mapeamento do acréscimo real no valor do faturamento por bandeira
impacto_bandeira = {
    "Verde (Tarifa Normal)": 1.00,
    "Amarela (+ Extra)": 1.05,       
    "Vermelha P1 (Escassez)": 1.12,  
    "Vermelha P2 (Crise Máxima)": 1.20 
}
fator_bandeira = impacto_bandeira[bandeira_aneel]

# Cálculo dinâmico da taxa base reativa com a bandeira aplicada
faturamento_com_bandeira = faturamento_por_usina * fator_bandeira
taxa_base_calculada = (faturamento_com_bandeira / aporte_inicial) * 100 if aporte_inicial > 0 else 0

st.sidebar.metric(
    label="📈 Rendimento Base Atualizado", 
    value=f"{taxa_base_calculada:.2f}% ao mês", 
    delta=f"Impacto {bandeira_aneel.split(' ')[0]}"
)

months_projection = st.sidebar.slider("Prazo da Projeção (Meses)", 12, 120, 120, step=12)

# Configuração de Porcentagens Dinâmicas
pct_saque_int = st.sidebar.slider("% de Retirada do Lucro Líquido (Bolso)", 0, 100, 30, step=5)
pct_retirada = pct_saque_int / 100.0
pct_retencao_int = 100 - pct_saque_int

# Seletor de Estratégia Reativa com Título Dinâmico
st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color:#cbd5e1; margin-bottom: 2px;'>🎯 Alocação do Caixa</h4>", unsafe_allow_html=True)
estrategia_caixa = st.sidebar.radio(
    f"O que fazer com os {pct_retencao_int}% retidos?",
    ["Acumular em Caixa Vivo (CDI)", "Quitação Acelerada (Abater Bancos)"]
)

# Mapeamento do ritmo de expansão
expandir_usinas = True
if "Conservador" in perfil:
    meses_para_nova_usina = 12
    max_usinas = 999
elif "Agressivo" in perfil:
    meses_para_nova_usina = 2
    max_usinas = 999
else:
    st.sidebar.markdown("---")
    ativar_expansao = st.sidebar.toggle("Ativar Novas Expansões", value=True)
    if ativar_expansao:
        meses_para_nova_usina = st.sidebar.slider("Frequência de Nova Usina (A cada X meses)", 1, 24, 6)
        max_usinas = st.sidebar.slider("Quantidade Máxima Total de Usinas", 1, 30, 5)
    else:
        expandir_usinas = False
        meses_para_nova_usina = 999
        max_usinas = 1

# 6. MOTOR DE CÁLCULO CORE REVISADO (UNIFICANDO REAJUSTE ANUAL + BANDEIRAS)
data = []
caixa_acumulado = 0.0
total_sacado_investidor = 0.0
usinas_ativas = 1
financiamentos = {}
id_usina_atual = 1

# Normalização de segurança das variáveis numéricas
val_faturamento = max(0.0, float(faturamento_por_usina))
val_aporte = max(1.0, float(aporte_inicial))
val_parcela = max(0.0, float(custo_parcela_banco))

# Base dinâmica que vai acumular a inflação ano a ano
faturamento_base_acumulado = val_faturamento

for m in range(1, months_projection + 1):
    
    # MOTOR DE VALORIZAÇÃO ANUAL: A cada 12 meses, aplica a taxa do slider cumulativamente
    if m > 1 and (m - 1) % 12 == 0:
        faturamento_base_acumulado *= (1 + reajuste_anual_pct)
        
    # Aplica o fator de bandeira atualizado sobre o valor corrigido do período
    faturamento_periodo_usina = faturamento_base_acumulado * fator_bandeira

    # Gatilho condicional de expansão patrimonial
    if expandir_usinas and m > 1 and m <= 60 and (m - 1) % meses_para_nova_usina == 0:
        if usinas_ativas < max_usinas:
            usinas_ativas += 1
            id_usina_atual += 1
            financiamentos[id_usina_atual] = {
                "parcelas_restantes": 60,
                "primeiras_12_pagas": False,
                "meses_sem_pagar": 0
            }

    # SISTEMA DE AMORTIZAÇÃO ANTECIPADA POR LOTES MENSAL
    if estrategia_caixa == "Quitação Acelerada (Abater Bancos)":
        for id_u in sorted(financiamentos.keys()):
            if not financiamentos[id_u]["primeiras_12_pagas"] and financiamentos[id_u]["parcelas_restantes"] >= 12:
                custo_12_parcelas_antecipadas = 12 * (val_parcela * 0.85)
                
                if caixa_acumulado >= custo_12_parcelas_antecipadas:
                    caixa_acumulado -= custo_12_parcelas_antecipadas
                    financiamentos[id_u]["primeiras_12_pagas"] = True
                    financiamentos[id_u]["parcelas_restantes"] -= 12
                    financiamentos[id_u]["meses_sem_pagar"] = 12 
                    break 

    # Varredura do custo real de boletos bancários ativos no mês
    parcelas_ativas_no_mes = 0
    for id_u in financiamentos.keys():
        if financiamentos[id_u]["parcelas_restantes"] > 0:
            if financiamentos[id_u]["primeiras_12_pagas"] and financiamentos[id_u]["meses_sem_pagar"] > 0:
                parcelas_ativas_no_mes += 0 
            else:
                parcelas_ativas_no_mes += 1

    # CONTABILIDADE OPERACIONAL DINÂMICA
    faturamento_bruto_visivel = usinas_ativas * faturamento_periodo_usina
    faturamento_estatico_sem_reajuste = usinas_ativas * (val_faturamento * fator_bandeira)
    
    custo_parcelas = parcelas_ativas_no_mes * val_parcela
    lucro_liquido_empresa = faturamento_bruto_visivel - custo_parcelas
    
    saque_investidor = lucro_liquido_empresa * pct_retirada
    retencao_caixa = lucro_liquido_empresa - saque_investidor
    
    caixa_acumulado += retencao_caixa
    total_sacado_investidor += saque_investidor

    # CÁLCULO DA TAXA DE RENDIMENTO REAL CRESCENTE CONFORME A INFLAÇÃO TARIFFÁRIA
    capital_proporcional = usinas_ativas * val_aporte
    taxa_rendimento_mes = (lucro_liquido_empresa / capital_proporcional) * 100 if capital_proporcional > 0 else 0

    # Consumo do tempo de carência e dos contratos paralelos
    for id_u in financiamentos.keys():
        if financiamentos[id_u]["primeiras_12_pagas"] and financiamentos[id_u]["meses_sem_pagar"] > 0:
            financiamentos[id_u]["meses_sem_pagar"] -= 1 
        elif financiamentos[id_u]["parcelas_restantes"] > 0:
            financiamentos[id_u]["parcelas_restantes"] -= 1 

    patrimonio_ativos = usinas_ativas * val_aporte
    valor_total_holding = caixa_acumulado + patrimonio_ativos

    # Alimentação da matriz de auditoria
    data.append({
        "Mês": m,
        "Usinas": usinas_ativas,
        "Faturamento Bruto": faturamento_bruto_visivel,
        "Fat. Sem Reajuste": faturamento_estatico_sem_reajuste,
        "Parcelas Banco": custo_parcelas,
        "Lucro Líquido": lucro_liquido_empresa,
        "Rendimento Mensal (%)": f"{taxa_rendimento_mes:.2f}%",
        "Saque Mensal": saque_investidor,
        "Caixa Acumulado": caixa_acumulado,
        "Patrimônio Usinas": patrimonio_ativos,
        "Valor Total Negócio": valor_total_holding
    })

df = pd.DataFrame(data)
retorno_solar_total = df["Valor Total Negócio"].iloc[-1]

# CÁLCULO DE ROI DO PAINEL 3 REALISTA
anos_totais = months_projection / 12.0
taxa_cdi_anual = 0.095
retorno_cdi_final = val_aporte * ((1 + taxa_cdi_anual) ** anos_totais)
retorno_imovel_final = val_aporte * ((1 + 0.08) ** anos_totais)

# Configuração Padrão de Design Gráfico (Estilo TradingView)
layout_charts = dict(
    paper_bgcolor='#131722', plot_bgcolor='#131722',
    font=dict(color='#787b86', size=10),
    xaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False),
    margin=dict(l=45, r=15, t=15, b=25), hovermode='x unified'
)

# --- 🚀 RENDERIZAÇÃO DA LINHA 1 COM TÍTULOS TOTALMENTE DINÂMICOS ---
with st.container():
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        render_metric_card(f"Caixa Livre na Empresa ({pct_retencao_int}%)", formato_real(df['Caixa Acumulado'].iloc[-1]), "neon-green")
    with col_m2:
        render_metric_card(f"Dinheiro Sacado para o Bolso ({pct_saque_int}%)", formato_real(total_sacado_investidor), "neon-blue")
    with col_m3:
        render_metric_card("Valor Total da Holding (Usinas + Caixa)", formato_real(retorno_solar_total), "neon-purple")

st.markdown("<br>", unsafe_allow_html=True)

# --- LINHA 2: RENDIMENTOS GRÁFICOS ---
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("""<div class="panel-title-bar">📈 PAINEL 1: ESCALA PATRIMONIAL (ATIVOS VS LIQUIDEZ VS HOLDING)</div>""", unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["Mês"], y=df["Patrimônio Usinas"], name="Patrimônio Real", line=dict(color="#10B981", width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.03)'))
    fig1.add_trace(go.Scatter(x=df["Mês"], y=df["Caixa Acumulado"], name="Dinheiro Vivo", line=dict(color="#3B82F6", width=2, dash='dot')))
    fig1.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Total Negócio"], name="Valor da Holding", line=dict(color="#FF9F43", width=3)))
    fig1.update_layout(**layout_charts, height=260)
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

with row2_col2:
    st.markdown("""<div class="panel-title-bar">💸 PAINEL 2: FLUXO DE CAIXA MENSAL EM CASCATA</div>""", unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Faturamento Bruto"], name="Fat. Reajustado", line=dict(color="#FBBF24", width=4)))
    fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Fat. Sem Reajuste"], name="Fat. Sem Reajuste", line=dict(color="#4b5563", width=1.5, dash='dash')))
    fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Lucro Líquido"], name="Lucro Líq.", line=dict(color="#A78BFA", width=2), fill='tozeroy', fillcolor='rgba(167, 139, 250, 0.01)'))
    fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Saque Mensal"], name="Seu Saque", line=dict(color="#F43F5E", width=1.5, dash='dash')))
    fig2.update_layout(**layout_charts, height=260)
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)

# --- LINHA 3: COMPARATIVO EM JUROS COMPOSTOS E INSIGHTS ---
row3_col1, row3_col2 = st.columns([1.2, 1])

with row3_col1:
    st.markdown("""<div class="panel-title-bar">🏛️ PAINEL 3: DESTRUIÇÃO DE ALTERNATIVAS DO MERCADO</div>""", unsafe_allow_html=True)
    fig3 = go.Figure(go.Bar(
        x=[retorno_solar_total, retorno_cdi_final, retorno_imovel_final],
        y=["Império Solar", "Renda Fixa (CDI)", "Imóvel Físico"],
        orientation='h',
        marker_color=['#10B981', '#334155', '#1e293b']
    ))
    fig3.update_layout(
        paper_bgcolor='#131722', plot_bgcolor='#131722',
        font=dict(color='#787b86', size=10),
        xaxis=dict(showgrid=True, gridcolor='#2a2e39'),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=15, t=15, b=15), height=160
    )
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

with row3_col2:
    st.markdown("""<div class="panel-title-bar">📝 INSIGHT ESTRATÉGICO PARA O PITCH</div>""", unsafe_allow_html=True)
    multiplicador = retorno_solar_total / (retorno_cdi_final if retorno_cdi_final > 0 else 1)
    st.markdown(f"""
        <div style="background-color: #131722; border: 1px solid #2a2e39; border-radius: 0 0 4px 4px; padding: 20px; height: 160px; font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">
            Ao adotar a estratégia selecionada, o capital injetado se multiplica de forma geométrica através do efeito caixa livre. 
            Enquanto as aplicações tradicionais prendem o investidor em uma linha reta corroída pela inflação, o modelo operacional 
            solar entrega um retorno total estimado de <b style="color:#10b981;">{multiplicador:.1f}x maior que o CDI</b>, capitalizando a tarifa reajustada em patrimônio líquido consolidado.
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- LINHA 4: TABELA MÊS A MÊS ATUALIZADA ---
st.markdown("""<div class="panel-title-bar">📋 TABELA DE AUDITORIA DO TERMINAL (MÊS A MÊS)</div>""", unsafe_allow_html=True)
st.dataframe(df.style.format({
    "Faturamento Bruto": formato_real,
    "Fat. Sem Reajuste": formato_real,
    "Parcelas Banco": formato_real,
    "Lucro Líquido": formato_real,
    "Saque Mensal": formato_real,
    "Caixa Acumulado": formato_real,
    "Patrimônio Usinas": formato_real,
    "Valor Total Negócio": formato_real
}), use_container_width=True, height=250, hide_index=True)
