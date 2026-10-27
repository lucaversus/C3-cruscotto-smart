"""Serigrafia della scheda madre per il montaggio a mano (D-046): sigle, pallini del piedino 1, nomi dei fili.

Uso (con il Python di KiCad, dopo tools/completa-sbroglio-scheda-madre.py):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" tools/serigrafia-scheda-madre.py [--pcb=<file>]
- Ogni sigla (R1, C3…) va nel primo posto libero attorno al suo componente: lontano dalle piazzole, dai contorni
  degli altri componenti, dalle altre scritte, dal bordo e dai fori; altezza 1,0 mm (0,8 mm se non c'è posto),
  tratto 0,15 mm, minimo consigliato dai produttori. Nei componenti grandi la sigla può stare sul corpo.
- Un pallino accanto al piedino 1 di circuiti integrati, transistor, moduli e connettori. Diodi, LED ed
  elettrolitici hanno già nella loro impronta la barra del catodo o il segno «+».
- Accanto alle piazzole dei fili saldati (D-059) e dei moduli il nome di ogni filo; titolo e lato su F e B.
I testi e i segni aggiunti da questo script hanno il prefisso «SERIGRAFIA» nel nome interno e vengono rifatti
a ogni esecuzione. Controllare poi con il DRC di KiCad (avvisi silk_*).
"""
from pathlib import Path
import math
import sys

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb'
for a in sys.argv[1:]:
    if a.startswith('--pcb='):
        PCB = Path(a[6:])
mm, nm = pcbnew.FromMM, pcbnew.ToMM
TAG = 'SERIGRAFIA'
PAD_GAP = 0.2       # distanza dalla serigrafia alle piazzole
TEXT_GAP = 0.15     # distanza tra scritte e contorni
EDGE_GAP = 0.4      # distanza dal bordo e dai fori
SIZES = (1.0, 0.8)  # sotto 0,8 mm la scritta non si legge più dopo la stampa
STROKE = 0.15
# Nomi dei fili e dei piedini dei moduli, in ordine di piedino (schema C3AI-CR-EL-002/004/005).
LABELS = {
    'J4': ['GND', '12V', 'RPM', 'PWM'],          # ventola Delta: nero, rosso, blu, giallo
    'J5': ['NTC', 'GND'],
    'J7': ['3V3', 'CS', 'MOSI', 'CLK', 'MISO', 'GND'],
    'J8': ['3V3', 'GND', 'RX', 'TX'],
    'J9': ['CANH', 'CANL'],
    'J10': ['5V', 'TXD', 'RXD', 'GND'],
    'J11': ['IO19', 'IO11', 'IO12', 'IO13'],
    'J12': ['SPK', 'SPK'],
}
PIN1 = ('U', 'Q', 'J', 'K')   # prefissi delle sigle con pallino sul piedino 1

board = pcbnew.LoadBoard(str(PCB))
SILK = {'F': pcbnew.F_SilkS, 'B': pcbnew.B_SilkS}
CU = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}

# Via i segni aggiunti da un'esecuzione precedente.
REMOVED = []
for d in list(board.GetDrawings()):
    if d.GetClass() in ('PCB_TEXT', 'PCB_SHAPE') and d.GetLayer() in SILK.values():
        if (d.GetClass() == 'PCB_TEXT' and d.GetText().startswith('\u200b')) or \
                (d.GetClass() == 'PCB_SHAPE' and d.GetWidth() == mm(0.151)):
            board.Remove(d)
            REMOVED.append(d)

outline = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(outline, False)
inner = pcbnew.SHAPE_POLY_SET(outline)
inner.Deflate(mm(EDGE_GAP), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, mm(0.01))


def box(b, grow=0.0):
    return (nm(b.GetLeft()) - grow, nm(b.GetTop()) - grow, nm(b.GetRight()) + grow, nm(b.GetBottom()) + grow)


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def inside_board(b):
    x0, y0, x1, y1 = b
    pts = [(x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2),
           (x1, (y0 + y1) / 2)]
    return all(inner.Contains(pcbnew.VECTOR2I(mm(x), mm(y))) for x, y in pts)


# Ostacoli per faccia: piazzole, contorni serigrafati delle impronte, fori senza rame.
OBST = {'F': [], 'B': []}
for fp in board.GetFootprints():
    for p in fp.Pads():
        th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        for s in ('F', 'B'):
            if th or p.IsOnLayer(CU[s]):
                OBST[s].append(box(p.GetBoundingBox(), PAD_GAP))
    for g in fp.GraphicalItems():
        for s in ('F', 'B'):
            if g.GetLayer() == SILK[s]:
                OBST[s].append(box(g.GetBoundingBox(), TEXT_GAP))
PLACED = {'F': [], 'B': []}


def free(s, b):
    return inside_board(b) and not any(overlap(b, o) for o in OBST[s]) and not any(overlap(b, o) for o in PLACED[s])


def side_of(fp):
    return 'B' if fp.IsFlipped() else 'F'


def body_box(fp):
    s = side_of(fp)
    c = fp.GetCourtyard(pcbnew.B_CrtYd if s == 'B' else pcbnew.F_CrtYd)
    if c.OutlineCount():
        return box(c.BBox())
    return box(fp.GetBoundingBox(False))


def try_text(text, s, cx, cy, size, angle):
    """Posiziona il testo centrato in (cx, cy); restituisce il riquadro se il posto è libero."""
    text.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    text.SetTextThickness(mm(STROKE))
    text.SetTextAngleDegrees(angle)
    text.SetPosition(pcbnew.VECTOR2I(mm(cx), mm(cy)))
    b = box(text.GetBoundingBox(), TEXT_GAP)
    return b if free(s, b) else None


def place_reference(fp):
    s = side_of(fp)
    ref = fp.Reference()
    ref.SetLayer(SILK[s])
    ref.SetMirrored(s == 'B')
    ref.SetVisible(True)
    x0, y0, x1, y1 = body_box(fp)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    big = (x1 - x0) * (y1 - y0) > 60
    for size in SIZES:
        cands = [(cx, cy, 0), (cx, cy, 90)] if big else []
        g = 0.2
        while g <= 4.0:
            h = size / 2 + g
            cands += [(cx, y0 - h, 0), (cx, y1 + h, 0), (x0 - h, cy, 90), (x1 + h, cy, 90),
                      (cx, y0 - h, 90), (cx, y1 + h, 90), (x0 - h, cy, 0), (x1 + h, cy, 0),
                      (x0 - h, y0 - h, 0), (x1 + h, y0 - h, 0), (x0 - h, y1 + h, 0), (x1 + h, y1 + h, 0)]
            g += 0.3
        for px, py, ang in cands:
            b = try_text(ref, s, px, py, size, ang)
            if b:
                PLACED[s].append(b)
                return True
    ref.SetVisible(False)  # nessun posto libero: la sigla resta nel disegno di montaggio
    return False


def add_text(s, txt, cx, cy, size, angle=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText('\u200b' + txt)  # segno invisibile: testo di questo script, rifatto a ogni esecuzione
    t.SetLayer(SILK[s])
    t.SetMirrored(s == 'B')
    b = try_text(t, s, cx, cy, size, angle)
    if b:
        board.Add(t)
        PLACED[s].append(b)
        return True
    return False


def add_dot(s, x, y, r=0.25):
    b = (x - r - TEXT_GAP, y - r - TEXT_GAP, x + r + TEXT_GAP, y + r + TEXT_GAP)
    if not free(s, b):
        return False
    c = pcbnew.PCB_SHAPE(board)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetCenter(pcbnew.VECTOR2I(mm(x), mm(y)))
    c.SetEnd(pcbnew.VECTOR2I(mm(x + r / 2), mm(y)))
    c.SetWidth(mm(0.151))   # larghezza di riconoscimento dei segni di questo script
    c.SetFilled(True)
    c.SetLayer(SILK[s])
    board.Add(c)
    PLACED[s].append(b)
    return True


def pin1_dot(fp):
    pads = {p.GetNumber(): p for p in fp.Pads()}
    p1 = pads.get('1') or pads.get('A1')
    if p1 is None:
        return False
    s = side_of(fp)
    px, py = nm(p1.GetPosition().x), nm(p1.GetPosition().y)
    hx = nm(p1.GetBoundingBox().GetWidth()) / 2
    hy = nm(p1.GetBoundingBox().GetHeight()) / 2
    x0, y0, x1, y1 = body_box(fp)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # prima dalla parte opposta al centro del componente, poi gli altri lati del piedino
    dirs = sorted([(-1, 0), (1, 0), (0, -1), (0, 1), (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)],
                  key=lambda d: d[0] * (cx - px) + d[1] * (cy - py))
    for extra in (0.45, 0.8, 1.2, 1.6):
        for dx, dy in dirs:
            if add_dot(s, px + dx * (hx + extra), py + dy * (hy + extra)):
                return True
    return False


def pad_labels(fp, names):
    s = side_of(fp)
    pads = sorted(fp.Pads(), key=lambda p: int(p.GetNumber()) if p.GetNumber().isdigit() else 999)
    pads = [p for p in pads if p.GetNumber().isdigit()]
    xs = [nm(p.GetPosition().x) for p in pads]
    ys = [nm(p.GetPosition().y) for p in pads]
    horizontal = (max(xs) - min(xs)) >= (max(ys) - min(ys))
    ok = 0
    for p, name in zip(pads, names):
        x, y = nm(p.GetPosition().x), nm(p.GetPosition().y)
        h = nm(max(p.GetBoundingBox().GetWidth(), p.GetBoundingBox().GetHeight())) / 2
        placed = False
        for size in (0.8, 0.7):
            for d in (h + 0.9, h + 1.4):
                cands = [(x, y - d, 0), (x, y + d, 0)] if horizontal else [(x - d - 0.6, y, 0), (x + d + 0.6, y, 0)]
                for cx, cy, ang in cands:
                    if add_text(s, name, cx, cy, size, ang):
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        ok += placed
    return ok


def free_spot(s, txt, size):
    """Primo posto libero per un testo, cercato su una griglia di 1 mm dentro la scheda."""
    bb = board.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = box(bb)
    y = y0 + 3
    while y < y1 - 3:
        x = x0 + 10
        while x < x1 - 10:
            if add_text(s, txt, x, y, size):
                return True
            x += 1.0
        y += 1.0
    return False


missing = []
fps = sorted(board.GetFootprints(), key=lambda f: -(body_box(f)[2] - body_box(f)[0]) * (body_box(f)[3] - body_box(f)[1]))
for fp in fps:
    ref = fp.GetReference()
    if ref.startswith('H'):  # fori di fissaggio: niente sigla
        fp.Reference().SetVisible(False)
        continue
    fp.Value().SetVisible(False)
    if ref in LABELS:
        pad_labels(fp, LABELS[ref])
    if ref.startswith(PIN1) and not pin1_dot(fp):
        missing.append(ref + ' (pallino)')
    if not place_reference(fp):
        missing.append(ref)
free_spot('F', 'C3+AI scheda madre · LATO S3', 1.2)
free_spot('B', 'C3+AI scheda madre · RETRO · rev A 10/2026', 1.2)
pcbnew.SaveBoard(str(PCB), board)
print('sigle e segni senza posto (solo nel disegno di montaggio):', ', '.join(missing) if missing else 'nessuno')
print(PCB)
