"""Studio d'ingombro della scheda madre (C3AI-CR-PL-001), D-029…D-031, D-044, D-045, D-061.

Rev. F (D-061): contorno v3 dell'utente, 15 mm più in basso (bordo inferiore a y −6, raccordi R10),
fori invariati; -J1 Micro-Fit verticale subito sotto la ventola, nella parte più profonda del vano.

Rev. E: posizione degli interruttori e della scheda S3 dall'assieme 3D dell'utente
(cruscotto/meccanica/assieme-cruscotto.step): pulsanti originali in (±84,3, 32,2) mm nelle
coordinate del contorno; S3 137 × 84 centrata in x, da y −9,5 a 74,5; distanza tra il retro
della S3 e la scheda madre circa 9,9 mm; estremità del pulsante a circa 6,3 mm dalla scheda.
Rev. D (D-046): componenti che scaldano di più sulla faccia interna (verso la S3), attorno
alla ventola; montaggio a mano, solo il circuito stampato prodotto.
Rev. C (D-045): contorno e fori dal disegno dell'utente cruscotto/meccanica/scheda-madre-contorno.dxf
(178,7 × 74 mm, 6 fori Ø3), letto direttamente dal DXF; foro centrale con ventola che soffia
verso la S3 montata davanti; ai due estremi gli interruttori azionati dai pulsanti del quadro
originale; connettore -J1 Micro-Fit 24 vie (D-044). Il generatore controlla che ogni zona stia
dentro il contorno e non si sovrapponga ad altre zone, ai fori o alla ventola.
Rev. B: IMU LSM6DSO. Rev. A: contorno della scheda S3 137 × 84 mm.
Scala 1,5:1, vista dal lato componenti. Non è un circuito stampato.
"""
from pathlib import Path
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

DXF = ROOT / 'cruscotto/meccanica/scheda-madre-contorno.dxf'
SCALE = 1.5
OX, OY = 30.0, 44.0           # posizione sul foglio dell'angolo (xmin, ymax) del contorno


def read_dxf(path):
    """Entità LINE, ARC e CIRCLE della sezione ENTITIES (coordinate in mm)."""
    lines = path.read_text(encoding='latin-1').splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    out, cur, inside = [], None, False
    for code, value in pairs:
        if code == '2' and value == 'ENTITIES':
            inside = True
        if not inside:
            continue
        if code == '0':
            if cur:
                out.append(cur)
            cur = {'type': value} if value in ('LINE', 'ARC', 'CIRCLE') else None
            if value == 'ENDSEC':
                break
        elif cur is not None and code in ('10', '20', '11', '21', '40', '50', '51'):
            cur[code] = float(value)
    return out


ENT = read_dxf(DXF)
HOLES = [(e['10'], e['20'], e['40']) for e in ENT if e['type'] == 'CIRCLE']
YMIN = min(e.get('21', e['20']) for e in ENT if e['type'] == 'LINE')
YMAX = max(e.get('21', e['20']) for e in ENT if e['type'] == 'LINE')


def P(x, y):
    """Coordinate del DXF (mm, y verso l'alto) → foglio (y verso il basso)."""
    return OX + (x - XMIN) * SCALE, OY + (YMAX - y) * SCALE


def outline_points():
    """Contorno come poligono chiuso: segmenti e archi campionati, concatenati per vicinanza."""
    segs = []
    for e in ENT:
        if e['type'] == 'LINE':
            segs.append([(e['10'], e['20']), (e['11'], e['21'])])
        elif e['type'] == 'ARC':
            a0, a1 = e['50'], e['51']
            if a1 < a0:
                a1 += 360
            n = max(4, int((a1 - a0) / 5))
            segs.append([(e['10'] + e['40'] * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                          e['20'] + e['40'] * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)])
    poly = segs.pop(0)
    while segs:
        end = poly[-1]
        best = min(range(len(segs)), key=lambda i: min(math.dist(end, segs[i][0]), math.dist(end, segs[i][-1])))
        s = segs.pop(best)
        if math.dist(end, s[-1]) < math.dist(end, s[0]):
            s = s[::-1]
        assert math.dist(end, s[0]) < 0.01, 'contorno non chiuso'
        poly += s[1:]
    return poly


POLY = outline_points()
XMIN, XMAX = min(x for x, _ in POLY), max(x for x, _ in POLY)


def inside(x, y):
    hit = False
    for (x1, y1), (x2, y2) in zip(POLY, POLY[1:] + POLY[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


FAN_C, FAN_HOLE, FAN_SIZE = (0.0, 46.0), 38.0, 40.0      # ventola 40 × 40, foro Ø38
# Interruttori sotto i pulsanti originali: assieme 3D, pulsanti in (±84,28, 44,16) mm, scheda
# madre traslata di 12 mm in y → (±84,28, 32,16) nelle coordinate del contorno.
SW = [(-84.28, 32.16), (84.28, 32.16)]
SW_SIZE = 6.0                                             # tattile 6 × 6 sotto il pulsante (ruotato di circa 21°)
SW_CHECK = 5.0                                            # area verificata dentro il contorno
S3_BOX = (-68.5, 74.5, 137.0, 84.0)                       # S3 nell'assieme: x sinistra, y alta, larghezza, altezza
KEEP = 3.5                                                # zona libera attorno ai fori di fissaggio

# Zone: sigla, descrizione, x sinistra, y alta (mm del DXF), larghezza, altezza, facoltativa
ZONES = [
    ('-J1', 'Micro-Fit 3.0 2×12 verticale (D-061)', -21, 25, 42, 10, False),
    ('-X2', 'J2 verso S3 (P1, P2, P6)', -17, 81, 34, 8, False),
    ('-U1…U3', 'Ingresso 12 V protetto', -73, 42, 26, 20, False),
    ('-U4', 'Buck 12→5 V 3 A', -45, 41, 22, 16, False),
    ('-U5', 'LDO 3,3 V + sempre acceso', -45, 23, 16, 10, False),
    ('-U6', 'Front-end WROOM-32E-H4/H8', -43, 70, 18, 25.5, False),
    ('-U9', 'IMU LSM6DSO', -62, 60, 12, 10, False),
    ('-K1/K2', 'Relè audio + driver', 38, 40, 34, 14, False),
    ('-U7', 'VAN SN65HVD230', 23, 40, 12, 9, False),
    ('-U8', 'K-line KL-001 (SMD)', 23, 26, 22, 14, False),
    ('-U11', 'USB-C, CH340C, BOOT/EN', 47, 24, 24, 12, False),
    ('-X3', 'Ventola + 2 NTC', 23, 52, 12, 8, False),
    ('-U10', 'RTC DS3231 + CR2032', 39, 60, 24, 20, True),
    ('-X4', 'MicroSD', 23, 73, 15, 15, True),
]
HOT = {'-U1…U3', '-U4', '-U5', '-U6'}   # componenti più caldi: faccia interna, nel flusso della ventola (D-046)
AREAS = {'-J1': 420, '-X2': 272, '-U1…U3': 520, '-U4': 352, '-U5': 160, '-U6': 459, '-U9': 120, '-K1/K2': 476,
         '-U7': 108, '-U8': 308, '-U11': 288, '-X3': 96, '-U10': 480, '-X4': 225}


def rect_ok(name, x, y, w, h):
    """Dentro il contorno, fuori dai fori (con zona libera), dalla ventola e dagli interruttori."""
    errors = []
    pts = [(x + w * i / 4, y - h * j / 4) for i in range(5) for j in range(5)]
    if not all(inside(px, py) for px, py in pts):
        errors.append('fuori dal contorno')
    for hx, hy, r in HOLES:
        cx, cy = min(max(hx, x), x + w), min(max(hy, y - h), y)
        if math.dist((cx, cy), (hx, hy)) < r + KEEP:
            errors.append(f'troppo vicino al foro ({hx:g}, {hy:g})')
    fx, fy = FAN_C
    if abs(fx - (x + w / 2)) < (FAN_SIZE + w) / 2 and abs(fy - (y - h / 2)) < (FAN_SIZE + h) / 2:
        errors.append('sopra la ventola')
    for sx, sy in SW:
        if abs(sx - (x + w / 2)) < (SW_SIZE + w) / 2 and abs(sy - (y - h / 2)) < (SW_SIZE + h) / 2:
            errors.append('sopra un interruttore')
    return [f'{name}: {e}' for e in errors]


def overlaps():
    errs = []
    for i, a in enumerate(ZONES):
        for b in ZONES[i + 1:]:
            if a[2] < b[2] + b[4] and b[2] < a[2] + a[4] and a[3] - a[5] < b[3] and b[3] - b[5] < a[3]:
                errs.append(f'{a[0]} sovrapposta a {b[0]}')
    return errs


problems = [e for z in ZONES for e in rect_ok(z[0], *z[2:6])] + overlaps()
for sx, sy in SW:
    problems += [e for e in rect_ok('interruttore', sx - SW_CHECK / 2, sy + SW_CHECK / 2, SW_CHECK, SW_CHECK)
                 if 'interruttore' not in e.split(': ')[1]]
assert not problems, '\n'.join(problems)

d = Sheet('C3AI-CR-PL-001 rev E — Scheda madre, studio d\'ingombro')
d.frame()
d.text(25, 20, 'SCHEDA MADRE — STUDIO D\'INGOMBRO SUL CONTORNO DEFINITIVO (SCALA 1,5:1)', 5, bold=True)
d.text(25, 25, 'Contorno e fori dal disegno dell\'utente (scheda-madre-contorno.dxf v3, 178,7 × 89 mm). Zone con ingombri stimati, '
               'controllate dal generatore: non è un circuito stampato.', 2.5)

pts = ' '.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in POLY)
d.raw(f'<polygon points="{pts}" fill="#f6f9fc" stroke="#000" stroke-width="0.7"/>')
for hx, hy, r in HOLES:
    cx, cy = P(hx, hy)
    d.circle(cx, cy, r * SCALE, width=0.35)
    d.circle(cx, cy, (r + KEEP) * SCALE, width=0.2)

# Scheda S3 davanti alla scheda madre (posizione dall'assieme 3D), solo contorno.
sx0, sy0 = P(S3_BOX[0], S3_BOX[1])
d.rect(sx0, sy0, S3_BOX[2] * SCALE, S3_BOX[3] * SCALE, width=0.4, dash='6 2 1 2')
d.text(sx0 + 2, sy0 + S3_BOX[3] * SCALE - 2, 'contorno scheda S3 davanti (assieme 3D)', 2.4, 'start', True)

# Ventola: foro e ingombro del telaio 40 × 40 con fori di fissaggio a 32 mm.
fx, fy = P(*FAN_C)
d.rect(fx - FAN_SIZE / 2 * SCALE, fy - FAN_SIZE / 2 * SCALE, FAN_SIZE * SCALE, FAN_SIZE * SCALE, width=0.3, dash='3 1.5')
d.raw(f'<circle cx="{fx:.2f}" cy="{fy:.2f}" r="{FAN_HOLE / 2 * SCALE:.2f}" fill="#ffffff" stroke="#000" stroke-width="0.5"/>')
for dx in (-16, 16):
    for dy in (-16, 16):
        d.circle(fx + dx * SCALE, fy + dy * SCALE, 1.6 * SCALE, width=0.3)
d.text(fx, fy - 3, 'FORO Ø38', 3, 'middle', True)
d.text(fx, fy + 2, 'ventola 40 × 40 sul retro,', 2.3, 'middle')
d.text(fx, fy + 5.5, 'soffia verso la S3', 2.3, 'middle')

for i, (sx, sy) in enumerate(SW, 1):
    x, y = P(sx - SW_SIZE / 2, sy + SW_SIZE / 2)
    d.rect(x, y, SW_SIZE * SCALE, SW_SIZE * SCALE, width=0.4, fill='#fde9c8')
    d.text(x + SW_SIZE * SCALE / 2, y - 2, f'-S{i}', 3, 'middle', True)

for ref, label, x, y, w, h, optional in ZONES:
    zx, zy = P(x, y)
    d.rect(zx, zy, w * SCALE, h * SCALE, width=0.35, dash='3 1.5' if optional else None,
           fill='#fbe3d6' if ref in HOT else '#eef4fb' if not optional else 'none')
    d.text(zx + 1.2, zy + 4, ref, 2.6, 'start', True)
    d.text(zx + 1.2, zy + 7.5, label, 1.9)
    d.text(zx + 1.2, zy + 10.5, f'{w:g} × {h:g}', 1.9)

# Quote principali
x0, y1 = P(XMIN, YMIN)
x1, _ = P(XMAX, YMIN)
_, y0 = P(XMIN, YMAX)
d.line((x0, y1 + 6), (x1, y1 + 6), width=0.25)
d.line((x0, y1 + 2), (x0, y1 + 8), width=0.25)
d.line((x1, y1 + 2), (x1, y1 + 8), width=0.25)
d.text((x0 + x1) / 2, y1 + 5, f'{XMAX - XMIN:.1f}'.replace('.', ','), 3, 'middle')
d.line((x0 - 5, y0), (x0 - 5, y1), width=0.25)
d.text(x0 - 6, (y0 + y1) / 2, f'{YMAX - YMIN:.1f}'.replace('.', ','), 3, 'middle', rotate=-90)
d.text(x0, y1 + 12, 'Fori di fissaggio Ø3 (6): cerchio esterno = zona libera di 3,5 mm. Zone tratteggiate: facoltative.', 2.5)
d.raw(f'<rect x="{x0:.2f}" y="{y1 + 15:.2f}" width="6" height="3.5" fill="#fbe3d6" stroke="#000" stroke-width="0.2"/>')
d.text(x0 + 8, y1 + 18, 'Componenti più caldi: faccia interna (verso la S3), nel flusso della ventola (D-046).', 2.5)

rows = []
core = opt = 0
for ref, label, *_rest, optional in ZONES:
    rows.append((ref, label[:28], f'{AREAS[ref]}', 'facolt.' if optional else 'base'))
    opt += AREAS[ref] if optional else 0
    core += 0 if optional else AREAS[ref]
board_area = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(POLY, POLY[1:] + POLY[:1]))) / 2
fan_area = math.pi * (FAN_HOLE / 2) ** 2
rows.append(('', 'Totale base (netto)', f'{core}', ''))
rows.append(('', 'Totale facoltative', f'{opt}', ''))
rows.append(('', 'Base × 1,5 (piste, distanze)', f'{round(core * 1.5)}', ''))
rows.append(('', 'Contorno meno foro ventola', f'{round(board_area - fan_area)}', ''))
TX = 316
d.text(TX, 46, 'BILANCIO DELLE AREE (mm²)', 3.5, bold=True)
d.parts_list(TX, 49, list(reversed(rows)), widths=(14, 44, 12, 14), heads=('Sigla', 'Zona', 'mm²', 'Tipo'))

d.notes(25, 214, 'NOTE', [
    '1  Vista dal lato verso la S3. Assieme 3D: retro della S3 a circa 9,9 mm dalla scheda madre (componenti della faccia',
    '   interna più bassi, con margine per il flusso dell’aria); connettori P1/P2/P6 della S3 da rilevare sul pezzo.',
    '2  Ventola 40 × 40 × 10 (12 V, D-031) sul lato opposto, aspira dal retro e soffia attraverso il foro verso la S3;',
    '   in alternativa 30 × 30 con foro Ø28. Distanza tra le schede da scegliere per il flusso d\'aria.',
    '3  -S1/-S2 sotto i pulsanti originali (assieme 3D): estremità del pulsante a circa 6,3 mm dalla scheda, quindi',
    '   interruttore tattile con pulsante alto circa 7 mm o prolunga; corsa da verificare.',
    '4  -J1 verticale sotto la ventola, al centro (D-061): la spina entra dal retro, servono circa 30-35 mm dietro la scheda. Antenna del front-end -U6 verso il bordo, senza rame.',
    '5  Supercondensatore di riserva (-C1, 36 × 24) non trova posto su questa faccia: retro o fuori scheda, da decidere.',
    '6  Montaggio a mano, si produce solo il circuito stampato (D-046): passivi da 0805, SOIC/SOT/TSSOP, moduli; niente',
    '   QFN, BGA, LGA (IMU su modulo con connettore). Distanza tra le schede da fissare simulando lo spessore nel 3D.',
], h=2.4, step=3.9)

d.title_block(title=['Scheda madre', 'studio d\'ingombro'], subtitle='Cruscotto digitale',
              doc_type='Disposizione (1,5:1)', status='PRELIMINARE · NON VERIFICATO',
              code='C3AI-CR-PL-001', rev='F', date='28/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione: contorno S3, zone e bilancio aree (D-029…D-031)', '21/10/2026'),
                         ('B', 'IMU LSM6DSO (HW-IMU-LSM6DSO) al posto di LSM6DS3', '22/10/2026'),
                         ('C', 'Contorno definitivo dal DXF dell\'utente, foro ventola, interruttori -S1/-S2, J1 24 vie (D-045)', '24/10/2026'),
                         ('D', 'Componenti caldi sulla faccia interna, montaggio a mano (D-046)', '24/10/2026'),
                         ('E', 'Interruttori e scheda S3 posizionati dall’assieme 3D', '24/10/2026'),
                         ('F', 'Contorno v3 (+15 mm in basso), J1 Micro-Fit verticale (D-061)', '28/10/2026')])
out = ROOT / 'disegni/sorgenti/CR-PL-001_scheda-madre-ingombro.svg'
out.write_text(d.svg('Studio d\'ingombro della scheda madre sul contorno definitivo; stime, non PCB.'), encoding='utf-8')
print(out, 'base', core, 'facoltative', opt, 'area utile', round(board_area - fan_area))
