DARK = {
    "bg":      "#0d1117",
    "bg2":     "#161b22",
    "bg3":     "#21262d",
    "bg4":     "#30363d",
    "sidebar": "#010409",
    "accent":  "#58a6ff",
    "green":   "#3fb950",
    "red":     "#f85149",
    "yellow":  "#d29922",
    "orange":  "#e3702b",
    "text":    "#e6edf3",
    "text2":   "#8b949e",
    "text3":   "#484f58",
    "term_bg": "#0d1117",
}

LIGHT = {
    "bg":      "#f6f8fa",
    "bg2":     "#ffffff",
    "bg3":     "#eaeef2",
    "bg4":     "#d0d7de",
    "sidebar": "#24292f",
    "accent":  "#0969da",
    "green":   "#1a7f37",
    "red":     "#cf222e",
    "yellow":  "#9a6700",
    "orange":  "#bc4c00",
    "text":    "#1f2328",
    "text2":   "#656d76",
    "text3":   "#8c959f",
    "term_bg": "#f6f8fa",
}

C: dict = {}
C.update(DARK)


def set_theme(name: str) -> dict:
    C.update(LIGHT if name == "light" else DARK)
    return C


FONT_MAIN  = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_MONO  = ("Consolas", 9)
FONT_SMALL = ("Segoe UI", 8)
FONT_H2    = ("Segoe UI", 9, "bold")
