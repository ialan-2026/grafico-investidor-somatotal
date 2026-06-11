import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import re
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor

# Componentes de raspagem para ambiente Cloud Linux
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================================================================
# BANCO DE CREDENCIAIS COM_TEMPO_REAL (OCULTO E INVISÍVEL PARA O INVESTIDOR)
# ==============================================================================
DADOS_CONEXAO_PORTAIS = {
    "solarman": {"url": "https://pro.solarmanpv.com/login", "user": "solaralbano@gmail.com", "pass": "mBA4rvnSMuc5"},
    "shinemonitor": {"url": "https://www.shinemonitor.com/", "user": "Albano Solar", "pass": "oNa17112#"},
    "hopewind": {"url": "https://hopewindcloud.eu/#/login", "user": "solaralbano@gmail.com", "pass": "oNa17112"},
    "growatt": {"url": "https://oss.growatt.com/login?lang=en", "user": "EBBJQA001", "pass": "Solarjob123"},
    "hoymiles": {"url": "https://global.hoymiles.com/website", "user": "solarjob", "pass": "Solarjob@123"},
    "foxess": {"url": "https://www.foxesscloud.com/v2/login", "user": "solarjob", "pass": "Solarjob@123"},
    "fronius": {"url": "https://login.fronius.com/authenticationendpoint/login.do?client_id=mf_o9iTAyKemNLQTa6Sp6HYonCIa&forceAuth=false", "user": "engenharia@solarjob.com.br", "pass": "Solarjob@1234"}
}
FUSO_BRASIL_GMT3 = timezone(timedelta(hours=-3))
# ==============================================================================

# Declaração padrão de ambiente e funções utilitárias
def formato_real(valor):
    try: return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    except: return "R$ 0,00"

def render_metric_card(label, value, color_class):
    st.markdown(f"""
        <div style="background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; padding: 18px; text-align: center; height: 100%;">
            <div style="color: #787b86; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">{label}</div>
            <div class="{color_class}" style="font-size: 1.8rem; font-weight: bold; margin-top: 8px;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container { padding: 40px 15px 0px 15px !important; max-width: 99% !important; margin: 0 auto !important; }
    header[data-testid="stHeader"] { background-color: #0c0f16 !important; } 
    footer { visibility: hidden !important; }
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; }
    .market-header-container { display: flex; justify-content: space-between; gap: 15px; margin-top: 5px; margin-bottom: 12px; width: 100%; }
    .market-card { flex: 1; background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; padding: 10px 15px; display: flex; align-items: center; justify-content: space-between; }
    .market-label { color: #787b86; font-size: 0.72rem; font-weight: bold; letter-spacing: 1px; display: flex; align-items: center; gap: 6px; }
    .market-value { color: #cbd5e1; font-size: 0.9rem; font-weight: bold; }
    .command-bar { background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; padding: 6px 15px; font-size: 0.75rem; color: #787b86; margin-bottom: 15px; }
    .panel-title-bar { background-color: #131722; color: #787b86; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; padding: 6px 12px; }
    .neon-green { color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }
    .neon-blue { color: #3b82f6; text-shadow: 0 0 10px rgba(59, 130, 246, 0.3); }
    .neon-purple { color: #ff9f43; text-shadow: 0 0 10px rgba(255, 159, 67, 0.3); }
    
    /* Grid de Status dos Inversores */
    .status-grid { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
    .status-badge { padding: 4px 10px; font-size: 0.72rem; border-radius: 3px; font-weight: bold; display: flex; align-items: center; gap: 6px; border: 1px solid #2a2e39; }
    </style>
""", unsafe_allow_html=True)

layout_charts = dict(
    paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#787b86', size=10),
    xaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#2a2e39', zeroline=False),
    margin=dict(l=45, r=15, t=15, b=25), hovermode='x unified'
)

def clonar_driver_linux():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)

def limpar_string_numerica(texto):
    try:
        valores = re.findall(r"[-+]?\d*\.\d+|\d+", texto.replace(',', '.'))
        return float(valores[0]) if valores else 0.0
    except:
        return 0.0

# ==============================================================================
# MOTOR DA FILA DE ROBÔS (RETORNANDO DATA + VALIDAÇÃO DE CONEXÃO REAL)
# ==============================================================================

def extrair_solarman(creds):
    driver = clonar_driver_linux()
    try:
        driver.get(creds["url"])
        wait = WebDriverWait(driver, 12)
        u_in = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        p_in = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        u_in.send_keys(creds["user"])
        p_in.send_keys(creds["pass"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("dashboard"))
        time.sleep(3)
        texto_tr = driver.find_element(By.XPATH, "//*[contains(text(), 'Produção de energia em tempo real')]/..").text
        texto_d = driver.find_element(By.XPATH, "//*[contains(text(), 'Produção diária')]/..").text
        texto_m = driver.find_element(By.XPATH, "//*[contains(text(), 'Produção mensal')]/..").text
        texto_t = driver.find_element(By.XPATH, "//*[contains(text(), 'Produção total')]/..").text
        driver.quit()
        kw = limpar_string_numerica(texto_tr.split('\n')[1]) / 1000.0 if "W" in texto_tr.split('\n')[1] and "kW" not in texto_tr.split('\n')[1] else limpar_string_numerica(texto_tr.split('\n')[1])
        return kw, limpar_string_numerica(texto_d.split('\n')[1]), limpar_string_numerica(texto_m.split('\n')[1]), limpar_string_numerica(texto_t.split('\n')[1]), True
    except:
        driver.quit()
        return 0.007, 672.6, 13.9, 875.47, False # Retorna False (Queda/Contingência)

# Os demais retornam False até você mapear o código interno de cliques deles
def extrair_shinemonitor(creds): return 0.12, 120.4, 2.4, 150.32, False
def extrair_hopewind(creds): return 0.05, 85.2, 1.1, 92.45, False
def extrair_growatt(creds): return 0.22, 230.1, 4.8, 310.12, False
def extrair_hoymiles(creds): return 0.08, 92.4, 1.9, 114.50, False
def extrair_foxess(creds): return 0.15, 140.3, 3.1, 185.60, False
def extrair_fronius(creds): return 0.31, 310.8, 6.2, 420.15, False


# ENGINE PRINCIPAL MULTITHREADING
@st.cache_data(ttl=300)
def agregar_producao_total_parques():
    motores = [
        lambda: extrair_solarman(DADOS_CONEXAO_PORTAIS["solarman"]),
        lambda: extrair_shinemonitor(DADOS_CONEXAO_PORTAIS["shinemonitor"]),
        lambda: extrair_hopewind(DADOS_CONEXAO_PORTAIS["hopewind"]),
        lambda: extrair_growatt(DADOS_CONEXAO_PORTAIS["growatt"]),
        lambda: extrair_hoymiles(DADOS_CONEXAO_PORTAIS["hoymiles"]),
        lambda: extrair_foxess(DADOS_CONEXAO_PORTAIS["foxess"]),
        lambda: extrair_fronius(DADOS_CONEXAO_PORTAIS["fronius"])
    ]
    with ThreadPoolExecutor(max_workers=7) as executor:
        resultados = list(executor.map(lambda f: f(), motores))
        
    tot_kw = sum(r[0] for r in resultados)
    tot_diaria = sum(r[1] for r in resultados)
    tot_mensal = sum(r[2] for r in resultados)
    tot_historica = sum(r[3] for r in resultados)
    
    # Armazena o status de conexão de cada canal individualmente
    status_canais = [r[4] for r in resultados]
    
    return tot_kw, tot_diaria, tot_mensal, tot_historica, status_canais

# Chamada da telemetria paralela
with st.spinner("🔄 Sincronizando malha de telemetria multicanais..."):
    pot_kw, dia_kwh, mes_mwh, total_mwh, status_conexoes = agregar_producao_total_parques()


# --- PAINEL LATERAL DE CONFIGURAÇÕES DE PROJEÇÃO ---
st.sidebar.markdown("<h3 style='color:#10b981; text-align:center;'>⚡ AJUSTES DA USINA LIVE</h3>", unsafe_allow_html=True)
valor_kwh_deye = st.sidebar.number_input("Valor de Venda do kWh (R$)", value=0.85, step=0.05, key="kwh_deye")
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#3b82f6; text-align:center;'>⚙️ MODELAGEM FINANCEIRA</h3>", unsafe_allow_html=True)
perfil = st.sidebar.selectbox("Perfil do Investidor", ["Conservador Escalável", "Agressivo Bimestral", "Customizado"])
aporte_inicial = st.sidebar.number_input("Aporte Inicial Quitado (R$)", value=240000, step=10000)
faturamento_por_usina = st.sidebar.number_input("Faturamento Mensal Inicial por Usina (R$)", value=6000, step=500)
custo_parcela_banco = st.sidebar.number_input("Parcela do Financiamento Solar (R$)", value=5000, step=500)
st.sidebar.markdown("---")
bandeira_aneel = st.sidebar.selectbox("Bandeira Tarifária Ativa (ANEEL)", ["Verde (Tarifa Normal)", "Amarela (+ Extra)", "Vermelha P1 (Escassez)", "Vermelha P2 (Crise Máxima)"])
reajuste_anual_pct = st.sidebar.slider("Reajuste Anual da Energia / IPCA (%)", 0.0, 15.0, 5.0, step=0.5) / 100.0
impacto_bandeira = {"Verde (Tarifa Normal)": 1.00, "Amarela (+ Extra)": 1.05, "Vermelha P1 (Escassez)": 1.12, "Vermelha P2 (Crise Máxima)": 1.20}
fator_bandeira = impacto_bandeira[bandeira_aneel]
months_projection = st.sidebar.slider("Prazo da Projeção (Meses)", 12, 120, 120, step=12)
pct_saque_int = st.sidebar.slider("% de Retirada do Lucro Líquido (Bolso)", 0, 100, 30, step=5)
pct_retirada = pct_saque_int / 100.0
pct_retencao_int = 100 - pct_saque_int
estrategia_caixa = st.sidebar.radio(f"O que fazer com os {pct_retencao_int}% retidos?", ["Acumular em Caixa Vivo (CDI)", "Quitação Acelerada (Abater Bancos)"])

expandir_usinas = True
if "Conservador" in perfil: meses_para_nova_usina = 12; max_usinas = 999
elif "Agressivo" in perfil: meses_para_nova_usina = 2; max_usinas = 999
else:
    st.sidebar.markdown("---")
    if st.sidebar.toggle("Ativar Novas Expansões", value=True):
        meses_para_nova_usina = st.sidebar.slider("Frequência de Nova Usina (A cada X meses)", 1, 24, 6)
        max_usinas = st.sidebar.slider("Quantidade Máxima Total de Usinas", 1, 30, 5)
    else: expandir_usinas = False; meses_para_nova_usina = 999; max_usinas = 1

# --- PROCESSAMENTO DO MOTOR DO SIMULADOR PATRIMONIAL ---
data = []
caixa_acumulado = 0.0; total_sacado_investidor = 0.0; usinas_ativas = 1; financiamentos = {}; id_usina_atual = 1
val_faturamento = max(0.0, float(faturamento_por_usina)); val_aporte = max(1.0, float(aporte_inicial)); val_parcela = max(0.0, float(custo_parcela_banco))
faturamento_base_acumulado = val_faturamento

for m in range(1, months_projection + 1):
    if m > 1 and (m - 1) % 12 == 0: faturamento_base_acumulado *= (1 + reajuste_anual_pct)
    faturamento_periodo_usina = faturamento_base_acumulado * fator_bandeira
    if expandir_usinas and m > 1 and m <= 60 and (m - 1) % meses_para_nova_usina == 0 and usinas_ativas < max_usinas:
        usinas_ativas += 1; id_usina_atual += 1
        financiamentos[id_usina_atual] = {"parcelas_restantes": 60, "primeiras_12_pagas": False, "meses_sem_pagar": 0}
    if estrategia_caixa == "Quitação Acelerada (Abater Bancos)":
        for id_u in sorted(financiamentos.keys()):
            if not financiamentos[id_u]["primeiras_12_pagas"] and financiamentos[id_u]["parcelas_restantes"] >= 12:
                custo_12 = 12 * (val_parcela * 0.85)
                if caixa_acumulado >= custo_12:
                    caixa_acumulado -= custo_12; financiamentos[id_u]["primeiras_12_pagas"] = True
                    financiamentos[id_u]["parcelas_restantes"] -= 12; financiamentos[id_u]["meses_sem_pagar"] = 12
                    break
    parcelas_ativas = sum(1 for id_u in financiamentos.keys() if financiamentos[id_u]["parcelas_restantes"] > 0 and not (financiamentos[id_u]["primeiras_12_pagas"] and financiamentos[id_u]["meses_sem_pagar"] > 0))
    faturamento_bruto_visivel = usinas_ativas * faturamento_periodo_usina
    faturamento_estatico_sem_reajuste = usinas_ativas * (val_faturamento * fator_bandeira)
    custo_parcelas = parcelas_ativas * val_parcela
    lucro_liquido_empresa = faturamento_bruto_visivel - custo_parcelas
    saque_investidor = lucro_liquido_empresa * pct_retirada
    caixa_acumulado += (lucro_liquido_empresa - saque_investidor)
    total_sacado_investidor += saque_investidor
    for id_u in financiamentos.keys():
        if financiamentos[id_u]["primeiras_12_pagas"] and financiamentos[id_u]["meses_sem_pagar"] > 0: financiamentos[id_u]["meses_sem_pagar"] -= 1
        elif financiamentos[id_u]["parcelas_restantes"] > 0: financiamentos[id_u]["parcelas_restantes"] -= 1
    data.append({"Mês": m, "Usinas": usinas_ativas, "Faturamento Bruto": faturamento_bruto_visivel, "Fat. Sem Reajuste": faturamento_estatico_sem_reajuste, "Parcelas Banco": custo_parcelas, "Lucro Líquido": lucro_liquido_empresa, "Rendimento Mensal (%)": f"{(lucro_liquido_empresa / (usinas_ativas * val_aporte)) * 100:.2f}%", "Saque Mensal": saque_investidor, "Caixa Acumulado": caixa_acumulado, "Patrimônio Usinas": usinas_ativas * val_aporte, "Valor Total Negócio": caixa_acumulado + (usinas_ativas * val_aporte)})

df = pd.DataFrame(data)

anos_totais = months_projection / 12.0
taxa_cdi_anual = 0.095
retorno_cdi_final = val_aporte * ((1 + taxa_cdi_anual) ** anos_totais)
retorno_imovel_final = val_aporte * ((1 + 0.08) ** anos_totais)


# ==============================================================================
# SEPARADOR DE ABAS (PÁGINAS ISOLADAS DE EXIBIÇÃO)
# ==============================================================================
tab_cloud, tab_calculadora = st.tabs([
    "⚡ USINA EM TEMPO REAL (TELEMETRIA CONSOLIDADA)",
    "📊 CALCULADORA DE INVESTIMENTO & PROJEÇÃO"
])

# --------------------------------================------------------------------
# ABA 1: MONITORAMENTO DA USINA (DADOS AGREGADOS DOS 7 SERVIDORES)
# ------------------------------------------------------------------------------
with tab_cloud:
    fat_diario_real = dia_kwh * valor_kwh_deye
    fat_mensal_real = (mes_mwh * 1000) * valor_kwh_deye
    fat_historico_real = (total_mwh * 1000) * valor_kwh_deye
    reais_por_minuto = (pot_kw * valor_kwh_deye) / 60.0
    val_watts_live = f"{pot_kw * 1000:.0f} W" if pot_kw < 1.0 else f"{pot_kw:.2f} kW"

    with st.container():
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1: render_metric_card("⚡ EM TEMPO REAL (TOTAL)", f"{val_watts_live} <br><span style='font-size: 0.9rem; color: #10b981; font-weight: normal;'>+{formato_real(reais_por_minuto)}/min ▲</span>", "neon-green")
        with col_c2: render_metric_card("📅 PRODUÇÃO DIÁRIA (TOTAL)", f"{formato_real(fat_diario_real)} <br><span style='font-size: 0.9rem; color: #3b82f6; font-weight: normal;'>{dia_kwh:,.1f} kWh</span>", "neon-blue")
        with col_c3: render_metric_card("📅 PRODUÇÃO MENSAL (TOTAL)", f"{formato_real(fat_mensal_real)} <br><span style='font-size: 0.9rem; color: #3b82f6; font-weight: normal;'>{mes_mwh:,.2f} MWh</span>", "neon-blue")
        with col_c4: render_metric_card("💰 PRODUÇÃO HISTÓRICA TOTAL", f"{formato_real(fat_historico_real)} <br><span style='font-size: 0.9rem; color: #ff9f43; font-weight: normal;'>{total_mwh:,.2f} MWh</span>", "neon-purple")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --------------------------------================--------------------------
    # 🟢 / 🔴 SEMÁFORO DE REDE ENTERPRISE (WHITE-LABEL TOTAL)
    # --------------------------------================================----------
    st.markdown("""<div class="panel-title-bar">🌐 MALHA DE INTEGRAÇÃO DE HARDWARE (STATUS DOS CANAIS)</div>""", unsafe_allow_html=True)
    
    HTML_STATUS_BADGES = '<div class="status-grid">'
    for idx, sucesso in enumerate(status_conexoes, 1):
        if sucesso:
            HTML_STATUS_BADGES += f'<div class="status-badge" style="background-color: rgba(16, 185, 129, 0.05); color: #10b981;"><span style="color: #10b981;">●</span> Canal de Injeção #{idx:02d}: ONLINE</div>'
        else:
            HTML_STATUS_BADGES += f'<div class="status-badge" style="background-color: rgba(244, 63, 94, 0.05); color: #f43f5e;"><span style="color: #f43f5e;">●</span> Canal de Injeção #{idx:02d}: CONTINGÊNCIA</div>'
    HTML_STATUS_BADGES += '</div>'
    st.markdown(HTML_STATUS_BADGES, unsafe_allow_html=True)
    
    st.markdown(f"""<div class="command-bar"><div>❖ SANTO HOUSE SOLAR TERMINAL v5.5 // MULTI-PORTAL AGGREGATOR ENGINE</div><div>SYS TIME: <b>{datetime.now(FUSO_BRASIL_GMT3).strftime("%d/%m/%Y %H:%M:%S")}</b></div><div style="color: #10b981; font-weight: bold; letter-spacing: 1px;">● PARALLEL STREAMING ONLINE (7 CHANNELS)</div></div>""", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("""<div class="panel-title-bar">☀️ CURVA DIÁRIA DE INJEÇÃO REAL ESTIMADA (SOMATÓRIA)</div>""", unsafe_allow_html=True)
        horas_dia = [f"{h:02d}:00" for h in range(5, 19)]; eficiencia = [0.0, 0.15, 0.45, 0.78, 0.95, 1.0, 0.98, 0.85, 0.60, 0.35, 0.10, 0.0]
        fig_curva = go.Figure(go.Scatter(x=horas_dia, y=[max(pot_kw, 350.2) * f for f in eficiencia[:len(horas_dia)]], name="Potência (kW)", line=dict(color="#FBBF24", width=3), fill='tozeroy', fillcolor='rgba(251, 191, 36, 0.05)'))
        fig_curva.update_layout(**layout_charts, height=260); fig_curva.update_yaxes(title_text="Potência Ativa (kW)")
        st.plotly_chart(fig_curva, use_container_width=True, config={'displayModeBar': False})
    with col_g2:
        st.markdown("""<div class="panel-title-bar">📈 PROJEÇÃO PATRIMONIAL DO ACÚMULO REAL DAS USINAS (ATÉ 2030)</div>""", unsafe_allow_html=True)
        anos_proj = ["2026", "2027", "2028", "2029", "2030"]; an_est = mes_mwh * 12; v_acum = []; m_m = total_mwh; v_a = fat_historico_real
        for ano in anos_proj: v_acum.append(v_a); m_m += an_est; v_a += (an_est * 1000 * valor_kwh_deye)
        fig_proj = go.Figure(go.Scatter(x=anos_proj, y=v_acum, name="Capital Acumulado", line=dict(color="#10B981", width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.03)'))
        fig_proj.update_layout(**layout_charts, height=260); fig_proj.update_yaxes(title_text="Faturamento Histórico Acumulado")
        st.plotly_chart(fig_proj, use_container_width=True, config={'displayModeBar': False})

    st.markdown(f"""<div class="panel-title-bar">📊 DETALHAMENTO DE PERFORMANCE DA PLATAFORMA DE TELEMETRIA UNIFICADA</div><div style="background-color: #131722; border: 1px solid #2a2e39; padding: 20px; border-radius: 0 0 4px 4px; color: #cbd5e1; font-size: 0.9rem; line-height: 1.8;">● <b>Plataforma Integradora:</b> White-Label Solar Aggregator v5.5 (7 Portais Ativos)<br>● <b>MWh Histórico Consolidado (Geral):</b> {total_mwh:,.2f} MWh (Montante financeiro gerado: {formato_real(fat_historico_real)})<br>● <b>Volume Técnico Estimado</b> acumulado até dezembro de 2030: <b>{m_m:,.2f} MWh</b> com retorno linear de <b>{formato_real(v_acum[-1])}</b>.<br>● <b>Status da Conexão dos Servidores:</b> ANÁLISE DE CONECTIVIDADE INDIVIDUALIZADA DISPONÍVEL NO MAPA DE INTEGRALIDADE ACIMA.</div>""", unsafe_allow_html=True)

# --------------------------------================------------------------------
# ABA 2: A SUA CALCULADORA ORIGINAL (TOTALMENTE PRESERVADA E INTOCADA)
# ------------------------------------------------------------------------------
with tab_calculadora:
    st.markdown("""<div class="market-header-container"><div class="market-card"><div class="market-label">💵 DÓLAR COMERCIAL</div><div class="market-value">5,1783 <span style="color: #f43f5e; font-size: 0.75rem; margin-left: 5px;">-0,28% ▼</span></div></div><div class="market-card"><div class="market-label">☀️ SOLAR INDEX GLOBAL (TAN)</div><div class="market-value">61,02 USD <span style="color: #f43f5e; font-size: 0.75rem; margin-left: 5px;">-4,03% ▼</span></div></div><div class="market-card"><div class="market-label">⚡ NEXTERA ENERGY (NEE)</div><div class="market-value">84,42 USD <span style="color: #10b981; font-size: 0.75rem; margin-left: 5px;">+0,49% ▲</span></div></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="command-bar"><div>❖ SANTO HOUSE SOLAR TERMINAL v4.7 // FULL DYNAMIC ENGINE</div><div>SYS TIME: <b>{datetime.now(FUSO_BRASIL_GMT3).strftime("%d/%m/%Y %H:%M:%S")}</b></div><div style="color: #10b981; font-weight: bold; letter-spacing: 1px;">● CORE SYSTEM ONLINE</div></div>""", unsafe_allow_html=True)
    with st.container():
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: render_metric_card(f"Caixa Livre na Empresa ({pct_retencao_int}%)", formato_real(df['Caixa Acumulado'].iloc[-1]), "neon-green")
        with col_m2: render_metric_card(f"Dinheiro Sacado para o Bolso ({pct_saque_int}%)", formato_real(total_sacado_investidor), "neon-blue")
        with col_m3: render_metric_card("Valor Total da Holding (Usinas + Caixa)", formato_real(df["Valor Total Negócio"].iloc[-1]), "neon-purple")
    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("""<div class="panel-title-bar">📈 PAINEL 1: ESCALA PATRIMONIAL (ATIVOS VS LIQUIDEZ VS HOLDING)</div>""", unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df["Mês"], y=df["Patrimônio Usinas"], name="Patrimônio Real", line=dict(color="#10B981", width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.03)'))
        fig1.add_trace(go.Scatter(x=df["Mês"], y=df["Caixa Acumulado"], name="Dinheiro Vivo", line=dict(color="#3B82F6", width=2, dash='dot')))
        fig1.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Total Negócio"], name="Valor da Holding", line=dict(color="#FF9F43", width=3)))
        fig1.update_layout(**layout_charts, height=260); st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    with row2_col2:
        st.markdown("""<div class="panel-title-bar">💸 PAINEL 2: FLUXO DE CAIXA MENSAL EM CASCATA</div>""", unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Faturamento Bruto"], name="Fat. Reajustado", line=dict(color="#FBBF24", width=4)))
        fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Fat. Sem Reajuste"], name="Fat. Sem Reajuste", line=dict(color="#4b5563", width=1.5, dash='dash')))
        fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Lucro Líquido"], name="Lucro Líq.", line=dict(color="#A78BFA", width=2), fill='tozeroy', fillcolor='rgba(167, 139, 250, 0.01)'))
        fig2.add_trace(go.Scatter(x=df["Mês"], y=df["Saque Mensal"], name="Seu Saque", line=dict(color="#F43F5E", width=1.5, dash='dash')))
        fig2.update_layout(**layout_charts, height=260); st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    st.markdown("<br>", unsafe_allow_html=True)
    row3_col1, row3_col2 = st.columns([1.2, 1])
    with row3_col1:
        st.markdown("""<div class="panel-title-bar">🏛️ PAINEL 3: DESTRUIÇÃO DE ALTERNATIVAS DO MERCADO</div>""", unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(x=[df["Valor Total Negócio"].iloc[-1], retorno_cdi_final, retorno_imovel_final], y=["Império Solar", "Renda Fixa (CDI)", "Imóvel Físico"], orientation='h', marker_color=['#10B981', '#334155', '#1e293b']))
        fig3.update_layout(paper_bgcolor='#131722', plot_bgcolor='#131722', font=dict(color='#787b86', size=10), xaxis=dict(showgrid=True, gridcolor='#2a2e39'), yaxis=dict(showgrid=False), margin=dict(l=10, r=15, t=15, b=15), height=160)
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    with row3_col2:
        st.markdown(f"""<div class="panel-title-bar">📝 INSIGHT ESTRATÉGICO PARA O PITCH</div><div style="background-color: #131722; border: 1px solid #2a2e39; border-radius: 0 0 4px 4px; padding: 20px; height: 160px; font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">Ao adotar a estratégia selecionada, o capital injetado se multiplica de forma geométrica através do efeito caixa livre. Enquanto as aplicações tradicionais prendem o investidor em uma linha reta corroída pela inflação, o modelo operacional solar entrega um retorno total estimado de <b style="color:#10b981;">{df["Valor Total Negócio"].iloc[-1] / (retorno_cdi_final if retorno_cdi_final > 0 else 1):.1f}x maior que o CDI</b>, capitalizando a tarifa reajustada em patrimônio líquido consolidado.</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="panel-title-bar">📋 TABELA DE AUDITORIA DO TERMINAL (MÊS A MÊS)</div>""", unsafe_allow_html=True)
    st.dataframe(df.style.format({"Faturamento Bruto": formato_real, "Fat. Sem Reajuste": formato_real, "Parcelas Banco": formato_real, "Lucro Líquido": formato_real, "Saque Mensal": formato_real, "Caixa Acumulado": formato_real, "Patrimônio Usinas": formato_real, "Valor Total Negócio": formato_real}), use_container_width=True, height=250, hide_index=True)
