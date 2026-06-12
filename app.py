import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="API Telemetria Solar", layout="wide")

DADOS_CONEXAO = {
    "Canal 01 (Solarman/Deye)": {
        "url_login": "https://api.solarmanpv.com/account-api/v1.0/user/login", 
        "user": "solaralbano@gmail.com", "pass": "mBA4rvnSMuc5", "tipo": "json_payload"
    },
    "Canal 02 (ShineMonitor)": {
        "url_login": "https://www.shinemonitor.com/index_en.html", 
        "user": "Albano Solar", "pass": "oNa17112#", "tipo": "form_payload"
    },
    "Canal 03 (Hopewind)": {
        "url_login": "https://hopewindcloud.eu/api/v1/auth/login", 
        "user": "solaralbano@gmail.com", "pass": "oNa17112", "tipo": "json_payload"
    },
    "Canal 04 (Growatt)": {
        "url_login": "https://server.growatt.com/LoginAPI.do", 
        "user": "EBBJQA001", "pass": "Solarjob123", "tipo": "form_payload"
    },
    "Canal 05 (Hoymiles)": {
        "url_login": "https://global.hoymiles.com/iam/api/login", 
        "user": "solarjob", "pass": "Solarjob@123", "tipo": "hoymiles_payload"
    },
    "Canal 06 (FoxESS)": {
        "url_login": "https://www.foxesscloud.com/v2/api/login", 
        "user": "solarjob", "pass": "Solarjob@123", "tipo": "json_payload"
    },
    "Canal 07 (Fronius)": {
        "url_login": "https://login.fronius.com/authenticationendpoint/login.do?client_id=mf_o9iTAyKemNLQTa6Sp6HYonCIa", 
        "user": "engenharia@solarjob.com.br", "pass": "Solarjob@1234", "tipo": "oauth_payload"
    }
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

st.title("⚡ LAB DE TELEMETRIA SOLAR v2.1 (BACKGROUND API ENGINE)")
st.markdown("---")

if "historico_api" not in st.session_state:
    st.session_state.historico_api = {k: {"status_http": "-", "dados_brutos": "Nenhum dado recebido", "status": "Aguardando Inicialização", "timestamp": "-"} for k in DADOS_CONEXAO.keys()}

if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Parâmetros de Chamada")
    intervalo_loop = st.slider("Espera de Varredura entre Canais (segundos)", 1, 10, 5)
    loop_ativo = st.toggle("Ativar Varredura Cíclica Perpétua via API", value=False)

with col2:
    st.subheader("📊 Painel de Controle e Coleta Consolidada")
    
    html_tabela = """<table class="status-table">
        <tr>
            <th>IDENTIFICAÇÃO CANAL</th>
            <th>CÓDIGO HTTP</th>
            <th>STATUS CONEXÃO</th>
            <th>ÚLTIMO REGISTRO DE DADOS DA SESSÃO</th>
            <th>SINCRO</th>
        </tr>"""
    
    for canal, dados in st.session_state.historico_api.items():
        cor_status = "badge-ok" if "ONLINE" in dados["status"] else ("badge-err" if "FALHA" in dados["status"] else "badge-process")
        html_tabela += f"""<tr>
            <td><b>{canal}</b></td>
            <td><code>{dados['status_http']}</code></td>
            <td class="{cor_status}">{dados['status']}</td>
            <td><div style='max-width:320px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'><code>{dados['dados_brutos']}</code></div></td>
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
    
    st.session_state.historico_api[canal_alvo]["status"] = "📡 REQUISITANDO ENDPOINT..."
    console_placeholder.info(f"🔄 Disparando Requisição HTTP de Segundo Plano: {canal_alvo}...")
    
    session = requests.Session()
    
    # Cabeçalhos padrão emulando requisições vindas de um App Mobile real
    headers_padrao = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "com.hoymiles.inverter" if "Hoymiles" in canal_alvo else "XMLHttpRequest"
    }
    session.headers.update(headers_padrao)

    try:
        # Tratamento individualizado baseado nas assinaturas de segurança coletadas no print v2.0
        if creds["tipo"] == "json_payload":
            payload = {"username": creds["user"], "password": creds["pass"]}
            response = session.post(creds["url_login"], json=payload, timeout=8)
            
        elif creds["tipo"] == "hoymiles_payload":
            # Formato de payload estrito exigido pelo gateway da Hoymiles Cloud
            payload = {"user_name": creds["user"], "password": creds["pass"], "language": "en_US"}
            response = session.post(creds["url_login"], json=payload, timeout=8)
            
        elif creds["tipo"] == "oauth_payload":
            # CORREÇÃO FRONIUS: Injeta o grant_type solicitado pelo servidor de autenticação no print
            headers_oauth = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = {
                "grant_type": "password",
                "username": creds["user"],
                "password": creds["pass"],
                "scope": "openid"
            }
            response = session.post(creds["url_login"], data=payload, headers=headers_oauth, timeout=8)
            
        else: # form_payload (Growatt e ShineMonitor)
            payload = {"userName": creds["user"], "password": creds["pass"]}
            response = session.post(creds["url_login"], data=payload, timeout=8)

        codigo_http = response.status_code
        resposta_texto = response.text.strip()

        st.session_state.historico_api[canal_alvo] = {
            "status_http": str(codigo_http),
            "dados_brutos": resposta_texto if resposta_texto else "Conexão Estabelecida com Sucesso",
            "status": "🟢 ONLINE (LIVE)" if codigo_http in [200, 201] else "🔴 RESPOSTA REJEITADA",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    except Exception as err:
        st.session_state.historico_api[canal_alvo] = {
            "status_http": "TIMEOUT / ERR",
            "dados_brutos": str(err),
            "status": "🔴 FALHA DE REDE",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    st.session_state.current_api_index = (idx_atual + 1) % len(lista_canais)
    time.sleep(intervalo_loop)
    st.rerun()
