import os
import json
import hashlib
import queue
import threading
from datetime import datetime


_SNAP_FILE = "comparacoes/snapshots.json"


def _load_snapshots(output_folder: str) -> dict:
    path = os.path.join(output_folder, "snapshots.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_snapshots(output_folder: str, snaps: dict) -> None:
    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, "snapshots.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snaps, f, indent=2, ensure_ascii=False)


def run_comparador(urls_path: str, output_folder: str, out_q: queue.Queue, stop_ev: threading.Event):
    def log(msg, tag="normal"):
        out_q.put((tag, msg + "\n"))

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        log(f"  [ERRO] Dependencia nao instalada: {e}", "error")
        out_q.put(("DONE", None))
        return

    if not os.path.exists(urls_path):
        log(f"  [ERRO] Arquivo nao encontrado: {urls_path}", "error")
        out_q.put(("DONE", None))
        return

    with open(urls_path, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not urls:
        log("  [ERRO] Nenhuma URL encontrada.", "error")
        out_q.put(("DONE", None))
        return

    snaps = _load_snapshots(output_folder)
    total = len(urls)
    log(f"  Comparando {total} pagina(s)...", "info")
    log(f"  Pasta de snapshots: {output_folder}", "info")
    log("")

    mudancas = 0
    novas = 0

    for i, url in enumerate(urls, 1):
        if stop_ev.is_set():
            log("\n  [!] Execucao interrompida.", "warning")
            break

        out_q.put(("PROGRESS", i / total))
        log(f"  [{i:02d}/{total}]  {url}", "info")

        try:
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.title.string.strip() if soup.title else url

            # hash do texto visivel da pagina (ignora scripts e estilos)
            for tag in soup(["script", "style", "meta", "link"]):
                tag.decompose()
            texto = " ".join(soup.get_text().split())
            novo_hash = hashlib.md5(texto.encode("utf-8", errors="ignore")).hexdigest()

            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if url not in snaps:
                snaps[url] = {"hash": novo_hash, "title": title,
                              "first_seen": agora, "last_change": agora, "last_check": agora}
                log(f"       Novo snapshot registrado: {title}", "success")
                novas += 1
            else:
                antigo = snaps[url]
                antigo["last_check"] = agora
                antigo["title"] = title
                if antigo["hash"] != novo_hash:
                    antigo["hash"] = novo_hash
                    antigo["last_change"] = agora
                    log(f"       MUDANCA DETECTADA! Pagina alterada desde {antigo.get('last_change', '?')}", "warning")
                    mudancas += 1
                else:
                    log(f"       Sem mudancas — ultimo check: {antigo.get('last_check', '?')}", "dim")

        except Exception as e:
            log(f"       [ERRO] {e}", "error")

    _save_snapshots(output_folder, snaps)

    log("")
    log("  " + "=" * 56, "dim")
    log("  COMPARACAO FINALIZADA!", "title")
    log(f"  Paginas verificadas : {total}", "info")
    log(f"  Mudancas detectadas : {mudancas}", "warning" if mudancas else "success")
    log(f"  Novos snapshots     : {novas}", "info")
    log(f"  Snapshots salvos em : {os.path.join(output_folder, 'snapshots.json')}", "info")
    log("  " + "=" * 56, "dim")

    out_q.put(("HISTORY", {
        "modulo": "comparador",
        "status": "sucesso",
        "detalhes": f"{total} paginas | {mudancas} mudancas | {novas} novas",
    }))
    out_q.put(("DONE", None))
