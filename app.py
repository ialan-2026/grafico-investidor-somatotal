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

# Banco de dados de conexões unificado
DADOS_CONEXAO = {
    "Canal 01 (Solarman/Deye)": {"url": "https://pro.solarmanpv.com/login", "user": "solaralbano@gmail.com", "pass": "mBA4rvnSMuc5", "tipo": "solarman"},
    "Canal 02 (ShineMonitor)": {"url": "https://www.shinemonitor.com/", "user": "Albano Solar", "pass": "oNa17112#", "tipo": "shinemonitor"},
    "Canal 03 (Hopewind)": {"url": "https://hopewindcloud.eu/#/login", "user": "solaralbano@gmail.com", "pass": "oNa17112", "tipo": "hopewind"},
    "Canal 04 (Growatt)": {"url": "https://oss.growatt.com/login?lang=en", "user": "EBBJQA001", "pass": "Solarjob123", "tipo": "growatt"},
    "Canal 05 (Hoymiles)": {"url": "https://global.hoymiles.com/website", "user": "solarjob", "pass": "Solarjob@123", "tipo": "hoymiles"},
    "Canal 06 (FoxESS)": {"url": "https://www.foxesscloud.com/v2/login", "user": "solarjob", "pass": "Solarjob@123", "tipo": "foxess"},
    "Canal 07 (Fronius)": {"url": "https://login.fronius.com/authenticationendpoint/login.do?client_id=mf_o9iTAyKemNLQTa6Sp6HYonCIa", "user": "engenharia@solarjob.com.br", "pass": "Solarjob@1234", "tipo": "fronius"}
}

st.markdown("""
    <style>
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; color: #cbd5e1; }
    .status-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.85rem; }
    .status-table th { background-color: #1e2232; color: #787b86; padding: 10px; text-align: left; border: 1px solid #2a2e39; }
    .status-table td { padding: 10px; border: 1px solid #2a2e39; background-color: #131722; }
    .badge-ok { color: #10b981; font-weight: bold; }
    .badge-err { color: #f43f5e; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ LAB DE ENGENHARIA E TELEMETRIA PRECOGNITIVA v1.5")
st.markdown("---")

# Inicialização da memória de persistência de dados entre os reloads do Streamlit
if "historico_leituras" not in st.session_state:
    st.session_state.historico_leituras = {k: {"potencia": "0 kW", "diaria": "0 kWh", "mensal": "0 MWh", "total": "0 MWh", "status": "Aguardando Varredura", "timestamp": "-"} for k in DADOS_CONEXAO.keys()}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Parâmetros do Ciclo")
    tempo_estabilizacao = st.slider("Tempo de Espera Pós-Login (segundos)", 5, 25, 12)
    intervalo_loop = st.slider("Intervalo entre Canais (segundos)", 5, 60, 25)
    loop_ativo = st.toggle("Ativar Varredura Cíclica Automática", value=False)

def inicializar_driver_antidetect():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

def extrair_valor_regex(padrao, texto, default="0.0"):
    try:
        busca = re.search(padrao, texto, re.IGNORECASE)
        return busca.group(1).strip() if busca else default
    except:
        return default

# Interface de Monitoramento em Tempo Real
with col2:
    st.subheader("📊 Painel de Controle e Coleta Consolidada")
    
    # Renderização da Tabela Corporativa White-Label de Engenharia
    html_tabela = """<table class="status-table">
        <tr>
            <th>IDENTIFICAÇÃO</th>
            <th>POTÊNCIA LIVE</th>
            <th>PROD. DIÁRIA</th>
            <th>PROD. MENSAL</th>
            <th>PROD. HISTÓRICA</th>
            <th>INTEGRIDADE</th>
            <th>ÚLT. LEITURA</th>
        </tr>"""
    
    for canal, dados in st.session_state.historico_leituras.items():
        cor_status = "badge-ok" if "ONLINE" in dados["status"] else ("badge-err" if "FALHA" in dados["status"] else "")
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

# --- EXECUÇÃO DO LOOP DA MALHA DE CAPTURA ---
if loop_ativo:
    for canal_alvo in DADOS_CONEXAO.keys():
        creds = DADOS_CONEXAO[canal_alvo]
        console_placeholder.info(f"🔄 Iniciando Conexão Segura: {canal_alvo}...")
        
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

            # Execução estruturada dos payloads de login por canal
            if creds["tipo"] == "solarman":
                inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='text']")))
                u_in = [i for i in inputs if i.is_displayed()][0]
                p_in = driver.find_element(By.XPATH, "//input[@type='password']")
                forcar_preenchimento(u_in, creds["user"])
                forcar_preenchimento(p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Login')]")
                driver.execute_script("arguments[0].click();", btn)
                
            elif creds["tipo"] == "shinemonitor":
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'username') or @type='text']")))
                p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'password') or @type='password']")
                forcar_preenchimento(u_in, creds["user"])
                forcar_preenchimento(p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@id, 'login') or @type='submit' or contains(@class, 'btn')]")
                driver.execute_script("arguments[0].click();", btn)

            elif creds["tipo"] == "hopewind":
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Account')]")))
                p_in = driver.find_element(By.XPATH, "//input[@type='password']")
                forcar_input_framework(u_in, creds["user"])
                forcar_input_framework(p_in, creds["pass"])
                try:
                    checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'] or //span[contains(@class, 'checkbox')]")
                    driver.execute_script("arguments[0].click();", checkbox)
                except: pass
                btn = driver.find_element(By.XPATH, "//button[contains(@class, 'el-button--primary') or @type='button']")
                driver.execute_script("arguments[0].click();", btn)

            elif creds["tipo"] == "growatt":
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username' or @id='val_login_account' or @name='username']")))
                p_in = driver.find_element(By.XPATH, "//input[@id='password' or @id='val_login_pwd' or @name='password']")
                forcar_preenchimento(u_in, creds["user"])
                forcar_preenchimento(p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@class, 'login') or @type='submit']")
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

            elif creds["tipo"] == "fronius":
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username' or @name='username' or @type='text']")))
                p_in = driver.find_element(By.XPATH, "//input[@id='password' or @name='password' or @type='password']")
                forcar_preenchimento(u_in, creds["user"])
                forcar_preenchimento(p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@id, 'login') or @type='submit']")
                driver.execute_script("arguments[0].click();", btn)

            time.sleep(tempo_estabilizacao)
            corpo_texto = driver.find_element(By.TAG_NAME, "body").text
            
            # --- PARSERS DINÂMICOS BASEADOS NAS ASSINATURAS TEXTUAIS DE CADA PORTAL ---
            pot, dia, mes, tot = "0 kW", "0 kWh", "0 MWh", "0 MWh"
            
            if creds["tipo"] == "solarman":
                linhas = corpo_texto.split('\n')
                for i, linha in enumerate(linhas):
                    if "tempo real" in linha and i+1 < len(linhas): pot = linhas[i+1]
                    if "diária" in linha and i+1 < len(linhas): dia = linhas[i+1]
                    if "mensal" in linha and i+1 < len(linhas): mes = linhas[i+1]
                    if "total" in server_linha and i+1 < len(linhas): tot = linhas[i+1]
            elif creds["tipo"] == "hoymiles":
                mes = extrair_valor_regex(r"This month\n([\d.,\s\w]+)", corpo_texto, "0 MWh")
                tot = extrair_valor_regex(r"Lifetime\n([\d.,\s\w]+)", corpo_texto, "0 MWh")
            elif creds["tipo"] == "shinemonitor":
                pot = extrair_valor_regex(r"Current Power\n([\d.,\s\w]+)", corpo_texto, "0 kW")
                dia = extrair_valor_regex(r"Today Energy\n([\d.,\s\w]+)", corpo_texto, "0 kWh")
                tot = extrair_valor_regex(r"Total Energy\n([\d.,\s\w]+)", corpo_texto, "0 MWh")
            else:
                pot = extrair_valor_regex(r"(?:Power Now|Current Power|Potência)[\s:]*([\d.,]+\s*(?:W|kW))", corpo_texto, "0 kW")
                dia = extrair_valor_regex(r"(?:Today|Diária)[\s:]*([\d.,]+\s*kWh)", corpo_texto, "0 kWh")
                tot = extrair_valor_regex(r"(?:Cumulative|Total)[\s:]*([\d.,]+\s*(?:kWh|MWh))", corpo_texto, "0 MWh")

            # Atualização da memória global de telemetria
            st.session_state.historico_leituras[canal_alvo] = {
                "potencia": pot, "diaria": dia, "mensal": mes, "total": tot,
                "status": "🟢 ONLINE (LIVE)", "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            driver.quit()

        except Exception as err:
            st.session_state.historico_leituras[canal_alvo]["status"] = "🔴 FALHA DE REDE"
            st.session_state.historico_leituras[canal_alvo]["timestamp"] = datetime.now().strftime("%H:%M:%S")
            driver.quit()

        # Tempo de transição entre os canais do parque fotovoltaico
        time.sleep(intervalo_loop)
        st.rerun()
