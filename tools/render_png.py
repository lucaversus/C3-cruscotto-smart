"""Anteprime PNG dei disegni SVG A3 (D-024): 200 dpi, 3307 x 2339 pixel.

Uso: python tools/render_png.py cruscotto/docs/scheda-madre-blocchi.svg [altri.svg ...]
Richiede Chrome, Chromium o Edge (modalità headless); il percorso si può forzare con la
variabile d'ambiente CHROME. Il PNG viene scritto accanto all'SVG con lo stesso nome.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

WIDTH, HEIGHT = 3307, 2339
CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'google-chrome', 'chromium', 'chromium-browser', 'microsoft-edge',
]


def browser():
    if os.environ.get('CHROME'):
        return os.environ['CHROME']
    for name in CANDIDATES:
        found = name if Path(name).is_file() else shutil.which(name)
        if found:
            return found
    raise SystemExit('Browser headless non trovato: impostare CHROME con il percorso di Chrome/Edge.')


def render(svg, exe):
    svg = Path(svg).resolve()
    out = svg.with_suffix('.png')
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / 'page.html'
        page.write_text(f'<html><body style="margin:0"><img src="{svg.as_uri()}" '
                        f'style="width:{WIDTH}px;height:{HEIGHT}px;display:block"></body></html>',
                        encoding='utf-8')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--allow-file-access-from-files', '--force-device-scale-factor=1',
                        f'--window-size={WIDTH},{HEIGHT}', f'--user-data-dir={Path(tmp) / "profile"}',
                        f'--screenshot={out}', page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(out)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    exe = browser()
    for svg in sys.argv[1:]:
        render(svg, exe)


if __name__ == '__main__':
    main()
