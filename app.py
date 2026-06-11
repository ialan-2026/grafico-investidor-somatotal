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

st.title("⚡ LAB DE ENGENHARIA E DIAGNÓSTICO SOLAR v1.2")
st.markdown("---")

col1, col2 = st.columns([1, 2])
with col1:
    canal_alvo = st.selectbox("Escolha a Integradora para Validar:", list(DADOS_CONEXAO.keys()))
    tempo_aguardo = st.slider("Tempo de Carregamento da Página (segundos)", 3, 20, 10)
    botao_iniciar = st.button("🚀 INICIAR CAPTURA DE TELEMETRIA EM LIVE", use_container_width=True)

def inicializar_driver_antidetect():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

if botao_iniciar:
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
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        try:
            status_placeholder.warning("🔄 Passo 1: Carregando URL de Autenticação...")
            driver.get(creds["url"])
            wait = WebDriverWait(driver, 15)
            print_log(f"Conectado com sucesso em: {creds['url']}")

            status_placeholder.warning("🔄 Passo 2: Forçando bypass e injeção direta de dados...")
            
            if "Solarman" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//form//input[@type='text']")))
                p_in = driver.find_element(By.XPATH, "//form//input[@type='password']")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Login')]")
                driver.execute_script("arguments[0].click();", btn)
                
            elif "ShineMonitor" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'username') or contains(@id, 'email')]")))
                p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'password')]")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@id, 'login') or @type='submit']")
                driver.execute_script("arguments[0].click();", btn)

            elif "Hopewind" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Account')]")))
                p_in = driver.find_element(By.XPATH, "//input[@type='password']")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                
                # CRÍTICO: Força o clique na caixinha de aceite dos termos da Hopewind antes de logar
                try:
                    checkbox_termos = driver.find_element(By.XPATH, "//input[@type='checkbox'] or [contains(@class, 'checkbox')]")
                    driver.execute_script("arguments[0].click();", checkbox_termos)
                    print_log("Caixa de Termos e Privacidade aceita via JS.")
                except:
                    pass
                
                btn = driver.find_element(By.XPATH, "//button[contains(@class, 'el-button--primary') or @type='button']")
                driver.execute_script("arguments[0].click();", btn)

            elif "Growatt" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'account') or @name='username']")))
                p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'pwd') or @name='password']")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@class, 'login') or @type='submit']")
                driver.execute_script("arguments[0].click();", btn)

            elif "Hoymiles" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
                p_in = driver.find_element(By.XPATH, "//input[@type='password']")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                btn = driver.find_element(By.CLASS_NAME, "ant-btn-primary")
                driver.execute_script("arguments[0].click();", btn)

            elif "FoxESS" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'user') or @placeholder='Username']")))
                p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'pass') or @placeholder='Password']")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@class, 'login') or @type='button']")
                driver.execute_script("arguments[0].click();", btn)

            elif "Fronius" in canal_alvo:
                u_in = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'user') or @name='username']")))
                p_in = driver.find_element(By.XPATH, "//input[contains(@id, 'pass') or @name='password']")
                driver.execute_script("arguments[0].value = arguments[1];", u_in, creds["user"])
                driver.execute_script("arguments[0].value = arguments[1];", p_in, creds["pass"])
                btn = driver.find_element(By.XPATH, "//*[contains(@id, 'login') or @type='submit']")
                driver.execute_script("arguments[0].click();", btn)

            print_log("Payload de autenticação forçado na memória da página.")
            status_placeholder.warning(f"🔄 Passo 3: Aguardando processamento interno ({tempo_aguardo}s)...")
            time.sleep(tempo_aguardo)

            print_log(f"URL Atual pós-login: {driver.current_url}")
            
            status_placeholder.warning("🔄 Passo 4: Mapeando árvore de telemetria...")
            corpo_pagina_texto = driver.find_element(By.TAG_NAME, "body").text
            
            st.markdown("### 📄 Texto Cru Detectado na Tela Logada:")
            st.text_area("Dados extraídos da sessão ativa:", value=corpo_pagina_texto, height=250)
            
            status_placeholder.success("✅ Processo Concluído com Sucesso!")
            driver.quit()

        except Exception as falha:
            print_log(f"❌ Falha de varredura: {str(falha)}")
            status_placeholder.error("🔴 Falha encontrada. Veja os logs do Console.")
            driver.quit()
