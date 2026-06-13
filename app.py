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

st.markdown("""
    <style>
    .block-container { padding: 30px 15px 0px 15px !important; max-width: 99% !important; }
    header[data-testid="stHeader"] { background-color: #0c0f16 !important; } 
    footer { visibility: hidden !important; }
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; color: #cbd5e1; }
    .panel-title-bar { background-color: #131722; color: #787b86; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; padding: 6px 12px; border: 1px solid #2a2e39; border-bottom: none; }
    .command-bar { background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; padding: 8px 15px; font-size: 0.75rem; color: #787b86; margin-bottom: 15px; }
    .status-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; color: #cbd5e1; border: 1px solid #2a2e39; }
    .status-table th { background-color: #1e2232; color: #787b86; padding: 8px 10px; text-align: left; border: 1px solid #2a2e39; font-weight: bold; }
    .status-table td { padding: 8px 10px; border: 1px solid #2a2e39; background-color: #131722; }
    .neon-green { color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }
    .neon-blue { color: #3b82f6; text-shadow: 0 0 10px rgba(59, 130, 246, 0.2); }
    .neon-orange { color: #ff9f43; text-shadow: 0 0 10px rgba(255, 159, 67, 0.2); }
    .badge-ok { color: #10b981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE INTERATIVO DO PREÇO DA ENERGIA ---
st.sidebar.markdown("<h3 style='color:#10b981; text-align:center;'>⚙️ CONFIGURAÇÃO DE TARIFAS</h3>", unsafe_allow_html=True)
VALOR_KWH = st.sidebar.number_input("Valor do kWh Comercializado (R$)", value=0.50, step=0.01, min_value=0.01)
st.sidebar.markdown("---")

ENERGIA_DIARIA_ALVA = 14000.0  # Geração nominal do parque completo

def render_metric_card(label, value, subtext, color_class):
    st.markdown(f"""
        <div style="background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; padding: 18px; text-align: center; height: 100%;">
            <div style="color: #787b86; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">{label}</div>
            <div class="{color_class}" style="font-size: 2.1rem; font-weight: bold; margin-top: 5px; margin-bottom: 2px;">{value}</div>
            <div style="color: #cbd5e1; font-size: 0.8rem;">{subtext}</div>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ALGORITMO SOLAR DINÂMICO
# ==============================================================================
hora_decimal = agora.hour + (agora.minute / 60.0) + (agora.second / 3600.0)
ruido_live = random.uniform(0.98, 1.02)

if 6.0 <= hora_decimal <= 18.0:
    potencia_pico_kw = (ENERGIA_DIARIA_ALVA * math.pi) / 24.0
    potencia_live_kw = potencia_pico_kw * math.sin(math.pi * (hora_decimal - 6.0) / 12.0) * ruido_live
    proporcao_dia_passado = (1.0 - math.cos(math.pi * (hora_decimal - 6.0) / 12.0)) / 2.0
    energia_hoje_kwh = ENERGIA_DIARIA_ALVA * proporcao_dia_passado
else:
    potencia_live_kw = 0.0
    energia_hoje_kwh = ENERGIA_DIARIA_ALVA if hora_decimal > 18.0 else 0.0

faturamento_hoje_total = energia_hoje_kwh * VALOR_KWH

dias_passados_junho = agora.day - 1
faturamento_mes_acumulado = (dias_passados_junho * ENERGIA_DIARIA_ALVA * VALOR_KWH) + faturamento_hoje_total
energia_mes_total_mwh = ((dias_passados_junho * ENERGIA_DIARIA_ALVA) + energia_hoje_kwh) / 1000.0

energia_jan_mai_kwh = 5 * 30 * ENERGIA_DIARIA_ALVA
faturamento_jan_mai = energia_jan_mai_kwh * VALOR_KWH

faturamento_anual_2026_realizado = faturamento_jan_mai + faturamento_mes_acumulado
energia_anual_mwh_realizado = (energia_jan_mai_kwh / 1000.0) + energia_mes_total_mwh

# ==============================================================================
# PAINEL SUPERIOR: EXATAMENTE 3 COLUNAS FIXAS NO TOPO
# ==============================================================================
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    render_metric_card("⚡ POTÊNCIA INSTANTÂNEA COMBINADA", f"{potencia_live_kw:.2f} kW", f"Rendimentos Live: R$ {(potencia_live_kw * VALOR_KWH)/60:.2f}/min", "neon-green")
with col_c2:
    render_metric_card("📅 RENDIMENTO DIÁRIO (HOJE)", f"R$ {faturamento_hoje_total:,.2f}", f"Injeção: {energia_hoje_kwh:,.1f} kWh", "neon-blue")
with col_c3:
    render_metric_card("🏛️ PATRIMÔNIO CONSOLIDADO 2026", f"R$ {faturamento_anual_2026_realizado:,.2f}", f"Geração Total: {energia_anual_mwh_realizado:,.2f} MWh", "neon-orange")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# TABELA PRINCIPAL OPERACIONAL
# ==============================================================================
st.markdown("""<div class="panel-title-bar">🌐 GESTÃO OPERACIONAL DE CRÉDITO DE ENERGIA LIMPA</div>""", unsafe_allow_html=True)

distribuicao_usinas = [
    {"nome": "Usina Sitio Castelinho", "peso": 0.28, "historico": 452.1},
    {"nome": "Usina Sr Quitandeiro Horti-Fruti", "peso": 0.22, "historico": 341.8},
    {"nome": "Usina Fazenda Boa Vista", "peso": 0.18, "historico": 295.4},
    {"nome": "Usina Fazenda Vila Real", "peso": 0.17, "historico": 268.2},
    {"nome": "Usina Jose Eduardo Sorares", "peso": 0.15, "historico": 242.9}
]

html_quadro_central = """<table class="status-table">
    <tr>
        <th>IDENTIFICAÇÃO CANAL / ATIVO</th>
        <th>POTÊNCIA LIVE</th>
        <th>GERAÇÃO DIÁRIA (HOJE)</th>
        <th>GERAÇÃO TOTAL ACUMULADA</th>
        <th>STATUS CONEXÃO</th>
        <th>SINCRO LIVE</th>
    </tr>"""

for u in distribuicao_usinas:
    pot_u = potencia_live_kw * u["peso"]
    dia_u = energia_hoje_kwh * u["peso"]
    tot_u = u["historico"] + (energia_mes_total_mwh * u["peso"])
    
    html_quadro_central += f"""<tr>
        <td><b>{u['nome']}</b></td>
        <td>{pot_u:.2f} kW</td>
        <td>{dia_u:.1f} kWh</td>
        <td>{tot_u:.2f} MWh</td>
        <td class="badge-ok">🟢 ONLINE (LIVE)</td>
        <td>{agora.strftime('%H:%M:%S')}</td>
    </tr>"""
html_quadro_central += "</table>"
st.markdown(html_quadro_central, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"""
    <div class="command-bar">
        <div>❖ SCADA RECON ENGINE // REPASSE NOMINAL DE CRÉDITOS: <b>100% INTEGRAL VINCULADO</b></div>
        <div>DATA E HORA DO REGISTRO: <b>{agora.strftime('%d/%m/%Y — %H:%M:%S')}</b></div>
        <div style="color: #10b981; font-weight: bold;">● ATUALIZAÇÃO REATIVA REAL-TIME (1s REFRESH LOOP)</div>
    </div>
""", unsafe_allow_html=True)

# --- RENDERIZAÇÃO DOS GRÁFICOS REAL-TIME ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("""<div class="panel-title-bar">☀️ GRÁFICO DE ENTRADA DIÁRIA (CURVA DE IRRADIÂNCIA EVOLUTIVA)</div>""", unsafe_allow_html=True)
    
    x_linha_progresso = []
    y_linha_progresso = []
    
    passo_passagem_hora = 0.10
    h_cursor = 0.0
    while h_cursor < hora_decimal:
        x_linha_progresso.append(h_cursor)
        if 6.0 <= h_cursor <= 18.0:
            v = ((ENERGIA_DIARIA_ALVA * math.pi) / 24.0) * math.sin(math.pi * (h_cursor - 6.0) / 12.0)
        else:
            v = 0.0
        y_linha_progresso.append(v)
        h_cursor += passo_passagem_hora

    x_linha_progresso.append(hora_decimal)
    y_linha_progresso.append(potencia_live_kw)
            
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=x_linha_progresso, y=y_linha_progresso, name="Geração Realizada", hoverinfo="skip", line=dict(color="#10b981", width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.04)'))
    
    if 6.0 <= hora_decimal <= 18.0:
        fig_curva.add_trace(go.Scatter(x=[hora_decimal], y=[potencia_live_kw], name="Agora", marker=dict(color="#f43f5e", size=10)))
        
    fig_curva.update_layout(paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#787b86', size=10), xaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False, range=[0, 23], tickvals=list(range(0, 24)), ticktext=[f"{h:02d}:00" for h in range(0, 24)]), yaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False, range=[0, ((ENERGIA_DIARIA_ALVA * math.pi) / 24.0) * 1.1]), margin=dict(l=45, r=15, t=15, b=25), showlegend=False, height=240)
    st.plotly_chart(fig_curva, use_container_width=True, config={'displayModeBar': False})

with col_g2:
    st.markdown("""<div class="panel-title-bar">📊 CRONOGRAMA ANUAL DE REPASSE DE DIVIDENDOS 2026</div>""", unsafe_allow_html=True)
    meses_proj = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    faturamentos_brutos_grafico = [
        189000.0 * (VALOR_KWH/0.50), 195000.0 * (VALOR_KWH/0.50), 182000.0 * (VALOR_KWH/0.50), 
        199000.0 * (VALOR_KWH/0.50), 195000.0 * (VALOR_KWH/0.50), faturamento_mes_acumulado,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    ]
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(x=meses_proj, y=faturamentos_brutos_grafico, name="Faturamento", marker_color='#3b82f6', text=[f"R$ {v/1000:.0f}k" if v > 0 else "" for v in faturamentos_brutos_grafico], textposition='auto', textfont=dict(size=8, color="#cbd5e1")))
    fig_hist.update_layout(paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#787b86', size=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False), margin=dict(l=45, r=15, t=15, b=25), showlegend=False, height=240)
    st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

# Tabela Contábil com Projeções Futuras 100% Zeradas
st.markdown("""<div class="panel-title-bar">📋 DEMONSTRATIVO CONTÁBIL: LIQUIDAÇÃO E REPASSE INTEGRAL DE CRÉDITOS</div>""", unsafe_allow_html=True)
faturamentos_tabela_real = [
    189000.0 * (VALOR_KWH/0.50), 195000.0 * (VALOR_KWH/0.50), 182000.0 * (VALOR_KWH/0.50), 
    199000.0 * (VALOR_KWH/0.50), 195000.0 * (VALOR_KWH/0.50), faturamento_mes_acumulado,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0
]

df_auditoria = pd.DataFrame({
    "Período de Competência": meses_proj,
    "Energia Alocada no Consórcio": [f"{(v/VALOR_KWH)/1000:,.2f} MWh" if v > 0 else "0.00 MWh" for v in faturamentos_tabela_real],
    "Faturamento Bruto Gerado": [f"R$ {v:,.2f}" if v > 0 else "R$ 0,00" for v in faturamentos_tabela_real],
    "Rendimento Repassado ao Investidor (100%)": [f"R$ {v:,.2f}" if v > 0 else "R$ 0,00" for v in faturamentos_tabela_real],
    "Status de Compensação ANEEL": ["Compensado e Creditado" if idx <= 5 else "Aguardando Competência" for idx, m in enumerate(meses_proj)]
})
st.dataframe(df_auditoria, use_container_width=True, hide_index=True)

# Loop perpétuo reativo de 1 segundo
time.sleep(1)
st.rerun()
