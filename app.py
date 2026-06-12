import streamlit as st
import requests
import time
import html
import json
from datetime import datetime

st.set_page_config(page_title="API Telemetria Solar", layout="wide")

# Mantemos a estrutura global, mas calibramos o motor interno da Growatt
DADOS_CONEXAO = {
    "Canal 01 (Solarman/Deye)": {"url_login": "https://api.solarmanpv.com/account-api/v1.0/user/login", "user": "solaralbano@gmail.com", "pass": "mBA4rvnSMuc5", "tipo": "json_payload"},
    "Canal 02 (ShineMonitor)": {"url_login": "https://www.shinemonitor.com/index_en.html", "user": "Albano Solar", "pass": "oNa17112#", "tipo": "form_payload"},
    "Canal 03 (Hopewind)": {"url_login": "https://hopewindcloud.eu/api/v1/auth/login", "user": "solaralbano@gmail.com", "pass": "oNa17112", "tipo": "json_payload"},
    "Canal 04 (Growatt)": {"url_login": "https://server.growatt.com/login.do", "user": "EBBJQA001", "pass": "Solarjob123", "tipo": "growatt_api"},
    "Canal 05 (Hoymiles)": {"url_login": "https://global.hoymiles.com/iam/api/login", "user": "solarjob", "pass": "Solarjob@123", "tipo": "hoymiles_payload"},
    "Canal 06 (FoxESS)": {"url_login": "https://www.foxesscloud.com/v2/api/login", "user": "solarjob", "pass": "Solarjob@123", "tipo": "json_payload"},
    "Canal 07 (Fronius)": {"url_login": "https://login.fronius.com/oauth2/token", "user": "engenharia@solarjob.com.br", "pass": "Solarjob@1234", "tipo": "oauth_payload"}
}

st.markdown("""
    <style>
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; color: #cbd5e1; }
    .status-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.85rem; }
    .status-table th { background-color: #1e2232; color: #787b86; padding: 10px; text-align: left; border: 1px solid #2a2e39; }
    .status-table td { padding: 10px; border: 1px solid #2a2e39; background-color: #131722; }
    .badge-ok { color: #10b981; font-weight: bold; }
    .badge-err { color: #f43f5e; font-weight: bold; }
    .badge-process { color: #3b82f6; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ LAB DE TELEMETRIA SOLAR v2.4 (LIVE DATA EXTRACTOR)")
st.markdown("---")

if "historico_api" not in st.session_state:
    st.session_state.historico_api = {k: {"potencia": "- W", "diaria": "- kWh", "total": "- MWh", "status": "Aguardando Inicialização", "timestamp": "-"} for k in DADOS_CONEXAO.keys()}

if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Parâmetros de Chamada")
    intervalo_loop = st.slider("Espera de Varredura entre Canais (segundos)", 1, 10, 4)
    loop_ativo = st.toggle("Ativar Varredura Cíclica Perpétua via API", value=False)

with col2:
    st.subheader("📊 Painel de Controle e Coleta Consolidada")
    
    html_tabela = """<table class="status-table">
        <tr>
            <th>IDENTIFICAÇÃO CANAL</th>
            <th>POTÊNCIA LIVE</th>
            <th>GERAÇÃO DIÁRIA</th>
            <th>GERAÇÃO TOTAL</th>
            <th>STATUS CONEXÃO</th>
            <th>SINCRO</th>
        </tr>"""
    
    for canal, dados in st.session_state.historico_api.items():
        if "ONLINE" in dados["status"]: cor_status = "badge-ok"
        elif "FALHA" in dados["status"]: cor_status = "badge-err"
        else: cor_status = "badge-process"
        
        html_tabela += f"""<tr>
            <td><b>{canal}</b></td>
            <td><code>{dados['potencia']}</code></td>
            <td><code>{dados['diaria']}</code></td>
            <td><code>{dados['total']}</code></td>
            <td class="{cor_status}">{dados['status']}</td>
            <td>{dados['timestamp']}</td>
        </tr>"""
    html_tabela += "</table>"
    st.markdown(html_tabela, unsafe_allow_html=True)

    console_placeholder = st.empty()

if loop_ativo:
    lista_canais = list(DADOS_CONEXAO.keys())
    
    if st.session_state.current_api_index >= len(lista_canais):
        st.session_state.current_api_index = 0
        
    idx_atual = st.session_state.current_api_index
    canal_alvo = lista_canais[idx_atual]
    creds = DADOS_CONEXAO[canal_alvo]
    
    st.session_state.historico_api[canal_alvo]["status"] = "📡 AUTENTICANDO APP..."
    console_placeholder.info(f"🔄 Conectando via API de Segundo Plano: {canal_alvo}...")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Accept": "application/json, text/plain, */*"
    })

    try:
        # ==============================================================================
        # MOTOR EXCLUSIVO: IMPLEMENTAÇÃO DO CRACHÁ DIGITAL GROWATT
        # ==============================================================================
        if creds["tipo"] == "growatt_api":
            # Passo 1: Envia o batedor de login para obter o Cookie de Sessão corporativo
            payload_login = {"account": creds["user"], "password": creds["pass"], "validateCode": ""}
            response_login = session.post(creds["url_login"], data=payload_login, timeout=8)
            
            # Passo 2: Se o login passou, usa a mesma sessão para colher a árvore de dados puros
            if response_login.status_code == 200:
                url_dados = "https://server.growatt.com/NewPlantAPI.do?action=getCenterEnergyData"
                response_dados = session.get(url_dados, timeout=8)
                
                try:
                    dados_json = response_dados.json()
                    # Garimpa os valores exatos de dentro do mapa de memória do servidor
                    pot = dados_json.get("power", "0") + " W"
                    dia = dados_json.get("todayEnergy", "0") + " kWh"
                    tot = dados_json.get("totalEnergy", "0") + " MWh"
                    status_txt = "🟢 ONLINE (LIVE)"
                except:
                    # Fallback de segurança caso o formato JSON varie
                    pot, dia, tot = "- W", "- kWh", "- MWh"
                    status_txt = "🔴 ERRO NO PARSER JSON"
            else:
                pot, dia, tot = "- W", "- kWh", "- MWh"
                status_txt = "🔴 LOGIN REJEITADO"

        # ==============================================================================
        # CANAIS ADICIONAIS (EM ESTÁGIO DE MAPEAMENTO PROGRESSIVO)
        # ==============================================================================
        else:
            # Mantém as outras conexões batendo o ponto no servidor para auditoria de portas
            if creds["tipo"] == "json_payload":
                session.post(creds["url_login"], json={"username": creds["user"], "password": creds["pass"]}, timeout=5)
            elif creds["tipo"] == "hoymiles_payload":
                session.post(creds["url_login"], json={"user_name": creds["user"], "password": creds["pass"], "language": "en_US"}, timeout=5)
            
            pot, dia, tot = "Staging", "Staging", "Staging"
            status_txt = "🟠 AGUARDANDO REVERSÃO"

        # Consolida os dados na interface gráfica
        st.session_state.historico_api[canal_alvo] = {
            "potencia": pot, "diaria": dia, "total": tot,
            "status": status_txt, "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    except Exception as err:
        st.session_state.historico_api[canal_alvo] = {
            "potencia": "- W", "diaria": "- kWh", "total": "- MWh",
            "status": "🔴 FALHA DE REDE", "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    st.session_state.current_api_index = (idx_atual + 1) % len(lista_canais)
    time.sleep(intervalo_loop)
    st.rerun()
