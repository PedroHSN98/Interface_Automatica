"""Camada compartilhada entre a interface desktop (ui/app.py) e a interface
web (web/server.py).

Cada `build_*` recebe os parametros ja resolvidos/validados pela interface
que o chama e devolve o callable `(out_q, stop_ev) -> None` pronto para ser
executado em uma thread. Existe para nao duplicar a construcao desse
callable nas duas interfaces.
"""

from automations.amaweb import run_amaweb
from automations.logs import run_logs
from automations.relatorio import run_relatorio
from automations.scraper import run_scraper


def build_logs(datas, servidores_elastic, servidores_liferay):
    return lambda q, ev: run_logs(
        datas, q, ev,
        servidores_elastic=servidores_elastic,
        servidores_liferay=servidores_liferay,
    )


def build_scraper(links_path, output_folder):
    return lambda q, ev: run_scraper(links_path, output_folder, q, ev)


def build_amaweb(urls_path, resultado_path, threshold):
    return lambda q, ev: run_amaweb(urls_path, resultado_path, q, ev, threshold=threshold)


def build_relatorio(output_path):
    return lambda q, ev: run_relatorio(output_path, q, ev)
