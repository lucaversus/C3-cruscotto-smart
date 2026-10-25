"""Circuito stampato della scheda madre (KiCad 10): contorno e parti meccaniche.

Uso (con il Python di KiCad):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" tools/genera-pcb-scheda-madre.py
Crea cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb con:
- bordo (Edge.Cuts) letto da cruscotto/meccanica/scheda-madre-contorno.dxf (D-045) e foro
  centrale Ø38 della ventola;
- 6 fori di fissaggio Ø3 senza rame, 4 fori Ø3,2 per la ventola 40 × 40 (interasse 32);
- interruttori -S1/-S2 (tattili 6 × 6 alti 7,3 mm) sotto i pulsanti originali (assieme 3D);
- connettore -J1 Micro-Fit 2×12 orizzontale al bordo inferiore (D-044);
- su User.Drawings il contorno della S3 e le zone dello studio C3AI-CR-PL-001.
Faccia F (rame superiore) = faccia interna rivolta verso la S3 (D-046).
Regole minime per un circuito stampato a 2 strati prodotto senza montaggio (D-046).
Il file va rigenerato da qui: le modifiche fatte a mano in KiCad su questi elementi si perdono.
"""
from pathlib import Path
import importlib.util
import math

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'cruscotto/pcb/scheda-madre'
LIB = Path(pcbnew.__file__).resolve().parents[3] / 'share/kicad/footprints'
if not LIB.is_dir():
    LIB = Path(r'C:\Program Files\KiCad\10.0\share\kicad\footprints')

spec = importlib.util.spec_from_file_location('ingombro', ROOT / 'tools/genera-ingombro-scheda-madre.py')
ing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ing)  # contorno, fori, zone e posizioni già controllate dallo studio

CX, CY = 148.5, 105.0  # centro del foglio A4 di KiCad


def at(x, y):
    """mm del DXF (y verso l'alto, origine al centro del bordo inferiore) → KiCad (nm, y verso il basso)."""
    return pcbnew.VECTOR2I(pcbnew.FromMM(CX + x), pcbnew.FromMM(CY + 46.0 - y))


board = pcbnew.BOARD()
tb = board.GetTitleBlock()
tb.SetTitle('Scheda madre cruscotto C3+AI')
tb.SetRevision('A')
tb.SetDate('2026-10-24')
tb.SetCompany('Cruscotto C3+AI')
tb.SetComment(0, 'Contorno D-045, montaggio a mano D-046, J1 D-044')
tb.SetComment(1, 'Generato da tools/genera-pcb-scheda-madre.py - preliminare, non verificato')

ds = board.GetDesignSettings()
ds.SetCopperLayerCount(2)
ds.SetBoardThickness(pcbnew.FromMM(1.6))
ds.m_MinClearance = pcbnew.FromMM(0.2)
ds.m_TrackMinWidth = pcbnew.FromMM(0.2)
ds.m_ViasMinSize = pcbnew.FromMM(0.6)
ds.m_MinThroughDrill = pcbnew.FromMM(0.2)  # fori termici delle impronte (es. ESP32): 0,2 mm, standard dei produttori
ds.m_CopperEdgeClearance = pcbnew.FromMM(0.5)
ds.m_HoleClearance = pcbnew.FromMM(0.25)


def add_shape(kind, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(kind)
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)
    return s


# Bordo: segmenti e archi del DXF (archi per tre punti: nessuna ambiguità di verso con y capovolta).
for e in ing.ENT:
    if e['type'] == 'LINE':
        s = add_shape(pcbnew.SHAPE_T_SEGMENT, pcbnew.Edge_Cuts)
        s.SetStart(at(e['10'], e['20']))
        s.SetEnd(at(e['11'], e['21']))
    elif e['type'] == 'ARC':
        a0, a1 = e['50'], e['51']
        if a1 < a0:
            a1 += 360
        pts = [at(e['10'] + e['40'] * math.cos(math.radians(a)), e['20'] + e['40'] * math.sin(math.radians(a)))
               for a in (a0, (a0 + a1) / 2, a1)]
        s = add_shape(pcbnew.SHAPE_T_ARC, pcbnew.Edge_Cuts)
        s.SetArcGeometry(*pts)
# Foro della ventola.
fan = add_shape(pcbnew.SHAPE_T_CIRCLE, pcbnew.Edge_Cuts)
fan.SetCenter(at(*ing.FAN_C))
fan.SetEnd(at(ing.FAN_C[0] + ing.FAN_HOLE / 2, ing.FAN_C[1]))


def place(lib, name, ref, x, y, angle=0.0, back=False, value=''):
    fp = pcbnew.FootprintLoad(str(LIB / f'{lib}.pretty'), name)
    assert fp is not None, f'impronta non trovata: {lib}:{name}'
    fp.SetReference(ref)
    fp.SetValue(value or name)
    fp.SetPosition(at(x, y))
    fp.SetOrientationDegrees(angle)
    board.Add(fp)
    if back:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    return fp


for i, (hx, hy, r) in enumerate(ing.HOLES, 1):
    assert abs(r - 1.5) < 0.01
    place('MountingHole', 'MountingHole_3mm', f'H{i}', hx, hy, value='Foro Ø3 (D-045)')
for i, (dx, dy) in enumerate(((-16, -16), (16, -16), (-16, 16), (16, 16)), 1):
    place('MountingHole', 'MountingHole_3.2mm_M3', f'H{6 + i}', ing.FAN_C[0] + dx, ing.FAN_C[1] + dy,
          value='Ventola 40x40')
for i, (sx, sy) in enumerate(ing.SW, 1):
    # Pulsanti originali inclinati di circa 21° (assieme 3D): interruttore ruotato come il pulsante.
    sw = place('Button_Switch_THT', 'SW_PUSH_6mm_H7.3mm', f'S{i}', sx, sy, angle=111.0 if sx > 0 else -111.0,
               value='Tattile 6x6 H7,3 (pulsante quadro)')
    # L'origine dell'impronta è il piedino 1: si sposta il centro del corpo sotto il pulsante.
    centre = sw.GetCourtyard(pcbnew.F_CrtYd).BBox().Centre()
    sw.Move(pcbnew.VECTOR2I(at(sx, sy).x - centre.x, at(sx, sy).y - centre.y))
j1 = place('Connector_Molex', 'Molex_Micro-Fit_3.0_43045-2400_2x12_P3.00mm_Horizontal', 'J1', 0.0, 16.0, angle=0.0,
           back=True, value='Micro-Fit 2x12 verso auto (D-044)')
# L'origine dell'impronta è il piedino 1: centrare in x e portare il fronte del connettore al bordo
# inferiore (y = 9 mm nel DXF), così la spina si innesta dal basso.
box = j1.GetCourtyard(pcbnew.B_CrtYd).BBox()
edge_y = at(0, ing.YMIN).y
j1.Move(pcbnew.VECTOR2I(at(0, 0).x - box.Centre().x, edge_y - box.GetBottom()))


# --- Componenti dello schema (CR-EL-001…005): reti dal netlist di KiCad, piazzamento preliminare a blocchi ----
import re
import subprocess
import tempfile

SCH = OUT / 'scheda-madre.kicad_sch'
CLI = Path(pcbnew.__file__).resolve().parents[3] / 'bin' / 'kicad-cli.exe'
if not CLI.is_file():
    CLI = Path(r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe')


def read_netlist():
    with tempfile.TemporaryDirectory() as tmp:
        net = Path(tmp) / 'n.net'
        subprocess.run([str(CLI), 'sch', 'export', 'netlist', '-o', str(net), str(SCH)], check=True, capture_output=True)
        t = net.read_text(encoding='utf-8')
    comps = {}
    for blk in t.split('\n\t\t(comp\n')[1:]:
        ref = re.search(r'\(ref "([^"]+)"', blk).group(1)
        fp = re.search(r'\(footprint "([^"]*)"', blk)
        if fp and fp.group(1):
            comps[ref] = (fp.group(1), re.search(r'\(value "([^"]*)"', blk).group(1))
    pins = {}
    for blk in re.split(r'\n\t\t\(net\n', t[t.index('(nets'):])[1:]:
        name = re.search(r'\(name "([^"]+)"', blk).group(1)
        for ref, pin in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', blk):
            pins[(ref, pin)] = name
    return comps, pins


COMPS, PINS = read_netlist()
NETS = {}


def assign_nets(fp, ref):
    for pad in fp.Pads():
        name = PINS.get((ref, pad.GetNumber()))
        if not name or name.startswith('unconnected-'):
            continue
        if name not in NETS:
            NETS[name] = pcbnew.NETINFO_ITEM(board, name)
            board.Add(NETS[name])
        pad.SetNet(NETS[name])


def dxf(p):
    return pcbnew.ToMM(p.x) - CX, CY + 46.0 - pcbnew.ToMM(p.y)


def box_dxf(fp):
    """Ingombro (courtyard, o contorno se manca) in coordinate del DXF: x0, y0, x1, y1 con y verso l'alto."""
    lay = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    bb = fp.GetCourtyard(lay).BBox()
    if fp.GetReference() in BODY_ONLY:  # radio del modulo non usata: ingombro del solo corpo, senza zona d'antenna
        fab = pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab
        boxes = [it.GetBoundingBox() for it in fp.GraphicalItems()
                 if it.GetLayer() == fab and isinstance(it, pcbnew.PCB_SHAPE)]
        x0, y0 = min(q.GetLeft() for q in boxes), min(q.GetTop() for q in boxes)
        x1, y1 = max(q.GetRight() for q in boxes), max(q.GetBottom() for q in boxes)
        m = pcbnew.FromMM(0.5)
        bb = pcbnew.BOX2I(pcbnew.VECTOR2I(x0 - m, y0 - m), pcbnew.VECTOR2L(x1 - x0 + 2 * m, y1 - y0 + 2 * m))
    if bb.GetWidth() == 0:
        bb = fp.GetBoundingBox(False)
    (x0, y1), (x1, y0) = dxf(bb.GetOrigin()), dxf(bb.GetEnd())
    return x0, y0, x1, y1


BODY_ONLY = {'U4'}  # ESP32 del front-end: Wi-Fi/BLE non usati (D-029, D-036), la zona d'antenna può avere componenti vicini
FAN_SQ = (ing.FAN_C[0] - 21, ing.FAN_C[1] - 21, ing.FAN_C[0] + 21, ing.FAN_C[1] + 21)   # corpo della ventola sul retro
OCC = {'F': [], 'B': []}                                    # ingombri già occupati per faccia


def is_tht(fp):
    # Piedini a foro passante veri (non i fori termici sotto le piazzole): occupano anche l'altra faccia.
    return any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and pcbnew.ToMM(p.GetDrillSize().x) >= 0.6 for p in fp.Pads())


def occupy(fp, side):
    b = box_dxf(fp)
    for s in (('F', 'B') if is_tht(fp) else (side,)):   # i componenti a foro passante occupano le due facce
        OCC[s].append(b)


WHY = []


def free(b, side, margin=0.6, check_outline=True):
    x0, y0, x1, y1 = b[0] - margin, b[1] - margin, b[2] + margin, b[3] + margin
    if check_outline:
        n = max(2, int((x1 - x0) / 1.0)), max(2, int((y1 - y0) / 1.0))
        per = [(x0 + (x1 - x0) * i / n[0], y) for i in range(n[0] + 1) for y in (y0, y1)]
        per += [(x, y0 + (y1 - y0) * j / n[1]) for j in range(n[1] + 1) for x in (x0, x1)]
        if not all(ing.inside(px, py) for px, py in per):
            WHY.append('bordo')
            return False
    for hx, hy, r in ing.HOLES:
        cx, cy = min(max(hx, x0), x1), min(max(hy, y0), y1)
        if math.hypot(cx - hx, cy - hy) < r + 3.2:
            WHY.append(f'foro {hx:g},{hy:g}')
            return False
    fx, fy = ing.FAN_C
    cx, cy = min(max(fx, x0), x1), min(max(fy, y0), y1)
    if math.hypot(cx - fx, cy - fy) < ing.FAN_HOLE / 2 + 1.0:
        WHY.append('foro ventola')
        return False
    if side == 'B' and not (x1 <= FAN_SQ[0] or x0 >= FAN_SQ[2] or y1 <= FAN_SQ[1] or y0 >= FAN_SQ[3]):
        WHY.append('ventola')
        return False
    hit = [o for o in OCC[side] if not (x1 <= o[0] or x0 >= o[2] or y1 <= o[1] or y0 >= o[3])]
    if hit:
        WHY.append(f'occupato {[round(v, 1) for v in hit[0]]}')
    return all(x1 <= o[0] or x0 >= o[2] or y1 <= o[1] or y0 >= o[3] for o in OCC[side])


def new_fp(ref, side, rot=0.0):
    fpid, value = COMPS[ref]
    lib, name = fpid.split(':')
    path = OUT / f'{lib}.pretty' if lib == 'scheda-madre' else LIB / f'{lib}.pretty'
    fp = pcbnew.FootprintLoad(str(path), name)
    assert fp is not None, f'impronta non trovata: {fpid}'
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    if side == 'B':
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    assign_nets(fp, ref)
    if ref in BODY_ONLY:  # niente zona vietata né courtyard d'antenna: courtyard sul solo corpo del modulo
        for z in list(fp.Zones()):
            fp.Remove(z)
        fab = [it for it in fp.GraphicalItems() if it.GetLayer() == pcbnew.F_Fab and isinstance(it, pcbnew.PCB_SHAPE)]
        x0 = min(it.GetBoundingBox().GetLeft() for it in fab); x1 = max(it.GetBoundingBox().GetRight() for it in fab)
        y0 = min(it.GetBoundingBox().GetTop() for it in fab); y1 = max(it.GetBoundingBox().GetBottom() for it in fab)
        for it in [it for it in fp.GraphicalItems() if it.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd)]:
            fp.Remove(it)
        m = pcbnew.FromMM(0.5)
        cy = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_RECT)
        cy.SetStart(pcbnew.VECTOR2I(x0 - m, y0 - m))
        cy.SetEnd(pcbnew.VECTOR2I(x1 + m, y1 + m))
        cy.SetLayer(pcbnew.B_CrtYd if side == 'B' else pcbnew.F_CrtYd)
        cy.SetWidth(pcbnew.FromMM(0.05))
        fp.Add(cy)
    return fp


def move_box_to(fp, cx, cy):
    """Sposta il componente perché il centro del suo ingombro cada in (cx, cy) del DXF."""
    b = box_dxf(fp)
    dx, dy = cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2
    fp.Move(pcbnew.VECTOR2I(pcbnew.FromMM(dx), pcbnew.FromMM(-dy)))


def sides_of(fp, side):
    return ('F', 'B') if is_tht(fp) else (side,)


def put(ref, side, cx, cy, rot=0.0, check_outline=True):
    fp = new_fp(ref, side, rot)
    move_box_to(fp, cx, cy)
    WHY.clear()
    assert all(free(box_dxf(fp), sd, check_outline=check_outline) for sd in sides_of(fp, side)),         f'{ref}: posizione fissa non libera: {WHY}'
    occupy(fp, side)
    return fp


def pack(refs, side, region, from_right=False, rot=0.0):
    """Piazza i componenti nella regione (x0, y0, x1, y1) nel primo posto libero, dall'alto, accanto alla ventola se richiesto."""
    x0, y0, x1, y1 = region
    for ref in sorted(refs, key=lambda r: -area_of(r)):
        fp = new_fp(ref, side, rot)
        done = False
        for r in (rot, rot + 90):  # prima l'orientamento richiesto, poi ruotato di 90°
            fp.SetOrientationDegrees(r if side == 'F' else 180 - r)
            b = box_dxf(fp)
            w, h = b[2] - b[0], b[3] - b[1]
            y = y1 - h / 2
            while y >= y0 + h / 2 and not done:
                xs = [x1 - w / 2 - i * 0.5 for i in range(int((x1 - x0 - w) / 0.5) + 1)]
                for x in (xs if from_right else reversed(xs)):
                    cand = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                    if all(free(cand, sd) for sd in sides_of(fp, side)):
                        move_box_to(fp, x, y)
                        occupy(fp, side)
                        done = True
                        break
                y -= 0.5
            if done:
                break
        if not done:  # lasciato fuori dalla scheda, a destra, e segnalato: il piazzamento va rivisto
            FAILED.append(ref)
            move_box_to(fp, 110.0 + 25 * (len(FAILED) // 8), 80.0 - 10 * (len(FAILED) % 8))


_area = {}
FAILED = []


def area_of(ref):
    if ref not in _area:
        fpid = COMPS[ref][0]
        lib, name = fpid.split(':')
        path = OUT / f'{lib}.pretty' if lib == 'scheda-madre' else LIB / f'{lib}.pretty'
        f = pcbnew.FootprintLoad(str(path), name)
        bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
        _area[ref] = pcbnew.ToMM(bb.GetWidth()) * pcbnew.ToMM(bb.GetHeight())
    return _area[ref]


# Componenti meccanici già posati: reti e ingombri.
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in COMPS:
        assign_nets(fp, ref)
    occupy(fp, 'B' if fp.IsFlipped() else 'F')
placed = {fp.GetReference() for fp in board.GetFootprints()}

# Posizioni fisse: modulo ESP32 con l'antenna al bordo superiore libero dalla S3, USB-C al bordo superiore,
# cavetti verso i connettori della S3 vicino ai suoi lati (assieme 3D).
put('J3', 'F', 14.0, ing.YMAX - 5.0, check_outline=False)
# La faccia F guarda la S3: rispetto al DXF (visto dal retro) le x dei pezzi legati alla S3 sono speculari.
# P1 della S3 è nell'assieme a x ≈ +65, Speak a +56, P2 a +2: qui a x negative. Spine ad angolo retto verso il
# bordo inferiore, da cui i cavetti scendono ai connettori sul lato inferiore della S3.
put('J10', 'F', -64.0, 13.5)
put('J12', 'F', -52.0, 13.5)
put('J11', 'F', -26.0, 13.5)
put('J4', 'B', 26.0, 30.0, rot=90)
placed |= {'J3', 'J10', 'J11', 'J12', 'J4'}
pack(['U4'], 'F', (20.0, 9.0, 80.0, 62.0), from_right=True)
placed.add('U4')

USB = ['U5', 'U6', 'R31', 'R32', 'R33', 'R34', 'R37', 'C25', 'C26', 'C27', 'Q6', 'Q7', 'R35', 'R36']
BACK = ['C3', 'K1', 'K2', 'D11', 'D12', 'Q9', 'R54', 'R55', 'J6', 'J8', 'J9', 'U10', 'C34']
rest = [r for r in COMPS if r not in placed]
put('J6', 'B', 56.5, 25.0, rot=90)
placed.add('J6')
pack(USB, 'F', (-24.0, 62.0, 24.0, ing.YMAX), from_right=False)
pack(['K1', 'K2', 'C3', 'D11', 'D12', 'Q9', 'R54', 'R55', 'U10', 'C34'], 'B', (-72.0, 9.0, -21.5, ing.YMAX), from_right=True)
pack(['J8', 'J9'], 'B', (21.5, 9.0, 72.0, ing.YMAX), from_right=False)
POWER = [r for r in rest if r not in USB + BACK and (
    re.fullmatch(r'(U[123]|Q1|L[12]|FB1|D[1-6]|C([1-9]|1[0-9])|R([1-9]|1[0-4]))', r))]
pack(POWER, 'F', (-72.0, 9.0, -20.0, ing.YMAX), from_right=True)
VEH = [r for r in rest if re.fullmatch(r'(U[789]|Q8|D[89]|D10|C(2[89]|3[0-2])|R(3[89]|4[0-8]))', r)]
pack(VEH, 'F', (20.0, 9.0, 72.0, 48.0), from_right=False)
OTHER = [r for r in rest if r not in USB + BACK + POWER + VEH and r not in placed]
pack(OTHER, 'F', (-24.0, 9.0, 89.0, ing.YMAX), from_right=False)


def rect(layer, x, y, w, h, width=0.12):
    for (x1, y1), (x2, y2) in (((x, y), (x + w, y)), ((x + w, y), (x + w, y - h)),
                               ((x + w, y - h), (x, y - h)), ((x, y - h), (x, y))):
        s = add_shape(pcbnew.SHAPE_T_SEGMENT, layer, width)
        s.SetStart(at(x1, y1))
        s.SetEnd(at(x2, y2))


def text(layer, x, y, value, size=1.2):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(value)
    t.SetLayer(layer)
    t.SetPosition(at(x, y))
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    board.Add(t)


sx, sy, sw, sh = ing.S3_BOX
rect(pcbnew.Dwgs_User, sx, sy, sw, sh, 0.2)
text(pcbnew.Dwgs_User, sx + sw / 2, sy - sh + 2, 'Contorno scheda S3 davanti (assieme 3D)')
for ref, label, x, y, w, h, optional in ing.ZONES:
    if ref == '-J1':
        continue
    rect(pcbnew.Cmts_User, x, y, w, h)
    text(pcbnew.Cmts_User, x + w / 2, y - h / 2, ref.lstrip('-'), 1.5)

OUT.mkdir(parents=True, exist_ok=True)
print('componenti piazzati:', len([f for f in board.GetFootprints() if f.GetReference() in COMPS]), 'di', len(COMPS),
      '| senza posto:', ' '.join(FAILED) or 'nessuno')
pcb = OUT / 'scheda-madre.kicad_pcb'
pcbnew.SaveBoard(str(pcb), board)
print(pcb)
