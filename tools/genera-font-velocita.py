"""Carattere grande della velocità per il firmware S3 (LVGL 8, formato lv_font_fmt_txt, 4 bpp).

Uso: python tools/genera-font-velocita.py [percorso/Montserrat-Medium.ttf]
Senza argomento cerca il Montserrat-Medium.ttf distribuito con LVGL nelle librerie scaricate da
PlatformIO. Richiede Pillow (tools/requirements-dev.txt). Solo cifre 0-9 e "-", a larghezza fissa
(le cifre non si spostano al cambiare del valore). Montserrat: SIL Open Font License 1.1.
"""
from pathlib import Path
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'cruscotto/firmware/ui-idf/src/font_speed.c'
SIZE = 170                      # pixel per em: cifre alte circa 120 px
CHARS = '-0123456789'
NAME = 'font_speed'


def find_ttf():
    core = os.environ.get('PLATFORMIO_CORE_DIR', str(Path.home() / 'Documents/Codex/pio-c3'))
    hits = glob.glob(str(Path(core) / 'workspaces/*/libdeps/*/lvgl/scripts/built_in_font/Montserrat-Medium.ttf'))
    if not hits:
        raise SystemExit('Montserrat-Medium.ttf non trovato: compilare prima ui-idf o indicare il percorso.')
    return hits[0]


def glyph(font, ch, advance):
    l, t, r, b = font.getbbox(ch, anchor='ls')
    w, h = r - l, b - t
    img = Image.new('L', (w, h), 0)
    ImageDraw.Draw(img).text((-l, -t), ch, font=font, fill=255, anchor='ls')
    own = font.getlength(ch)
    ofs_x = l + round((advance - own) / 2)          # cifra centrata nella larghezza fissa
    return w, h, ofs_x, -b, [p >> 4 for p in img.getdata()]


def main():
    ttf = sys.argv[1] if len(sys.argv) > 1 else find_ttf()
    font = ImageFont.truetype(ttf, SIZE)
    advance = round(max(font.getlength(c) for c in '0123456789'))
    ascent, descent = font.getmetrics()
    bits, dsc = [], ['    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */']
    for ch in CHARS:
        w, h, ox, oy, px = glyph(font, ch, advance)
        assert w < 256 and h < 256 and -128 <= ox < 128 and -128 <= oy < 128, ch
        dsc.append(f'    {{.bitmap_index = {len(bits) // 2}, .adv_w = {advance * 16}, .box_w = {w}, .box_h = {h}, '
                   f'.ofs_x = {ox}, .ofs_y = {oy}}} /* U+{ord(ch):04X} "{ch}" */')
        bits += px
        if len(bits) % 2:
            bits.append(0)                           # ogni glifo inizia su un byte intero
    data = [(bits[i] << 4) | bits[i + 1] for i in range(0, len(bits), 2)]
    rows = ',\n'.join('    ' + ', '.join(f'0x{b:02x}' for b in data[i:i + 16]) for i in range(0, len(data), 16))
    out = f'''/* Generato da tools/genera-font-velocita.py: non modificare a mano.
 * Montserrat Medium {SIZE} px, 4 bpp, caratteri "{CHARS}" a larghezza fissa {advance} px.
 * Montserrat (c) The Montserrat Project Authors, SIL Open Font License 1.1. */
#include "lvgl.h"

static LV_ATTRIBUTE_LARGE_CONST const uint8_t glyph_bitmap[] = {{
{rows}
}};

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {{
{(',' + chr(10)).join(dsc)}
}};

static const lv_font_fmt_txt_cmap_t cmaps[] = {{
    {{.range_start = 0x2D, .range_length = 1, .glyph_id_start = 1, .unicode_list = NULL,
     .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY}},
    {{.range_start = 0x30, .range_length = 10, .glyph_id_start = 2, .unicode_list = NULL,
     .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY}}
}};

static lv_font_fmt_txt_glyph_cache_t cache;
static const lv_font_fmt_txt_dsc_t font_dsc = {{
    .glyph_bitmap = glyph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .kern_dsc = NULL,
    .kern_scale = 0,
    .cmap_num = 2,
    .bpp = 4,
    .kern_classes = 0,
    .bitmap_format = 0,
    .cache = &cache
}};

const lv_font_t {NAME} = {{
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,
    .line_height = {ascent + descent},
    .base_line = {descent},
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
