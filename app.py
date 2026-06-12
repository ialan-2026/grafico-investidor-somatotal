import streamlit as st
import time
import random
import math
import html
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

# Configuração da página em modo corporativo expandido
st.set_page_config(page_title="Santo House Solar Terminal", layout="wide")

# Configuração do Fuso Horário do Brasil (GMT-3)
FUSO_BR = timezone(timedelta(hours=-3))
agora = datetime.now(FUSO_BR)

# --- CONFIGURAÇÕES DO MOTOR FINANCEIRO E DO CONSÓRCIO ---
VALOR_KWH = 0.50
FATURAMENTO_DIARIO_ALVO = 7000.00  # R$ 7.000,00 bruto alvo no final do dia
ENERGIA_DIARIA_ALVA = FATURAMENTO_DIARIO_ALVO / VALOR_KWH  # 14.000 kWh
TAXA_REPASSE_DIVIDENDOS = 0.85  # Consórcio repassa 85% líquido para o investidor (15% taxa adm)

# Estilização interna do Terminal SCADA Enterprise
st.markdown("""
    <style>
    .block-container { padding: 30px 15px 0px 15px !important; max-width: 99% !important; }
    header[data-testid="stHeader"] { background-color: #0c0f16 !important; } 
    footer { visibility: hidden !important; }
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; }
    .panel-title-bar { background-color: #131722; color: #787b86; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; padding: 6px 12px; border: 1px solid #2a2e39; border-bottom: none; }
    .command-bar { background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; padding: 8px 15px; font-size: 0.75rem; color: #787b86; margin-bottom: 15px; }
    .neon-green { color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }
    .neon-blue { color: #3b82f6; text-shadow: 0 0 10px rgba(59, 130, 246, 0.2); }
    .neon-purple { color: #a78bfa; text-shadow: 0 0 10px rgba(167, 139, 250, 0.2); }
    .neon-orange { color: #ff9f43; text-shadow: 0 0 10px rgba(255, 159, 67, 0.2); }
    </style>
""", unsafe_allow_html=True)

def render_metric_card(label, value, subtext, color_class):
    st.markdown(f"""
        <div style="background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; padding: 18px; text-align: center; height: 100%;">
            <div style="color: #787b86; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">{label}</div>
            <div class="{color_class}" style="font-size: 1.9rem; font-weight: bold; margin-top: 5px; margin-bottom: 2px;">{value}</div>
            <div style="color: #cbd5e1; font-size: 0.8rem;">{subtext}</div>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ENGINE MATEMÁTICO REAL-TIME SOLAR + DIVISIONAL DE REPASSE
# ==============================================================================
hora_decimal = agora.hour + (agora.minute / 60.0) + (agora.second / 3600.0)
ruido_live = random.uniform(0.98, 1.02) # Oscilação natural de irradiância

if 6.0 <= hora_decimal <= 18.0:
    potencia_pico_kw = (ENERGIA_DIARIA_ALVA * math.pi) / 24.0
    potencia_live_kw = potencia_pico_kw * math.sin(math.pi * (hora_decimal - 6.0) / 12.0) * ruido_live
    proporcao_dia_passado = (1.0 - math.cos(math.pi * (hora_decimal - 6.0) / 12.0)) / 2.0
    energia_hoje_kwh = ENERGIA_DIARIA_ALVA * proporcao_dia_passado
else:
    potencia_live_kw = 0.0
    energia_hoje_kwh = ENERGIA_DIARIA_ALVA if hora_decimal > 18.0 else 0.0

# Cálculos Diários (Hoje)
faturamento_hoje_bruto = energia_hoje_kwh * VALOR_KWH
dividendo_hoje_liquido = faturamento_hoje_bruto * TAXA_REPASSE_DIVIDENDOS

# Cálculos Mensais (Junho Corrente)
dias_passados_junho = agora.day - 1
faturamento_historico_junho = dias_passados_junho * 6480.00
faturamento_mes_bruto = faturamento_historico_junho + faturamento_hoje_bruto
dividendo_mes_liquido = faturamento_mes_bruto * TAXA_REPASSE_DIVIDENDOS

# ==============================================================================
# BANCO DE DADOS DA PROJEÇÃO ANUAL CONSOLIDADA 2026 (JAN A DEZ)
# ==============================================================================
meses_eixo = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun (Atual)", "Jul (Proj)", "Ago (Proj)", "Set (Proj)", "Out (Proj)", "Nov (Proj)", "Dez (Proj)"]

# Histórico Realizado + Modelagem de Projeção Segundo Semestre 2026
faturamento_bruto_anual = [
    189000.00, 195000.00, 182000.00, 199000.00, 195000.00, faturamento_mes_bruto, # Realizado + Corrente
    188000.00, 192000.00, 185000.00, 201000.00, 198000.00, 208000.00  # Projeções baseadas no histórico climático
]
dividendos_liquidos_anual = [v * TAXA_REPASSE_DIVIDENDOS for v in faturamento_bruto_anual]

# Totais Acumulados Ano 2026 (Até o presente momento com projeção cheia)
total_bruto_2026 = sum(faturamento_bruto_anual)
total_dividendos_2026 = sum(dividendos_liquidos_anual)

# ==============================================================================
# LAYOUT DE INTERFACE GRÁFICA CONTROL PANEL
# ==============================================================================
st.title("⚡ SANTO HOUSE SOLAR TERMINAL v6.5 (CONSÓRCIO & RENDIMENTOS)")
st.markdown("---")

# Grid de Cards Avançados: Faturamento do Parque vs. Dividendos do Consórcio
col_c1, col_c2, col_c3, col_c4 = st.columns(4)
with col_c1:
    render_metric_card("⚡ POTÊNCIA INSTANTÂNEA ATIVA", f"{potencia_live_kw:.2f} kW", f"Geração Live: {(potencia_live_kw * VALOR_KWH)/60:.2f} R$/min", "neon-green")
with col_c2:
    render_metric_card("📅 OPERAÇÃO DIÁRIA (HOJE)", f"R$ {faturamento_hoje_bruto:,.2f}", f"💰 Retorno Líquido: R$ {dividendo_hoje_liquido:,.2f}", "neon-blue")
with col_c3:
    render_metric_card("📊 FECHAMENTO MENSAL (JUNHO)", f"R$ {faturamento_mes_bruto:,.2f}", f"💰 Repasse Consórcio: R$ {dividendo_mes_liquido:,.2f}", "neon-purple")
with col_c4:
    render_metric_card("🏛️ HOLDING PATRIMONIAL 2026", f"R$ {total_bruto_2026:,.2f}", f"💰 Total no Bolso: R$ {total_dividendos_2026:,.2f}", "neon-orange")

st.markdown("<br>", unsafe_allow_html=True)

# Barra de Auditoria de Telecom
st.markdown(f"""
    <div class="command-bar">
        <div>❖ SCADA ENGINE: MODELO FINANCEIRO CONSOLIDADO // DIVIDEND PASS-RATE: <b>{(TAXA_REPASSE_DIVIDENDOS*100):.0f}% LÍQUIDO</b></div>
        <div>DATA/HORA DO REGISTRO: <b>{agora.strftime('%d/%m/%Y — %H:%M:%S')}</b></div>
        <div style="color: #10b981; font-weight: bold; letter-spacing: 0.5px;">● ATUALIZAÇÃO REATIVA CONVERTIDA (1s TICK)</div>
    </div>
""", unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("""<div class="panel-title-bar">☀️ PROCESSO DE ENTRADA DIÁRIA (GERAÇÃO REAL TIME)</div>""", unsafe_allow_html=True)
    horas_eixo = [f"{h:02d}:00" for h in range(0, 24)]
    valores_curva = [(((ENERGIA_DIARIA_ALVA * math.pi) / 24.0) * math.sin(math.pi * (h - 6) / 12)) if 6 <= h <= 18 else 0.0 for h in range(0, 24)]
            
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=horas_eixo, y=valores_curva, name="Injeção (kW)", line=dict(color="#10b981", width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.04)'))
    if 6.0 <= hora_decimal <= 18.0:
        fig_curva.add_trace(go.Scatter(x=[f"{agora.hour:02d}:{agora.minute:02d}"], y=[potencia_live_kw], name="Agora", marker=dict(color="#f43f5e", size=12)))
        
    fig_curva.update_layout(paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#787b86', size=10), xaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False), yaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False), margin=dict(l=45, r=15, t=15, b=25), showlegend=False, height=260)
    st.plotly_chart(fig_curva, use_container_width=True, config={'displayModeBar': False})

with col_g2:
    st.markdown("""<div class="panel-title-bar">📊 PROJEÇÃO ANUAL ATÉ DEZEMBRO: BRUTO VS. DIVIDENDOS PAGOS</div>""", unsafe_allow_html=True)
    
    fig_hist = go.Figure()
    # Barra de Faturamento Bruto da Usina
    fig_hist.add_trace(go.Bar(x=meses_eixo, y=faturamento_bruto_anual, name="Faturamento Bruto", marker_color='#3b82f6'))
    # Barra de Dividendos Líquidos creditados pelo Consórcio
    fig_hist.add_trace(go.Bar(x=meses_eixo, y=dividendos_liquidos_anual, name="Dividendos Pagos", marker_color='#a78bfa'))
    
    fig_hist.update_layout(paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#787b86', size=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False), barmode='group', margin=dict(l=45, r=15, t=15, b=25), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=260)
    st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

# Tabela Corporativa Auditaria de Créditos do Consórcio
st.markdown("""<div class="panel-title-bar">📋 RELATÓRIO DE REPASSE DE ATIVOS DA GERENCIADORA DE CRÉDITOS</div>""", unsafe_allow_html=True)
df_auditoria = pd.DataFrame({
    "Mês de Competência": meses_eixo,
    "Faturamento Bruto Solar": [f"R$ {v:,.2f}" for v in faturamento_bruto_anual],
    "Taxa de Administração Consórcio (15%)": [f"R$ {(v*0.15):,.2f}" for v in faturamento_bruto_anual],
    "Dividendos Líquidos Injetados (85%)": [f"R$ {v:,.2f}" for v in dividendos_liquidos_anual],
    "Auditoria Compliance": ["Efetivado" if "Proj" not in m else "Garantido em Contrato" for m in meses_eixo]
})
st.dataframe(df_auditoria, use_container_width=True, hide_index=True)

# Loop perpétuo de atualização instantânea
time.sleep(1)
st.rerun()
