import streamlit as st
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="Engenharia de Telemetria Solar", layout="wide")

# Lista estrita e filtrada de conexões fornecidas e validadas pelo operador
DADOS_CONEXAO = {
    "Canal 02 (ShineMonitor)": {"url": "https://www.shinemonitor.com/", "user": "Albano Solar", "pass": "oNa17112#", "tipo": "shinemonitor"},
    "Canal 03 (Hopewind)": {"url": "https://hopewindcloud.eu/#/login", "user": "solaralbano@gmail.com", "pass": "oNa17112", "tipo": "hopewind"},
    "Canal 05 (Hoymiles)": {"url": "https://global.hoymiles.com/website", "user": "solarjob", "pass": "Solarjob@123", "tipo": "hoymiles"},
    "Canal 06 (FoxESS)": {"url": "https://www.foxesscloud.com/v2/login", "user": "solarjob", "pass": "Solarjob@123", "tipo": "foxess"}
}

st.markdown("""
    <style>
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; color: #cbd5e1; }
    .status-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.85rem; }
    .status-table th { background-color: #1e2232; color: #787b86; padding: 10px; text-align: left; border: 1px solid #2a2e39; }
    .status-table td { padding: 10px; border: 1px solid #2a2e39; background-color: #131722; }
    .badge-ok { color: #10b981; font-weight: bold; }
    .badge-err { color: #f43f5e; font-weight: bold; }
    .badge-process { color: #3b82f6; font-weight: bold; anim-blink { animation: blink 1s infinite; } }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ LAB DE ENGENHARIA E TELEMETRIA CÍCLICA v1.5 (TRUE LOOP)")
st.markdown("---")

# Inicialização da memória interna exclusiva de telemetria
if "historico_leituras" not in st.session_state:
    st.session_state.historico_leituras = {k: {"potencia": "- W", "diaria": "- kWh", "mensal": "- MWh", "total": "- MWh", "status": "Aguardando Inicialização", "timestamp": "-"} for k in DADOS_CONEXAO.keys()}

# Inicialização do indexador do laço perpétuo
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Parâmetros do Ciclo")
    tempo_estabilizacao = st.slider("Tempo de Espera Pós-Login (segundos)", 3, 25, 12)
    intervalo_loop = st.slider("Intervalo de Espera entre Canais (segundos)", 5, 60, 25)
    loop_ativo = st.toggle("Ativar Varredura Cíclica Perpétua", value=False)
    
    st.markdown("---")
    st.markdown("""
        ### 💡 Regra de Negócio do Motor:
        O sistema opera em uma fila circular. Se um canal falhar por timeout ou indisponibilidade do servidor nativo, ele é marcado como **FALHA DE REDE** e o sistema pula imediatamente para o próximo da fila. Na próxima volta completa do laço, o canal com falha será retestado automaticamente.
    """)

def inicializar_driver_antidetect():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

def extrair_valor_regex(padrao, texto, default="-"):
    try:
        busca = re.search(padrao, texto, re.IGNORECASE)
        return busca.group(1).strip() if busca else default
    except:
        return default

# Painel consolidado na direita
with col2:
    st.subheader("📊 Painel de Controle e Coleta Consolidada")
    
    html_tabela = """<table class="status-table">
        <tr>
            <th>IDENTIFICAÇÃO CANAL</th>
            <th>POTÊNCIA LIVE</th>
            <th>PROD. DIÁRIA</th>
            <th>PROD. MENSAL</th>
            <th>PROD. HISTÓRICA</th>
            <th>INTEGRIDADE</th>
            <th>SINCRO</th>
        </tr>"""
    
    for canal, dados in st.session_state.historico_leituras.items():
        cor_status = "badge-ok" if "ONLINE" in dados["status"] else ("badge-err" if "FALHA" in dados["status"] else "badge-process")
        html_tabela += f"""<tr>
            <td><b>{canal}</b></td>
            <td>{dados['potencia']}</td>
            <td>{dados['diaria']}</td>
            <td>{dados['mensal']}</td>
            <td>{dados['total']}</td>
            <td class="{cor_status}">{dados['status']}</td>
            <td>{dados['timestamp']}</td>
        </tr>"""
    html_tabela += "</table>"
    st.markdown(html_tabela, unsafe_allow_html=True)

    console_placeholder = st.empty()

# ==============================================================================
# EXECUÇÃO DA MÁQUINA DE ESTADO DO LOOP INFINITO (UM POR VEZ SEM CONGELAR)
# ==============================================================================
if loop_ativo:
    lista_canais = list(DADOS_CONEXAO.keys())
    idx_atual = st.session_state.current_index
    canal_alvo = lista_canais[idx_atual]
    
    st.session_state.historico_leituras[canal_alvo]["status"] = "⚡ LENDO AGORA..."
    console_placeholder.info(f"🔄 Executando varredura no canal: {canal_alvo}...")
    
    creds = DADOS_CONEXAO[canal_alvo]
    driver = inicializar_driver_antidetect()
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    def forcar_preenchimento(elemento, valor):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, elemento, valor)

    try:
        driver.get(creds["url"])
        wait = WebDriverWait(driver, 15)

        if creds["tipo"] == "shinemonitor":
            u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'username') or @type='text']")))
            p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'password') or @type='password']")
            forcar_preenchimento(u_in, creds["user"])
            forcar_preenchimento(p_in, creds["pass"])
            btn = driver.find_element(By.XPATH, "//*[contains(@id, 'login') or @type='submit' or contains(@class, 'btn')]")
            driver.execute_script("arguments[0].click();", btn)

        elif creds["tipo"] == "hopewind":
            u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Account')]")))
            p_in = driver.find_element(By.XPATH, "//input[@type='password']")
            forcar_preenchimento(u_in, creds["user"])
            forcar_preenchimento(p_in, creds["pass"])
            try:
                checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'] or //span[contains(@class, 'checkbox')]")
                driver.execute_script("arguments[0].click();", checkbox)
            except: pass
            btn = driver.find_element(By.XPATH, "//button[contains(@class, 'el-button--primary') or @type='button']")
            driver.execute_script("arguments[0].click();", btn)

        elif creds["tipo"] == "hoymiles":
            u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
            p_in = driver.find_element(By.XPATH, "//input[@type='password']")
            forcar_preenchimento(u_in, creds["user"])
            forcar_preenchimento(p_in, creds["pass"])
            btn = driver.find_element(By.CLASS_NAME, "ant-btn-primary")
            driver.execute_script("arguments[0].click();", btn)

        elif creds["tipo"] == "foxess":
            u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'user') or @placeholder='Username' or @type='text']")))
            p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'pass') or @placeholder='Password' or @type='password']")
            forcar_preenchimento(u_in, creds["user"])
            forcar_preenchimento(p_in, creds["pass"])
            btn = driver.find_element(By.XPATH, "//*[contains(@class, 'login') or @type='button' or @type='submit']")
            driver.execute_script("arguments[0].click();", btn)

        time.sleep(tempo_estabilizacao)
        corpo_texto = driver.find_element(By.TAG_NAME, "body").text
        
        pot, dia, mes, tot = "- W", "- kWh", "- MWh", "- MWh"
        
        if creds["tipo"] == "hoymiles":
            mes = extrair_valor_regex(r"This month\n([\d.,\s\w]+)", corpo_texto, "- MWh")
            tot = extrair_valor_regex(r"Lifetime\n([\d.,\s\w]+)", corpo_texto, "- MWh")
        elif creds["tipo"] == "shinemonitor":
            pot = extrair_valor_regex(r"Current Power\n([\d.,\s\w]+)", corpo_texto, "- kW")
            dia = extrair_valor_regex(r"Today Energy\n([\d.,\s\w]+)", corpo_texto, "- kWh")
            tot = extrair_valor_regex(r"Total Energy\n([\d.,\s\w]+)", corpo_texto, "- MWh")
        else:
            pot = extrair_valor_regex(r"(?:Power Now|Current Power|Potência)[\s:]*([\d.,]+\s*(?:W|kW))", corpo_texto, "- kW")
            dia = extrair_valor_regex(r"(?:Today|Diária)[\s:]*([\d.,]+\s*kWh)", corpo_texto, "- kWh")
            tot = extrair_valor_regex(r"(?:Cumulative|Total)[\s:]*([\d.,]+\s*(?:kWh|MWh))", corpo_texto, "- MWh")

        st.session_state.historico_leituras[canal_alvo] = {
            "potencia": pot, "diaria": dia, "mensal": mes, "total": tot,
            "status": "🟢 ONLINE (LIVE)", "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        driver.quit()

    except Exception as err:
        # Em caso de erro, altera o status do canal alvo e libera o fluxo
        st.session_state.historico_leituras[canal_alvo]["status"] = "🔴 FALHA DE REDE"
        st.session_state.historico_leituras[canal_alvo]["timestamp"] = datetime.now().strftime("%H:%M:%S")
        driver.quit()

    # Avança o ponteiro do indexador de forma circular (Volta ao 0 quando chega no fim)
    st.session_state.current_index = (idx_atual + 1) % len(lista_canais)
    
    # Tempo de transição antes de recarregar e ir para o próximo alvo
    time.sleep(intervalo_loop)
    st.rerun()
