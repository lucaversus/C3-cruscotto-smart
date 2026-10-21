"""Studio d'ingombro della scheda madre (C3AI-CR-PL-001), D-029…D-031.

Rev. A: contorno e fori ricavati dal disegno del rivenditore della scheda S3 (137 x 84 mm,
fori Ø3,2 su interasse 130 x 76 mm), zone funzionali con ingombri stimati dei componenti,
scala 2:1. Non è un circuito stampato: serve a valutare l'area.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

BOARD_W, BOARD_H = 137.0, 84.0
HOLES = [(3.5, 4.0), (133.5, 4.0), (3.5, 80.0), (133.5, 80.0)]
SCALE = 2.0
OX, OY = 32.0, 48.0          # origine della scheda sul foglio (angolo in alto a sinistra)


def P(x, y):
    return OX + x * SCALE, OY + y * SCALE


# Zone: sigla, descrizione, x, y, larghezza, altezza (mm reali), facoltativa, area netta stimata (mm²)
ZONES = [
    ('-U6', 'Front-end WROOM-32E-H4/H8', 8, 0, 18, 25.5, False, 459),
    ('-U11', 'USB-C, CH340C, BOOT/EN', 28, 2, 24, 14, False, 336),
    ('-U7', 'VAN SN65HVD230', 53, 2, 12, 9, False, 108),
    ('-U8', 'K-line KL-001 (SMD)', 66, 2, 22, 14, False, 308),
    ('-U9', 'IMU LSM6DS3', 8, 30, 12, 10, False, 120),
    ('-U5', 'LDO 3,3 V + sempre acc.', 22, 30, 16, 10, False, 160),
    ('-X3', 'Ventola 4 poli, 2 NTC', 54, 18, 24, 8, False, 192),
    ('-U4', 'Buck 12→5 V 3 A', 40, 30, 22, 16, False, 352),
    ('-U1…U3', 'Ingresso 12 V protetto', 64, 30, 26, 20, False, 520),
    ('-K1/K2', 'Relè audio + driver', 8, 60, 34, 14, False, 476),
    ('-X2', 'J2 verso S3 (P1, P2, P6)', 8, 76, 34, 8, False, 272),
    ('-J1', 'Micro-Fit 3.0 2×8', 60, 71, 28, 13, False, 364),
    ('-C1', 'Riserva avviamento (da dimensionare)', 94, 10, 36, 24, True, 864),
    ('-U10', 'RTC DS3231 + CR2032', 94, 40, 24, 24, True, 576),
    ('-X4', 'MicroSD', 119, 40, 15, 15, True, 225),
]

d = Sheet('C3AI-CR-PL-001 rev A — Scheda madre, studio d\'ingombro')
d.frame()
d.text(25, 20, 'SCHEDA MADRE — STUDIO D\'INGOMBRO SUL CONTORNO DELLA SCHEDA S3 (SCALA 2:1)', 5, bold=True)
d.text(25, 25, 'Contorno e fori dal disegno del rivenditore della scheda ESP32-8048S050 (137 × 84 mm), da verificare '
               'sul pezzo. Zone con ingombri stimati: non è un circuito stampato.', 2.5)

# Contorno, fori e quote principali
x0, y0 = P(0, 0); x1, y1 = P(BOARD_W, BOARD_H)
d.rect(x0, y0, x1 - x0, y1 - y0, width=0.7)
for hx, hy in HOLES:
    cx, cy = P(hx, hy)
    d.circle(cx, cy, 1.6 * SCALE, width=0.35)
    d.circle(cx, cy, 3.5 * SCALE, width=0.25)
d.line((x0, y1 + 6), (x1, y1 + 6), width=0.25); d.line((x0, y1 + 2), (x0, y1 + 8), width=0.25)
d.line((x1, y1 + 2), (x1, y1 + 8), width=0.25); d.text((x0 + x1) / 2, y1 + 5, '137,0', 3, 'middle')
d.line((x0 - 5, y0), (x0 - 5, y1), width=0.25); d.line((x0 - 7, y0), (x0 - 1, y0), width=0.25)
d.line((x0 - 7, y1), (x0 - 1, y1), width=0.25); d.text(x0 - 6, (y0 + y1) / 2, '84,0', 3, 'middle', rotate=-90)
d.text(x0, y1 + 12, 'Fori Ø3,2 (M3) su interasse 130 × 76, a 3,5 / 4,0 mm dai bordi; cerchio esterno = zona libera Ø7.', 2.5)

# Area essenziale e area facoltativa
ex, ey = P(92, 0)
d.line((ex, y0), (ex, y1), width=0.35, dash='3 1.5')
d.text(*P(46, -1.5), 'AREA ESSENZIALE ≈ 90 × 84 mm', 3, 'middle', True)
d.text(*P(114.5, -1.5), 'AREA FACOLTATIVA / FLUSSO D\'ARIA', 3, 'middle', True)
d.text(*P(114.5, 70), 'se -C1, -U10, -X4 non montati qui:', 2.5, 'middle')
d.text(*P(114.5, 74), 'spazio per dissipatore e ventola (D-031)', 2.5, 'middle')

for ref, label, x, y, w, h, optional, _ in ZONES:
    zx, zy = P(x, y)
    d.rect(zx, zy, w * SCALE, h * SCALE, width=0.35, dash='3 1.5' if optional else None,
           fill='#eef4fb' if not optional else 'none')
    d.text(zx + 1.5, zy + 4.5, ref, 2.8, 'start', True)
    d.text(zx + 1.5, zy + 8.5, label, 2.2)
    d.text(zx + 1.5, zy + 12, f'{w:g} × {h:g}', 2.2)

# Antenna del front-end: bordo scheda, nessun rame sotto.
ax, ay = P(8, 0)
d.rect(ax, ay, 18 * SCALE, 6.5 * SCALE, width=0.25, fill='#f8d0d0')
d.text(ax + 18, ay + 8.5, 'antenna: niente rame', 2, 'middle')

# Tabella delle aree
rows = []
core = opt = 0
for ref, label, x, y, w, h, optional, area in ZONES:
    rows.append((ref, label[:30], f'{area}', 'facolt.' if optional else 'base'))
    if optional:
        opt += area
    else:
        core += area
rows.append(('', 'Totale base (netto)', f'{core}', ''))
rows.append(('', 'Totale facoltative', f'{opt}', ''))
rows.append(('', 'Base × 1,5 (piste, distanze)', f'{round(core * 1.5)}', ''))
rows.append(('', 'Contorno S3 137 × 84', f'{round(BOARD_W * BOARD_H)}', ''))
TX = 318
d.text(TX, 46, 'BILANCIO DELLE AREE (mm²)', 3.5, bold=True)
d.parts_list(TX, 49, list(reversed(rows)), widths=(14, 46, 12, 14), heads=('Sigla', 'Zona', 'mm²', 'Tipo'))

d.notes(25, 248, 'NOTE', [
    '1  Vista dal lato componenti, opposto alla scheda S3; la scheda madre si monta sui 4 fori della S3 con distanziali.',
    '2  Componenti su una sola faccia; con montaggio su due facce l\'area essenziale si riduce ulteriormente.',
    '3  Posizione dei connettori P1/P2/P6, USB-C e MicroSD della S3, altezze dei componenti sul retro e zona antenna',
    '   Wi-Fi della S3 da rilevare sul pezzo prima del disegno definitivo; distanziali da scegliere con dissipatore e flusso d\'aria.',
], h=2.5, step=4.2)

d.title_block(title=['Scheda madre', 'studio d\'ingombro'], subtitle='Cruscotto digitale',
              doc_type='Disposizione (2:1)', status='PRELIMINARE · NON VERIFICATO',
              code='C3AI-CR-PL-001', rev='A', date='21/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione: contorno S3, zone e bilancio aree (D-029…D-031)', '21/10/2026')])
out = ROOT / 'disegni/sorgenti/CR-PL-001_scheda-madre-ingombro.svg'
out.write_text(d.svg('Studio d\'ingombro della scheda madre sul contorno della scheda S3; stime, non PCB.'), encoding='utf-8')
print(out, core, opt)
