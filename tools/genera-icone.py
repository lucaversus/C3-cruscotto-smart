"""Icone delle spie e della dashboard per il firmware S3 (LVGL 8, immagini LV_IMG_CF_ALPHA_8BIT).

Uso: python tools/genera-icone.py [--anteprima file.png]
Disegni originali del progetto ispirati ai simboli ISO 2575 delle spie, tracciati con Pillow
(tools/requirements-dev.txt) su una griglia 100x100, a 4x e ridotti con antialias. Sono solo
trasparenza: il colore lo dà il firmware (img_recolor), così la stessa icona serve in ogni colore.
Richiesta dell'utente 23/10/2026: nessuna scritta nella schermata di viaggio, solo icone.
"""
from pathlib import Path
import importlib.util
import math
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_C = ROOT / 'cruscotto/firmware/ui-idf/src/icons.c'
OUT_H = ROOT / 'cruscotto/firmware/ui-idf/src/icons.h'
UP = 4                       # sovracampionamento
G = 100                      # griglia di disegno


class Pen:
    """Disegno su griglia (100 di larghezza, salvo indicazione) con coordinate e spessori in
    unità di griglia; immagine quadrata di px pixel o rettangolare (larghezza, altezza)."""

    def __init__(self, px, grid=G):
        w, h = px if isinstance(px, tuple) else (px, px)
        self.k = w * UP / grid
        self.img = Image.new('L', (w * UP, h * UP), 0)
        self.d = ImageDraw.Draw(self.img)

    def p(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def line(self, pts, w, ink=255):
        pts = self.p(pts)
        self.d.line(pts, fill=ink, width=round(w * self.k), joint='curve')
        r = w * self.k / 2
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=ink)

    def poly(self, pts, ink=255):
        self.d.polygon(self.p(pts), fill=ink)

    def disc(self, cx, cy, r, ink=255):
        k = self.k
        self.d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), fill=ink)

    def ring(self, cx, cy, r, w, ink=255):
        k = self.k
        self.d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), outline=ink, width=round(w * k))

    def arc(self, box, a0, a1, w, ink=255):
        k = self.k
        self.d.arc([v * k for v in box], a0, a1, fill=ink, width=round(w * k))

    def rect(self, x0, y0, x1, y1, ink=255, r=0):
        k = self.k
        self.d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), radius=r * k, fill=ink)

    def frame(self, x0, y0, x1, y1, w, r=0, ink=255):
        k = self.k
        self.d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), radius=r * k, outline=ink, width=round(w * k))

    def wave(self, x0, x1, y, amp, w, vertical=False):
        pts = []
        for i in range(41):
            t = x0 + (x1 - x0) * i / 40
            v = y + amp * math.sin((t - x0) / (x1 - x0) * 4 * math.pi)
            pts.append((v, t) if vertical else (t, v))
        self.line(pts, w)

    def text(self, cx, cy, value, size):
        font = ImageFont.truetype(montserrat(), round(size * self.k))
        self.d.text((cx * self.k, cy * self.k), value, font=font, fill=255, anchor='mm', stroke_width=round(self.k))

    def done(self, px, round_r=0):
        img = self.img
        if round_r:                               # angoli arrotondati: sfocatura e soglia a metà
            img = img.filter(ImageFilter.GaussianBlur(round_r * self.k)).point(lambda v: 255 if v > 127 else 0)
        return img.resize(px if isinstance(px, tuple) else (px, px), Image.LANCZOS)


def montserrat():
    spec = importlib.util.spec_from_file_location('font', ROOT / 'tools/genera-font-velocita.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.find_ttf()


def circled(p):                                  # cerchio con parentesi laterali (freni, ABS, P)
    p.ring(50, 50, 27, 7)
    p.arc((6, 14, 94, 86), 125, 235, 7)
    p.arc((6, 14, 94, 86), 305, 55, 7)


def turn_left(p):
    p.poly([(6, 50), (46, 14), (46, 34), (94, 34), (94, 66), (46, 66), (46, 86)])


def turn_right(p):
    p.poly([(94, 50), (54, 14), (54, 34), (6, 34), (6, 66), (54, 66), (54, 86)])


def brake(p):
    circled(p)
    p.rect(45, 31, 55, 58, r=4)
    p.disc(50, 68, 5.5)


def park_brake(p):
    circled(p)
    p.line([(42, 70), (42, 32), (54, 32)], 8)
    p.arc((38, 32, 64, 54), 270, 90, 8)
    p.line([(42, 53), (54, 53)], 8)


def oil(p):
    p.poly([(14, 46), (58, 46), (70, 36), (93, 30), (93, 36), (74, 48), (70, 74), (14, 74)])
    p.frame(4, 46, 16, 64, 5, r=4)
    p.rect(30, 38, 44, 46)
    p.disc(91, 58, 4.5)
    p.poly([(87, 57), (91, 46), (95, 57)])


def thermometer(p, waves=True):
    p.frame(43, 6, 57, 62, 6, r=7)
    p.disc(50, 66, 12)
    p.rect(47, 30, 53, 62)
    for y in (18, 30, 42):
        p.line([(60, y), (72, y)], 5)
    if waves:
        p.wave(8, 92, 86, 4, 5)
        p.wave(8, 92, 96, 4, 5)


def coolant(p):
    thermometer(p, True)


def outside(p):
    thermometer(p, False)


def battery(p):
    p.frame(10, 30, 90, 80, 7, r=5)
    p.rect(20, 20, 36, 30)
    p.rect(64, 20, 80, 30)
    p.line([(64, 55), (80, 55)], 6)
    p.line([(72, 47), (72, 63)], 6)
    p.line([(20, 55), (36, 55)], 6)


def engine(p):
    p.frame(26, 34, 76, 78, 7, r=3)
    p.rect(36, 22, 66, 34)
    p.line([(44, 22), (58, 22)], 7)
    p.line([(26, 50), (12, 50), (12, 66), (26, 66)], 7)
    p.line([(76, 46), (90, 38), (90, 76), (76, 68)], 7)


def glow_plugs(p):
    pts = []
    for i in range(121):
        t = i / 120 * 6 * math.pi
        pts.append((16 + 3.6 * t - 10 * math.sin(t), 50 - 20 * math.cos(t)))
    p.line(pts, 6)


def abs_(p):
    circled(p)
    p.text(50, 51, 'ABS', 17)


def airbag(p):
    p.disc(30, 18, 10)
    p.line([(30, 34), (36, 62), (60, 62), (64, 88)], 11)
    p.line([(32, 44), (50, 50)], 9)
    p.disc(66, 38, 18)


def seat_belt(p):
    p.disc(50, 16, 11)
    p.poly([(26, 38), (74, 38), (70, 92), (30, 92)])
    p.line([(32, 40), (68, 86)], 8, ink=0)
    p.line([(36, 44), (64, 82)], 3)


def headlamp(p, facing_left=True):
    if facing_left:                              # parte arrotondata a destra
        p.disc(64, 50, 24)
        p.rect(0, 0, 64, 100, ink=0)
        p.rect(60, 26, 66, 74)
    else:
        p.disc(36, 50, 24)
        p.rect(36, 0, 100, 100, ink=0)
        p.rect(34, 26, 40, 74)


def high_beam(p):
    headlamp(p, True)
    for y in (30, 40, 50, 60, 70):
        p.line([(10, y), (50, y)], 6)


def front_fog(p):
    headlamp(p, True)
    for y in (30, 42, 54, 66):
        p.line([(48, y), (14, y + 10)], 5)
    p.wave(16, 86, 32, 4, 5, vertical=True)


def rear_fog(p):
    headlamp(p, False)
    for y in (30, 42, 54, 66):
        p.line([(52, y), (90, y)], 5)
    p.wave(16, 86, 70, 4, 5, vertical=True)


def door_open(p):
    p.frame(32, 8, 68, 92, 6, r=12)
    p.line([(36, 32), (64, 32)], 4)
    p.line([(36, 70), (64, 70)], 4)
    p.line([(32, 40), (12, 58)], 7)


def fuel(p):
    p.rect(18, 18, 60, 90, r=4)
    p.rect(25, 26, 53, 44, ink=0, r=2)
    p.rect(12, 86, 66, 94, r=2)
    p.line([(60, 36), (74, 36), (82, 46), (82, 74), (74, 78)], 6)
    p.line([(74, 36), (74, 24)], 6)


def link_lost(p):
    p.rect(8, 38, 36, 62, r=4)
    p.line([(36, 44), (46, 44)], 5)
    p.line([(36, 56), (46, 56)], 5)
    p.rect(64, 38, 92, 62, r=4)
    p.rect(64, 44, 70, 56, ink=0)
    p.line([(42, 84), (52, 50), (48, 50), (58, 16)], 6)


def c3_silhouette(p):
    """Citroën C3 prima serie vista di lato (muso a destra), solo contorno: dentro si scrive
    la temperatura dell'abitacolo. Griglia 200x100."""
    # Tetto ad arco alto e continuo fino al parabrezza, cofano corto e muso arrotondato.
    body = [(14, 74), (10, 58), (12, 42), (18, 28), (30, 16), (50, 8), (78, 5), (104, 6), (124, 12),
            (140, 24), (156, 40), (176, 46), (188, 52), (192, 62), (190, 74), (168, 74)]
    p.line(body, 6)
    p.arc((132, 58, 168, 94), 180, 360, 5)          # passaruota anteriore
    p.line([(132, 74), (68, 74)], 5)
    p.arc((32, 58, 68, 94), 180, 360, 5)            # passaruota posteriore
    p.line([(32, 74), (14, 74)], 5)
    p.disc(50, 78, 12)
    p.disc(150, 78, 12)
    p.line([(126, 16), (136, 30)], 3)               # montante anteriore


ICONS = {  # nome: (funzione, dimensioni in pixel)
    'turn_left': (turn_left, (84,)), 'turn_right': (turn_right, (84,)),
    'brake': (brake, (44, 110)), 'oil': (oil, (44, 110)), 'coolant': (coolant, (44, 42, 110)),
    'battery': (battery, (44, 28, 110)), 'park_brake': (park_brake, (44,)),
    'engine': (engine, (44,)), 'glow_plugs': (glow_plugs, (44,)), 'abs': (abs_, (44,)),
    'airbag': (airbag, (44,)), 'seat_belt': (seat_belt, (44,)), 'high_beam': (high_beam, (44,)),
    'front_fog': (front_fog, (44,)), 'rear_fog': (rear_fog, (44,)), 'door_open': (door_open, (44,)),
    'fuel': (fuel, (44, 42)), 'outside': (outside, (28,)), 'link_lost': (link_lost, (110,)),
    'c3': (c3_silhouette, ((176, 88),)),
}


ROUNDED = {'turn_left': 2.5, 'turn_right': 2.5}   # raggio di arrotondamento, unità di griglia


GRID = {'c3': 200}   # griglie diverse da 100 di larghezza


def render(name, fn, px):
    pen = Pen(px, GRID.get(name, G))
    fn(pen)
    return pen.done(px, ROUNDED.get(name, 0))


def main():
    images = {(name, px): render(name, fn, px) for name, (fn, sizes) in ICONS.items() for px in sizes}
    if len(sys.argv) > 2 and sys.argv[1] == '--anteprima':
        sheet = Image.new('L', (16 + 190 * 10, 16 + 120 * ((len(images) + 9) // 10)), 40)
        for i, img in enumerate(images.values()):
            sheet.paste(img, (16 + 190 * (i % 10), 16 + 120 * (i // 10)))
        sheet.save(sys.argv[2])
    c = ['/* Generato da tools/genera-icone.py: non modificare a mano. Icone originali del progetto\n'
         ' * (spie in stile ISO 2575), solo trasparenza a 8 bit: il colore lo dà img_recolor. */',
         '#include "icons.h"', '']
    h = ['// Icone della dashboard (tools/genera-icone.py). Formato LV_IMG_CF_ALPHA_8BIT.',
         '#pragma once', '#include "lvgl.h"', '']
    for (name, px), img in images.items():
        w, hh = img.size
        sym = f'icon_{name}_{w}' if w == hh else f'icon_{name}_{w}x{hh}'
        data = list(img.getdata())
        rows = ',\n'.join('    ' + ', '.join(f'0x{v:02x}' for v in data[i:i + 24]) for i in range(0, len(data), 24))
        c += [f'static const uint8_t {sym}_map[] = {{', rows, '};',
              f'const lv_img_dsc_t {sym} = {{',
              f'    .header = {{.cf = LV_IMG_CF_ALPHA_8BIT, .always_zero = 0, .reserved = 0, .w = {w}, .h = {hh}}},',
              f'    .data_size = {w * hh},', f'    .data = {sym}_map,', '};', '']
        h.append(f'extern const lv_img_dsc_t {sym};')
    OUT_C.write_text('\n'.join(c), encoding='utf-8', newline='\n')
    OUT_H.write_text('\n'.join(h) + '\n', encoding='utf-8', newline='\n')
    print(OUT_C, len(images), 'immagini')


if __name__ == '__main__':
    main()
