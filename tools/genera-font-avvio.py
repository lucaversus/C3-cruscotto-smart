"""Carattere dei controlli d'avvio "Matrix" per il firmware S3 (LVGL 8, lv_font_fmt_txt, 4 bpp).

Uso: python tools/genera-font-avvio.py
Share Tech Mono (tools/fonts, SIL Open Font License 1.1, scelto dall'utente il 23/10/2026):
monospaziato da terminale, con antialias a 16 livelli. Caratteri ASCII 0x20-0x7E.
Richiede Pillow (tools/requirements-dev.txt).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TTF = ROOT / 'tools/fonts/ShareTechMono-Regular.ttf'
OUT = ROOT / 'cruscotto/firmware/ui-idf/src/font_check.c'
SIZE = 20
NAME = 'font_check'
FIRST, LAST = 0x20, 0x7E


def main():
    font = ImageFont.truetype(str(TTF), SIZE)
    ascent, descent = font.getmetrics()
    bits, dsc = [], ['    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */']
    for code in range(FIRST, LAST + 1):
        ch = chr(code)
        adv = round(font.getlength(ch) * 16)
        box = font.getbbox(ch, anchor='ls')
        if box[2] <= box[0] or box[3] <= box[1]:   # spazio: nessun pixel
            dsc.append(f'    {{.bitmap_index = {len(bits) // 2}, .adv_w = {adv}, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0}}')
            continue
        l, t, r, b = box
        img = Image.new('L', (r - l, b - t), 0)
        ImageDraw.Draw(img).text((-l, -t), ch, font=font, fill=255, anchor='ls')
        dsc.append(f'    {{.bitmap_index = {len(bits) // 2}, .adv_w = {adv}, .box_w = {r - l}, .box_h = {b - t}, '
                   f'.ofs_x = {l}, .ofs_y = {-b}}} /* U+{code:04X} */')
        bits += [p >> 4 for p in img.getdata()]
        if len(bits) % 2:
            bits.append(0)
    data = [(bits[i] << 4) | bits[i + 1] for i in range(0, len(bits), 2)] or [0]
    rows = ',\n'.join('    ' + ', '.join(f'0x{v:02x}' for v in data[i:i + 16]) for i in range(0, len(data), 16))
    OUT.write_text(f'''/* Generato da tools/genera-font-avvio.py: non modificare a mano.
 * Share Tech Mono {SIZE} px, 4 bpp, ASCII 0x20-0x7E.
 * Share Tech Mono (c) 2012 Carrois Type Design, SIL Open Font License 1.1 (tools/fonts). */
#include "lvgl.h"

static LV_ATTRIBUTE_LARGE_CONST const uint8_t glyph_bitmap[] = {{
{rows}
}};

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {{
{(',' + chr(10)).join(dsc)}
}};

static const lv_font_fmt_txt_cmap_t cmaps[] = {{
    {{.range_start = 0x{FIRST:02X}, .range_length = {LAST - FIRST + 1}, .glyph_id_start = 1, .unicode_list = NULL,
     .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY}}
}};

static lv_font_fmt_txt_glyph_cache_t cache;
static const lv_font_fmt_txt_dsc_t font_dsc = {{
    .glyph_bitmap = glyph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .kern_dsc = NULL,
    .kern_scale = 0,
    .cmap_num = 1,
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
''', encoding='utf-8', newline='\n')
    print(OUT, f'{len(data)} byte')


if __name__ == '__main__':
    main()
