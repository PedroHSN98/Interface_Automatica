#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fpdf import FPDF
from datetime import datetime

ACCENT  = (88, 166, 255)
DARK    = (13, 17, 23)
DARK2   = (22, 27, 34)
DARK3   = (33, 38, 45)
BORDER  = (48, 54, 61)
TEXT    = (230, 237, 243)
TEXT2   = (139, 148, 158)
WHITE   = (255, 255, 255)
GREEN   = (63, 185, 80)
YELLOW  = (210, 153, 34)
RED     = (248, 81, 73)
ORANGE  = (227, 112, 43)


class PDF(FPDF):

    def header(self):
        self.set_fill_color(*DARK2)
        self.rect(0, 0, 210, 16, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*ACCENT)
        self.set_xy(10, 4)
        self.cell(0, 8, "AutoHub Pro  -  Documentacao do Projeto", align="L")
        self.set_text_color(*TEXT2)
        self.set_xy(0, 4)
        self.cell(w=200, h=8, text=f"Gerado em {datetime.now().strftime('%d/%m/%Y')}", align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_fill_color(*DARK2)
        self.rect(0, self.get_y(), 210, 12, "F")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*TEXT2)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="C")

    def cover(self):
        self.set_fill_color(*DARK)
        self.rect(0, 0, 210, 297, "F")

        self.set_fill_color(*DARK2)
        self.rect(20, 60, 170, 155, "F")

        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.rect(20, 60, 170, 155, "D")

        self.set_font("Helvetica", "B", 42)
        self.set_text_color(*ACCENT)
        self.set_xy(20, 72)
        self.cell(170, 20, "A", align="C")

        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*TEXT)
        self.set_xy(20, 98)
        self.cell(170, 12, "AutoHub Pro", align="C")

        self.set_font("Helvetica", "", 12)
        self.set_text_color(*TEXT2)
        self.set_xy(20, 112)
        self.cell(170, 8, "Central de Automacoes", align="C")

        self.set_draw_color(*BORDER)
        self.set_line_width(0.3)
        self.line(45, 126, 165, 126)

        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*GREEN)
        self.set_xy(20, 130)
        self.cell(170, 8, "Documentacao Tecnica Completa", align="C")

        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*TEXT2)
        self.set_xy(25, 142)
        self.multi_cell(160, 6,
            "Este documento descreve a arquitetura, tecnologias, modulos\n"
            "e decisoes de implementacao do projeto AutoHub Pro.",
            align="C")

        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*ACCENT)
        self.set_xy(20, 170)
        self.cell(170, 8, "v1.0.0  |  Python 3.13  |  Windows 10 / 11", align="C")

        self.set_font("Helvetica", "", 8)
        self.set_text_color(*TEXT2)
        self.set_xy(20, 240)
        self.cell(170, 6, "Autor: Pedro Henrique Santana Nascimento", align="C")
        self.set_xy(20, 247)
        self.cell(170, 6, f"Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}", align="C")

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def section_title(self, num, title):
        self.ln(4)
        self.set_fill_color(*DARK2)
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.5)
        y = self.get_y()
        self.rect(10, y, 190, 10, "F")
        self.line(10, y, 10, y + 10)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*ACCENT)
        self.set_xy(14, y + 1)
        self.cell(10, 8, f"{num}.", align="L")
        self.set_text_color(*TEXT)
        self.set_xy(24, y + 1)
        self.cell(0, 8, title, align="L")
        self.ln(12)

    def subsection(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*ACCENT)
        self.set_x(10)
        self.cell(0, 7, f"  {title}", align="L")
        self.ln(8)

    def body(self, text, indent=14):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*TEXT2)
        self.set_x(indent)
        self.multi_cell(190 - indent + 10, 5.5, text)
        self.ln(1)

    def bullet(self, text, color=None):
        col = color or TEXT2
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*col)
        self.set_x(16)
        self.cell(6, 6, "-", align="L")
        self.set_x(22)
        self.multi_cell(178, 5.5, text)

    def code_block(self, lines):
        self.ln(2)
        h_total = len(lines) * 6 + 8
        self.set_fill_color(*DARK3)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.3)
        y0 = self.get_y()
        self.rect(12, y0, 186, h_total, "FD")
        self.set_font("Courier", "", 9)
        self.set_text_color(*GREEN)
        for line in lines:
            self.set_x(16)
            self.cell(0, 6, line, align="L")
            self.ln(6)
        self.ln(3)

    def info_box(self, label, text, color=None):
        col = color or YELLOW
        self.ln(2)
        self.set_fill_color(col[0] // 6, col[1] // 6, col[2] // 6)
        self.set_draw_color(*col)
        self.set_line_width(0.4)
        y0 = self.get_y()
        self.set_x(12)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*col)
        self.cell(20, 7, f"  {label}", align="L")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*TEXT2)
        self.multi_cell(170, 7, text)
        self.set_draw_color(*col)
        self.set_line_width(0.4)
        self.line(12, y0, 12, self.get_y())
        self.ln(2)

    def table_header(self, cols):
        self.set_fill_color(*DARK3)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*ACCENT)
        x0 = 12
        for text, w in cols:
            self.set_x(x0)
            self.cell(w, 8, f"  {text}", border=1, fill=True, align="L")
            x0 += w
        self.ln(8)

    def table_row(self, cols, values, shade=False):
        if shade:
            self.set_fill_color(22, 27, 34)
        else:
            self.set_fill_color(*DARK)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*TEXT2)
        x0 = 12
        for val, (_, w) in zip(values, cols):
            self.set_x(x0)
            self.cell(w, 7, f"  {val}", border=1, fill=True, align="L")
            x0 += w
        self.ln(7)

    def divider(self):
        self.ln(3)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.line(12, self.get_y(), 198, self.get_y())
        self.ln(4)

    def page_bg(self):
        self.set_fill_color(*DARK)
        self.rect(0, 0, 210, 297, "F")

    def tag_badge(self, text, color):
        self.set_fill_color(*color)
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "B", 8)
        x = self.get_x()
        y = self.get_y()
        self.set_xy(x, y)
        self.cell(len(text) * 2 + 8, 6, text, fill=True, align="C")
        self.ln(8)


# ====================================================================== #
#  CONTEUDO                                                               #
# ====================================================================== #

def build(output_path: str):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=16)

    # ---- CAPA ----
    pdf.add_page()
    pdf.cover()

    # ================================================================== #
    #  PAG 2 - O que e o projeto + Estrutura de pastas                    #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(1, "O que e o AutoHub Pro?")
    pdf.body(
        "AutoHub Pro e uma aplicacao desktop para Windows construida com Python 3.13 e Tkinter. "
        "Ela funciona como uma central que reune tres automacoes distintas em uma unica interface "
        "grafica com tema escuro inspirado no GitHub Dark. O objetivo e simplificar tarefas "
        "repetitivas internas: analise de logs de servidor, download de imagens de portais web "
        "e avaliacao de acessibilidade de sites."
    )
    pdf.ln(2)

    cols_mod = [("Modulo", 52), ("Tecnologia principal", 60), ("Saida gerada", 74)]
    pdf.table_header(cols_mod)
    rows = [
        ("Analisador de Logs", "Paramiko (SSH)",      "Relatorio .txt com contagem de erros"),
        ("Scraper de Imagens",  "Requests + BeautifulSoup", "Imagens .jpg + planilha .xlsx"),
        ("AMAWeb",              "Selenium (Chrome)",  "Planilha .xlsx com notas de acesso"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(cols_mod, r, shade=i % 2 == 0)

    pdf.divider()
    pdf.section_title(2, "Estrutura de Pastas")
    pdf.body("O projeto e organizado em pacotes Python separados por responsabilidade:")

    pdf.set_font("Courier", "", 8.5)
    pdf.set_text_color(*TEXT2)
    tree = [
        "interface_automacao/",
        "  app.py                  <- ponto de entrada da aplicacao",
        "  criar_atalho.py         <- gera icone .ico e atalho .lnk no Desktop",
        "  gerar_pdf.py            <- gera o manual de instalacao em PDF",
        "  requirements.txt        <- dependencias pip",
        "  .env                    <- credenciais SSH (nao versionado)",
        "  .env.example            <- template das variaveis de ambiente",
        "",
        "  automations/            <- logica de negocio das 3 automacoes",
        "    logs.py               <- analisador de logs via SSH",
        "    scraper.py            <- downloader de imagens",
        "    amaweb.py             <- avaliador de acessibilidade",
        "",
        "  config/",
        "    theme.py              <- cores, fontes e constantes visuais",
        "",
        "  ui/",
        "    app.py                <- classe principal da janela (AutoHubApp)",
        "    utils.py              <- helper de output por fila",
        "",
        "  assets/",
        "    icon.ico              <- icone gerado pelo criar_atalho.py",
    ]
    for line in tree:
        pdf.set_x(14)
        pdf.cell(0, 5.2, line)
        pdf.ln(5.2)
    pdf.ln(4)

    # ================================================================== #
    #  PAG 3 - Modulo Analisador de Logs                                  #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(3, "Modulo 1: Analisador de Logs")
    pdf.body(
        "Arquivo: automations/logs.py\n"
        "Finalidade: Conecta via SSH em servidores internos, le arquivos de log no formato "
        "XML (log4j) e gera um relatorio consolidado com contagem de padroes de erro."
    )

    pdf.subsection("Como funciona")
    pdf.bullet("As credenciais SSH (usuario e senha) sao carregadas do arquivo .env via python-dotenv")
    pdf.bullet("A data de analise e selecionada pelo usuario na interface (formato dd/mm/aaaa)")
    pdf.bullet("O modulo conecta nos servidores Elasticsearch (192.168.200.124, .161, .162) e Liferay (.140, .147)")
    pdf.bullet("Os logs sao lidos remotamente via SSH usando o Paramiko, sem copiar os arquivos")
    pdf.bullet("O XML e analisado para contar 16 padroes de erro predefinidos")
    pdf.bullet("Os resultados sao exibidos com barras visuais (caracteres de bloco) no terminal")
    pdf.bullet("Erros de template FTL sao agrupados e exibidos separadamente")
    pdf.bullet("O usuario pode fazer download do relatorio como arquivo .txt")
    pdf.ln(2)

    pdf.subsection("Padroes de erro monitorados")
    erros = [
        "ElasticsearchStatusException",
        "404 Not Found",
        "Broken Pipe / Connection Reset",
        "LDAP authentication failures",
        "FTL template errors",
        "SAX Security Manager issues",
        "E outros 10 padroes internos",
    ]
    for e in erros:
        pdf.bullet(e)
    pdf.ln(2)

    pdf.subsection("Tecnologia usada")
    cols_t = [("Biblioteca", 50), ("Versao", 30), ("Para que serve", 106)]
    pdf.table_header(cols_t)
    pdf.table_row(cols_t, ["paramiko",      "3.0.0+", "Conexao SSH e execucao de comandos remotos"], shade=True)
    pdf.table_row(cols_t, ["python-dotenv", "1.0.0+", "Leitura de credenciais do arquivo .env"])
    pdf.table_row(cols_t, ["xml (stdlib)",  "nativo", "Parse dos arquivos de log no formato XML"], shade=True)

    pdf.divider()
    pdf.section_title(4, "Modulo 2: Scraper de Imagens")
    pdf.body(
        "Arquivo: automations/scraper.py\n"
        "Finalidade: Le uma lista de URLs de um arquivo .txt, acessa cada portal, "
        "extrai todas as imagens e baixa apenas as que estao dentro do limite de tamanho."
    )

    pdf.subsection("Como funciona")
    pdf.bullet("Le o arquivo de URLs (uma por linha) - padrao: fontes/links.txt")
    pdf.bullet("Para cada URL: faz requisicao HTTP, extrai todas as tags <img> com BeautifulSoup")
    pdf.bullet("Faz uma requisicao HEAD para verificar o tamanho antes de baixar (economiza banda)")
    pdf.bullet("Filtra: minimo 40 KB e maximo 2 MB - imagens fora desse intervalo sao ignoradas")
    pdf.bullet("Usa ThreadPoolExecutor com 5 workers por URL para downloads simultaneos")
    pdf.bullet("Salva as imagens como JPEG na pasta galeria_noticias/")
    pdf.bullet("Ao final, grava ou atualiza registro_noticias.xlsx com estatisticas da varredura")
    pdf.ln(2)

    pdf.subsection("Colunas do Excel gerado")
    cols_xl = [("Coluna", 50), ("Descricao", 136)]
    pdf.table_header(cols_xl)
    xl_rows = [
        ("Data",         "Data/hora da execucao"),
        ("Portal",       "Nome extraido do caminho da URL"),
        ("URL",          "URL original varrida"),
        ("Encontradas",  "Total de imagens encontradas na pagina"),
        ("Baixadas",     "Imagens dentro do filtro de tamanho, efetivamente salvas"),
        ("Fora_Padrao",  "Imagens acima de 2 MB que foram ignoradas"),
    ]
    for i, r in enumerate(xl_rows):
        pdf.table_row(cols_xl, r, shade=i % 2 == 0)

    # ================================================================== #
    #  PAG 4 - Modulo AMAWeb + Tecnologias                                #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(5, "Modulo 3: AMAWeb")
    pdf.body(
        "Arquivo: automations/amaweb.py\n"
        "Finalidade: Avalia automaticamente a acessibilidade de uma lista de sites "
        "acessando o portal AMAWeb (amaweb.unifesp.br) via navegador Chrome headless."
    )

    pdf.subsection("Como funciona")
    pdf.bullet("Le o arquivo de dominios/URLs - padrao: urls.txt")
    pdf.bullet("Inicia o Chrome em modo headless (sem interface grafica) usando Selenium")
    pdf.bullet("Para cada site, navega ate a pagina de resultados do avaliador AMAWeb")
    pdf.bullet("Aguarda ate 180 segundos para o carregamento completo da pagina")
    pdf.bullet("Extrai a nota do seletor CSS .score-circle-value")
    pdf.bullet("Se o site expirar o tempo ou der erro, registra 'Timeout / Erro' e continua")
    pdf.bullet("Exibe progresso em tempo real: nota atual, tempo medio, estimativa restante e barra visual")
    pdf.bullet("Salva os resultados em resultado.xlsx (caminho configuravel pela interface)")
    pdf.ln(2)

    pdf.subsection("Configuracao do Chrome Headless")
    pdf.body("O Selenium e iniciado com flags de estabilidade e segurança para funcionar sem janela:")
    pdf.code_block([
        "--headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
    ])

    pdf.divider()
    pdf.section_title(6, "Tecnologias e Bibliotecas")
    pdf.body("Todas as dependencias externas estao em requirements.txt e sao instaladas via pip.")

    cols_dep = [("Biblioteca", 46), ("Versao min.", 28), ("Usado em", 112)]
    pdf.table_header(cols_dep)
    deps = [
        ("tkinter",        "nativo",  "Interface grafica - janela, botoes, terminal, sidebar"),
        ("paramiko",       "3.0.0",   "Modulo de Logs - conexao SSH e leitura remota"),
        ("requests",       "2.31.0",  "Scraper - requisicoes HTTP para buscar HTML e imagens"),
        ("beautifulsoup4", "4.12.0",  "Scraper - parse do HTML para encontrar tags <img>"),
        ("selenium",       "4.18.0",  "AMAWeb - automacao do Chrome (headless)"),
        ("pandas",         "2.0.0",   "Scraper e AMAWeb - criacao e leitura de planilhas"),
        ("openpyxl",       "3.1.0",   "Scraper e AMAWeb - leitura/escrita de arquivos .xlsx"),
        ("pillow",         "10.0.0",  "criar_atalho.py - geracao do icone multi-resolucao"),
        ("python-dotenv",  "1.0.0",   "Logs - carregamento de credenciais do .env"),
        ("fpdf2",          "2.x",     "gerar_pdf.py - geracao dos manuais em PDF"),
        ("tqdm",           "4.66.0",  "Barras de progresso no terminal"),
    ]
    for i, row in enumerate(deps):
        pdf.table_row(cols_dep, row, shade=i % 2 == 0)

    # ================================================================== #
    #  PAG 5 - Interface Grafica + Threading                              #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(7, "Interface Grafica (ui/app.py)")
    pdf.body(
        "A janela principal e implementada na classe AutoHubApp em ui/app.py. "
        "O layout e dividido em quatro regioes fixas:"
    )
    pdf.bullet("Sidebar (215px): navegacao com 3 botoes + logo do projeto")
    pdf.bullet("Header: titulo da pagina atual + badge de status")
    pdf.bullet("Area de conteudo: cards de configuracao por modulo (seletor de arquivo/pasta + botoes Run/Stop)")
    pdf.bullet("Terminal de output: widget de texto com cores por tipo de mensagem")
    pdf.bullet("Status bar: relogio em tempo real + indicador da operacao atual")
    pdf.ln(2)

    pdf.subsection("Cores do terminal de output")
    cols_tags = [("Tag", 40), ("Cor", 40), ("Quando e usada", 106)]
    pdf.table_header(cols_tags)
    tags = [
        ("normal",   "Branco",        "Mensagens gerais"),
        ("info",     "Azul (#58a6ff)","Informacoes e status"),
        ("success",  "Verde",         "Conclusao bem-sucedida"),
        ("warning",  "Amarelo",       "Avisos e alertas"),
        ("error",    "Vermelho",      "Erros e falhas"),
        ("progress", "Laranja",       "Atualizacoes de progresso"),
        ("dim",      "Cinza escuro",  "Texto secundario / separadores"),
        ("title",    "Branco negrito","Titulos de secao no output"),
    ]
    for i, r in enumerate(tags):
        pdf.table_row(cols_tags, r, shade=i % 2 == 0)

    pdf.divider()
    pdf.section_title(8, "Modelo de Threading")
    pdf.body(
        "Para que a interface nao trave durante a execucao das automacoes, "
        "cada modulo roda em uma thread separada. A comunicacao com a UI e feita "
        "de forma segura via fila (queue.Queue)."
    )
    pdf.ln(2)

    pdf.subsection("Fluxo de execucao")
    pdf.bullet("Botao Run: cria um threading.Event (stop_ev) e inicia uma thread com a funcao do modulo")
    pdf.bullet("A funcao do modulo recebe a fila (out_q) e o evento de parada (stop_ev)")
    pdf.bullet("Para enviar texto ao terminal, o modulo chama: out_q.put((tag, mensagem))")
    pdf.bullet("A UI faz polling da fila a cada 50ms com _poll_output() e renderiza as mensagens")
    pdf.bullet("Botao Stop: chama stop_ev.set(), sinalizando a thread para encerrar graciosamente")
    pdf.bullet("Ao terminar, a thread envia out_q.put(('DONE', None)) para notificar a UI")
    pdf.ln(2)

    pdf.subsection("Por que essa arquitetura?")
    pdf.info_box("MOTIVO",
        "Tkinter nao e thread-safe: nunca atualize widgets diretamente de uma thread secundaria. "
        "A fila (Queue) age como canal seguro - a thread escreve, a UI le no seu proprio ciclo de 50ms.",
        ACCENT)

    pdf.code_block([
        "# Padrao seguido por todos os modulos:",
        "def run_modulo(input_path, output_path, out_q, stop_ev):",
        "    def log(msg, tag='normal'):",
        "        out_q.put((tag, msg + '\\n'))",
        "",
        "    log('Iniciando...', 'info')",
        "    for item in lista:",
        "        if stop_ev.is_set():  # verifica cancelamento",
        "            break",
        "        # ... processar item ...",
        "        log(f'Processado: {item}', 'success')",
        "",
        "    out_q.put(('DONE', None))  # sinaliza conclusao",
    ])

    # ================================================================== #
    #  PAG 6 - Tema + Configuracao + Utilitarios                          #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(9, "Sistema de Tema (config/theme.py)")
    pdf.body(
        "Todas as cores, fontes e tamanhos da interface estao centralizados em config/theme.py. "
        "Isso garante consistencia visual e facilita mudancas futuras - basta alterar um valor "
        "nesse arquivo para refletir em toda a aplicacao."
    )
    pdf.ln(2)

    pdf.subsection("Paleta de cores (GitHub Dark)")
    cols_c = [("Constante", 60), ("Hex / RGB", 50), ("Onde e aplicada", 76)]
    pdf.table_header(cols_c)
    cores = [
        ("DARK (fundo principal)",    "#0d1117",  "Background da janela e paginas"),
        ("DARK2 (fundo secundario)",  "#161b22",  "Cards, header, footer"),
        ("DARK3 (fundo terciario)",   "#21262d",  "Code blocks, linhas de tabela"),
        ("SIDEBAR",                   "#010409",  "Painel lateral de navegacao"),
        ("ACCENT (azul)",             "#58a6ff",  "Botoes, destaques, links"),
        ("GREEN (sucesso)",           "#3fb950",  "Status OK, mensagens de sucesso"),
        ("RED (erro)",                "#f85149",  "Erros, alertas criticos"),
        ("YELLOW (aviso)",            "#d29922",  "Avisos, alertas moderados"),
        ("ORANGE (progresso)",        "#e3702b",  "Mensagens de progresso"),
        ("TEXT (texto principal)",    "#e6edf3",  "Todo texto de conteudo"),
        ("TEXT2 (texto secundario)",  "#8b949e",  "Subtitulos, labels, descricoes"),
    ]
    for i, r in enumerate(cores):
        pdf.table_row(cols_c, r, shade=i % 2 == 0)

    pdf.ln(2)
    pdf.subsection("Fontes utilizadas")
    pdf.bullet("Interface (UI): Segoe UI - fonte nativa do Windows, clara e moderna")
    pdf.bullet("Terminal de output: Consolas - monospace nativa do Windows, ideal para logs")
    pdf.bullet("Tamanhos: 7px (labels pequenos) ate 14px (titulos de secao)")
    pdf.ln(2)

    pdf.divider()
    pdf.section_title(10, "Utilitarios e Scripts Auxiliares")

    pdf.subsection("criar_atalho.py")
    pdf.body(
        "Script que cria um atalho (.lnk) do aplicativo na Area de Trabalho do Windows. "
        "Ele tambem gera automaticamente o icone .ico multi-resolucao usando Pillow."
    )
    pdf.bullet("Gera o icone em 6 resolucoes: 16, 32, 48, 64, 128 e 256 pixels")
    pdf.bullet("O icone tem fundo escuro (#0d1117) com borda de destaque e letra 'A' centralizada")
    pdf.bullet("O atalho usa pythonw.exe para abrir o app sem mostrar janela de console")
    pdf.bullet("O arquivo AutoHub Pro.lnk e criado diretamente na Area de Trabalho")
    pdf.ln(2)

    pdf.subsection("gerar_pdf.py")
    pdf.body(
        "Script que gera o manual de instalacao do projeto em formato PDF usando fpdf2. "
        "Segue o mesmo tema visual da aplicacao (GitHub Dark) com header, footer e estilos proprios."
    )
    pdf.ln(2)

    pdf.subsection("ui/utils.py")
    pdf.body(
        "Helper simples com a funcao de polling da fila de output. "
        "Centraliza a logica de leitura da queue e atualizacao do widget de terminal."
    )

    # ================================================================== #
    #  PAG 7 - Configuracao de Ambiente + Resumo Tecnico                  #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(11, "Configuracao de Ambiente (.env)")
    pdf.body(
        "O arquivo .env armazena credenciais sensiveis que NAO devem ser versionadas no git. "
        "O arquivo .env.example serve de template e PODE ser versionado."
    )
    pdf.ln(2)

    pdf.subsection("Variaveis necessarias")
    pdf.code_block([
        "# .env.example",
        "LIFERAY_USUARIO=seu_usuario",
        "LIFERAY_SENHA=sua_senha",
    ])
    pdf.body("Essas credenciais sao usadas exclusivamente pelo modulo Analisador de Logs "
             "para autenticar as conexoes SSH nos servidores internos.")
    pdf.info_box("SEGURANCA",
        "O arquivo .env esta listado no .gitignore e nunca deve ser commitado. "
        "Cada desenvolvedor deve criar o proprio .env localmente a partir do .env.example.",
        RED)

    pdf.divider()
    pdf.section_title(12, "Resumo Tecnico do Projeto")

    cols_r = [("Aspecto", 70), ("Detalhe", 116)]
    pdf.table_header(cols_r)
    resumo = [
        ("Linguagem",              "Python 3.13"),
        ("Interface grafica",      "Tkinter (nativo do Python)"),
        ("Sistema operacional",    "Windows 10 / 11"),
        ("Versao",                 "v1.0.0"),
        ("Modulos de automacao",   "3 (Logs, Scraper, AMAWeb)"),
        ("Dependencias externas",  "11 pacotes pip"),
        ("Modelo de execucao",     "Multi-thread com Queue para comunicacao UI"),
        ("Armazenamento",          "Baseado em arquivos (Excel, TXT, JPEG)"),
        ("Banco de dados",         "Nenhum"),
        ("Rede",                   "SSH (Logs) + HTTP (Scraper) + Selenium (AMAWeb)"),
        ("Linhas de codigo (est.)", "~1.330 linhas no total"),
        ("Autor",                  "Pedro Henrique Santana Nascimento"),
        ("Gerado em",              datetime.now().strftime("%d/%m/%Y as %H:%M")),
    ]
    for i, r in enumerate(resumo):
        pdf.table_row(cols_r, r, shade=i % 2 == 0)

    pdf.ln(6)
    pdf.info_box("OBSERVACAO",
        "Este documento foi gerado automaticamente pelo script gerar_documentacao.py "
        "e reflete o estado do projeto na data indicada acima.",
        ACCENT)

    pdf.output(output_path)
    print(f"PDF gerado: {output_path}")


if __name__ == "__main__":
    build("AutoHub_Pro_Documentacao.pdf")
