import os
import queue
import threading
from datetime import datetime
import paramiko
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCHS = {
    "Elasticsearch 1": "192.168.200.124",
    "Elasticsearch 2": "192.168.200.161",
    "Elasticsearch 3": "192.168.200.162",
}

LIFERAYS = {
    "Liferay 1": "192.168.200.140",
    "Liferay 2": "192.168.200.147",
}

USUARIO = os.getenv("LIFERAY_USUARIO")
SENHA   = os.getenv("LIFERAY_SENHA")

ARQUIVO_LOG_ELASTIC = "/var/log/elasticsearch/LiferayElasticsearchCluster.log"
BASE_LIFERAY = "/home/liferay/logs/liferay.{data}"

PADROES = {
    '<log4j:message><![CDATA[org.elasticsearch.ElasticsearchStatusException:':
        "ElasticSearchException",
    '<log4j:message><![CDATA[{code="404", msg="Not Found",':
        "Notfound",
    '<log4j:message><![CDATA[java.io.IOException: Broken pipe]]></log4j:message>':
        "Broken Pipe",
    '<log4j:message><![CDATA[java.io.IOException: Connection reset by peer]]></log4j:message>':
        "Connection Reset By Peer",
    'ldap.internal.exportimport.LDAPUserImporterImpl':
        "LDAPUserImporterImpl",
    '<log4j:message><![CDATA[Problem accessing LDAP server]]></log4j:message>':
        "Problem accessing LDAP server",
    '(ldap.internal.authenticator.LDAPAuth)':
        "LDAPAuth",
    '<log4j:message><![CDATA[Skip /o/js/resolved-module/frontend-js-metal-web$metal':
        "Skip /frontend-js-metal-web$metal",
    '<log4j:message><![CDATA[No theme found for specified theme id mtportal_WAR_mtportaltheme.':
        "No theme found for mtportal_WAR",
    '<log4j:message><![CDATA[{code="404"':
        'Error {code="404"}',
    '<log4j:message><![CDATA[SAX Security Manager':
        "SAX Security Manager",
    'uri=/mt-portal-theme/images/ajax-loader.gif':
        "Ajax-Loader",
    'com.liferay.change.tracking.internal.servlet.filter.CTCollectionPreviewFilter':
        "CTCollectionPreviewFilter",
    'FTL stack trace':
        "FTL stack trace",
    'log4j:throwable><![CDATA[com.liferay.document.library.kernel.exception.NoSuchFileEntryException':
        "NoSuchFileEntryException",
    'InvalidRepositoryIdException':
        "InvalidRepositoryIdException",
    '[PaginationLimitFilter] Applying limit: bot UA detected':
        "PaginationLimitFilter — bot UA detected",
}


def _ssh_client(ip):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=USUARIO, password=SENHA, timeout=20)
    return ssh


def _exec_cmd(ssh, cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors="ignore").strip()
    err = stderr.read().decode(errors="ignore").strip()
    return out, err


def _obter_tamanho_elastic(nome, ip):
    try:
        ssh = _ssh_client(ip)
        out, err = _exec_cmd(ssh, f"stat -c%s {ARQUIVO_LOG_ELASTIC}")
        ssh.close()
        if err:
            return None, f"{nome}: erro ao obter tamanho ({err})"
        return int(out), None
    except Exception as e:
        return None, f"{nome}: falha de conexão ({e})"


def _obter_tamanho_liferay(nome, ip, data_iso):
    try:
        ssh = _ssh_client(ip)
        arq = BASE_LIFERAY.format(data=data_iso) + ".log"
        out, err = _exec_cmd(ssh, f"stat -c%s '{arq}'")
        ssh.close()
        if err:
            return None, f"{nome}: arquivo LOG não encontrado para {data_iso}"
        return int(out), None
    except Exception as e:
        return None, f"{nome}: falha na etapa tamanho LOG ({e})"


def _grep_padroes(ssh, xml):
    totais = dict.fromkeys(PADROES.values(), 0)
    for busca, exibicao in PADROES.items():
        out, _ = _exec_cmd(ssh, f"grep -F -c {repr(busca)} '{xml}'")
        try:
            totais[exibicao] = int(out or "0")
        except ValueError:
            totais[exibicao] = 0
    return totais


def _grep_ftl_templates(ssh, xml):
    cmd = f"grep -oP '\\[in template \"[^\"]*\"' '{xml}' | sort | uniq -c | sort -rn"
    out, _ = _exec_cmd(ssh, cmd)
    templates = {}
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            try:
                templates[parts[1]] = int(parts[0])
            except ValueError:
                pass
    return templates


def _contar_padroes(nome, ip, data_iso):
    try:
        ssh = _ssh_client(ip)
        xml = BASE_LIFERAY.format(data=data_iso) + ".xml"
        out, _ = _exec_cmd(ssh, f"test -f '{xml}' && echo OK")
        if out != "OK":
            ssh.close()
            return None, f"{nome}: arquivo XML não encontrado para {data_iso}"
        totais = _grep_padroes(ssh, xml)
        ftl_templates = {}
        if totais.get("FTL stack trace", 0) > 0:
            ftl_templates = _grep_ftl_templates(ssh, xml)
        ssh.close()
        return {"totais": totais, "ftl_templates": ftl_templates}, None
    except Exception as e:
        return None, f"{nome}: falha na análise XML ({e})"


def run_logs(datas: list, out_q: queue.Queue, stop_ev: threading.Event):
    def log(msg, tag="normal"):
        out_q.put((tag, msg + "\n"))

    log("  Iniciando coleta de logs via SSH...", "info")
    log("")

    # Coleta tamanhos Elasticsearch
    log("  ── Elasticsearch ──────────────────────────────────────", "dim")
    elastic_bytes = {}
    for nome, ip in ELASTICSEARCHS.items():
        if stop_ev.is_set():
            break
        log(f"  → Conectando {nome} ({ip})...", "progress")
        tamanho, erro = _obter_tamanho_elastic(nome, ip)
        if erro:
            log(f"  [!] {erro}", "warning")
        else:
            log(f"  ✓ {nome}: {tamanho:,} bytes", "success")
        elastic_bytes[nome] = tamanho

    result_por_data = {}

    for data in datas:
        if stop_ev.is_set():
            break

        data_iso = data.strftime("%Y-%m-%d")
        data_br  = data.strftime("%d/%m/%Y")

        log(f"\n  {'─' * 54}", "dim")
        log(f"  Data: {data_br}", "title")
        log(f"  {'─' * 54}", "dim")

        consolidado        = dict.fromkeys(PADROES.values(), 0)
        ftl_consolidado    = {}
        tamanhos_logs      = {}

        for nome, ip in LIFERAYS.items():
            if stop_ev.is_set():
                break

            log(f"\n  → Analisando XML {nome} ({data_iso})...", "info")
            contagens, erro = _contar_padroes(nome, ip, data_iso)
            if erro:
                log(f"  [!] {erro}", "warning")
            else:
                for k, v in contagens["totais"].items():
                    consolidado[k] += v
                for tmpl, cnt in contagens["ftl_templates"].items():
                    ftl_consolidado[tmpl] = ftl_consolidado.get(tmpl, 0) + cnt

            log(f"  → Obtendo tamanho LOG {nome} ({data_iso})...", "info")
            tamanho, erro = _obter_tamanho_liferay(nome, ip, data_iso)
            if erro:
                log(f"  [!] {erro}", "warning")
            tamanhos_logs[nome] = tamanho

        log("")
        total_data = 0
        for i, (nome_erro, qty) in enumerate(consolidado.items(), 1):
            if qty == 0:
                tag = "dim"
            elif qty < 5:
                tag = "success"
            elif qty < 20:
                tag = "warning"
            else:
                tag = "error"
            bar = "█" * min(qty, 30)
            log(f"  {i:02d}. {nome_erro:<52} {qty:>5}   {bar}", tag)
            total_data += qty

        log("")
        for nome in LIFERAYS:
            tam = tamanhos_logs.get(nome)
            if tam is None:
                log(f"  LOG {nome}: arquivo não encontrado", "warning")
            else:
                log(f"  LOG {nome}: {tam / 1024 / 1024:.1f} MB", "info")

        result_por_data[data_iso] = {
            "contagem":      consolidado,
            "tamanhos_logs": tamanhos_logs,
            "ftl_templates": ftl_consolidado,
        }

    if stop_ev.is_set():
        log("\n  [!] Execução interrompida.", "warning")
        out_q.put(("DONE", None))
        return

    log(f"\n  {'─' * 54}", "dim")
    log("  Tamanho em bytes — Elasticsearch:", "title")
    log("")
    for nome, valor in elastic_bytes.items():
        if valor is None:
            log(f"  {nome}: erro ao obter", "warning")
        else:
            log(f"  {nome}: {valor:,} bytes", "info")

    # Seção consolidada de FTL stack trace (todas as datas)
    ftl_geral = {}
    for info in result_por_data.values():
        for tmpl, cnt in info["ftl_templates"].items():
            ftl_geral[tmpl] = ftl_geral.get(tmpl, 0) + cnt

    if ftl_geral:
        log(f"\n  {'─' * 54}", "dim")
        log("  Erros de FTL stack trace:", "title")
        log("")
        for tmpl, cnt in sorted(ftl_geral.items(), key=lambda x: -x[1]):
            log(f"  {tmpl}  ({cnt}x)", "warning")

    log("\n  Coleta concluída com sucesso!", "success")

    out_q.put(("RESULT_DATA", {
        "elastic_bytes": elastic_bytes,
        "por_data":      result_por_data,
    }))
    out_q.put(("DONE", None))
