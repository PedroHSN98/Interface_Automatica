#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fpdf import FPDF
from datetime import datetime

ACCENT   = (88, 166, 255)
DARK     = (13, 17, 23)
DARK2    = (22, 27, 34)
DARK3    = (33, 38, 45)
BORDER   = (48, 54, 61)
TEXT     = (230, 237, 243)
TEXT2    = (139, 148, 158)
WHITE    = (255, 255, 255)
GREEN    = (63, 185, 80)
YELLOW   = (210, 153, 34)
RED      = (248, 81, 73)
ORANGE   = (227, 112, 43)


class PDF(FPDF):

    def header(self):
        self.set_fill_color(*DARK2)
        self.rect(0, 0, 210, 16, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*ACCENT)
        self.set_xy(10, 4)
        self.cell(0, 8, "AutoHub Pro  -  Manual de Instalacao", align="L")
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

    # ------------------------------------------------------------------ #

    def cover(self):
        # Fundo escuro total
        self.set_fill_color(*DARK)
        self.rect(0, 0, 210, 297, "F")

        # Bloco central
        self.set_fill_color(*DARK2)
        self.rect(20, 70, 170, 130, "F")

        # Borda accent
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.rect(20, 70, 170, 130, "D")

        # Icone / simbolo
        self.set_font("Helvetica", "B", 42)
        self.set_text_color(*ACCENT)
        self.set_xy(20, 82)
        self.cell(170, 20, "A", align="C")

        # Titulo
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*TEXT)
        self.set_xy(20, 108)
        self.cell(170, 12, "AutoHub Pro", align="C")

        # Subtitulo
        self.set_font("Helvetica", "", 12)
        self.set_text_color(*TEXT2)
        self.set_xy(20, 122)
        self.cell(170, 8, "Central de Automacoes", align="C")

        # Linha separadora
        self.set_draw_color(*BORDER)
        self.set_line_width(0.3)
        self.line(45, 136, 165, 136)

        # Descricao
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*TEXT2)
        self.set_xy(20, 140)
        self.multi_cell(170, 6,
            "Manual completo de instalacao e configuracao\npara implantacao em novo computador.",
            align="C")

        # Versao
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*ACCENT)
        self.set_xy(20, 163)
        self.cell(170, 8, "v1.0.0  |  Python 3.13  |  Windows 10 / 11", align="C")

        # Rodape da capa
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*TEXT2)
        self.set_xy(20, 260)
        self.cell(170, 6, "Pedro Henrique Santana Nascimento", align="C")

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
    #  PAG 2 - Visao Geral + Pre-requisitos                               #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(1, "Visao Geral do Projeto")
    pdf.body(
        "AutoHub Pro e uma aplicacao desktop construida em Python com interface grafica "
        "Tkinter. Ela centraliza tres automacoes distintas em um unico painel: analisador "
        "de logs de servidor, scraper de imagens e avaliador de acessibilidade web (AMAWeb). "
        "Toda a interface usa tema escuro inspirado no GitHub Dark, com fontes nativas do Windows."
    )
    pdf.ln(2)

    cols_mod = [("Modulo", 52), ("Descricao resumida", 138)]
    pdf.table_header(cols_mod)
    rows = [
        ("Analisador de Logs", "Le arquivo XML (log4j), conta padroes de erro e gera relatorio"),
        ("Scraper de Imagens", "Baixa imagens entre 40 KB e 2 MB das URLs listadas em .txt"),
        ("AMAWeb", "Avalia acessibilidade de sites via amaweb.unifesp.br com Selenium"),
    ]
    for i, (m, d) in enumerate(rows):
        pdf.table_row(cols_mod, [m, d], shade=i % 2 == 0)

    pdf.divider()
    pdf.section_title(2, "Pre-requisitos obrigatorios")
    pdf.body("Instale os tres itens abaixo ANTES de executar qualquer passo de instalacao do projeto.")
    pdf.ln(2)

    pdf.subsection("2.1  Python 3.13")
    pdf.body("Baixe o instalador oficial em:  https://www.python.org/downloads/")
    pdf.info_box("IMPORTANTE",
        'Durante a instalacao, marque a opcao "Add Python to PATH" antes de clicar em Install Now.',
        YELLOW)
    pdf.body("Verifique apos instalar abrindo o terminal e digitando:")
    pdf.code_block(["python --version", "# Esperado: Python 3.13.x"])

    pdf.subsection("2.2  Google Chrome")
    pdf.body("Instale a versao mais recente do Chrome:")
    pdf.bullet("Acesse: https://www.google.com/chrome")
    pdf.bullet("O Chrome e necessario apenas para o modulo AMAWeb (Selenium).")
    pdf.ln(2)

    pdf.subsection("2.3  ChromeDriver")
    pdf.body(
        "O ChromeDriver precisa estar na mesma versao principal do Chrome instalado. "
        "A forma mais simples e instalar via pip apos criar o ambiente virtual (Passo 3), "
        "pois o Selenium 4.x gerencia o driver automaticamente. Se preferir instalar manualmente:"
    )
    pdf.bullet("Acesse: https://chromedriver.chromium.org/downloads")
    pdf.bullet("Coloque o chromedriver.exe em C:\\Windows\\System32 ou qualquer pasta no PATH.")

    # ================================================================== #
    #  PAG 3 - Instalacao passo a passo                                   #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(3, "Instalacao passo a passo")

    pdf.subsection("Passo 1 - Copiar o projeto")
    pdf.body(
        "Copie a pasta completa do projeto para o novo computador. "
        "Recomenda-se colocar em um caminho sem espacos ou acentos, por exemplo:"
    )
    pdf.code_block(["C:\\Projetos\\interface_automacao\\"])
    pdf.info_box("ATENCAO",
        "NAO copie a pasta .venv. Ela sera recriada no novo computador no proximo passo.",
        RED)

    pdf.subsection("Passo 2 - Abrir o terminal na pasta do projeto")
    pdf.body("No Windows Explorer, navegue ate a pasta do projeto, clique na barra de endereco, "
             "digite  cmd  ou  powershell  e pressione Enter. O terminal abrira ja dentro da pasta.")
    pdf.info_box("DICA",
        "Voce tambem pode abrir o PowerShell ou Prompt de Comando normalmente e usar:\n"
        "  cd C:\\Projetos\\interface_automacao",
        ACCENT)

    pdf.subsection("Passo 3 - Criar o ambiente virtual")
    pdf.body("Execute o comando abaixo para criar um ambiente Python isolado dentro da pasta:")
    pdf.code_block(["python -m venv .venv"])
    pdf.body("Isso cria a pasta .venv com uma copia isolada do Python.")

    pdf.subsection("Passo 4 - Ativar o ambiente virtual")
    pdf.body("Antes de instalar as dependencias, ative o ambiente:")
    pdf.code_block([
        "# PowerShell:",
        ".venv\\Scripts\\activate",
        "",
        "# Prompt de Comando (cmd):",
        ".venv\\Scripts\\activate.bat",
    ])
    pdf.body('Apos ativar, o terminal mostrara (.venv) no inicio da linha.')

    pdf.subsection("Passo 5 - Instalar as dependencias")
    pdf.body("Com o ambiente ativo, instale todos os pacotes de uma vez:")
    pdf.code_block(["pip install -r requirements.txt"])
    pdf.info_box("AGUARDE",
        "A instalacao pode levar alguns minutos dependendo da conexao. "
        "Packages como numpy e pandas sao maiores.",
        YELLOW)

    pdf.subsection("Passo 6 - Executar o aplicativo")
    pdf.body("Ainda com o ambiente ativo, execute:")
    pdf.code_block(["python app.py"])
    pdf.body("A janela do AutoHub Pro sera aberta.")

    # ================================================================== #
    #  PAG 4 - Atalho + Estrutura + Dependencias                          #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(4, "Criar atalho na Area de Trabalho (opcional)")
    pdf.body(
        "Com o ambiente virtual ativo, execute o script auxiliar incluido no projeto. "
        "Ele gera o icone .ico e cria um atalho .lnk na Area de Trabalho apontando "
        "para pythonw.exe (sem abrir janela de console ao iniciar):"
    )
    pdf.code_block(["python criar_atalho.py"])
    pdf.body("Apos executar, o arquivo  AutoHub Pro.lnk  aparecera na Area de Trabalho.")

    pdf.divider()
    pdf.section_title(5, "Estrutura de pastas do projeto")

    pdf.set_font("Courier", "", 8.5)
    pdf.set_text_color(*TEXT2)
    tree = [
        "interface_automacao/",
        "  app.py                  <- ponto de entrada, execute este",
        "  criar_atalho.py         <- gerador de atalho para desktop",
        "  requirements.txt        <- lista de dependencias pip",
        "  automations/",
        "    logs.py               <- modulo Analisador de Logs",
        "    scraper.py            <- modulo Scraper de Imagens",
        "    amaweb.py             <- modulo AMAWeb (Selenium)",
        "  config/",
        "    theme.py              <- cores e fontes da interface",
        "  ui/",
        "    app.py                <- classe principal da janela",
        "  assets/                 <- icone gerado por criar_atalho.py",
    ]
    for line in tree:
        pdf.set_x(14)
        pdf.cell(0, 5.5, line)
        pdf.ln(5.5)
    pdf.ln(4)

    pdf.divider()
    pdf.section_title(6, "Dependencias Python")
    pdf.body("Todas as dependencias estao listadas em requirements.txt e sao instaladas pelo Passo 5.")

    cols_dep = [("Pacote", 44), ("Versao minima", 32), ("Finalidade", 110)]
    pdf.table_header(cols_dep)
    deps = [
        ("requests",       "2.31.0",  "Requisicoes HTTP para scraper e amaweb"),
        ("beautifulsoup4", "4.12.0",  "Parse de HTML para extracao de imagens"),
        ("pandas",         "2.0.0",   "Geracao e leitura de planilhas Excel"),
        ("openpyxl",       "3.1.0",   "Leitura e escrita de arquivos .xlsx"),
        ("tqdm",           "4.66.0",  "Barras de progresso no terminal"),
        ("selenium",       "4.18.0",  "Automacao do Chrome (modulo AMAWeb)"),
        ("pillow",         "10.0.0",  "Geracao do icone .ico do atalho"),
        ("fpdf2",          "2.x",     "Geracao deste PDF (nao usado pela app)"),
        ("tkinter",        "nativo",  "Interface grafica - ja incluso no Python"),
    ]
    for i, row in enumerate(deps):
        pdf.table_row(cols_dep, row, shade=i % 2 == 0)

    # ================================================================== #
    #  PAG 5 - Arquivos de entrada/saida + Solucao de problemas           #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(7, "Arquivos de entrada e saida por modulo")

    pdf.subsection("7.1  Analisador de Logs")
    cols_io = [("Tipo", 26), ("Caminho padrao", 70), ("Descricao", 90)]
    pdf.table_header(cols_io)
    pdf.table_row(cols_io, ["Entrada", "logs_servidor/logs.xml", "Arquivo XML no formato log4j"], shade=True)
    pdf.table_row(cols_io, ["Saida",   "terminal da interface",  "Relatorio de erros exibido na tela"])
    pdf.table_row(cols_io, ["Saida",   "relatorio_logs.txt",     "Download opcional pelo botao na tela"], shade=True)
    pdf.ln(4)

    pdf.subsection("7.2  Scraper de Imagens")
    pdf.table_header(cols_io)
    pdf.table_row(cols_io, ["Entrada", "fontes/links.txt",                     "Uma URL por linha"], shade=True)
    pdf.table_row(cols_io, ["Saida",   "galeria_noticias/",                    "Imagens baixadas (.jpg)"])
    pdf.table_row(cols_io, ["Saida",   "galeria_noticias/registro_noticias.xlsx", "Planilha com relatorio da varredura"], shade=True)
    pdf.ln(4)

    pdf.subsection("7.3  AMAWeb")
    pdf.table_header(cols_io)
    pdf.table_row(cols_io, ["Entrada", "urls.txt",         "Um dominio ou URL por linha"], shade=True)
    pdf.table_row(cols_io, ["Saida",   "resultado.xlsx",   "Planilha com URL e nota de acessibilidade"])

    pdf.divider()
    pdf.section_title(8, "Solucao de problemas frequentes")

    problemas = [
        (
            "ModuleNotFoundError ao abrir o app",
            RED,
            "O ambiente virtual nao esta ativo ou as dependencias nao foram instaladas. "
            "Certifique-se de ativar com  .venv\\Scripts\\activate  e execute  pip install -r requirements.txt."
        ),
        (
            "ChromeDriver nao iniciado (modulo AMAWeb)",
            RED,
            "O Google Chrome nao esta instalado, ou o ChromeDriver esta desatualizado. "
            "Reinstale o Chrome e execute:  pip install --upgrade selenium"
        ),
        (
            "Tkinter nao encontrado",
            YELLOW,
            'Reinstale o Python marcando a opcao "tcl/tk and IDLE" durante a instalacao.'
        ),
        (
            "Erro de permissao ao criar .venv",
            YELLOW,
            "Execute o terminal como Administrador ou verifique se o Windows Defender "
            "nao esta bloqueando a criacao de executaveis na pasta."
        ),
        (
            "Fonte ou layout diferente do original",
            ACCENT,
            "A interface usa Segoe UI e Consolas, ambas nativas do Windows. "
            "Em Windows 10 mais antigo o layout pode diferir levemente, mas funciona normalmente."
        ),
    ]

    for titulo, cor, texto in problemas:
        pdf.info_box(titulo, texto, cor)

    # ================================================================== #
    #  PAG 6 - Resumo rapido (cheat-sheet)                                #
    # ================================================================== #
    pdf.add_page()
    pdf.page_bg()

    pdf.section_title(9, "Resumo rapido - Cheat Sheet")
    pdf.body("Cole os comandos abaixo em sequencia para instalar e executar do zero:")
    pdf.code_block([
        "# 1. Entre na pasta do projeto",
        "cd C:\\Projetos\\interface_automacao",
        "",
        "# 2. Crie o ambiente virtual",
        "python -m venv .venv",
        "",
        "# 3. Ative o ambiente",
        ".venv\\Scripts\\activate",
        "",
        "# 4. Instale as dependencias",
        "pip install -r requirements.txt",
        "",
        "# 5. Execute o app",
        "python app.py",
        "",
        "# (Opcional) Crie atalho na Area de Trabalho",
        "python criar_atalho.py",
    ])

    pdf.divider()
    pdf.section_title(10, "Informacoes do projeto")

    info = [
        ("Linguagem",          "Python 3.13"),
        ("Interface grafica",  "Tkinter (nativo do Python)"),
        ("Sistema operacional","Windows 10 / 11"),
        ("Versao do app",      "v1.0.0"),
        ("Autor",              "Pedro Henrique Santana Nascimento"),
        ("Gerado em",          datetime.now().strftime("%d/%m/%Y as %H:%M")),
    ]
    cols_info = [("Campo", 60), ("Valor", 126)]
    pdf.table_header(cols_info)
    for i, row in enumerate(info):
        pdf.table_row(cols_info, row, shade=i % 2 == 0)

    pdf.output(output_path)
    print(f"PDF gerado: {output_path}")


if __name__ == "__main__":
    build("AutoHub_Pro_Manual_Instalacao.pdf")
