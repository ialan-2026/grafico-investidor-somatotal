import streamlit as st
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="Engenharia de Telemetria Solar", layout="wide")

# Credenciais oficiais enviadas pelo operador
DADOS_CONEXAO = {
    "Canal 01 (Solarman/Deye)": {"url": "https://pro.solarmanpv.com/login", "user": "solaralbano@gmail.com", "pass": "mBA4rvnSMuc5"},
    "Canal 02 (ShineMonitor)": {"url": "https://www.shinemonitor.com/", "user": "Albano Solar", "pass": "oNa17112#"},
    "Canal 03 (Hopewind)": {"url": "https://hopewindcloud.eu/#/login", "user": "solaralbano@gmail.com", "pass": "oNa17112"},
    "Canal 04 (Growatt)": {"url": "https://oss.growatt.com/login?lang=en", "user": "EBBJQA001", "pass": "Solarjob123"},
    "Canal 05 (Hoymiles)": {"url": "https://global.hoymiles.com/website", "user": "solarjob", "pass": "Solarjob@123"},
    "Canal 06 (FoxESS)": {"url": "https://www.foxesscloud.com/v2/login", "user": "solarjob", "pass": "Solarjob@123"},
    "Canal 07 (Fronius)": {"url": "https://login.fronius.com/authenticationendpoint/login.do?client_id=mf_o9iTAyKemNLQTa6Sp6HYonCIa", "user": "engenharia@solarjob.com.br", "pass": "Solarjob@1234"}
}

st.markdown("""
    <style>
    .stApp { background-color: #0c0f16; font-family: 'Consolas', monospace; color: #cbd5e1; }
    .console-box { background-color: #131722; border: 1px solid #2a2e39; border-radius: 4px; padding: 15px; font-size: 0.82rem; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ LAB DE ENGENHARIA E DIAGNÓSTICO SOLAR v1.0")
st.markdown("---")

# Interface de seleção do alvo de teste
col1, col2 = st.columns([1, 2])
with col1:
    canal_alvo = st.selectbox("Escolha a Integradora para Validar:", list(DADOS_CONEXAO.keys()))
    tempo_aguardo = st.slider("Tempo de Carregamento da Página (segundos)", 3, 15, 6)
    executar = st.button("🚀 INICIAR CAPTURA DE TELEMETRIA EM LIVE", use_container_width=True)

# Função centralizada com flags de evasão de detecção de robôs
def inicializar_driver_antidetect():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Tira o carimbo de robô que o Chrome Headless deixa nos servidores
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

if ejecutar:
    creds = DADOS_CONEXAO[canal_alvo]
    logs = []
    
    with col2:
        st.subheader(f"🛠️ Console Log: {canal_alvo}")
        status_placeholder = st.empty()
        console_placeholder = st.empty()
        
        def print_log(texto):
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {texto}")
            console_placeholder.code("\n".join(logs))

        driver = inicializar_driver_antidetect()
        # Executa script para apagar vestígios de automação que acionam Cloudflare/Captchas
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        try:
            status_placeholder.warning("🔄 Passo 1: Carregando URL de Autenticação...")
            driver.get(creds["url"])
            wait = WebDriverWait(driver, 15)
            print_log(f"Conectado com sucesso em: {creds['url']}")

            status_placeholder.warning("🔄 Passo 2: Tentando Injetar Credenciais...")
            
            # --- BLOCOS CONDICIONAIS DE LOGIN POR INTEGRATOR ---
            if "Solarman" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
                p_in = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                
            elif "ShineMonitor" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.ID, "username")))
                p_in = driver.find_element(By.ID, "password")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.ID, "login_btn").click()

            elif "Hopewind" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Account']")))
                p_in = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.CLASS_NAME, "el-button--primary").click()

            elif "Growatt" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.ID, "val_login_account")))
                p_in = driver.find_element(By.ID, "val_login_pwd")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.CLASS_NAME, "btn-login").click()

            elif "Hoymiles" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
                p_in = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.CLASS_NAME, "ant-btn-primary").click()

            elif "FoxESS" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.ID, "username")))
                p_in = driver.find_element(By.ID, "password")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.CLASS_NAME, "login-btn").click()

            elif "Fronius" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.ID, "username")))
                p_in = driver.find_element(By.ID, "password")
                u_in.send_keys(creds["user"])
                p_in.send_keys(creds["pass"])
                driver.find_element(By.ID, "login-btn").click()

            print_log("Formulário enviado. Aguardando processamento dos scripts da página...")
            status_placeholder.warning(f"🔄 Passo 3: Aguardando janela de segurança ({tempo_aguardo}s)...")
            time.sleep(tempo_aguardo)

            # Validação pós-login
            print_log(f"URL Atual após o envio do Login: {driver.current_url}")
            
            status_placeholder.warning("🔄 Passo 4: Tentando Ler Árvore de Elementos (HTML)...")
            # Salva o texto cru visível da tela inteira para sabermos se entramos no painel de gráficos
            corpo_pagina_texto = driver.find_element(By.TAG_BODY).text
            
            st.markdown("### 📄 Texto Cru Detectado na Tela Logada:")
            st.text_area("Use esta caixa para caçar palavras como 'Today', 'MWh' ou 'Total' para calibrar seus XPATHs:", value=corpo_pagina_texto, height=250)
            
            status_placeholder.success("✅ Processo Concluído! Analise os dados capturados acima.")
            driver.quit()

        except Exception as falha:
            print_log(f"❌ Falha crítica de Varredura: {str(falha)}")
            status_placeholder.error("🔴 Falha na Operação. Verifique a sintaxe ou o XPATH do console.")
            driver.quit()
