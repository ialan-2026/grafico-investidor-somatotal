import streamlit as st
import requests
import time
import html
import json
from datetime import datetime

st.set_page_config(page_title="API Telemetria Solar", layout="wide")

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

st.title("⚡ LAB DE TELEMETRIA SOLAR v2.6 (SESSION INITIALIZER)")
st.markdown("---")

if "historico_api" not in st.session_state or any("potencia" not in v for v in st.session_state.historico_api.values()):
    st.session_state.historico_api = {k: {"potencia": "- W", "diaria": "- kWh", "total": "- MWh", "status": "Aguardando Inicialização", "timestamp": "-"} for k in DADOS_CONEXAO.keys()}

if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0

lista_canais = list(DADOS_CONEXAO.keys())

if st.session_state.current_api_index >= len(lista_canais) or st.session_state.current_api_index < 0:
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
        status_txt = dados.get("status", "Aguardando")
        if "ONLINE" in status_txt: cor_status = "badge-ok"
        elif "FALHA" in status_txt or "RESP" in status_txt: cor_status = "badge-err"
        else: cor_status = "badge-process"
        
        html_tabela += f"""<tr>
            <td><b>{canal}</b></td>
            <td><code>{dados.get('potencia', '- W')}</code></td>
            <td><code>{dados.get('diaria', '- kWh')}</code></td>
            <td><code>{dados.get('total', '- MWh')}</code></td>
            <td class="{cor_status}">{status_txt}</td>
            <td>{dados.get('timestamp', '-')}</td>
        </tr>"""
    html_tabela += "</table>"
    st.markdown(html_tabela, unsafe_allow_html=True)

    console_placeholder = st.empty()

if loop_ativo:
    idx_atual = st.session_state.current_api_index
    canal_alvo = lista_canais[idx_atual]
    creds = DADOS_CONEXAO[canal_alvo]
    
    st.session_state.historico_api[canal_alvo]["status"] = "📡 PROCESSANDO..."
    console_placeholder.info(f"🔄 Conectando via API de Segundo Plano: {canal_alvo}...")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest"
    })

    try:
        if creds["tipo"] == "growatt_api":
            payload_login = {"account": creds["user"], "password": creds["pass"], "validateCode": ""}
            response_login = session.post(creds["url_login"], data=payload_login, timeout=8)
            
            if response_login.status_code == 200:
                # 🛡️ PASSO CRÍTICO DE ENGENHARIA: Inicializa a usina na memória batendo no index antes de pedir os dados
                session.get("https://server.growatt.com/index.do", timeout=8)
                
                # Passo 3: Agora sim, requisita os dados puros com a sessão já carregada
                url_dados = "https://server.growatt.com/NewPlantAPI.do?action=getCenterEnergyData"
                response_dados = session.get(url_dados, timeout=8)
                
                try:
                    dados_json = response_dados.json()
                    pot = str(dados_json.get("power", "0")) + " W"
                    dia = str(dados_json.get("todayEnergy", "0")) + " kWh"
                    tot = str(dados_json.get("totalEnergy", "0")) + " MWh"
                    status_txt = "🟢 ONLINE (LIVE)"
                except:
                    pot, dia, tot = "- W", "- kWh", "- MWh"
                    retorno_cru = response_dados.text.strip()[:35]
                    status_txt = f"🔴 RESP: {html.escape(retorno_cru)}"
            else:
                pot, dia, tot = "- W", "- kWh", "- MWh"
                status_txt = f"🔴 FALHA LOGIN ({response_login.status_code})"

        else:
            if creds["tipo"] == "json_payload":
                session.post(creds["url_login"], json={"username": creds["user"], "password": creds["pass"]}, timeout=5)
            elif creds["tipo"] == "hoymiles_payload":
                session.post(creds["url_login"], json={"user_name": creds["user"], "password": creds["pass"], "language": "en_US"}, timeout=5)
            
            pot, dia, tot = "Staging", "Staging", "Staging"
            status_txt = "🟠 AGUARDANDO REVERSÃO"

        st.session_state.historico_api[canal_alvo] = {
            "potencia": pot, "diaria": dia, "total": tot,
            "status": status_txt, "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    except Exception as err:
        st.session_state.historico_api[canal_alvo] = {
            "potencia": "- W", "diaria": "- kWh", "total": "- MWh",
            "status": "🔴 FALHA DE CONEXÃO", "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    st.session_state.current_api_index = (idx_atual + 1) % len(lista_canais)
    time.sleep(intervalo_loop)
    st.rerun()
