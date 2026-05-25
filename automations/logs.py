import os
import queue
import threading


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


def run_logs(log_path: str, out_q: queue.Queue, stop_ev: threading.Event):
    def log(msg, tag="normal"):
        out_q.put((tag, msg + "\n"))

    log("  Iniciando análise de logs...", "info")
    log(f"  Arquivo: {log_path}", "info")
    log("")

    if not os.path.exists(log_path):
        log(f"  [ERRO] Arquivo não encontrado: {log_path}", "error")
        log("  Verifique o caminho e tente novamente.", "warning")
        out_q.put(("DONE", None))
        return

    contagem = {nome: 0 for nome in PADROES.values()}

    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                if stop_ev.is_set():
                    log("\n  [!] Execução interrompida.", "warning")
                    out_q.put(("DONE", None))
                    return
                for termo, nome in PADROES.items():
                    if termo in linha:
                        contagem[nome] += 1
    except Exception as e:
        log(f"  [ERRO] {e}", "error")
        out_q.put(("DONE", None))
        return

    log("  " + "─" * 56, "dim")
    log("  RELATÓRIO DE ERROS", "title")
    log("  " + "─" * 56, "dim")
    log("")

    total = 0
    for i, (erro, qty) in enumerate(contagem.items(), 1):
        if qty == 0:
            tag = "dim"
        elif qty < 5:
            tag = "success"
        elif qty < 20:
            tag = "warning"
        else:
            tag = "error"

        bar = "█" * min(qty, 30)
        log(f"  {i:02d}. {erro:<52} {qty:>5}   {bar}", tag)
        total += qty

    log("")
    log("  " + "─" * 56, "dim")
    log(f"  Total de ocorrências encontradas: {total}", "title")
    log("  " + "─" * 56, "dim")
    log("")
    log("  Análise concluída com sucesso!", "success")
    out_q.put(("DONE", None))