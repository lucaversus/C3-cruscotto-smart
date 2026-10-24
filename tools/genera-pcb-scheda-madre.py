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
ds.m_MinThroughDrill = pcbnew.FromMM(0.3)
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
    place('Button_Switch_THT', 'SW_PUSH_6mm_H7.3mm', f'S{i}', sx, sy, angle=21.0 if sx > 0 else -21.0,
          value='Tattile 6x6 H7,3 (pulsante quadro)')
j1 = place('Connector_Molex', 'Molex_Micro-Fit_3.0_43045-2400_2x12_P3.00mm_Horizontal', 'J1', 0.0, 16.0, angle=0.0,
           back=True, value='Micro-Fit 2x12 verso auto (D-044)')
# L'origine dell'impronta è il piedino 1: centrare in x e portare il fronte del connettore al bordo
# inferiore (y = 9 mm nel DXF), così la spina si innesta dal basso.
box = j1.GetCourtyard(pcbnew.B_CrtYd).BBox()
edge_y = at(0, ing.YMIN).y
j1.Move(pcbnew.VECTOR2I(at(0, 0).x - box.Centre().x, edge_y - box.GetBottom()))


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
pcb = OUT / 'scheda-madre.kicad_pcb'
pcbnew.SaveBoard(str(pcb), board)
print(pcb)
