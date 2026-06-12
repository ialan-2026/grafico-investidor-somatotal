import streamlit as st
import requests
import time
import json
from datetime import datetime

st.set_page_config(page_title="API Telemetria Solar", layout="wide")

# Banco de dados centralizado com os endpoints de autenticação das plataformas
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
        "user": "solarjob", "pass": "Solarjob@123", "tipo": "json_payload"
    },
    "Canal 06 (FoxESS)": {
        "url_login": "https://www.foxesscloud.com/v2/api/login", 
        "user": "solarjob", "pass": "Solarjob@123", "tipo": "json_payload"
    },
    "Canal 07 (Fronius)": {
        "url_login": "https://login.fronius.com/oauth2/token", 
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

st.title("⚡ LAB DE TELEMETRIA SOLAR v2.0 (BACKGROUND API ENGINE)")
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
    
    st.markdown("---")
    st.markdown("""
        ### 📡 Vantagens desta Nova Arquitetura:
        * **Velocidade Extrema:** Sem abrir navegadores, as chamadas HTTP levam milissegundos.
        * **Sem Bloqueio Visual:** Ignora mudanças de botões, cores ou layouts do site.
        * **Leitura de Dados Puros:** Captura direto a resposta de memória enviada para o painel.
    """)

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
        if "ONLINE" in dados["status"]: cor_status = "badge-ok"
        elif "FALHA" in dados["status"]: cor_status = "badge-err"
        else: cor_status = "badge-process"
        
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

# --- INSTANCIAÇÃO DA MÁQUINA DE ESTADO ASSÍNCRONA ---
if loop_ativo:
    lista_canais = list(DADOS_CONEXAO.keys())
    
    if st.session_state.current_api_index >= len(lista_canais):
        st.session_state.current_api_index = 0
        
    idx_atual = st.session_state.current_api_index
    canal_alvo = lista_canais[idx_atual]
    creds = DADOS_CONEXAO[canal_alvo]
    
    st.session_state.historico_api[canal_alvo]["status"] = "📡 REQUISITANDO ENDPOINT..."
    console_placeholder.info(f"🔄 Disparando Requisição HTTP de Segundo Plano: {canal_alvo}...")
    
    # Cria uma sessão HTTP isolada na memória para guardar os cookies gerados automaticamente
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8" if creds["tipo"] == "json_payload" else "application/x-www-form-urlencoded"
    })

    try:
        # Montagem inteligente do payload dependendo de como o servidor aceita a informação
        if creds["tipo"] == "json_payload":
            payload = {"username": creds["user"], "password": creds["pass"]}
            response = session.post(creds["url_login"], json=payload, timeout=8)
        else:
            payload = {"username": creds["user"], "password": creds["pass"], "account": creds["user"], "password": creds["pass"]}
            response = session.post(creds["url_login"], data=payload, timeout=8)

        codigo_http = response.status_code
        resposta_texto = response.text.strip()

        # Armazena os dados brutos de retorno (JSON ou HTML cru) na tabela de auditoria
        st.session_state.historico_api[canal_alvo] = {
            "status_http": str(codigo_http),
            "dados_brutos": resposta_texto if resposta_texto else "Sessão Inicializada (Vazio)",
            "status": "🟢 ONLINE (LIVE)" if codigo_http == 200 else "🔴 RESPOSTA INVÁLIDA",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    except Exception as err:
        st.session_state.historico_api[canal_alvo] = {
            "status_http": "TIMEOUT / ERR",
            "dados_brutos": f"Erro de conexão com o endpoint: {str(err)}",
            "status": "🔴 FALHA DE REDE",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    # Avança a fila perpétua circular de forma imediata
    st.session_state.current_api_index = (idx_atual + 1) % len(lista_canais)
    time.sleep(intervalo_loop)
    st.rerun()
