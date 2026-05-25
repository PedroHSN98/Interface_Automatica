#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cria o ícone do AutoHub Pro e um atalho na Área de Trabalho.
Execute uma vez: python criar_atalho.py
"""

import os
import subprocess
import sys
import tempfile

# garante UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH  = os.path.join(ASSETS_DIR, "icon.ico")


# ------------------------------------------------------------------ #
#  GERAÇÃO DO ÍCONE                                                    #
# ------------------------------------------------------------------ #
def _gerar_icone() -> str | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[!] Pillow não encontrado — atalho usará ícone padrão do Python.")
        return None

    os.makedirs(ASSETS_DIR, exist_ok=True)

    BG      = "#0d1117"
    BG2     = "#161b22"
    ACCENT  = "#58a6ff"
    WHITE   = "#e6edf3"
    SIZES   = [256, 128, 64, 48, 32, 16]
    frames  = []

    # Tenta carregar Segoe UI Bold (Windows) ou Arial como fallback
    def _font(size):
        for name in ("segoeuib.ttf", "arialbd.ttf", "arial.ttf"):
            path = os.path.join("C:\\Windows\\Fonts", name)
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    for s in SIZES:
        img  = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        pad  = max(2, s // 12)
        r    = s // 6          # border-radius

        # Fundo arredondado
        draw.rounded_rectangle([pad, pad, s - pad, s - pad],
                                radius=r, fill=BG2)

        # Borda accent
        bw = max(2, s // 28)
        draw.rounded_rectangle([pad, pad, s - pad, s - pad],
                                radius=r, outline=ACCENT, width=bw)

        if s >= 32:
            # Círculo interno preenchido
            cp = s // 5
            draw.ellipse([cp, cp, s - cp, s - cp], fill=BG)

            # Anel do círculo
            aw = max(1, s // 26)
            draw.ellipse([cp, cp, s - cp, s - cp],
                         outline=ACCENT, width=aw)

            # Letra "A" centralizada
            font_sz = int(s * 0.38)
            font    = _font(font_sz)
            draw.text((s // 2, s // 2), "A",
                      font=font, fill=WHITE, anchor="mm")

        frames.append(img)

    frames[0].save(
        ICON_PATH,
        format="ICO",
        append_images=frames[1:],
        sizes=[(s, s) for s in SIZES],
    )
    print(f"[✓] Ícone gerado: {ICON_PATH}")
    return ICON_PATH


# ------------------------------------------------------------------ #
#  CRIAÇÃO DO ATALHO                                                   #
# ------------------------------------------------------------------ #
def _criar_atalho(icon_path: str | None):
    desktop       = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "AutoHub Pro.lnk")

    # Usa pythonw.exe para não abrir janela de console
    pythonw = os.path.join(BASE_DIR, ".venv", "Scripts", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    app_py   = os.path.join(BASE_DIR, "app.py")
    icon_loc = icon_path if icon_path and os.path.exists(icon_path) else pythonw

    # Escreve script PS1 em arquivo temporário (evita problemas de escape)
    ps_content = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{pythonw}'
$Shortcut.Arguments = '"{app_py}"'
$Shortcut.WorkingDirectory = '{BASE_DIR}'
$Shortcut.IconLocation = '{icon_loc}'
$Shortcut.Description = 'AutoHub Pro - Central de Automacoes'
$Shortcut.WindowStyle = 1
$Shortcut.Save()
"""

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ps1", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(ps_content)
        ps_file = tmp.name

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file],
        capture_output=True, text=True,
    )
    os.unlink(ps_file)

    if result.returncode == 0:
        print(f"[✓] Atalho criado: {shortcut_path}")
        print()
        print("  Dica: arraste o atalho para fixá-lo na barra de tarefas.")
    else:
        print(f"[✗] Erro ao criar atalho:\n{result.stderr}")


# ------------------------------------------------------------------ #
#  ENTRY POINT                                                         #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    print("=" * 50)
    print("  AutoHub Pro — Criador de Atalho")
    print("=" * 50)
    print()

    icon = _gerar_icone()
    _criar_atalho(icon)

    print()
    input("  Pressione Enter para fechar...")