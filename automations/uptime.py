import os
import time
import queue
import threading
from datetime import datetime


def run_uptime(urls_path: str, intervalo: int, out_q: queue.Queue, stop_ev: threading.Event):
    def log(msg, tag="normal"):
        out_q.put((tag, msg + "\n"))

    try:
        import requests
    except ImportError:
        log("  [ERRO] requests nao instalado: pip install requests", "error")
        out_q.put(("DONE", None))
        return

    if not os.path.exists(urls_path):
        log(f"  [ERRO] Arquivo nao encontrado: {urls_path}", "error")
        out_q.put(("DONE", None))
        return

    with open(urls_path, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not urls:
        log("  [ERRO] Nenhuma URL encontrada no arquivo.", "error")
        out_q.put(("DONE", None))
        return

    try:
        intervalo = int(intervalo)
    except (ValueError, TypeError):
        intervalo = 60

    log(f"  Monitorando {len(urls)} site(s) — intervalo: {intervalo}s", "info")
    log("  Pressione PARAR para encerrar o monitoramento.", "dim")
    log("")

    ciclo = 0
    historico: dict[str, str] = {}

    while not stop_ev.is_set():
        ciclo += 1
        ts = datetime.now().strftime("%H:%M:%S")
        log(f"  -- Ciclo {ciclo} ({ts}) {'─' * 38}", "dim")

        for url in urls:
            if stop_ev.is_set():
                break
            try:
                t0 = time.time()
                r = requests.get(url, timeout=10, allow_redirects=True)
                ms = int((time.time() - t0) * 1000)
                code = r.status_code
                estado = "UP" if code < 400 else "DEGRADADO"
                tag = "success" if estado == "UP" else "warning"
            except Exception as e:
                ms = 0
                code = 0
                estado = "OFFLINE"
                tag = "error"

            mudou = historico.get(url) != estado
            historico[url] = estado

            alerta = " [MUDANCA DE ESTADO!]" if mudou and ciclo > 1 else ""
            status_str = f"{code}" if code else "---"
            log(f"  {estado:<10} {url:<48} {status_str}  {ms}ms{alerta}", tag)

        pct = 0.0
        out_q.put(("PROGRESS", pct))
        log("")

        for _ in range(intervalo):
            if stop_ev.is_set():
                break
            time.sleep(1)

    total_ok = sum(1 for s in historico.values() if s == "UP")
    out_q.put(("HISTORY", {
        "modulo": "uptime",
        "status": "encerrado",
        "detalhes": f"{len(urls)} sites | {ciclo} ciclos | {total_ok} UP no ultimo ciclo",
    }))
    log("  Monitoramento encerrado.", "warning")
    out_q.put(("DONE", None))
