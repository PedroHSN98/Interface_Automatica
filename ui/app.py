import os
import time
import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import threading
import queue
from datetime import datetime

import config.theme as theme
from config.theme import C, FONT_MAIN, FONT_MONO, FONT_SMALL, FONT_H2
from config import settings
from utils import historico as hist
from utils.notificacao import notificar
from automations.logs import run_logs, ELASTICSEARCHS, LIFERAYS
from automations.scraper import run_scraper
from automations.amaweb import run_amaweb
from automations.relatorio import run_relatorio

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s",
    encoding="utf-8",
)


class AutoHubApp:

    NAV_SECTIONS = [
        ("PRINCIPAL", [
            ("dashboard", "📊", "Dashboard",            "Visao geral"),
            ("logs",      "📋", "Analisador de Logs",   "XML -> Erros"),
            ("scraper",   "🗂️", "Scraper de Imagens",   "Extracao Web"),
            ("amaweb",    "🕵️", "AMAWeb",               "Acessibilidade"),
        ]),
        ("NOVAS FERRAMENTAS", [
            ("relatorio",  "📄", "Relatorio",           "Consolidado"),
        ]),
        ("SISTEMA", [
            ("historico", "📜", "Historico",            "Execucoes passadas"),
        ]),
    ]

    PAGE_META = {
        "dashboard":  ("📊  Dashboard",            "Visao geral do sistema"),
        "logs":       ("📋  Analisador de Logs",    "XML -> Relatorio de Erros"),
        "scraper":    ("🗂️  Scraper de Imagens",    "Extracao de Imagens Web"),
        "amaweb":     ("🕵️  AMAWeb",               "Avaliador de Acessibilidade"),
        "relatorio":  ("📄  Relatorio Consolidado", "Exporta todos os dados"),
        "historico":  ("📜  Historico",             "Execucoes anteriores"),
    }

    # ------------------------------------------------------------------ #
    #  INIT                                                                #
    # ------------------------------------------------------------------ #
    def __init__(self):
        cfg = settings.load()
        theme.set_theme(cfg.get("theme", "dark"))

        self.root = tk.Tk()
        self.root.title("AutoHub Pro")
        self.root.geometry("1220x760")
        self.root.minsize(1000, 640)
        self.root.configure(bg=C["bg"])

        self.current_page    = "dashboard"
        self.running         = False
        self._running_module = None
        self.stop_ev         = threading.Event()
        self.out_q           = queue.Queue()
        self._logs_result    = None
        self._ama_result_data = None
        self._scraper_folder = None
        self.logs_datas      = []

        # widget dicts (populated in _build_ui)
        self._run_btns      = {}
        self._stop_btns     = {}
        self._progress_vars = {}
        self._terms         = {}
        self._nav_btns      = {}

        # StringVars / state vars
        self._date_entry_var  = tk.StringVar()
        self._date_err_text   = tk.StringVar()
        self.scraper_links    = tk.StringVar(value=cfg.get("scraper_links",  "fontes/links.txt"))
        self.scraper_output   = tk.StringVar(value=cfg.get("scraper_output", "galeria_noticias"))
        self.scraper_agendado = tk.BooleanVar(value=cfg.get("scraper_agendado", False))
        self.scraper_horario  = tk.StringVar(value=cfg.get("scraper_horario",  "08:00"))
        self.ama_urls         = tk.StringVar(value=cfg.get("ama_urls",   "urls.txt"))
        self.ama_result       = tk.StringVar(value=cfg.get("ama_result", "resultado.xlsx"))
        self.ama_threshold    = tk.DoubleVar(value=cfg.get("ama_threshold", 5.0))
        self.notif_var        = tk.BooleanVar(value=cfg.get("notificacoes", True))
        self.relatorio_output = tk.StringVar(value="relatorio_consolidado.xlsx")

        self._elastic_vars = {
            n: tk.BooleanVar(value=n in cfg.get("logs_servidores_elastic", list(ELASTICSEARCHS)))
            for n in ELASTICSEARCHS
        }
        self._liferay_vars = {
            n: tk.BooleanVar(value=n in cfg.get("logs_servidores_liferay", list(LIFERAYS)))
            for n in LIFERAYS
        }

        self._build_ui()
        self._poll_output()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._sched_stop = threading.Event()
        threading.Thread(target=self._scheduler_loop, daemon=True).start()

    # ------------------------------------------------------------------ #
    #  BUILD UI                                                            #
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self.root.configure(bg=C["bg"])
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()
        self._build_statusbar()
        self._select_page(self.current_page)

    # ── Sidebar ──────────────────────────────────────────────────────── #
    def _build_sidebar(self):
        sb = tk.Frame(self.root, bg=C["sidebar"], width=220)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        lf = tk.Frame(sb, bg=C["sidebar"], pady=18)
        lf.pack(fill="x")
        tk.Label(lf, text="A", font=("Segoe UI", 22, "bold"),
                 bg=C["accent"], fg="#ffffff", width=3, pady=4).pack()
        tk.Label(lf, text="AutoHub Pro", font=("Segoe UI", 11, "bold"),
                 bg=C["sidebar"], fg=C["text"]).pack(pady=(6, 0))
        tk.Label(lf, text="Central de Automacoes", font=FONT_SMALL,
                 bg=C["sidebar"], fg=C["text3"]).pack()

        tk.Frame(sb, bg=C["bg4"], height=1).pack(fill="x", padx=12, pady=6)

        for section_label, items in self.NAV_SECTIONS:
            tk.Label(sb, text=section_label, font=("Segoe UI", 7, "bold"),
                     bg=C["sidebar"], fg=C["text3"]).pack(anchor="w", padx=16, pady=(8, 2))
            for key, icon, label, desc in items:
                self._nav_btns[key] = self._make_nav_btn(sb, key, icon, label, desc)

        # Tema toggle + notificações
        tk.Frame(sb, bg=C["bg4"], height=1).pack(fill="x", padx=12, pady=8)
        bottom = tk.Frame(sb, bg=C["sidebar"])
        bottom.pack(fill="x", padx=12, pady=(0, 6))
        tk.Button(bottom, text="☀ / 🌙  Tema", font=FONT_SMALL,
                  bg=C["bg3"], fg=C["text2"], relief="flat", cursor="hand2",
                  command=self._toggle_theme, padx=8, pady=4).pack(fill="x", pady=2)
        tk.Checkbutton(bottom, text="Notificacoes", font=FONT_SMALL,
                       variable=self.notif_var,
                       bg=C["sidebar"], fg=C["text2"],
                       selectcolor=C["bg3"], activebackground=C["sidebar"],
                       relief="flat").pack(anchor="w", pady=2)

        tk.Label(sb, text="v1.4  •  2025", font=FONT_SMALL,
                 bg=C["sidebar"], fg=C["text3"]).pack(side="bottom", pady=8)

    def _make_nav_btn(self, parent, key, icon, label, desc):
        outer = tk.Frame(parent, bg=C["sidebar"], cursor="hand2")
        outer.pack(fill="x", padx=6, pady=1)
        inner = tk.Frame(outer, bg=C["sidebar"], padx=10, pady=7)
        inner.pack(fill="x")
        ic = tk.Label(inner, text=icon, font=("Segoe UI", 11),
                      bg=C["sidebar"], fg=C["text2"])
        ic.pack(side="left")
        tf = tk.Frame(inner, bg=C["sidebar"])
        tf.pack(side="left", padx=(8, 0))
        nl = tk.Label(tf, text=label, font=FONT_H2,
                      bg=C["sidebar"], fg=C["text2"], anchor="w")
        nl.pack(anchor="w")
        dl = tk.Label(tf, text=desc, font=FONT_SMALL,
                      bg=C["sidebar"], fg=C["text3"], anchor="w")
        dl.pack(anchor="w")

        def click(_=None):
            self._select_page(key)
        for w in [outer, inner, ic, tf, nl, dl]:
            w.bind("<Button-1>", click)

        outer._inner = inner
        outer._ic    = ic
        outer._nl    = nl
        outer._dl    = dl
        outer._tf    = tf
        return outer

    def _select_page(self, key):
        for k, btn in self._nav_btns.items():
            active = k == key
            bg  = C["bg3"]    if active else C["sidebar"]
            fgi = C["accent"] if active else C["text2"]
            fgn = C["text"]   if active else C["text2"]
            btn.configure(bg=bg)
            btn._inner.configure(bg=bg)
            btn._tf.configure(bg=bg)
            btn._ic.configure(bg=bg, fg=fgi)
            btn._nl.configure(bg=bg, fg=fgn)
            btn._dl.configure(bg=bg)
        self.current_page = key
        title, badge = self.PAGE_META[key]
        self._hdr_title.configure(text=title)
        self._hdr_badge.configure(text=f"  {badge}  ")
        for k, pg in self._pages.items():
            pg.grid() if k == key else pg.grid_remove()
        if key == "dashboard":
            self._refresh_dashboard()
        elif key == "historico":
            self._load_historico_page()

    # ── Main area ────────────────────────────────────────────────────── #
    def _build_main(self):
        main = tk.Frame(self.root, bg=C["bg"])
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        hdr = tk.Frame(main, bg=C["bg2"], height=56)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)

        self._hdr_title = tk.Label(hdr, text="", font=("Segoe UI", 13, "bold"),
                                   bg=C["bg2"], fg=C["text"])
        self._hdr_title.pack(side="left", padx=20, pady=12)
        self._hdr_badge = tk.Label(hdr, text="", font=FONT_SMALL,
                                   bg=C["bg3"], fg=C["text2"], pady=4)
        self._hdr_badge.pack(side="left", pady=18)

        pc = tk.Frame(main, bg=C["bg"])
        pc.grid(row=1, column=0, sticky="nsew")
        pc.columnconfigure(0, weight=1)
        pc.rowconfigure(0, weight=1)

        self._pages = {
            "dashboard":  self._page_dashboard(pc),
            "logs":       self._page_logs(pc),
            "scraper":    self._page_scraper(pc),
            "amaweb":     self._page_amaweb(pc),
            "relatorio":  self._page_relatorio(pc),
            "historico":  self._page_historico(pc),
        }

    # ── Status bar ───────────────────────────────────────────────────── #
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C["bg2"], height=26)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        self._status_dot = tk.Label(bar, text="●", font=("Segoe UI", 10),
                                    bg=C["bg2"], fg=C["green"])
        self._status_dot.pack(side="left", padx=(12, 4))
        self._status_lbl = tk.Label(bar, text="Pronto", font=FONT_SMALL,
                                    bg=C["bg2"], fg=C["text2"])
        self._status_lbl.pack(side="left")
        self._clock_lbl = tk.Label(bar, text="", font=FONT_SMALL,
                                   bg=C["bg2"], fg=C["text3"])
        self._clock_lbl.pack(side="right", padx=14)

        if hasattr(self, "_clock_after_id"):
            self.root.after_cancel(self._clock_after_id)
        self._tick_clock()

    def _tick_clock(self):
        self._clock_lbl.configure(text=datetime.now().strftime("%d/%m/%Y   %H:%M:%S"))
        self._clock_after_id = self.root.after(1000, self._tick_clock)

    def _set_status(self, text, dot_color=None):
        self._status_lbl.configure(text=text)
        if dot_color:
            self._status_dot.configure(fg=dot_color)

    # ------------------------------------------------------------------ #
    #  WIDGET HELPERS                                                      #
    # ------------------------------------------------------------------ #
    def _make_page(self, parent):
        f = tk.Frame(parent, bg=C["bg"])
        f.grid(row=0, column=0, sticky="nsew")
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)
        return f

    def _config_card(self, parent):
        card = tk.Frame(parent, bg=C["bg2"], padx=20, pady=12)
        card.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        card.columnconfigure(1, weight=1)
        tk.Label(card, text="CONFIGURACOES", font=("Segoe UI", 7, "bold"),
                 bg=C["bg2"], fg=C["text3"]).grid(
                     row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        return card

    def _file_row(self, card, row, label, var, mode="file"):
        tk.Label(card, text=label, font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=18, anchor="e").grid(
                     row=row, column=0, sticky="e", padx=(0, 10), pady=4)
        tk.Entry(card, textvariable=var, font=FONT_MONO,
                 bg=C["bg4"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=0).grid(
                     row=row, column=1, sticky="ew", ipady=6, padx=(0, 8))

        def browse():
            if mode == "file":
                p = filedialog.askopenfilename()
            elif mode == "save":
                p = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel", "*.xlsx")])
            else:
                p = filedialog.askdirectory()
            if p:
                var.set(p)

        tk.Button(card, text="Browse", font=FONT_SMALL, bg=C["bg4"],
                  fg=C["text2"], relief="flat", cursor="hand2",
                  command=browse, padx=8, pady=3).grid(row=row, column=2, pady=4)

    def _err_label(self, card, row):
        lbl = tk.Label(card, textvariable=self._date_err_text,
                       font=FONT_SMALL, bg=C["bg2"], fg=C["red"])
        lbl.grid(row=row, column=1, columnspan=3, sticky="w")
        return lbl

    def _action_row(self, card, row, run_cmd, module_key):
        frm = tk.Frame(card, bg=C["bg2"])
        frm.grid(row=row, column=0, columnspan=4, sticky="w", pady=(10, 0))

        run_btn = tk.Button(
            frm, text="▶  Executar",
            font=("Segoe UI", 10, "bold"),
            bg=C["accent"], fg="#ffffff",
            activebackground="#388bfd", activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=20, pady=8,
            command=run_cmd,
        )
        run_btn.pack(side="left", padx=(0, 8))

        stop_btn = tk.Button(
            frm, text="■  Parar",
            font=("Segoe UI", 10),
            bg=C["bg4"], fg=C["text2"],
            activebackground=C["red"], activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=16, pady=8,
            command=self._stop,
        )
        stop_btn.pack(side="left")

        self._run_btns[module_key]  = run_btn
        self._stop_btns[module_key] = stop_btn

    def _progress_row(self, card, row, module_key):
        pvar = tk.DoubleVar(value=0.0)
        self._progress_vars[module_key] = pvar
        style_name = f"{module_key}.Horizontal.TProgressbar"
        style = ttk.Style()
        style.theme_use("default")
        style.configure(style_name,
                        troughcolor=C["bg4"],
                        background=C["accent"],
                        thickness=6)
        pb = ttk.Progressbar(card, variable=pvar, maximum=1.0,
                              style=style_name, length=400)
        pb.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(6, 0))

    def _terminal_card(self, parent, key):
        card = tk.Frame(parent, bg=C["bg2"], padx=12, pady=10)
        card.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        hdr = tk.Frame(card, bg=C["bg2"])
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        tk.Label(hdr, text="▌ TERMINAL DE SAIDA", font=("Segoe UI", 8, "bold"),
                 bg=C["bg2"], fg=C["text3"]).pack(side="left")
        tk.Button(hdr, text="Limpar", font=FONT_SMALL,
                  bg=C["bg4"], fg=C["text2"], relief="flat", cursor="hand2",
                  padx=8, pady=2,
                  command=lambda: self._clear(term)).pack(side="right")

        term = tk.Text(
            card, font=FONT_MONO,
            bg=C["term_bg"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=0,
            wrap="word", state="disabled", cursor="arrow",
            selectbackground=C["bg4"],
        )
        sb = tk.Scrollbar(card, command=term.yview, bg=C["bg3"],
                          troughcolor=C["bg2"], width=10)
        term.configure(yscrollcommand=sb.set)

        for tag, fg in [
            ("normal",   "#e6edf3"), ("info",    "#58a6ff"),
            ("success",  "#3fb950"), ("warning", "#d29922"),
            ("error",    "#f85149"), ("progress","#e3702b"),
            ("dim",      "#484f58"),
        ]:
            term.tag_configure(tag, foreground=fg)
        term.tag_configure("title", foreground="#e6edf3",
                           font=("Consolas", 9, "bold"))

        term.grid(row=1, column=0, sticky="nsew")
        sb.grid(row=1, column=1, sticky="ns")

        self._terms[key] = term
        return card

    # ------------------------------------------------------------------ #
    #  PAGES                                                               #
    # ------------------------------------------------------------------ #

    # ── Dashboard ────────────────────────────────────────────────────── #
    def _page_dashboard(self, parent):
        pg = self._make_page(parent)
        pg.rowconfigure(1, weight=1)

        cards_row = tk.Frame(pg, bg=C["bg"])
        cards_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        for i in range(4):
            cards_row.columnconfigure(i, weight=1)

        modules = [
            ("logs",    "📋", "Logs"),
            ("scraper", "🗂️", "Scraper"),
            ("amaweb",  "🕵️", "AMAWeb"),
        ]
        self._dash_cards = {}
        for i, (key, icon, label) in enumerate(modules):
            card = tk.Frame(cards_row, bg=C["bg2"], padx=16, pady=14)
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 10))
            tk.Label(card, text=f"{icon} {label}", font=("Segoe UI", 10, "bold"),
                     bg=C["bg2"], fg=C["text"]).pack(anchor="w")
            lbl_status = tk.Label(card, text="—", font=FONT_SMALL,
                                  bg=C["bg2"], fg=C["text3"])
            lbl_status.pack(anchor="w", pady=(4, 0))
            lbl_det = tk.Label(card, text="", font=FONT_SMALL,
                               bg=C["bg2"], fg=C["text2"], wraplength=200, justify="left")
            lbl_det.pack(anchor="w", pady=(2, 0))
            self._dash_cards[key] = (lbl_status, lbl_det)

        # Botao de atualizar dashboard
        tk.Button(cards_row, text="↻  Atualizar", font=FONT_SMALL,
                  bg=C["bg3"], fg=C["text2"], relief="flat", cursor="hand2",
                  padx=10, pady=6, command=self._refresh_dashboard).grid(
                      row=0, column=3, sticky="nsew", padx=(0, 0))

        # Lista de historico recente
        hist_frame = tk.Frame(pg, bg=C["bg2"], padx=16, pady=12)
        hist_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        hist_frame.columnconfigure(0, weight=1)
        hist_frame.rowconfigure(1, weight=1)

        tk.Label(hist_frame, text="HISTORICO RECENTE", font=("Segoe UI", 7, "bold"),
                 bg=C["bg2"], fg=C["text3"]).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self._dash_hist_text = tk.Text(
            hist_frame, font=FONT_MONO, bg=C["term_bg"], fg=C["text2"],
            relief="flat", bd=0, state="disabled", cursor="arrow",
            selectbackground=C["bg4"], height=14,
        )
        hs = tk.Scrollbar(hist_frame, command=self._dash_hist_text.yview,
                          bg=C["bg3"], troughcolor=C["bg2"], width=10)
        self._dash_hist_text.configure(yscrollcommand=hs.set)
        self._dash_hist_text.grid(row=1, column=0, sticky="nsew")
        hs.grid(row=1, column=1, sticky="ns")

        for tag, fg in [("sucesso", "#3fb950"), ("erro", "#f85149"),
                        ("aviso", "#d29922"), ("dim", "#484f58")]:
            self._dash_hist_text.tag_configure(tag, foreground=fg)

        return pg

    def _refresh_dashboard(self):
        if not hasattr(self, "_dash_cards"):
            return
        for key, (lbl_s, lbl_d) in self._dash_cards.items():
            entry = hist.ultima(key)
            if entry:
                status = entry["status"]
                color = C["green"] if status == "sucesso" else C["red"]
                lbl_s.configure(text=f"● {status.upper()}  {entry['data']}", fg=color)
                lbl_d.configure(text=entry.get("detalhes", ""))
            else:
                lbl_s.configure(text="Nenhuma execucao registrada", fg=C["text3"])
                lbl_d.configure(text="")

        entries = hist.listar(30)
        w = self._dash_hist_text
        w.configure(state="normal")
        w.delete("1.0", "end")
        for e in entries:
            tag = "sucesso" if e["status"] == "sucesso" else "erro"
            w.insert("end", f"  {e['data']}  ", "dim")
            w.insert("end", f"[{e['modulo'].upper():<10}]  ", "dim")
            w.insert("end", f"{e['status']:<10}  ", tag)
            w.insert("end", f"{e.get('detalhes','')}\n", "dim")
        if not entries:
            w.insert("end", "  Nenhum registro ainda.\n", "dim")
        w.configure(state="disabled")

    # ── Logs ─────────────────────────────────────────────────────────── #
    def _page_logs(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)

        # Data entry
        tk.Label(card, text="Data (dd/mm/aaaa)", font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=18, anchor="e").grid(
                     row=1, column=0, sticky="e", padx=(0, 10), pady=4)
        self._date_entry = tk.Entry(
            card, textvariable=self._date_entry_var, font=FONT_MONO,
            bg=C["bg4"], fg=C["text"], insertbackground=C["text"],
            relief="flat", bd=0, width=14)
        self._date_entry.grid(row=1, column=1, sticky="w", ipady=6, padx=(0, 8))
        self._date_entry.bind("<Return>", lambda _: self._add_date())

        btn_frm = tk.Frame(card, bg=C["bg2"])
        btn_frm.grid(row=1, column=2, columnspan=2, sticky="w")
        tk.Button(btn_frm, text="+ Adicionar", font=FONT_SMALL,
                  bg=C["accent"], fg="#ffffff", relief="flat", cursor="hand2",
                  command=self._add_date, padx=8, pady=3).pack(side="left", padx=(0, 6))
        tk.Button(btn_frm, text="✕ Remover", font=FONT_SMALL,
                  bg=C["bg4"], fg=C["red"], relief="flat", cursor="hand2",
                  command=self._remove_date, padx=8, pady=3).pack(side="left")

        self._date_err_lbl = tk.Label(card, text="", font=FONT_SMALL,
                                      bg=C["bg2"], fg=C["red"])
        self._date_err_lbl.grid(row=2, column=1, columnspan=3, sticky="w")

        lb_frm = tk.Frame(card, bg=C["bg2"])
        lb_frm.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(2, 4))
        self._dates_lb = tk.Listbox(
            lb_frm, font=FONT_MONO, bg=C["bg4"], fg=C["text"],
            selectbackground=C["accent"], selectforeground="#ffffff",
            relief="flat", height=3, bd=0)
        self._dates_lb.pack(fill="x")

        # Filtro de servidores
        tk.Label(card, text="Elasticsearch", font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=18, anchor="e").grid(
                     row=4, column=0, sticky="e", padx=(0, 10), pady=4)
        ef = tk.Frame(card, bg=C["bg2"])
        ef.grid(row=4, column=1, columnspan=3, sticky="w")
        for n, var in self._elastic_vars.items():
            tk.Checkbutton(ef, text=n, variable=var,
                           font=FONT_SMALL, bg=C["bg2"], fg=C["text2"],
                           selectcolor=C["bg4"], activebackground=C["bg2"],
                           relief="flat").pack(side="left", padx=(0, 10))

        tk.Label(card, text="Liferay", font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=18, anchor="e").grid(
                     row=5, column=0, sticky="e", padx=(0, 10), pady=4)
        lf = tk.Frame(card, bg=C["bg2"])
        lf.grid(row=5, column=1, columnspan=3, sticky="w")
        for n, var in self._liferay_vars.items():
            tk.Checkbutton(lf, text=n, variable=var,
                           font=FONT_SMALL, bg=C["bg2"], fg=C["text2"],
                           selectcolor=C["bg4"], activebackground=C["bg2"],
                           relief="flat").pack(side="left", padx=(0, 10))

        self._action_row(card, 6, self._exec_logs, "logs")
        self._progress_row(card, 7, "logs")

        # Botoes de download
        dl_frm = tk.Frame(card, bg=C["bg2"])
        dl_frm.grid(row=8, column=0, columnspan=4, sticky="w", pady=(6, 0))

        self._logs_dl_txt = tk.Button(
            dl_frm, text="⬇  Baixar .txt",
            font=("Segoe UI", 9), bg=C["bg4"], fg=C["text3"],
            activebackground=C["green"], activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=14, pady=7,
            state="disabled", command=self._download_logs_txt,
        )
        self._logs_dl_txt.pack(side="left", padx=(0, 8))

        self._logs_dl_xlsx = tk.Button(
            dl_frm, text="⬇  Baixar .xlsx",
            font=("Segoe UI", 9), bg=C["bg4"], fg=C["text3"],
            activebackground=C["green"], activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=14, pady=7,
            state="disabled", command=self._download_logs_xlsx,
        )
        self._logs_dl_xlsx.pack(side="left")

        self._terminal_card(pg, "logs")
        return pg

    def _add_date(self):
        entrada = self._date_entry_var.get().strip()
        try:
            d = datetime.strptime(entrada, "%d/%m/%Y")
        except ValueError:
            self._date_err_lbl.configure(text="Data invalida. Use dd/mm/aaaa.")
            return
        if any(e == d for e in self.logs_datas):
            self._date_err_lbl.configure(text="Data ja adicionada.")
            return
        self.logs_datas.append(d)
        self._dates_lb.insert("end", d.strftime("%d/%m/%Y"))
        self._date_entry_var.set("")
        self._date_err_lbl.configure(text="")

    def _remove_date(self):
        sel = self._dates_lb.curselection()
        if not sel:
            return
        idx = sel[0]
        self._dates_lb.delete(idx)
        self.logs_datas.pop(idx)

    # ── Scraper ──────────────────────────────────────────────────────── #
    def _page_scraper(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)
        self._file_row(card, 1, "Links (links.txt)", self.scraper_links,  "file")
        self._file_row(card, 2, "Pasta de saida",   self.scraper_output, "dir")

        # Agendamento
        tk.Label(card, text="Agendamento", font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=18, anchor="e").grid(
                     row=3, column=0, sticky="e", padx=(0, 10), pady=4)
        sched_frm = tk.Frame(card, bg=C["bg2"])
        sched_frm.grid(row=3, column=1, columnspan=3, sticky="w")
        tk.Checkbutton(sched_frm, text="Agendar execucao automatica",
                       variable=self.scraper_agendado,
                       font=FONT_SMALL, bg=C["bg2"], fg=C["text2"],
                       selectcolor=C["bg4"], activebackground=C["bg2"],
                       relief="flat").pack(side="left", padx=(0, 12))
        tk.Label(sched_frm, text="Horario (HH:MM):", font=FONT_SMALL,
                 bg=C["bg2"], fg=C["text3"]).pack(side="left")
        tk.Entry(sched_frm, textvariable=self.scraper_horario, font=FONT_MONO,
                 bg=C["bg4"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=0, width=7).pack(side="left", padx=(4, 0), ipady=4)

        self._action_row(card, 4, self._exec_scraper, "scraper")
        self._progress_row(card, 5, "scraper")

        # Botao de preview de imagens
        preview_frm = tk.Frame(card, bg=C["bg2"])
        preview_frm.grid(row=6, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self._scraper_preview_btn = tk.Button(
            preview_frm, text="🖼  Ver imagens baixadas",
            font=("Segoe UI", 9), bg=C["bg4"], fg=C["text3"],
            activebackground=C["accent"], activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=14, pady=7,
            state="disabled", command=self._show_image_preview,
        )
        self._scraper_preview_btn.pack(side="left")

        self._terminal_card(pg, "scraper")
        return pg

    # ── AMAWeb ───────────────────────────────────────────────────────── #
    def _page_amaweb(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)
        self._file_row(card, 1, "URLs (urls.txt)",   self.ama_urls,   "file")
        self._file_row(card, 2, "Resultado (.xlsx)", self.ama_result, "save")

        tk.Label(card, text="Alerta (nota min.)", font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=18, anchor="e").grid(
                     row=3, column=0, sticky="e", padx=(0, 10), pady=4)
        thr_frm = tk.Frame(card, bg=C["bg2"])
        thr_frm.grid(row=3, column=1, columnspan=3, sticky="w")
        tk.Spinbox(thr_frm, from_=0, to=10, increment=0.5,
                   textvariable=self.ama_threshold, width=6,
                   font=FONT_MONO, bg=C["bg4"], fg=C["text"],
                   relief="flat", bd=0).pack(side="left")
        tk.Label(thr_frm, text="  (0 = desabilitado)",
                 font=FONT_SMALL, bg=C["bg2"], fg=C["text3"]).pack(side="left")

        self._action_row(card, 4, self._exec_amaweb, "amaweb")
        self._progress_row(card, 5, "amaweb")

        dl_frm = tk.Frame(card, bg=C["bg2"])
        dl_frm.grid(row=6, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self._ama_dl_txt = tk.Button(
            dl_frm, text="⬇   Baixar resultado (.txt)",
            font=("Segoe UI", 10), bg=C["bg4"], fg=C["text3"],
            activebackground=C["green"], activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=18, pady=9,
            state="disabled", command=self._download_ama_txt,
        )
        self._ama_dl_txt.pack(side="left")

        self._terminal_card(pg, "amaweb")
        return pg

    # ── Relatorio ────────────────────────────────────────────────────── #
    def _page_relatorio(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)
        self._file_row(card, 1, "Salvar em (.xlsx)", self.relatorio_output, "save")
        tk.Label(card, font=FONT_SMALL, bg=C["bg2"], fg=C["text3"],
                 text="Consolida: Historico de execucoes + Scraper + AMAWeb em uma planilha").grid(
                     row=2, column=0, columnspan=4, sticky="w", padx=(0, 0), pady=2)
        self._action_row(card, 3, self._exec_relatorio, "relatorio")
        self._progress_row(card, 4, "relatorio")
        self._terminal_card(pg, "relatorio")
        return pg

    # ── Historico ────────────────────────────────────────────────────── #
    def _page_historico(self, parent):
        pg = self._make_page(parent)
        pg.rowconfigure(1, weight=1)

        ctrl = tk.Frame(pg, bg=C["bg2"], padx=16, pady=8)
        ctrl.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        tk.Label(ctrl, text="HISTORICO DE EXECUCOES", font=("Segoe UI", 7, "bold"),
                 bg=C["bg2"], fg=C["text3"]).pack(side="left")
        tk.Button(ctrl, text="↻ Atualizar", font=FONT_SMALL,
                  bg=C["bg3"], fg=C["text2"], relief="flat", cursor="hand2",
                  padx=8, pady=3, command=self._load_historico_page).pack(side="right")

        tbl_frame = tk.Frame(pg, bg=C["bg2"])
        tbl_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        tbl_frame.columnconfigure(0, weight=1)
        tbl_frame.rowconfigure(0, weight=1)

        self._hist_text = tk.Text(
            tbl_frame, font=FONT_MONO, bg=C["term_bg"], fg=C["text2"],
            relief="flat", bd=0, state="disabled", cursor="arrow",
            selectbackground=C["bg4"],
        )
        hs = tk.Scrollbar(tbl_frame, command=self._hist_text.yview,
                          bg=C["bg3"], troughcolor=C["bg2"], width=10)
        self._hist_text.configure(yscrollcommand=hs.set)
        self._hist_text.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        hs.grid(row=0, column=1, sticky="ns")

        for tag, fg in [("sucesso", "#3fb950"), ("erro", "#f85149"),
                        ("dim", "#484f58"), ("title", "#e6edf3")]:
            self._hist_text.tag_configure(tag, foreground=fg)
        self._hist_text.tag_configure("title", font=("Consolas", 9, "bold"))

        return pg

    def _load_historico_page(self):
        if not hasattr(self, "_hist_text"):
            return
        entries = hist.listar(100)
        w = self._hist_text
        w.configure(state="normal")
        w.delete("1.0", "end")
        w.insert("end", f"  {'DATA':<22} {'MODULO':<14} {'STATUS':<12} DETALHES\n", "title")
        w.insert("end", "  " + "─" * 78 + "\n", "dim")
        for e in entries:
            tag = "sucesso" if e["status"] == "sucesso" else "erro"
            w.insert("end", f"  {e['data']:<22} {e['modulo'].upper():<14} ", "dim")
            w.insert("end", f"{e['status']:<12} ", tag)
            w.insert("end", f"{e.get('detalhes','')}\n", "dim")
        if not entries:
            w.insert("end", "\n  Nenhum registro encontrado.\n", "dim")
        w.configure(state="disabled")

    # ------------------------------------------------------------------ #
    #  THEME TOGGLE                                                        #
    # ------------------------------------------------------------------ #
    def _toggle_theme(self):
        current = settings.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        settings.set_key("theme", new_theme)
        theme.set_theme(new_theme)
        # Reconstroi toda a UI com o novo tema
        for w in self.root.winfo_children():
            w.destroy()
        self._nav_btns = {}
        self._run_btns = {}
        self._stop_btns = {}
        self._progress_vars = {}
        self._terms = {}
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  TERMINAL HELPERS                                                    #
    # ------------------------------------------------------------------ #
    def _active_term(self):
        return self._terms.get(self._running_module or self.current_page)

    def _append(self, widget, text, tag="normal"):
        if widget is None:
            return
        widget.configure(state="normal")
        widget.insert("end", text, tag)
        widget.see("end")
        widget.configure(state="disabled")

    def _clear(self, widget):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.configure(state="disabled")

    def _term_header(self, widget):
        ts = datetime.now().strftime("%H:%M:%S")
        self._append(widget, f"\n{'─' * 60}\n", "dim")
        self._append(widget, f"  Iniciado em {ts}\n", "dim")
        self._append(widget, f"{'─' * 60}\n\n", "dim")

    def _term_footer(self, widget):
        ts = datetime.now().strftime("%H:%M:%S")
        self._append(widget, f"\n{'─' * 60}\n", "dim")
        self._append(widget, f"  Finalizado em {ts}\n", "dim")
        self._append(widget, f"{'─' * 60}\n", "dim")

    # ------------------------------------------------------------------ #
    #  EXECUTORS                                                           #
    # ------------------------------------------------------------------ #
    def _start(self, target, module_key, *args):
        if self.running:
            return
        self.running = True
        self._running_module = module_key
        self.stop_ev.clear()
        term = self._terms.get(module_key)
        if term:
            self._clear(term)
            self._term_header(term)
        if module_key in self._progress_vars:
            self._progress_vars[module_key].set(0.0)
        self._set_status(f"Executando {module_key}...", C["yellow"])
        threading.Thread(target=target,
                         args=(*args, self.out_q, self.stop_ev),
                         daemon=True).start()

    def _exec_logs(self):
        if not self.logs_datas:
            self._date_err_lbl.configure(text="Adicione ao menos uma data.")
            return
        if not any(v.get() for v in self._elastic_vars.values()) and \
           not any(v.get() for v in self._liferay_vars.values()):
            self._date_err_lbl.configure(text="Selecione ao menos um servidor.")
            return
        self._date_err_lbl.configure(text="")
        self._logs_result = None
        self._logs_dl_txt.configure(state="disabled", fg=C["text3"])
        self._logs_dl_xlsx.configure(state="disabled", fg=C["text3"])
        elastic_sel = [n for n, v in self._elastic_vars.items() if v.get()]
        liferay_sel = [n for n, v in self._liferay_vars.items() if v.get()]
        self._start(
            lambda *a: run_logs(a[0], a[1], a[2],
                                servidores_elastic=elastic_sel,
                                servidores_liferay=liferay_sel),
            "logs", list(self.logs_datas),
        )

    def _exec_scraper(self):
        if not os.path.exists(self.scraper_links.get()):
            self._append(self._terms.get("scraper"),
                         f"  [ERRO] Arquivo nao encontrado: {self.scraper_links.get()}\n", "error")
            return
        self._scraper_folder = None
        self._scraper_preview_btn.configure(state="disabled", fg=C["text3"])
        self._start(run_scraper, "scraper",
                    self.scraper_links.get(), self.scraper_output.get())

    def _exec_amaweb(self):
        if not os.path.exists(self.ama_urls.get()):
            self._append(self._terms.get("amaweb"),
                         f"  [ERRO] Arquivo nao encontrado: {self.ama_urls.get()}\n", "error")
            return
        self._ama_result_data = None
        self._ama_dl_txt.configure(state="disabled", fg=C["text3"])
        self._start(
            lambda *a: run_amaweb(a[0], a[1], a[2], a[3],
                                  threshold=self.ama_threshold.get()),
            "amaweb", self.ama_urls.get(), self.ama_result.get(),
        )

    def _exec_relatorio(self):
        self._start(run_relatorio, "relatorio", self.relatorio_output.get())

    def _stop(self):
        if self.running:
            self.stop_ev.set()
            self._set_status("Parando...", C["orange"])

    # ------------------------------------------------------------------ #
    #  DOWNLOADS — LOGS                                                    #
    # ------------------------------------------------------------------ #
    def _download_logs_txt(self):
        if not self._logs_result:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile="relatorio_logs.txt",
        )
        if not path:
            return
        data = self._logs_result
        ts   = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        lines = ["AutoHub Pro - Relatorio de Logs SSH",
                 f"Gerado em: {ts}", "=" * 80, ""]
        for data_iso, info in data["por_data"].items():
            dt = datetime.strptime(data_iso, "%Y-%m-%d")
            lines += [f"Data: {dt.strftime('%d/%m/%Y')}", "-" * 40]
            for i, (erro, qty) in enumerate(info["contagem"].items(), 1):
                lines.append(f"  {i:02d}. {erro} = {qty}")
            lines.append("")
            for nome, tam in info["tamanhos_logs"].items():
                if tam is None:
                    lines.append(f"  LOG {nome}: arquivo nao encontrado")
                else:
                    lines.append(f"  LOG {nome}: {tam / 1024 / 1024:.1f} MB")
            lines.append("")
        lines += ["", "-" * 80, "Tamanho em bytes - Elasticsearch:", ""]
        for nome, valor in data["elastic_bytes"].items():
            lines.append(f"  {nome}: {valor if valor is not None else 'erro'}")
        lines.append("")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self._set_status(f"Salvo: {os.path.basename(path)}", C["green"])
        self._append(self._terms.get("logs"),
                     f"\n  [OK] Relatorio TXT salvo: {path}\n", "success")

    def _download_logs_xlsx(self):
        if not self._logs_result:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="relatorio_logs.xlsx",
        )
        if not path:
            return
        try:
            from automations.logs import _exportar_excel
            _exportar_excel(self._logs_result, path)
            self._set_status(f"Salvo: {os.path.basename(path)}", C["green"])
            self._append(self._terms.get("logs"),
                         f"\n  [OK] Relatorio Excel salvo: {path}\n", "success")
        except Exception as e:
            logging.exception("Erro ao exportar Excel de logs")
            self._append(self._terms.get("logs"),
                         f"\n  [ERRO] {e}\n", "error")

    # ------------------------------------------------------------------ #
    #  DOWNLOADS — AMAWEB                                                  #
    # ------------------------------------------------------------------ #
    def _download_ama_txt(self):
        if not self._ama_result_data:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile="resultado_amaweb.txt",
        )
        if not path:
            return
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linhas = [
            "AutoHub Pro - Resultado AMAWeb",
            f"Gerado em: {ts}",
            "=" * 70,
            "",
            f"{'URL':<55}  {'NOTA':>6}",
            "-" * 70,
        ]
        for site, nota in self._ama_result_data:
            linhas.append(f"{site:<55}  {nota:>6}")
        linhas += ["", "-" * 70, f"Total de sites: {len(self._ama_result_data)}", ""]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas))
        self._set_status(f"Salvo: {os.path.basename(path)}", C["green"])
        self._append(
            self._terms.get("amaweb"),
            f"\n  [OK] Resultado TXT salvo: {path}\n", "success",
        )

    # ------------------------------------------------------------------ #
    #  IMAGE PREVIEW                                                       #
    # ------------------------------------------------------------------ #
    def _show_image_preview(self):
        folder = self._scraper_folder or self.scraper_output.get()
        if not os.path.isdir(folder):
            return
        imgs = [f for f in os.listdir(folder)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
                and not f.startswith(".")]
        if not imgs:
            self._append(self._terms.get("scraper"),
                         "  Nenhuma imagem encontrada na pasta de saida.\n", "warning")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Imagens baixadas ({len(imgs)} encontradas)")
        win.configure(bg=C["bg"])
        win.geometry("900x600")

        info_lbl = tk.Label(win, text=f"Exibindo ate 60 de {len(imgs)} imagens",
                            font=FONT_SMALL, bg=C["bg"], fg=C["text3"])
        info_lbl.pack(pady=(8, 0))

        frame_outer = tk.Frame(win, bg=C["bg"])
        frame_outer.pack(fill="both", expand=True, padx=10, pady=8)

        canvas = tk.Canvas(frame_outer, bg=C["bg"], highlightthickness=0)
        vsb = tk.Scrollbar(frame_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame_inner = tk.Frame(canvas, bg=C["bg"])
        canvas_win = canvas.create_window((0, 0), window=frame_inner, anchor="nw")

        COLS = 6
        THUMB = (130, 85)

        try:
            from PIL import Image, ImageTk
            has_pil = True
        except ImportError:
            has_pil = False

        for idx, fname in enumerate(imgs[:60]):
            path = os.path.join(folder, fname)
            col = idx % COLS
            row = idx // COLS
            if has_pil:
                try:
                    img = Image.open(path)
                    img.thumbnail(THUMB)
                    photo = ImageTk.PhotoImage(img)
                    lbl = tk.Label(frame_inner, image=photo, bg=C["bg3"],
                                   cursor="hand2", relief="flat")
                    lbl.image = photo
                    lbl.grid(row=row, column=col, padx=4, pady=4)
                    continue
                except Exception:
                    pass
            tk.Label(frame_inner, text=fname[:18], font=FONT_SMALL,
                     bg=C["bg3"], fg=C["text2"], width=16, height=5).grid(
                         row=row, column=col, padx=4, pady=4)

        def on_resize(event):
            canvas.itemconfig(canvas_win, width=event.width)
        canvas.bind("<Configure>", on_resize)
        frame_inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    # ------------------------------------------------------------------ #
    #  SCHEDULER (scraper agendado)                                        #
    # ------------------------------------------------------------------ #
    def _scheduler_loop(self):
        ultimo_trigger = None
        while not self._sched_stop.is_set():
            if self.scraper_agendado.get():
                now_hm = datetime.now().strftime("%H:%M")
                today  = datetime.now().date()
                if now_hm == self.scraper_horario.get() and ultimo_trigger != today:
                    ultimo_trigger = today
                    self.root.after(0, self._exec_scraper)
            time.sleep(30)

    # ------------------------------------------------------------------ #
    #  OUTPUT QUEUE POLLING  (50 ms)                                       #
    # ------------------------------------------------------------------ #
    def _poll_output(self):
        term = self._terms.get(self._running_module)
        try:
            while True:
                tag, payload = self.out_q.get_nowait()

                if tag == "DONE":
                    self.running = False
                    if term:
                        self._term_footer(term)
                    self._set_status("Concluido", C["green"])
                    if self.notif_var.get() and self._running_module:
                        notificar("AutoHub Pro",
                                  f"Modulo '{self._running_module}' concluido.")
                    self._running_module = None

                elif tag == "RESULT_DATA":
                    self._logs_result = payload
                    self._logs_dl_txt.configure(state="normal", fg=C["text2"])
                    self._logs_dl_xlsx.configure(state="normal", fg=C["text2"])

                elif tag == "RESULT_AMA":
                    self._ama_result_data = payload
                    self._ama_dl_txt.configure(state="normal", fg=C["text2"])

                elif tag == "DONE_SCRAPER":
                    self._scraper_folder = payload
                    self._scraper_preview_btn.configure(state="normal", fg=C["text2"])

                elif tag == "PROGRESS":
                    mod = self._running_module
                    if mod and mod in self._progress_vars:
                        self._progress_vars[mod].set(min(float(payload), 1.0))

                elif tag == "HISTORY":
                    try:
                        hist.registrar(
                            payload["modulo"], payload["status"],
                            payload.get("detalhes", ""),
                        )
                    except Exception:
                        pass

                else:
                    if term:
                        self._append(term, payload, tag)

        except queue.Empty:
            pass
        self.root.after(50, self._poll_output)

    # ------------------------------------------------------------------ #
    #  CLOSE / RUN                                                         #
    # ------------------------------------------------------------------ #
    def _on_close(self):
        try:
            settings.save({
                **settings.load(),
                "scraper_links":    self.scraper_links.get(),
                "scraper_output":   self.scraper_output.get(),
                "scraper_agendado": self.scraper_agendado.get(),
                "scraper_horario":  self.scraper_horario.get(),
                "ama_urls":         self.ama_urls.get(),
                "ama_result":       self.ama_result.get(),
                "ama_threshold":    self.ama_threshold.get(),
                "notificacoes":     self.notif_var.get(),
                "logs_servidores_elastic": [n for n, v in self._elastic_vars.items() if v.get()],
                "logs_servidores_liferay": [n for n, v in self._liferay_vars.items() if v.get()],
            })
        except Exception:
            pass
        self._sched_stop.set()
        self.stop_ev.set()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
