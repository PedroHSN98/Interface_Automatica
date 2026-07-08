import sys
import os
import queue
import threading
import json

# Garante que o cwd seja a raiz do projeto
ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from flask import Flask, Response, render_template, request, jsonify
from datetime import datetime

from automations.logs import run_logs, ELASTICSEARCHS, LIFERAYS
from automations.scraper import run_scraper
from automations.amaweb import run_amaweb
from automations.relatorio import run_relatorio
from config import settings
from utils import historico as hist

app = Flask(__name__)

# ─── Estado global ────────────────────────────────────────────────────────────
_out_q: queue.Queue = queue.Queue()
_stop_ev: threading.Event = threading.Event()
_state = {"running": False, "module": None}


def _clear_queue():
    while not _out_q.empty():
        try:
            _out_q.get_nowait()
        except queue.Empty:
            break


def _wrap_run(fn, out_q, stop_ev):
    try:
        fn(out_q, stop_ev)
    except Exception as e:
        out_q.put(("error", f"  [ERRO CRÍTICO] {e}\n"))
        out_q.put(("DONE", None))
    finally:
        _state["running"] = False
        _state["module"] = None


# ─── Rotas ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    cfg = settings.load()
    return render_template(
        "index.html",
        cfg=cfg,
        elasticsearchs=list(ELASTICSEARCHS.keys()),
        liferays=list(LIFERAYS.keys()),
    )


@app.route("/stream")
def stream():
    def generate():
        while True:
            try:
                tag, payload = _out_q.get(timeout=0.4)
                if tag == "DONE":
                    yield f"data: {json.dumps({'tag': 'DONE'})}\n\n"
                    return
                elif tag == "PROGRESS":
                    yield f"data: {json.dumps({'tag': 'PROGRESS', 'value': float(payload)})}\n\n"
                elif tag in ("RESULT_DATA", "RESULT_AMA", "DONE_SCRAPER"):
                    # Apenas server-side — não transmite
                    pass
                elif tag == "HISTORY":
                    try:
                        hist.registrar(
                            payload["modulo"], payload["status"],
                            payload.get("detalhes", ""),
                        )
                    except Exception:
                        pass
                else:
                    yield f"data: {json.dumps({'tag': tag, 'text': payload})}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'tag': 'ping'})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/run/<module>", methods=["POST"])
def run_module(module):
    if _state["running"]:
        return jsonify({"ok": False, "error": "Já há uma automação em execução."})

    data = request.get_json(force=True, silent=True) or {}
    cfg = settings.load()
    _clear_queue()
    _stop_ev.clear()

    target = None

    if module == "logs":
        datas_str = data.get("datas", [])
        if not datas_str:
            return jsonify({"ok": False, "error": "Adicione ao menos uma data."})
        try:
            datas = [datetime.strptime(d, "%d/%m/%Y") for d in datas_str]
        except ValueError:
            return jsonify({"ok": False, "error": "Data inválida. Use dd/mm/aaaa."})
        elastic_sel = data.get("elastic") or list(ELASTICSEARCHS.keys())
        liferay_sel = data.get("liferay") or list(LIFERAYS.keys())
        target = lambda q, ev: run_logs(
            datas, q, ev,
            servidores_elastic=elastic_sel,
            servidores_liferay=liferay_sel,
        )

    elif module == "scraper":
        links = data.get("links") or cfg.get("scraper_links", "fontes/links.txt")
        output = data.get("output") or cfg.get("scraper_output", "galeria_noticias")
        target = lambda q, ev: run_scraper(links, output, q, ev)

    elif module == "amaweb":
        urls = data.get("urls") or cfg.get("ama_urls", "urls.txt")
        result = data.get("result") or cfg.get("ama_result", "resultado.xlsx")
        threshold = float(data.get("threshold", cfg.get("ama_threshold", 5.0)))
        target = lambda q, ev: run_amaweb(urls, result, q, ev, threshold=threshold)

    elif module == "relatorio":
        output = data.get("output") or "relatorio_consolidado.xlsx"
        target = lambda q, ev: run_relatorio(output, q, ev)

    else:
        return jsonify({"ok": False, "error": f"Módulo desconhecido: {module}"})

    _state["running"] = True
    _state["module"] = module

    threading.Thread(target=_wrap_run, args=(target, _out_q, _stop_ev), daemon=True).start()
    return jsonify({"ok": True})


@app.route("/stop", methods=["POST"])
def stop():
    _stop_ev.set()
    return jsonify({"ok": True})


@app.route("/status")
def status():
    return jsonify(_state)


@app.route("/historico")
def historico_api():
    return jsonify(hist.listar(100))


@app.route("/config", methods=["POST"])
def config_save():
    data = request.get_json(force=True, silent=True) or {}
    settings.save({**settings.load(), **data})
    return jsonify({"ok": True})


if __name__ == "__main__":
    import webbrowser
    import threading as _th

    port = 5000

    print("=" * 52)
    print("  AutoHub Pro — Interface Web")
    print(f"  Acesse: http://localhost:{port}")
    print("  Ctrl+C para encerrar")
    print("=" * 52)

    def _open():
        import time
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{port}")

    _th.Thread(target=_open, daemon=True).start()
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
