"""Carattere grande della velocità per il firmware S3 (LVGL 8, formato lv_font_fmt_txt, 4 bpp).

Uso: python tools/genera-font-velocita.py [percorso/Montserrat-Medium.ttf]
Senza argomento cerca il Montserrat-Medium.ttf distribuito con LVGL nelle librerie scaricate da
PlatformIO. Richiede Pillow (tools/requirements-dev.txt). Solo cifre 0-9 e "-", a larghezza fissa
(le cifre non si spostano al cambiare del valore). Per il grassetto con angoli arrotondati
richiesto dall'utente (23/10/2026) il tratto del Montserrat Medium viene ingrossato in modo
uniforme e arrotondato: disegno a 4x, sfocatura e soglia, riduzione con antialias.
Montserrat: SIL Open Font License 1.1.
"""
from pathlib import Path
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'cruscotto/firmware/ui-idf/src/font_speed.c'
SIZE = 160                      # pixel per em: cifre alte circa 125 px dopo l'ingrossamento
UP = 4                          # sovracampionamento
BOLD = 5                        # ingrossamento del tratto per lato, pixel finali
GAP = 8                         # spazio tra le cifre, pixel finali
CHARS = '-0123456789GO'          # cifre della velocità e GO dell'avvio
NAME = 'font_speed'


def find_ttf():
    core = os.environ.get('PLATFORMIO_CORE_DIR', str(Path.home() / 'Documents/Codex/pio-c3'))
    hits = glob.glob(str(Path(core) / 'workspaces/*/libdeps/*/lvgl/scripts/built_in_font/Montserrat-Medium.ttf'))
    if not hits:
        raise SystemExit('Montserrat-Medium.ttf non trovato: compilare prima ui-idf o indicare il percorso.')
    return hits[0]


def ink(font4, ch, ascent, descent):
    """Glifo ingrossato e arrotondato: (immagine L finale, riga della linea di base)."""
    pad = (BOLD + 4) * UP
    w = int(font4.getlength(ch)) + 2 * pad
    h = (ascent + descent) * UP + 2 * pad
    w, h = w + (-w) % UP, h + (-h) % UP
    big = Image.new('L', (w, h), 0)
    base = pad + ascent * UP
    ImageDraw.Draw(big).text((pad, base), ch, font=font4, fill=255, anchor='ls')
    # Sfocatura e soglia bassa: dilatazione circolare (angoli convessi arrotondati) ...
    big = big.filter(ImageFilter.GaussianBlur(BOLD * UP * 0.75)).point(lambda v: 255 if v > 24 else 0)
    # ... poi sfocatura e soglia a metà: arrotonda anche gli angoli concavi.
    big = big.filter(ImageFilter.GaussianBlur(UP * 1.5)).point(lambda v: 255 if v > 127 else 0)
    return big.resize((w // UP, h // UP), Image.LANCZOS), base // UP


def glyph(img, base, advance):
    l, t, r, b = img.getbbox()
    w, h = r - l, b - t
    px = [p >> 4 for p in img.crop((l, t, r, b)).getdata()]
    return w, h, round((advance - w) / 2), base - b, px


def main():
    ttf = sys.argv[1] if len(sys.argv) > 1 else find_ttf()
    font = ImageFont.truetype(ttf, SIZE)
    ascent, descent = font.getmetrics()
    font4 = ImageFont.truetype(ttf, SIZE * UP)
    inked = {ch: ink(font4, ch, ascent, descent) for ch in CHARS}
    advance = max(img.getbbox()[2] - img.getbbox()[0] for ch, (img, _) in inked.items() if ch.isdigit()) + GAP
    bits, dsc = [], ['    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */']
    for ch in CHARS:
        img = inked[ch][0]
        adv = advance if ch.isdigit() or ch == '-' else img.getbbox()[2] - img.getbbox()[0] + GAP  # lettere: larghezza propria
        w, h, ox, oy, px = glyph(*inked[ch], adv)
        assert w < 256 and h < 256 and -128 <= ox < 128 and -128 <= oy < 128, ch
        dsc.append(f'    {{.bitmap_index = {len(bits) // 2}, .adv_w = {adv * 16}, .box_w = {w}, .box_h = {h}, '
                   f'.ofs_x = {ox}, .ofs_y = {oy}}} /* U+{ord(ch):04X} "{ch}" */')
        bits += px
        if len(bits) % 2:
            bits.append(0)                           # ogni glifo inizia su un byte intero
    data = [(bits[i] << 4) | bits[i + 1] for i in range(0, len(bits), 2)]
    # Tabelle dei codici: una per ogni gruppo di caratteri consecutivi.
    groups = []
    for gid, ch in enumerate(CHARS, start=1):
        if groups and ord(ch) == groups[-1][0] + groups[-1][1]:
            groups[-1][1] += 1
        else:
            groups.append([ord(ch), 1, gid])
    cmaps = ',\n'.join(f'    {{.range_start = 0x{a:02X}, .range_length = {n}, .glyph_id_start = {g}, .unicode_list = NULL,\n'
                        f'     .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY}}'
                        for a, n, g in groups)
    rows = ',\n'.join('    ' + ', '.join(f'0x{b:02x}' for b in data[i:i + 16]) for i in range(0, len(data), 16))
    out = f'''/* Generato da tools/genera-font-velocita.py: non modificare a mano.
 * Montserrat Medium {SIZE} px ingrossato di {BOLD} px e arrotondato, 4 bpp, caratteri "{CHARS}",
 * cifre a larghezza fissa {advance} px.
 * Montserrat (c) The Montserrat Project Authors, SIL Open Font License 1.1. */
#include "lvgl.h"

static LV_ATTRIBUTE_LARGE_CONST const uint8_t glyph_bitmap[] = {{
{rows}
}};

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {{
{(',' + chr(10)).join(dsc)}
}};

static const lv_font_fmt_txt_cmap_t cmaps[] = {{
{cmaps}
}};

static lv_font_fmt_txt_glyph_cache_t cache;
static const lv_font_fmt_txt_dsc_t font_dsc = {{
    .glyph_bitmap = glyph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .kern_dsc = NULL,
    .kern_scale = 0,
    .cmap_num = {len(groups)},
    .bpp = 4,
    .kern_classes = 0,
    .bitmap_format = 0,
    .cache = &cache
}};

const lv_font_t {NAME} = {{
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,
    .line_height = {ascent + descent + 2 * BOLD},
    .base_line = {descent + BOLD},
    .subpx = LV_FONT_SUBPX_NONE,
    .underline_position = 0,
    .underline_thickness = 0,
    .dsc = &font_dsc
}};
'''
    OUT.write_text(out, encoding='utf-8', newline='\n')
    print(OUT, f'{len(data)} byte, cifra {advance} px')


if __name__ == '__main__':
    main()
