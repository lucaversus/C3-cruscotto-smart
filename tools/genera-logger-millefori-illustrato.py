"""Data Logger completo a banco su millefori, collegamenti illustrati (C3AI-DL-EL-004).

Rev. A (D-042): ESP32 HW-394 su basetta 2, modulo K-line KL-001 rev F su basetta 1 (componenti e
fili interni letti dal generatore di KL-003),
RTC e lettore MicroSD su basetta 3, IMU LSM6DSO (STEVAL-MKI196V1) su basetta 4 ritagliata,
OLED, modulo VAN HW-CAN-VP230 (solo ricezione) e pulsante STOP con fili; fili saldati da una
basetta all'altra, senza morsetti. GPIO letti da hardware.json (firmware 0.3.x).
Disegno illustrativo: riferimenti tecnici KL-001 (K-line) e EL-003 (moduli).
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location('kl003', ROOT / 'tools/genera-kline-millefori.py')
KL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(KL)                    # dati di KL-003: componenti, fili, reti

PINS = json.loads((ROOT / 'data-logger/docs/hardware.json').read_text(encoding='utf-8'))['wiring_proposal']['pins']
assert (PINS['kKwpRx'], PINS['kKwpTx'], PINS['kSdCs'], PINS['kSck'], PINS['kMiso'], PINS['kMosi'],
        PINS['kSda'], PINS['kScl'], PINS['kStopPin'], PINS['kVanRx']) == (16, 17, 27, 18, 19, 23, 21, 22, 32, 34), \
    'GPIO cambiati in hardware.json: aggiornare il disegno'

C = {'GND': '#000000', '+5V': '#d00000', '+3V3': '#ff8c00', 'TX_INV': '#c8a000', 'RX_3V3': '#008000',
     'VBENCH': '#d040a0', 'K': '#0040d0', 'CS': '#8b4513', 'SCK': '#00a0a0', 'MISO': '#7030a0',
     'MOSI': '#606060', 'SDA': '#2080ff', 'SCL': '#e060e0', 'STOP': '#80a000',
     'VAN_RX': '#20a060', 'VAN': '#606060'}
NAMES = {'GND': 'massa', '+5V': '+5 V', '+3V3': '+3,3 V', 'TX_INV': 'TX K-line', 'RX_3V3': 'RX K-line',
         'VBENCH': '12 V banco', 'K': 'linea K', 'CS': 'SPI CS', 'SCK': 'SPI SCK', 'MISO': 'SPI MISO',
         'MOSI': 'SPI MOSI', 'SDA': 'I²C SDA', 'SCL': 'I²C SCL', 'STOP': 'STOP',
         'VAN_RX': 'RX VAN', 'VAN': 'bus VAN'}


def box(d, x, y, w, h, fill, rx=2, stroke='#000', sw=0.4):
    d.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def label(d, x, y, text, h=2.6, anchor='middle', bold=False, color='#000'):
    weight = ' font-weight="bold"' if bold else ''
    d.raw(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{h}" text-anchor="{anchor}" fill="{color}"{weight} '
          f'font-family="Arial, sans-serif">{text}</text>')


def wire(d, net, pts, width=1.4, ends=True):
    path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    d.raw(f'<polyline points="{path}" fill="none" stroke="{C[net]}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
    if ends:
        for x, y in (pts[0], pts[-1]):
            d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.1" fill="{C[net]}" stroke="#000" stroke-width="0.25"/>')


def inner(d, net, pts):
    """Filo interno di una basetta: più sottile, estremi saldati."""
    wire(d, net, pts, width=0.8)


def junction(d, net, x, y):
    d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.3" fill="{C[net]}" stroke="#000" stroke-width="0.3"/>')


def perfboard(d, x, y, w, h, title):
    box(d, x, y, w, h, '#e9d8a6', rx=2)
    step = 3.81                                  # passo 2,54 mm in scala 1,5:1
    for i in range(int((w - 4) / step)):
        for j in range(int((h - 4) / step)):
            d.raw(f'<circle cx="{x + 3.5 + i * step:.2f}" cy="{y + 3.5 + j * step:.2f}" r="0.55" fill="#c08040"/>')
    label(d, x + w / 2, y - 2.5, title, 3.2, bold=True)


def pad(d, x, y, text, side):
    d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.8" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
    label(d, x + (1.5 if side == 'L' else -1.5), y - 2.4, text, 2.1, 'start' if side == 'L' else 'end', True)
    return (x, y)


d = Sheet('C3AI-DL-EL-004 rev A — Data Logger completo a banco, collegamenti illustrati')
d.frame()
d.text(25, 20, 'DATA LOGGER COMPLETO A BANCO SU MILLEFORI — COLLEGAMENTI ILLUSTRATI', 5, bold=True)
d.text(25, 25, 'Disegno illustrativo, basette in scala 1,5:1 (millefori MC01009 72×47 mm): posizioni dei piedini indicative, collegare '
               'per nome secondo la serigrafia. Riferimenti tecnici: KL-001 rev F (K-line), EL-003 rev B (moduli). Nessun collegamento al veicolo.', 2.4)

# --- Basetta 2: ESP32 HW-394 ---------------------------------------------------------
perfboard(d, 28, 38, 70.5, 108, 'Basetta 2 — ESP32')
ex, ey, ew, eh = 42, 48, 42, 80
box(d, ex, ey, ew, eh, '#1f3a6e', rx=2)
box(d, ex + 9, ey + 2, 24, 12, '#d8d8d8', rx=1)
label(d, ex + ew / 2, ey + 9.5, 'ESP-32D', 2.6, bold=True)
box(d, ex + 14, ey + eh - 4, 14, 6, '#a0a0a0', rx=1)
label(d, ex + ew / 2, ey + eh + 6, 'USB → PC (5 V e seriale)', 2.4, bold=True)
label(d, ex + ew / 2, ey + 22, '-A1 HW-394', 2.6, bold=True, color='#ffffff')
esp = {}
LEFT = ['EN', 'VP', 'VN', 'D34', 'D35', 'D32', 'D33', 'D25', 'D26', 'D27', 'D14', 'D12', 'D13', 'GND', 'VIN']
RIGHT = ['D23', 'D22', 'TX0', 'RX0', 'D21', 'D19', 'D18', 'D5', 'TX2', 'RX2', 'D4', 'D2', 'D15', 'GND', '3V3']
HOT_L, HOT_R = {'D34', 'D32', 'D27', 'GND', 'VIN'}, {'D23', 'D22', 'D21', 'D19', 'D18', 'TX2', 'RX2', 'GND', '3V3'}
for side, names, hot_set in (('L', LEFT, HOT_L), ('R', RIGHT, HOT_R)):
    for i, n in enumerate(names):
        y = 56 + i * 3.81
        x = 44 if side == 'L' else 82
        hot = n in hot_set
        d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.2" fill="{"#ffd700" if hot else "#c0c0c0"}" stroke="#000" stroke-width="0.2"/>')
        label(d, x + (2.4 if side == 'L' else -2.4), y + 0.8, n, 2.0, 'start' if side == 'L' else 'end', hot, '#ffffff')
        esp[side + n] = (x, y)
label(d, 63, 141, 'ESP32 saldato sulla basetta', 2.3)

# --- Basetta 1: modulo K-line, disposizione e fili di KL-003 ------------------------
B1 = (150, 38, 108, 70.5)
box(d, *B1, '#e9d8a6', rx=2)
label(d, B1[0] + B1[2] / 2, B1[1] - 2.5, 'Basetta 1 — K-line KL-001 rev F (disposizione KL-003)', 3.2, bold=True)
KX0, KY0, KS = 160.2, 44.7, 3.81                 # foro A1 e passo 2,54 mm in scala 1,5:1
assert KL.verify() > 0                          # reti di KL-003 = netlist KL-001 rev F


def KP(h):
    c, r = KL.hole(h)
    return KX0 + c * KS, KY0 + r * KS


for c in range(-2, 26):
    for r in range(-1, 17):
        d.raw(f'<circle cx="{KX0 + c * KS:.2f}" cy="{KY0 + r * KS:.2f}" r="0.55" fill="#c08040"/>')
for net, holes in KL.BUSES:
    (xa, ya), (xb, yb) = KP(holes[0]), KP(holes[-1])
    d.raw(f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" y2="{yb:.2f}" stroke="#909090" stroke-width="1.0" stroke-linecap="round"/>')
for net, path in KL.WIRES:
    pts = ' '.join(f'{KP(h)[0]:.2f},{KP(h)[1]:.2f}' for h in path)
    d.raw(f'<polyline points="{pts}" fill="none" stroke="{KL.NET_COLOR[net]}" stroke-width="0.7" stroke-linejoin="round" opacity="0.9"/>')
    for h in (path[0], path[-1]):
        x, y = KP(h)
        d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.5" fill="{KL.NET_COLOR[net]}" stroke="#000" stroke-width="0.1"/>')
for ref, (ohms, precise) in KL.RES.items():
    (xa, ya), (xb, yb) = KP(KL.COMP[ref]['a'][0]), KP(KL.COMP[ref]['b'][0])
    mx, my = (xa + xb) / 2, (ya + yb) / 2
    horizontal = abs(ya - yb) < 0.1
    w, h = (6, 2) if horizontal else (2, 6)
    d.raw(f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" y2="{yb:.2f}" stroke="#606060" stroke-width="0.35"/>')
    d.raw(f'<rect x="{mx - w / 2:.2f}" y="{my - h / 2:.2f}" width="{w}" height="{h}" rx="0.9" fill="{"#8fb8e8" if precise else "#e8d2a0"}" stroke="#000" stroke-width="0.2"/>')
    bands = KL.resistor_bands(ohms, precise)
    for i, col in enumerate(bands):
        off = -2 + i * (4 / (len(bands) - 1))
        if horizontal:
            d.raw(f'<rect x="{mx + off - 0.25:.2f}" y="{my - h / 2:.2f}" width="0.5" height="{h}" fill="{col}"/>')
        else:
            d.raw(f'<rect x="{mx - w / 2:.2f}" y="{my + off - 0.25:.2f}" width="{w}" height="0.5" fill="{col}"/>')
    tx, ty = (mx, my - 1.6) if horizontal else (mx + 1.6, my + 0.6)
    label(d, tx, ty, f'{ref} {KL.RES_LABEL[ref]}', 1.5, 'middle' if horizontal else 'start', True)
# U1 LM2903B SOIC-8 incollato al centro dei suoi 8 fori, fili sottili dai piedini ai fori.
(xa, ya), (xb, yb) = KP(KL.COMP['U1']['8'][0]), KP(KL.COMP['U1']['4'][0])
cx, cy = (xa + xb) / 2, (ya + yb) / 2
for pin, (hl, _) in KL.COMP['U1'].items():
    x, y = KP(hl)
    px_ = cx + (int(pin) - 2.5 if int(pin) <= 4 else 6.5 - int(pin)) * 1.9
    py_ = cy + (2.2 if int(pin) <= 4 else -2.2)
    d.raw(f'<line x1="{px_:.2f}" y1="{py_:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="#b07020" stroke-width="0.3"/>')
    d.raw(f'<rect x="{x - 0.8:.2f}" y="{y - 0.8:.2f}" width="1.6" height="1.6" fill="#d0d0d0" stroke="#000" stroke-width="0.15"/>')
    label(d, x + (1.3 if int(pin) in (4, 5) else -1.3 if int(pin) in (1, 8) else 0), y + (2.4 if int(pin) <= 4 else -1.2), pin, 1.3, 'middle', True)
box(d, cx - 4.5, cy - 2, 9, 4, '#303030', rx=0.3)
d.raw(f'<circle cx="{cx - 3.6:.2f}" cy="{cy + 1.1:.2f}" r="0.35" fill="#ffffff"/>')
label(d, cx, cy + 0.6, 'U1', 1.6, bold=True, color='#ffffff')
for ref, shape in (('C1', 'disc'), ('C2', 'elec')):
    hl = list(KL.COMP[ref].values())
    (x1, y1), (x2, y2) = KP(hl[0][0]), KP(hl[1][0])
    cx, cy = (x1 + x2) / 2 - 1.4, (y1 + y2) / 2
    for (h, _) in hl:
        x, y = KP(h)
        d.raw(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="#606060" stroke-width="0.3"/>')
    if shape == 'disc':
        d.raw(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="0.9" ry="1.3" fill="#e0a020" stroke="#000" stroke-width="0.2"/>')
        label(d, cx + 0.5, cy + 4.3, 'C1', 1.5, 'middle', True)
    else:
        d.raw(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.3" fill="#203080" stroke="#000" stroke-width="0.2"/>'
              f'<rect x="{cx - 1.3:.2f}" y="{cy + 0.3:.2f}" width="2.6" height="0.5" fill="#c0c0c0"/>')
        label(d, cx - 1.8, cy + 0.5, 'C2', 1.5, 'end', True)
hs = [KP(h) for h, _ in KL.COMP['Q1'].values()]
xq = hs[0][0]
d.raw(f'<path d="M{xq + 1:.2f} {hs[0][1] - 1.2:.2f} L{xq + 1:.2f} {hs[-1][1] + 1.2:.2f} '
      f'A 2 {(hs[-1][1] - hs[0][1]) / 2 + 1.2:.2f} 0 0 1 {xq + 1:.2f} {hs[0][1] - 1.2:.2f} Z" fill="#202020" opacity="0.9"/>')
for pin, (h, _) in KL.COMP['Q1'].items():
    x, y = KP(h)
    label(d, x - 0.6, y + 0.5, pin, 1.3, 'end', True, '#ffffff')
label(d, xq - 3, hs[0][1] - 2, 'Q1', 1.6, 'end', True)
label(d, 204, 112, 'Componenti e fili interni come KL-003 (R3 fuori basetta). U1 SOIC-8 incollato, fili sottili piedino→foro;', 1.9)
label(d, 204, 114.6, 'X1/X2 = fori dove si saldano i fili W1-W5 e W24, W26, W27 (niente morsettiere).', 1.9)


def kpad(h, text, side):
    x, y = KP(h)
    d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.3" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
    label(d, x + (-1.8 if side == 'L' else 1.8), y - 1.6, text, 1.8, 'end' if side == 'L' else 'start', True)
    return (x, y)


X1, X2 = KL.COMP['X1'], KL.COMP['X2']
k = {'RX_3V3': kpad(X1['1'][0], 'X1:1 RX', 'L'), 'TX_INV': kpad(X1['2'][0], 'X1:2 TX', 'L'),
     '+5V': kpad(X1['3'][0], 'X1:3 +5V', 'L'), '+3V3': kpad(X1['4'][0], 'X1:4 +3V3', 'L'),
     'GND': kpad(X1['5'][0], 'X1:5 GND', 'L')}
kr = {'K': kpad(X2['1'][0], 'X2:1 K', 'R'), 'VBENCH': kpad(X2['2'][0], 'X2:2 VBENCH', 'R'),
      'GND': kpad(X2['3'][0], 'X2:3 GND', 'R')}

# --- Basetta 3: RTC e MicroSD ------------------------------------------------------
perfboard(d, 150, 122, 108, 70.5, 'Basetta 3 — RTC e MicroSD')
m = {n: pad(d, 155, y, t, 'L') for n, y, t in (('+3V3', 128, '3V3'), ('GND', 135, 'GND'), ('CS', 142, 'CS'),
                                                ('SCK', 149, 'SCK'), ('MISO', 156, 'MISO'), ('SDA', 163, 'SDA'),
                                                ('SCL', 170, 'SCL'), ('MOSI', 177, 'MOSI'))}
box(d, 182, 124, 28, 37, '#2050a0', rx=1.5)
box(d, 194, 128, 13, 20, '#c0c0c0', rx=1); label(d, 197, 155, 'MicroSD', 2.2, bold=True, color='#ffffff')
label(d, 197, 159, '-A2', 2.2, bold=True, color='#ffffff')
sd = {}
for i, n in enumerate(['3V3', 'CS', 'MOSI', 'CLK', 'MISO', 'GND']):
    y = 130 + i * 5
    d.raw(f'<circle cx="185" cy="{y}" r="1" fill="#ffd700" stroke="#000" stroke-width="0.2"/>')
    label(d, 187, y + 0.8, n, 1.8, 'start', False, '#ffffff')
    sd[n] = (185, y)
box(d, 220, 124, 36, 33, '#2050a0', rx=1.5)
d.raw('<circle cx="245" cy="137" r="8" fill="#d0d0d0" stroke="#000" stroke-width="0.3"/>')
label(d, 245, 138, 'CR2032', 2.0, bold=True); label(d, 238, 154, 'RTC DS3231  -A3', 2.2, bold=True, color='#ffffff')
rtc = {}
for i, n in enumerate(['GND', 'VCC', 'SDA', 'SCL', 'SQW', '32K']):
    y = 129 + i * 5
    d.raw(f'<circle cx="223" cy="{y}" r="1" fill="{"#ffd700" if i < 4 else "#c0c0c0"}" stroke="#000" stroke-width="0.2"/>')
    label(d, 225, y + 0.8, n, 1.8, 'start', False, '#ffffff')
    rtc[n] = (223, y)
o_pad = {n: pad(d, 253, y, t, 'R') for n, y, t in (('GND', 160, 'GND'), ('+3V3', 166, 'VCC'),
                                                   ('SDA', 172, 'SDA'), ('SCL', 179, 'SCL'))}
label(d, 240, 190, 'verso OLED', 2.2, bold=True)
v_pad = {'GND': (160, 188), '+3V3': (164, 188)}
for n, (x, y) in v_pad.items():
    d.raw(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
label(d, 162, 185.2, 'VAN', 1.8, bold=True)
inner(d, 'GND', [(169, 188), v_pad['GND']]); junction(d, 'GND', 169, 188)
inner(d, '+3V3', [(171, 186), (164, 186), v_pad['+3V3']]); junction(d, '+3V3', 171, 186)
# Fili interni della basetta 3: bus di massa e 3,3 V a sinistra, I²C verso RTC e OLED.
inner(d, 'GND', [m['GND'], (169, 135), (169, 188), (214, 188), (214, 129), rtc['GND']])
inner(d, '+3V3', [m['+3V3'], (171, 128), (171, 186), (212, 186), (212, 134), rtc['VCC']])
inner(d, '+3V3', [(171, 130), sd['3V3']]); junction(d, '+3V3', 171, 130)
inner(d, 'GND', [(169, 155), sd['GND']]); junction(d, 'GND', 169, 155)
inner(d, 'CS', [m['CS'], (173, 142), (173, 135), sd['CS']])
inner(d, 'SCK', [m['SCK'], (175, 149), (175, 145), sd['CLK']])
inner(d, 'MISO', [m['MISO'], (177, 156), (177, 150), sd['MISO']])
inner(d, 'MOSI', [m['MOSI'], (179, 177), (179, 140), sd['MOSI']])
inner(d, 'SDA', [m['SDA'], (216, 163), (216, 139), rtc['SDA']])
inner(d, 'SCL', [m['SCL'], (217.5, 170), (217.5, 144), rtc['SCL']])
inner(d, 'GND', [(214, 160), o_pad['GND']]); junction(d, 'GND', 214, 160)
inner(d, '+3V3', [(212, 166), o_pad['+3V3']]); junction(d, '+3V3', 212, 166)
inner(d, 'SDA', [(216, 163), (216, 172), o_pad['SDA']]); junction(d, 'SDA', 216, 163)
inner(d, 'SCL', [(217.5, 170), (217.5, 179), o_pad['SCL']]); junction(d, 'SCL', 217.5, 170)
for n in ('SQW', '32K'):
    x, y = rtc[n]
    d.raw(f'<path d="M{x - 3.2} {y - 1.2} l2.4 2.4 M{x - 3.2} {y + 1.2} l2.4 -2.4" stroke="#000" stroke-width="0.35"/>')

# --- OLED ------------------------------------------------------------------------------
box(d, 292, 140, 40, 38, '#1a1a1a', rx=1.5)
box(d, 302, 145, 27, 22, '#0a2a4a', rx=0.5); label(d, 315.5, 158, 'OLED', 3, bold=True, color='#80c0ff')
label(d, 312, 137, '-A4  OLED I²C (HW-OLED)', 3, bold=True)
oled = {}
for i, n in enumerate(['GND', 'VCC', 'SCL', 'SDA']):
    y = 148 + i * 6
    d.raw(f'<circle cx="295" cy="{y}" r="1.1" fill="#ffd700" stroke="#000" stroke-width="0.2"/>')
    label(d, 297.5, y + 0.8, n, 1.8, 'start', False, '#ffffff')
    oled[n] = (295, y)

# --- Basetta 4: IMU su ritaglio di millefori ------------------------------------------
perfboard(d, 345, 131, 37.5, 57, '')
label(d, 363.75, 129, 'Basetta 4 — IMU (ritaglio ~25×38 mm)', 2.6, bold=True)
box(d, 356, 135, 23, 48, '#1a6a3a', rx=1)
for j in range(12):
    for xx in (357.5, 377.5):
        d.raw(f'<circle cx="{xx}" cy="{137.5 + j * 3.81:.2f}" r="0.9" fill="#ffd700" stroke="#000" stroke-width="0.2"/>')
box(d, 363.5, 140, 8, 8, '#202020', rx=0.5)
label(d, 367.5, 152, 'STEVAL-', 1.9, bold=True, color='#ffffff'); label(d, 367.5, 155, 'MKI196V1', 1.9, bold=True, color='#ffffff')
label(d, 367.5, 159, 'LSM6DSO', 1.9, color='#ffffff'); label(d, 367.5, 163, '-A5', 2.2, bold=True, color='#ffffff')
d.raw('<path d="M362 178 h10 M372 178 l-2 -1.2 M372 178 l-2 1.2 M362 178 v-10 M362 168 l-1.2 2 M362 168 l1.2 2" stroke="#ffffff" stroke-width="0.5" fill="none"/>')
label(d, 373.5, 179, 'X', 2, 'start', True, '#ffffff'); label(d, 363, 167.5, 'Y', 2, 'start', True, '#ffffff')
imu = {n: pad(d, 349, y, t, 'L') for n, y, t in (('GND', 145, 'GND'), ('+3V3', 151, '3V3'), ('SDA', 157, 'SDA'), ('SCL', 163, 'SCL'))}
for n, (x, y) in imu.items():
    d.raw(f'<line x1="{x + 1.8:.2f}" y1="{y}" x2="356" y2="{y}" stroke="{C[n]}" stroke-width="0.8" stroke-dasharray="1.2 0.8"/>')
d.text(345, 192.5, 'Tratteggio: piedini DIL-24 dal manuale ST,', 2.0)
d.text(345, 195.5, 'da verificare. VDD, VDDIO e CS a 3V3 (I²C);', 2.0)
d.text(345, 198.5, 'SA0 a GND → indirizzo 0x6A.', 2.0)

# --- R3 e alimentatore da banco ------------------------------------------------------
d.raw('<line x1="272" y1="50" x2="318" y2="50" stroke="#808080" stroke-width="0.8"/>')
box(d, 280, 45.5, 30, 9, '#8fb8e8', rx=4)
for i, col in enumerate(('#00a000', '#8b4513', '#000000', '#000000', '#8b4513')):
    d.raw(f'<rect x="{285 + i * 4.5:.2f}" y="45.5" width="1.6" height="9" fill="{col}"/>')
label(d, 295, 42, '-R3  510 Ω 1 W — simulatore della linea (solo banco)', 2.4, bold=True)
px, py, pw, ph = 300, 70, 70, 44
box(d, px, py, pw, ph, '#d8d8d8', rx=3)
box(d, px + 6, py + 6, 34, 14, '#102010', rx=1); label(d, px + 23, py + 16, '12.0 V', 6, bold=True, color='#40ff40')
box(d, px + 6, py + 23, 34, 8, '#102010', rx=1); label(d, px + 23, py + 29, '0.10 A max', 3.6, bold=True, color='#ff4040')
plus, minus = (px + 50, py + 38), (px + 62, py + 38)
d.raw(f'<circle cx="{plus[0]}" cy="{plus[1]}" r="3.2" fill="#d00000" stroke="#000" stroke-width="0.3"/>'
      f'<circle cx="{minus[0]}" cy="{minus[1]}" r="3.2" fill="#202020" stroke="#000" stroke-width="0.3"/>')
label(d, plus[0], py + 30, '+', 4, bold=True); label(d, minus[0], py + 30, '−', 4, bold=True)
label(d, px + pw / 2, py - 2, '-G1  Alimentatore da banco (HW-BENCH-PSU)', 2.8, bold=True)

# --- Pulsante STOP ---------------------------------------------------------------------
box(d, 36, 163, 18, 10, '#404040', rx=2)
d.raw('<circle cx="45" cy="168" r="3.5" fill="#d00000" stroke="#000" stroke-width="0.3"/>')
s1a, s1b = (41, 163), (49, 163)
label(d, 36, 186, '-S1  STOP (NO), HW-STOP-BUTTON', 2.2, 'start', True)

# --- Modulo VAN: solo ricezione ------------------------------------------------------
box(d, 80, 160, 32, 30, '#2050a0', rx=1.5)
label(d, 96, 157.5, '-A6  VAN SN65HVD230 (HW-CAN-VP230)', 2.4, bold=True)
box(d, 101, 162, 9, 6, '#202020', rx=0.5); label(d, 105.5, 166, 'VP230', 1.6, bold=True, color='#ffffff')
box(d, 103, 184, 7, 3, '#303030', rx=0.3); label(d, 106.5, 186.3, '121', 1.5, color='#ffffff')
d.raw('<path d="M101.5 182.5 l10 6 M101.5 188.5 l10 -6" stroke="#ff3030" stroke-width="0.6"/>')
label(d, 96, 199.5, 'R 120 Ω «121» da scollegare (D-022 prova 1)', 1.8, bold=True, color='#c00000')
van = {}
for n, y in (('RX', 165), ('TX', 170), ('GND', 175), ('3V3', 180)):
    d.raw(f'<circle cx="83" cy="{y}" r="1" fill="#ffd700" stroke="#000" stroke-width="0.2"/>')
    label(d, 93.5, y + 0.8, n, 1.8, 'start', False, '#ffffff')
    van[n] = (83, y)
for n, y in (('CANH', 172), ('CANL', 178)):
    d.raw(f'<circle cx="109" cy="{y}" r="1" fill="#ffd700" stroke="#000" stroke-width="0.2"/>')
    label(d, 107, y + 0.8, n, 1.6, 'end', False, '#ffffff')
    van[n] = (109, y)
inner(d, '+3V3', [van['TX'], (90, 170), (90, 180), van['3V3']])
label(d, 84, 188, 'ponticello TX–3V3', 1.6, 'start', True, '#ffd080')
box(d, 118, 168, 6, 14, '#2e8b57', rx=0.5)
for y in (172, 178):
    d.raw(f'<circle cx="121" cy="{y}" r="1.3" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
for y in (172, 178):
    d.raw(f'<line x1="109" y1="{y}" x2="121" y2="{y}" stroke="{C["VAN"]}" stroke-width="1.2" stroke-dasharray="2 1"/>')
label(d, 113, 186, '-X3 verso quadro 0004 vie 1/3', 2.0, 'start', True)
label(d, 113, 189.2, 'NON COLLEGARE prima di D-022', 2.0, 'start', True, '#c00000')

# --- Fili tra le basette --------------------------------------------------------------
L, R = (lambda n: esp['L' + n]), (lambda n: esp['R' + n])
wire(d, 'RX_3V3', [R('RX2'), (104, R('RX2')[1]), (104, k['RX_3V3'][1]), k['RX_3V3']])
wire(d, 'TX_INV', [R('TX2'), (106, R('TX2')[1]), (106, k['TX_INV'][1]), k['TX_INV']])
wire(d, 'GND', [R('GND'), (110, R('GND')[1]), (110, k['GND'][1]), k['GND']])
wire(d, '+3V3', [R('3V3'), (112, R('3V3')[1]), (112, k['+3V3'][1]), k['+3V3']])
wire(d, '+5V', [L('VIN'), (31, L('VIN')[1]), (31, 152), (114, 152), (114, k['+5V'][1]), k['+5V']])
wire(d, 'GND', [(110, R('GND')[1]), (122, R('GND')[1]), (122, 135), m['GND']]); junction(d, 'GND', 110, R('GND')[1])
wire(d, '+3V3', [(112, R('3V3')[1]), (120, R('3V3')[1]), (120, 128), m['+3V3']]); junction(d, '+3V3', 112, R('3V3')[1])
wire(d, 'CS', [L('D27'), (34, L('D27')[1]), (34, 149), (126, 149), (126, 142), m['CS']])
wire(d, 'SCK', [R('D18'), (130, R('D18')[1]), (130, 149), m['SCK']])
wire(d, 'MISO', [R('D19'), (134, R('D19')[1]), (134, 156), m['MISO']])
wire(d, 'SDA', [R('D21'), (138, R('D21')[1]), (138, 163), m['SDA']])
wire(d, 'SCL', [R('D22'), (142, R('D22')[1]), (142, 170), m['SCL']])
wire(d, 'MOSI', [R('D23'), (146, R('D23')[1]), (146, 177), m['MOSI']])
wire(d, 'STOP', [L('D32'), (37, L('D32')[1]), (37, 157), (41, 157), s1a])
wire(d, 'GND', [L('GND'), (39, L('GND')[1]), (39, 155), (49, 155), s1b])
wire(d, 'VAN_RX', [L('D34'), (25, L('D34')[1]), (25, 160), (78, 160), (78, 165), van['RX']])
wire(d, 'GND', [v_pad['GND'], (160, 193), (77, 193), (77, 175), van['GND']])
wire(d, '+3V3', [v_pad['+3V3'], (164, 195), (75, 195), (75, 180), van['3V3']])
wire(d, 'GND', [o_pad['GND'], (266, 160), (266, 148), oled['GND']])
wire(d, '+3V3', [o_pad['+3V3'], (270, 166), (270, 154), oled['VCC']])
wire(d, 'SDA', [o_pad['SDA'], (278, 172), (278, 166), oled['SDA']])
wire(d, 'SCL', [o_pad['SCL'], (274, 179), (274, 160), oled['SCL']])
wire(d, 'GND', [o_pad['GND'], (288, 160), (288, 184), (336, 184), (336, 145), imu['GND']])
wire(d, '+3V3', [o_pad['+3V3'], (286, 166), (286, 186), (338, 186), (338, 151), imu['+3V3']])
wire(d, 'SDA', [o_pad['SDA'], (284, 172), (284, 188), (340, 188), (340, 157), imu['SDA']])
wire(d, 'SCL', [o_pad['SCL'], (282, 179), (282, 190), (342, 190), (342, 163), imu['SCL']])
wire(d, 'K', [kr['K'], (266, kr['K'][1]), (266, 50), (272, 50)])
wire(d, 'VBENCH', [(318, 50), (392, 50), (392, 62), (294, 62), (294, plus[1]), plus])
wire(d, 'VBENCH', [kr['VBENCH'], (276, kr['VBENCH'][1]), (276, 62), (293.99, 62)])
wire(d, 'GND', [kr['GND'], (272, kr['GND'][1]), (272, 124), (minus[0], 124), minus])

# --- Tabella dei fili tra le basette ---------------------------------------------------
rows = [('W1', 'RX_3V3', f'-A1 RX2 (GPIO{PINS["kKwpRx"]})', 'basetta 1 RX'),
        ('W2', 'TX_INV', f'-A1 TX2 (GPIO{PINS["kKwpTx"]})', 'basetta 1 TX'),
        ('W3', '+5V', '-A1 VIN (5 V da USB)', 'basetta 1 +5V'),
        ('W4', '+3V3', '-A1 3V3', 'basetta 1 +3V3'),
        ('W5', 'GND', '-A1 GND (lato destro)', 'basetta 1 GND'),
        ('W6', '+3V3', '-A1 3V3 (con W4)', 'basetta 3 3V3'),
        ('W7', 'GND', '-A1 GND (con W5)', 'basetta 3 GND'),
        ('W8', 'CS', f'-A1 D{PINS["kSdCs"]}', 'basetta 3 CS'),
        ('W9', 'SCK', f'-A1 D{PINS["kSck"]}', 'basetta 3 SCK'),
        ('W10', 'MISO', f'-A1 D{PINS["kMiso"]}', 'basetta 3 MISO'),
        ('W11', 'SDA', f'-A1 D{PINS["kSda"]}', 'basetta 3 SDA'),
        ('W12', 'SCL', f'-A1 D{PINS["kScl"]}', 'basetta 3 SCL'),
        ('W13', 'MOSI', f'-A1 D{PINS["kMosi"]}', 'basetta 3 MOSI'),
        ('W14', 'STOP', f'-A1 D{PINS["kStopPin"]}', '-S1 contatto 1'),
        ('W15', 'GND', '-A1 GND (lato sinistro)', '-S1 contatto 2'),
        ('W16', 'GND', 'basetta 3 GND (OLED)', '-A4 GND'),
        ('W17', '+3V3', 'basetta 3 VCC (OLED)', '-A4 VCC'),
        ('W18', 'SDA', 'basetta 3 SDA (OLED)', '-A4 SDA'),
        ('W19', 'SCL', 'basetta 3 SCL (OLED)', '-A4 SCL'),
        ('W20', 'GND', 'basetta 3 GND (con W16)', 'basetta 4 GND'),
        ('W21', '+3V3', 'basetta 3 VCC (con W17)', 'basetta 4 3V3'),
        ('W22', 'SDA', 'basetta 3 SDA (con W18)', 'basetta 4 SDA'),
        ('W23', 'SCL', 'basetta 3 SCL (con W19)', 'basetta 4 SCL'),
        ('W24', 'K', 'basetta 1 K', '-R3 capo 1'),
        ('W25', 'VBENCH', '-R3 capo 2', '-G1 +'),
        ('W26', 'VBENCH', 'basetta 1 VBENCH', '-G1 +'),
        ('W27', 'GND', 'basetta 1 GND (lato K)', '-G1 −'),
        ('W28', 'VAN_RX', f'-A1 D{PINS["kVanRx"]} (solo ingresso)', '-A6 RX'),
        ('W29', 'GND', 'basetta 3 GND (VAN)', '-A6 GND'),
        ('W30', '+3V3', 'basetta 3 3V3 (VAN)', '-A6 3V3'),
        ('W31', 'VAN', '-A6 CANH/CANL', '-X3, poi quadro: dopo D-022')]
TX0, TY0 = 25, 208
d.text(TX0, TY0 - 4, 'FILI TRA LE BASETTE E I MODULI (saldati, nessun morsetto)', 3.3, bold=True)
for i, (w, net, a, b) in enumerate(rows):
    col, r = divmod(i, 16)
    x, y = TX0 + col * 103, TY0 + 1 + r * 4.3
    d.raw(f'<line x1="{x}" y1="{y - 1}" x2="{x + 6}" y2="{y - 1}" stroke="{C[net]}" stroke-width="1.8"/>')
    d.text(x + 8, y, f'{w}  {a} → {b}  ({NAMES[net]})', 2.3)
d.text(25, 30.5, 'Basette (millefori MC01009 72×47 mm): 1 K-line KL-001 rev F a fili volanti · 2 ESP32 HW-394 · 3 RTC DS3231 + MicroSD · '
               '4 IMU (ritaglio) · modulo VAN -A6 con fili. Fili sottili = collegamenti interni; pallino = giunzione saldata; incrocio senza pallino = nessun contatto.', 2.2)
d.notes(292, 197, 'SEQUENZA E PRECAUZIONI', [
    '1 Tutto spento: saldare, poi controllare al tester continuità',
    '  e assenza di ponti, soprattutto sui piedini SOIC di U1.',
    '2 Ingombri reali di RTC e MicroSD da verificare sulla basetta 3.',
    '3 Prima USB da sola: VIN 4,75-5,25 V, 3V3 3,2-3,4 V.',
    '4 Alimentatore 12,0 V, limite 0,10 A, poi uscita accesa.',
    '5 Spegnere in ordine inverso. Mai 12 V su ESP32 o su 3V3.',
    '6 W4/W6, W5/W7, W16…W19/W20…W23: due fili sullo stesso punto.',
    '7 In auto: alimentazione HW-AUTO-POWER (non ancora posseduta).',
    '8 IMU solo 3,3 V; piedini DIL-24 dal manuale ST prima di saldare.',
    '9 VAN -A6: solo ricezione su GPIO34; prove 1-4 D-022 a banco,',
    '  collegamento al quadro solo dopo la prova 5 (punto identificato).',
], h=2.3, step=3.6)
d.title_block(title=['Data Logger completo', 'a banco, illustrato'], subtitle='Data Logger',
              doc_type='Schema illustrativo', status='PROPOSTO · NON COLLAUDATO',
              code='C3AI-DL-EL-004', rev='A', date='22/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione: quattro basette con fili saldati, IMU e VAN illustrati (D-042)', '22/10/2026')])
out = ROOT / 'disegni/sorgenti/DL-EL-004_logger-completo-millefori.svg'
out.write_text(d.svg('Collegamenti illustrati del Data Logger completo a banco su millefori; posizioni indicative.'),
               encoding='utf-8')
print(out)
