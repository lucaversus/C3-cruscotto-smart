"""Collegamenti illustrati della prova a banco K-line (C3AI-DL-KL-002).

Rev. A: ESP32 HW-394, modulo KL-001 rev F su millefori (KL-003), alimentatore da banco e
resistenza R3 del simulatore, disegnati come appaiono. Disegno illustrativo a complemento
dello schema elettrico IEC KL-001 (D-024), che resta il riferimento tecnico.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

C = {'GND': '#000000', '+5V': '#d00000', '+3V3': '#ff8c00', 'TX_INV': '#c8a000', 'RX_3V3': '#008000',
     'VBENCH': '#d040a0', 'K': '#0040d0'}


def box(d, x, y, w, h, fill, rx=2, stroke='#000', sw=0.4):
    d.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def label(d, x, y, text, h=2.6, anchor='middle', bold=False, color='#000'):
    weight = ' font-weight="bold"' if bold else ''
    d.raw(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{h}" text-anchor="{anchor}" fill="{color}"{weight} '
          f'font-family="Arial, sans-serif">{text}</text>')


def wire(d, net, pts, width=1.6):
    path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    d.raw(f'<polyline points="{path}" fill="none" stroke="{C[net]}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y in (pts[0], pts[-1]):
        d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.2" fill="{C[net]}" stroke="#000" stroke-width="0.25"/>')


d = Sheet('C3AI-DL-KL-002 rev A — K-line, collegamenti illustrati della prova a banco')
d.frame()
d.text(25, 20, 'PROVA A BANCO DEL MODULO K-LINE — COLLEGAMENTI ILLUSTRATI', 5, bold=True)
d.text(25, 25, 'Disegno illustrativo: posizioni dei piedini indicative, usare sempre la serigrafia dei moduli. Riferimento tecnico: '
               'schema KL-001 rev F; montaggio: KL-003. Nessun collegamento al veicolo.', 2.5)

# --- ESP32 HW-394 ---------------------------------------------------------------
ex, ey, ew, eh = 30, 50, 62, 120
box(d, ex, ey, ew, eh, '#1f3a6e', rx=3)
box(d, ex + 14, ey + 6, 34, 40, '#b8b8b8', rx=1)
box(d, ex + 17, ey + 9, 28, 30, '#d8d8d8', rx=1)
label(d, ex + 31, ey + 25, 'ESP32', 4, bold=True)
label(d, ex + 31, ey + 30, 'ESP-32D', 2.6)
box(d, ex + 23, ey + eh - 6, 16, 8, '#a0a0a0', rx=1)
label(d, ex + 31, ey + eh + 6, 'USB → PC', 2.6, bold=True)
label(d, ex + ew / 2, ey - 3, '-A1  ESP32 HW-394 (HW-ESP32)', 3.4, bold=True)
used = {}
for side, names in (('L', ['EN', 'VP', 'VN', 'D34', 'D35', 'D32', 'D33', 'D25', 'D26', 'D27', 'D14', 'D12', 'D13', 'GND', 'VIN']),
                    ('R', ['D23', 'D22', 'TX0', 'RX0', 'D21', 'D19', 'D18', 'D5', 'TX2', 'RX2', 'D4', 'D2', 'D15', 'GND', '3V3'])):
    for i, n in enumerate(names):
        y = ey + 52 + i * 4.4
        x = ex + 4 if side == 'L' else ex + ew - 4
        hot = n in ('VIN', 'GND', '3V3', 'TX2', 'RX2') and not (n == 'GND' and side == 'L')
        d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.3" fill="{"#ffd700" if hot else "#c0c0c0"}" stroke="#000" stroke-width="0.2"/>')
        label(d, x + (3 if side == 'L' else -3), y + 1, n, 2.2, 'start' if side == 'L' else 'end', hot, '#ffffff')
        if hot:
            used[n] = (x, y)
label(d, ex + ew + 4, ey + 46, 'TX2 = GPIO17', 2.4, 'start', True)
label(d, ex + ew + 4, ey + 49.5, 'RX2 = GPIO16', 2.4, 'start', True)

# --- Modulo KL-001 su millefori ---------------------------------------------------
mx, my, mw, mh = 150, 70, 90, 62
box(d, mx, my, mw, mh, '#e9d8a6', rx=2)
for i in range(16):
    for j in range(10):
        d.raw(f'<circle cx="{mx + 8 + i * 5:.2f}" cy="{my + 8 + j * 5:.2f}" r="0.8" fill="#c08040"/>')
box(d, mx + 38, my + 20, 18, 14, '#303030', rx=1)
label(d, mx + 47, my + 28, 'U1', 2.6, bold=True, color='#ffffff')
d.raw(f'<path d="M{mx + 70} {my + 16} a4 4 0 0 1 0 10 z" fill="#202020"/>')
label(d, mx + mw / 2, my - 3, '-A2  Modulo K-line KL-001 rev F (montaggio KL-003)', 3.4, bold=True)
x1 = {}
box(d, mx - 6, my + 6, 8, 50, '#2e8b57', rx=1)
for i, (n, net) in enumerate([('1 RX', 'RX_3V3'), ('2 TX', 'TX_INV'), ('3 +5V', '+5V'), ('4 +3V3', '+3V3'), ('5 GND', 'GND')]):
    y = my + 11 + i * 10
    d.raw(f'<circle cx="{mx - 2:.2f}" cy="{y:.2f}" r="2.2" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
    label(d, mx + 3, y + 1, n, 2.4, 'start', True)
    x1[net] = (mx - 2, y)
label(d, mx - 10, my + 4, '-X1', 3, 'end', True)
x2 = {}
box(d, mx + mw - 2, my + 16, 8, 30, '#2e8b57', rx=1)
for i, (n, net) in enumerate([('1 K', 'K'), ('2 VBENCH', 'VBENCH'), ('3 GND', 'GND')]):
    y = my + 21 + i * 10
    d.raw(f'<circle cx="{mx + mw + 2:.2f}" cy="{y:.2f}" r="2.2" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
    label(d, mx + mw - 3, y + 1, n, 2.4, 'end', True)
    x2[net] = (mx + mw + 2, y)
label(d, mx + mw + 8, my + 14, '-X2', 3, 'start', True)

# --- Alimentatore da banco ----------------------------------------------------------
px, py, pw, ph = 290, 140, 70, 48
box(d, px, py, pw, ph, '#d8d8d8', rx=3)
box(d, px + 6, py + 6, 34, 14, '#102010', rx=1)
label(d, px + 23, py + 16, '12.0 V', 6, bold=True, color='#40ff40')
box(d, px + 6, py + 23, 34, 8, '#102010', rx=1)
label(d, px + 23, py + 29, '0.10 A max', 3.6, bold=True, color='#ff4040')
for k, (cx, txt) in enumerate(((px + 50, 'V'), (px + 62, 'A'))):
    d.raw(f'<circle cx="{cx}" cy="{py + 14}" r="4.5" fill="#404040" stroke="#000" stroke-width="0.3"/>')
    label(d, cx, py + 23, txt, 2.4, bold=True)
plus, minus = (px + 50, py + 38), (px + 62, py + 38)
d.raw(f'<circle cx="{plus[0]}" cy="{plus[1]}" r="3.2" fill="#d00000" stroke="#000" stroke-width="0.3"/>'
      f'<circle cx="{minus[0]}" cy="{minus[1]}" r="3.2" fill="#202020" stroke="#000" stroke-width="0.3"/>')
label(d, plus[0], plus[1] + 7.5, '+', 4, bold=True)
label(d, minus[0], minus[1] + 7.5, '−', 4, bold=True)
label(d, px + pw / 2, py - 3, '-G1  Alimentatore da banco (HW-BENCH-PSU)', 3.4, bold=True)

# --- R3 simulatore: 510 ohm 1 W ---------------------------------------------------------
rx, ry = 300, 92
d.raw(f'<line x1="{rx - 10}" y1="{ry}" x2="{rx + 40}" y2="{ry}" stroke="#808080" stroke-width="0.8"/>')
box(d, rx, ry - 4.5, 30, 9, '#8fb8e8', rx=4)
for i, col in enumerate(('#00a000', '#8b4513', '#000000', '#000000', '#8b4513')):
    d.raw(f'<rect x="{rx + 5 + i * 4.5:.2f}" y="{ry - 4.5}" width="1.6" height="9" fill="{col}"/>')
label(d, rx + 15, ry - 7, '-R3  510 Ω 1 W 1% — simulatore della linea', 2.8, bold=True)
label(d, rx + 15, ry + 10, 'solo per il banco, non montata sul modulo (D-018)', 2.4)
r3a, r3b = (rx - 10, ry), (rx + 40, ry)

# --- Fili ---------------------------------------------------------------------------
wire(d, 'RX_3V3', [x1['RX_3V3'], (130, x1['RX_3V3'][1]), (130, used['RX2'][1]), used['RX2']])
wire(d, 'TX_INV', [x1['TX_INV'], (125, x1['TX_INV'][1]), (125, used['TX2'][1]), used['TX2']])
wire(d, '+3V3', [x1['+3V3'], (120, x1['+3V3'][1]), (120, used['3V3'][1]), used['3V3']])
wire(d, 'GND', [x1['GND'], (115, x1['GND'][1]), (115, used['GND'][1]), used['GND']])
vin = used['VIN']
wire(d, '+5V', [x1['+5V'], (135, x1['+5V'][1]), (135, 182), (vin[0] - 8, 182), (vin[0] - 8, vin[1]), vin])
wire(d, 'K', [x2['K'], (r3a[0] - 6, x2['K'][1]), (r3a[0] - 6, r3a[1]), r3a])
wire(d, 'VBENCH', [r3b, (375, r3b[1]), (375, 125), (px - 6, 125), (px - 6, plus[1]), plus])
wire(d, 'VBENCH', [x2['VBENCH'], (270, x2['VBENCH'][1]), (270, 125), (px - 6.01, 125)])
wire(d, 'GND', [x2['GND'], (265, x2['GND'][1]), (265, 205), (minus[0], 205), minus])

# --- Tabella collegamenti e note ------------------------------------------------------
rows = [('W1', 'RX_3V3', '-X1:1 RX', '-A1 RX2 (GPIO16)'), ('W2', 'TX_INV', '-X1:2 TX', '-A1 TX2 (GPIO17)'),
        ('W3', '+5V', '-X1:3 +5V', '-A1 VIN (5 V da USB)'), ('W4', '+3V3', '-X1:4 +3V3', '-A1 3V3'),
        ('W5', 'GND', '-X1:5 GND', '-A1 GND'), ('W6', 'K', '-X2:1 K', '-R3 capo 1'),
        ('W7', 'VBENCH', '-R3 capo 2', '-G1 +'), ('W8', 'VBENCH', '-X2:2 VBENCH', '-G1 +'),
        ('W9', 'GND', '-X2:3 GND', '-G1 −')]
TX0, TY0 = 25, 215
d.text(TX0, TY0 - 3, 'COLLEGAMENTI', 3.5, bold=True)
for i, (w, net, a, b) in enumerate(rows):
    y = TY0 + 2 + i * 4.4
    d.raw(f'<line x1="{TX0}" y1="{y - 1}" x2="{TX0 + 8}" y2="{y - 1}" stroke="{C[net]}" stroke-width="1.8"/>')
    d.text(TX0 + 11, y, f'{w}   {a}  →  {b}   ({net})', 2.6)
d.notes(200, 212, 'SEQUENZA E PRECAUZIONI', [
    '1 Tutto spento: montare, controllare continuità e assenza di corti (KL-003).',
    '2 Misurare VIN dell\'ESP32 con USB collegato: deve essere 4,75-5,25 V.',
    '3 Alimentatore: impostare 12,0 V e limite di corrente basso (es. 0,10 A) a uscita spenta.',
    '4 Accendere prima la logica (USB), poi l\'alimentatore; spegnere in ordine inverso.',
    '5 Le masse di ESP32 e alimentatore si uniscono nel modulo (X1:5 e X2:3).',
    '6 Mai 12 V su un piedino dell\'ESP32 o sul 3V3. Nessun collegamento al veicolo.',
], h=2.5, step=4.0)
d.title_block(title=['K-line, banco', 'illustrato'], subtitle='Data Logger',
              doc_type='Schema illustrativo', status='PROPOSTO · NON COLLAUDATO',
              code='C3AI-DL-KL-002', rev='A', date='22/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione: moduli illustrati a complemento di KL-001 rev F', '22/10/2026')])
out = ROOT / 'data-logger/docs/kline-collegamenti-illustrati.svg'
out.write_text(d.svg('Collegamenti illustrati della prova a banco del modulo K-line; posizioni dei piedini indicative.'),
               encoding='utf-8')
print(out)
