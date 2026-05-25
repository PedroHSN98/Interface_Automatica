import os
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import math
from datetime import datetime

from config.theme import C, FONT_MAIN, FONT_MONO, FONT_SMALL, FONT_H2
from automations.logs import run_logs
from automations.scraper import run_scraper
from automations.amaweb import run_amaweb


class AutoHubApp:

    NAV_ITEMS = [
        ("logs",    "📋", "Analisador de Logs",  "XML → Relatório de Erros"),
        ("scraper", "🖼", "Scraper de Imagens",  "Extração de Imagens Web"),
        ("amaweb",  "♿", "AMAWeb",              "Avaliador de Acessibilidade"),
    ]

    PAGE_META = {
        "logs":    ("📋  Analisador de Logs",  "XML → Relatório de Erros"),
        "scraper": ("🖼  Scraper de Imagens",  "Extração de Imagens Web"),
        "amaweb":  ("♿  AMAWeb",              "Avaliador de Acessibilidade"),
    }

    # ------------------------------------------------------------------ #
    #  INIT                                                                #
    # ------------------------------------------------------------------ #
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoHub Pro")
        self.root.geometry("1150x720")
        self.root.minsize(960, 620)
        self.root.configure(bg=C["bg"])

        self.current_page = "logs"
        self.running  = False
        self.stop_ev  = threading.Event()
        self.out_q    = queue.Queue()
        self._logs_result   = None

        self.logs_path      = tk.StringVar(value="logs_servidor/logs.xml")
        self.scraper_links  = tk.StringVar(value="fontes/links.txt")
        self.scraper_output = tk.StringVar(value="galeria_noticias")
        self.ama_urls       = tk.StringVar(value="urls.txt")
        self.ama_result     = tk.StringVar(value="resultado.xlsx")

        self._build_ui()
        self._poll_output()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    #  BUILD UI                                                            #
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()
        self._build_statusbar()
        self._select_page("logs")

    # ---- Sidebar ---- #
    def _build_sidebar(self):
        sb = tk.Frame(self.root, bg=C["sidebar"], width=215)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        lf = tk.Frame(sb, bg=C["sidebar"], pady=22)
        lf.pack(fill="x")
        tk.Label(lf, text="⚙", font=("Segoe UI", 26),
                 bg=C["sidebar"], fg=C["accent"]).pack()
        tk.Label(lf, text="AutoHub Pro", font=("Segoe UI", 12, "bold"),
                 bg=C["sidebar"], fg=C["text"]).pack()
        tk.Label(lf, text="Central de Automações", font=FONT_SMALL,
                 bg=C["sidebar"], fg=C["text3"]).pack()

        tk.Frame(sb, bg=C["bg4"], height=1).pack(fill="x", padx=14, pady=6)
        tk.Label(sb, text="AUTOMAÇÕES", font=("Segoe UI", 7, "bold"),
                 bg=C["sidebar"], fg=C["text3"]).pack(anchor="w", padx=18, pady=(10, 4))

        self._nav_btns = {}
        for key, icon, label, desc in self.NAV_ITEMS:
            self._nav_btns[key] = self._make_nav_btn(sb, key, icon, label, desc)

        tk.Frame(sb, bg=C["bg4"], height=1).pack(fill="x", padx=14, pady=10)
        tk.Label(sb, text="v1.0.0  •  2025", font=FONT_SMALL,
                 bg=C["sidebar"], fg=C["text3"]).pack(side="bottom", pady=10)

    def _make_nav_btn(self, parent, key, icon, label, desc):
        outer = tk.Frame(parent, bg=C["sidebar"], cursor="hand2")
        outer.pack(fill="x", padx=8, pady=2)
        inner = tk.Frame(outer, bg=C["sidebar"], padx=12, pady=9)
        inner.pack(fill="x")

        ic = tk.Label(inner, text=icon, font=("Segoe UI", 13),
                      bg=C["sidebar"], fg=C["text2"])
        ic.pack(side="left")

        tf = tk.Frame(inner, bg=C["sidebar"])
        tf.pack(side="left", padx=(10, 0))
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

    # ---- Main area ---- #
    def _build_main(self):
        main = tk.Frame(self.root, bg=C["bg"])
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        hdr = tk.Frame(main, bg=C["bg2"], height=58)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)

        self._hdr_title = tk.Label(hdr, text="", font=("Segoe UI", 14, "bold"),
                                   bg=C["bg2"], fg=C["text"])
        self._hdr_title.pack(side="left", padx=22, pady=14)

        self._hdr_badge = tk.Label(hdr, text="", font=FONT_SMALL,
                                   bg=C["bg3"], fg=C["text2"], pady=4)
        self._hdr_badge.pack(side="left", pady=20)

        pc = tk.Frame(main, bg=C["bg"])
        pc.grid(row=1, column=0, sticky="nsew")
        pc.columnconfigure(0, weight=1)
        pc.rowconfigure(0, weight=1)

        self._pages = {
            "logs":    self._page_logs(pc),
            "scraper": self._page_scraper(pc),
            "amaweb":  self._page_amaweb(pc),
        }

    # ---- Status bar ---- #
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
        self._tick_clock()

    def _tick_clock(self):
        self._clock_lbl.configure(text=datetime.now().strftime("%d/%m/%Y   %H:%M:%S"))
        self.root.after(1000, self._tick_clock)

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
        card = tk.Frame(parent, bg=C["bg2"], padx=22, pady=14)
        card.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        card.columnconfigure(1, weight=1)
        tk.Label(card, text="CONFIGURAÇÕES", font=("Segoe UI", 7, "bold"),
                 bg=C["bg2"], fg=C["text3"]).grid(
                     row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        return card

    def _file_row(self, card, row, label, var, mode="file"):
        tk.Label(card, text=label, font=FONT_MAIN, bg=C["bg2"],
                 fg=C["text2"], width=16, anchor="e").grid(
                     row=row, column=0, sticky="e", padx=(0, 10), pady=5)

        tk.Entry(card, textvariable=var, font=FONT_MONO,
                 bg=C["bg4"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=0).grid(
                     row=row, column=1, sticky="ew", ipady=7, padx=(0, 8))

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
                  command=browse, padx=10, pady=4).grid(row=row, column=2, pady=5)

    def _action_row(self, card, row, run_cmd):
        frm = tk.Frame(card, bg=C["bg2"])
        frm.grid(row=row, column=0, columnspan=4, sticky="w", pady=(12, 0))

        self._run_btn = tk.Button(
            frm, text="▶   Executar",
            font=("Segoe UI", 10, "bold"),
            bg=C["accent"], fg="#ffffff",
            activebackground="#388bfd", activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=22, pady=9,
            command=run_cmd,
        )
        self._run_btn.pack(side="left", padx=(0, 10))

        self._stop_btn = tk.Button(
            frm, text="■   Parar",
            font=("Segoe UI", 10),
            bg=C["bg4"], fg=C["text2"],
            activebackground=C["red"], activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=18, pady=9,
            command=self._stop,
        )
        self._stop_btn.pack(side="left")

    def _terminal_card(self, parent, key):
        card = tk.Frame(parent, bg=C["bg2"], padx=14, pady=12)
        card.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        hdr = tk.Frame(card, bg=C["bg2"])
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        tk.Label(hdr, text="▌ TERMINAL DE SAÍDA", font=("Segoe UI", 8, "bold"),
                 bg=C["bg2"], fg=C["text3"]).pack(side="left")

        term = tk.Text(
            card, font=FONT_MONO,
            bg=C["term_bg"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=0,
            wrap="word", state="disabled", cursor="arrow",
            selectbackground=C["bg4"],
        )
        scrollbar = tk.Scrollbar(card, command=term.yview, bg=C["bg3"],
                                 troughcolor=C["bg2"], width=12)
        term.configure(yscrollcommand=scrollbar.set)

        term.tag_configure("normal",   foreground="#e6edf3")
        term.tag_configure("info",     foreground="#58a6ff")
        term.tag_configure("success",  foreground="#3fb950")
        term.tag_configure("warning",  foreground="#d29922")
        term.tag_configure("error",    foreground="#f85149")
        term.tag_configure("title",    foreground="#e6edf3",
                           font=("Consolas", 9, "bold"))
        term.tag_configure("dim",      foreground="#484f58")
        term.tag_configure("progress", foreground="#e3702b")

        term.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        tk.Button(hdr, text="Limpar terminal", font=FONT_SMALL,
                  bg=C["bg4"], fg=C["text2"], relief="flat", cursor="hand2",
                  padx=8, pady=2,
                  command=lambda: self._clear(term)).pack(side="right")

        return term

    # ------------------------------------------------------------------ #
    #  PAGES                                                               #
    # ------------------------------------------------------------------ #
    def _page_logs(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)
        self._file_row(card, 1, "Arquivo logs.xml", self.logs_path, "file")
        self._action_row(card, 2, self._exec_logs)

        dl_frm = tk.Frame(card, bg=C["bg2"])
        dl_frm.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self._logs_download_btn = tk.Button(
            dl_frm,
            text="⬇   Baixar resultado (.txt)",
            font=("Segoe UI", 10),
            bg=C["bg4"],
            fg=C["text3"],
            activebackground=C["green"],
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=9,
            state="disabled",
            command=self._download_logs,
        )
        self._logs_download_btn.pack(side="left")

        self.term_logs = self._terminal_card(pg, "logs")
        return pg

    def _page_scraper(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)
        self._file_row(card, 1, "Links (links.txt)", self.scraper_links,  "file")
        self._file_row(card, 2, "Pasta de saída",   self.scraper_output, "dir")
        self._action_row(card, 3, self._exec_scraper)
        self.term_scraper = self._terminal_card(pg, "scraper")
        return pg

    def _page_amaweb(self, parent):
        pg = self._make_page(parent)
        card = self._config_card(pg)
        self._file_row(card, 1, "URLs (urls.txt)",   self.ama_urls,    "file")
        self._file_row(card, 2, "Resultado (.xlsx)", self.ama_result,  "save")
        self._action_row(card, 3, self._exec_amaweb)
        self.term_amaweb = self._terminal_card(pg, "amaweb")
        return pg

    # ------------------------------------------------------------------ #
    #  TERMINAL HELPERS                                                    #
    # ------------------------------------------------------------------ #
    def _current_term(self):
        return {
            "logs":    self.term_logs,
            "scraper": self.term_scraper,
            "amaweb":  self.term_amaweb,
        }[self.current_page]

    def _append(self, widget, text, tag="normal"):
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
    def _start(self, target, *args):
        if self.running:
            return
        self.running = True
        self.stop_ev.clear()
        term = self._current_term()
        self._clear(term)
        self._term_header(term)
        self._set_status("Executando...", C["yellow"])
        threading.Thread(target=target,
                         args=(*args, self.out_q, self.stop_ev),
                         daemon=True).start()

    def _exec_logs(self):
        self._logs_result = None
        self._logs_download_btn.configure(state="disabled", fg=C["text3"])
        self._start(run_logs, self.logs_path.get())

    def _exec_scraper(self):
        self._start(run_scraper, self.scraper_links.get(), self.scraper_output.get())

    def _exec_amaweb(self):
        self._start(run_amaweb, self.ama_urls.get(), self.ama_result.get())

    def _download_logs(self):
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
        lines = [
            "AutoHub Pro — Relatório de Logs",
            f"Gerado em:          {ts}",
            f"Arquivo analisado:  {data['arquivo']}",
            "─" * 64,
            "",
        ]
        for i, (erro, qty) in enumerate(data["contagem"].items(), 1):
            lines.append(f"  {i:02d}. {erro} = {qty}")
        lines += [
            "",
            "─" * 64,
            f"  Total de ocorrências: {data['total']}",
            "─" * 64,
        ]
        if data.get("ftl_details"):
            lines += [
                "",
                "─" * 64,
                "  FTL STACK TRACE — Detalhamento por template",
                "─" * 64,
                "",
            ]
            for loc, qty in sorted(data["ftl_details"].items(), key=lambda x: -x[1]):
                lines.append(f"  {loc} = {qty}")
            lines += [
                "",
                "─" * 64,
                f"  Total de ocorrências FTL: {sum(data['ftl_details'].values())}",
                "─" * 64,
            ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self._set_status(f"Salvo: {os.path.basename(path)}", C["green"])
        self._append(self.term_logs, f"\n  [✓] Relatório salvo: {path}\n", "success")

    def _stop(self):
        if self.running:
            self.stop_ev.set()
            self._set_status("Parando...", C["orange"])

    # ------------------------------------------------------------------ #
    #  OUTPUT QUEUE POLLING  (50 ms)                                       #
    # ------------------------------------------------------------------ #
    def _poll_output(self):
        term = self._current_term()
        try:
            while True:
                tag, text = self.out_q.get_nowait()
                if tag == "DONE":
                    self.running = False
                    self._term_footer(term)
                    self._set_status("Concluído", C["green"])
                elif tag == "RESULT_DATA":
                    self._logs_result = text
                    self._logs_download_btn.configure(state="normal", fg=C["text2"])
                else:
                    self._append(term, text, tag)
        except queue.Empty:
            pass
        self.root.after(50, self._poll_output)

    # ------------------------------------------------------------------ #
    #  CLOSE / RUN                                                         #
    # ------------------------------------------------------------------ #
    def _on_close(self):
        self.stop_ev.set()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
