import os
import time
import math
import queue
import threading


TIMEOUT = 180


def run_amaweb(urls_path: str, resultado_path: str, out_q: queue.Queue, stop_ev: threading.Event):
    def log(msg, tag="normal"):
        out_q.put((tag, msg + "\n"))

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from openpyxl import Workbook
    except ImportError as e:
        log(f"  [ERRO] Dependência não instalada: {e}", "error")
        log("  Execute: pip install selenium openpyxl", "warning")
        out_q.put(("DONE", None))
        return

    if not os.path.exists(urls_path):
        log(f"  [ERRO] Arquivo não encontrado: {urls_path}", "error")
        out_q.put(("DONE", None))
        return

    with open(urls_path, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip()]

    total = len(urls)
    log(f"  Iniciando avaliação de acessibilidade em {total} sites...", "info")
    log(f"  Timeout por site: {TIMEOUT}s", "info")
    log(f"  Resultado: {resultado_path}", "info")
    log("")

    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"
    ws.append(["URL", "Nota"])

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        log(f"  [ERRO] ChromeDriver não iniciado: {e}", "error")
        log("  Verifique se o ChromeDriver está instalado e no PATH.", "warning")
        log("  Download: https://chromedriver.chromium.org/downloads", "info")
        out_q.put(("DONE", None))
        return

    inicio_total = time.time()

    try:
        for i, site in enumerate(urls, 1):
            if stop_ev.is_set():
                log("\n  [!] Execução interrompida.", "warning")
                break

            url = (
                f"https://amaweb.unifesp.br/avaliador/results/{site}"
                if not site.startswith("http") else site
            )
            log(f"  [{i:03d}/{total}]  Avaliando → {site}", "info")

            try:
                driver.get(url)
                nota_el = WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".score-circle-value"))
                )
                nota = nota_el.text.strip().replace("Nota:", "").strip() or "Erro"
            except Exception:
                nota = "Timeout / Erro"

            ws.append([site, nota])
            wb.save(resultado_path)

            decorrido = time.time() - inicio_total
            media     = decorrido / i
            restante  = (total - i) * media

            tag = "success" if nota not in ("Erro", "Timeout / Erro") else "error"
            log(f"           Nota: {nota:<10}  média: {media:.1f}s/site  restante: ~{restante / 60:.1f}min", tag)

            pct  = i / total
            barra = "█" * int(30 * pct) + "░" * (30 - int(30 * pct))
            out_q.put(("progress", f"  [{barra}] {math.floor(pct * 100)}%\n"))

    finally:
        driver.quit()
        wb.save(resultado_path)

    log("")
    log("  " + "═" * 56, "dim")
    log("  AVALIAÇÃO FINALIZADA!", "title")
    log(f"  Planilha salva: {resultado_path}", "success")
    log("  " + "═" * 56, "dim")
    out_q.put(("DONE", None))
