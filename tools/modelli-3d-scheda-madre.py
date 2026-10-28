"""Ingombri 3D della scheda madre: blocchi STEP per i componenti senza modello KiCad e ventola.

Uso (con il Python di KiCad, dopo tools/serigrafia-scheda-madre.py):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" tools/modelli-3d-scheda-madre.py [--pcb=<file>]
Scrive in cruscotto/pcb/scheda-madre/modelli-3d/ un parallelepipedo STEP (AP214) per ogni componente che non ha
un modello nelle librerie di KiCad, con le dimensioni di ingombro della scheda tecnica o misurate, lo assegna
all'impronta e aggiunge la ventola Delta 40 × 40 × 10 (D-052) sul retro, centrata sul foro, come oggetto solo
meccanico (fuori da distinta e posizioni). Sono ingombri, non modelli dettagliati: servono per l'assieme
meccanico (profondità dietro la scheda, spazio verso la S3). Poi:
  kicad-cli pcb export step --subst-models --user-origin 148.5x151mm --include-tracks --include-zones ...
"""
from pathlib import Path
import sys

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb'
for a in sys.argv[1:]:
    if a.startswith('--pcb='):
        PCB = Path(a[6:])
OUT = PCB.parent / 'modelli-3d'
mm, nm = pcbnew.FromMM, pcbnew.ToMM

# Ingombri nelle coordinate dell'impronta (x a destra, y in basso come in KiCad), z sopra la faccia di montaggio.
# Una voce per blocco: (x0, y0, x1, y1, z0, z1); None = rettangolo del courtyard dell'impronta.
BOXES = {
    'J3': [(None, 0.0, 3.3)],                              # USB-C HRO TYPE-C-31-M-12, alta 3,26
    'U2': [(None, 0.0, 1.7)],                              # TPS54360B in SO-PowerPAD-8
    'K1': [(None, 0.0, 15.7)],                             # Omron G2RL-2: 29 × 12,7 × 15,7
    'K2': [(None, 0.0, 15.7)],
    'J1': [(None, 0.0, 9.9), (None, 9.9, 35.0)],            # 43045-2412 verticale alto 9,9; sopra, spina e fili (~25 mm, stima)
    'J6': [((-1.75, -1.48, 16.75, 29.42), 0.0, 5.6)],      # STEVAL 18,5 × 30,9 misurata, sui pin diritti (D-059)
    'J8': [((-1.3, -2.69, 33.7, 10.31), 0.0, 5.7),         # modulo VAN 35 × 13 sui pin diritti (D-060)
           ((24.0, -2.0, 33.7, 9.6), 5.7, 14.0)],          # morsetto a vite, altezza stimata
    'C3': [((-2.5, -5.0, 7.5, 5.0), 0.0, 17.5)],           # EEU-FR1H221 Ø10 × 17,5 (verificata 28/10/2026)
}
FAN = (40.0, 10.0)   # Delta AFB0412VA-00: 40 × 40 × 10


def step_boxes(path, boxes, name):
    """Scrive un file STEP AP214 con uno o più parallelepipedi (coordinate del modello: y verso l'alto)."""
    ents = []

    def e(text):
        ents.append(text)
        return len(ents)

    ctx_unit_mm = None
    solids = []
    for (x0, y0, z0, x1, y1, z1) in boxes:
        P = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        pts = [e(f"CARTESIAN_POINT('',({x:.4f},{y:.4f},{z:.4f}))") for x, y, z in P]
        vtx = [e(f"VERTEX_POINT('',#{p})") for p in pts]
        edges = {}

        def edge(a, b):
            k = (min(a, b), max(a, b))
            if k not in edges:
                (ax, ay, az), (bx, by, bz) = P[k[0]], P[k[1]]
                d = (bx - ax, by - ay, bz - az)
                ln = max(abs(c) for c in d)
                dr = e(f"DIRECTION('',({d[0] / ln:.4f},{d[1] / ln:.4f},{d[2] / ln:.4f}))")
                vec = e(f"VECTOR('',#{dr},{ln:.4f})")
                line = e(f"LINE('',#{pts[k[0]]},#{vec})")
                edges[k] = e(f"EDGE_CURVE('',#{vtx[k[0]]},#{vtx[k[1]]},#{line},.T.)")
            return edges[k], '.T.' if a < b else '.F.'
        faces = []
        for loop, normal, ref in (([0, 3, 2, 1], (0, 0, -1), (1, 0, 0)), ([4, 5, 6, 7], (0, 0, 1), (1, 0, 0)),
                                  ([0, 1, 5, 4], (0, -1, 0), (1, 0, 0)), ([2, 3, 7, 6], (0, 1, 0), (-1, 0, 0)),
                                  ([3, 0, 4, 7], (-1, 0, 0), (0, -1, 0)), ([1, 2, 6, 5], (1, 0, 0), (0, 1, 0))):
            oes = []
            for a, b in zip(loop, loop[1:] + loop[:1]):
                ec, sense = edge(a, b)
                oes.append(e(f"ORIENTED_EDGE('',*,*,#{ec},{sense})"))
            el = e("EDGE_LOOP('',(" + ','.join(f'#{o}' for o in oes) + "))")
            fb = e(f"FACE_OUTER_BOUND('',#{el},.T.)")
            n = e(f"DIRECTION('',({normal[0]:.1f},{normal[1]:.1f},{normal[2]:.1f}))")
            r = e(f"DIRECTION('',({ref[0]:.1f},{ref[1]:.1f},{ref[2]:.1f}))")
            ax = e(f"AXIS2_PLACEMENT_3D('',#{pts[loop[0]]},#{n},#{r})")
            pl = e(f"PLANE('',#{ax})")
            faces.append(e(f"ADVANCED_FACE('',(#{fb}),#{pl},.T.)"))
        shell = e("CLOSED_SHELL('',(" + ','.join(f'#{f}' for f in faces) + "))")
        solids.append(e(f"MANIFOLD_SOLID_BREP('{name}',#{shell})"))
    o = e("CARTESIAN_POINT('',(0.,0.,0.))")
    dz = e("DIRECTION('',(0.,0.,1.))")
    dx = e("DIRECTION('',(1.,0.,0.))")
    origin = e(f"AXIS2_PLACEMENT_3D('',#{o},#{dz},#{dx})")
    lu = e("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
    au = e("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
    su = e("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
    un = e(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05),#{lu},'distance_accuracy_value','')")
    gctx = e(f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{un})) "
             f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu},#{au},#{su})) REPRESENTATION_CONTEXT('','') )")
    rep = e("ADVANCED_BREP_SHAPE_REPRESENTATION('',(#" + str(origin) + ''.join(f',#{s}' for s in solids) + f"),#{gctx})")
    actx = e("APPLICATION_CONTEXT('automotive design')")
    e(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{actx})")
    pctx = e(f"PRODUCT_CONTEXT('',#{actx},'mechanical')")
    prod = e(f"PRODUCT('{name}','{name}','',(#{pctx}))")
    pdf = e(f"PRODUCT_DEFINITION_FORMATION('','',#{prod})")
    pdctx = e(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{actx},'design')")
    pd = e(f"PRODUCT_DEFINITION('design','',#{pdf},#{pdctx})")
    pds = e(f"PRODUCT_DEFINITION_SHAPE('','',#{pd})")
    e(f"SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})")
    body = ''.join(f'#{i}={t};\n' for i, t in enumerate(ents, 1))
    path.write_text("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('ingombro'),'2;1');\n"
                    f"FILE_NAME('{path.name}','2026-10-28T00:00:00',(''),(''),'','','');\n"
                    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n" + body +
                    "ENDSEC;\nEND-ISO-10303-21;\n", encoding='ascii')


def local_courtyard(fp):
    """Rettangolo del courtyard nelle coordinate dell'impronta, senza rotazione né ribaltamento."""
    loc = pcbnew.FOOTPRINT(fp)   # copia riportata sulla faccia F, senza rotazione, nell'origine
    if loc.IsFlipped():
        loc.Flip(loc.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    loc.SetOrientationDegrees(0)
    loc.SetPosition(pcbnew.VECTOR2I(0, 0))
    bb = loc.GetCourtyard(pcbnew.F_CrtYd).BBox()
    return nm(bb.GetLeft()), nm(bb.GetTop()), nm(bb.GetRight()), nm(bb.GetBottom())


def set_model(fp, fname):
    fp.Models().clear()
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = '${KIPRJMOD}/modelli-3d/' + fname
    fp.Models().push_back(m)


board = pcbnew.LoadBoard(str(PCB))
OUT.mkdir(exist_ok=True)
for ref, boxes in BOXES.items():
    fp = board.FindFootprintByReference(ref)
    solids = []
    for xy, z0, z1 in boxes:
        x0, y0, x1, y1 = xy if xy else local_courtyard(fp)
        solids.append((x0, -y1, z0, x1, -y0, z1))   # y del modello verso l'alto
    fname = f'ingombro-{ref}.step'
    step_boxes(OUT / fname, solids, ref)
    set_model(fp, fname)

# Ventola: impronta solo meccanica sul retro, centrata sul foro (fori di fissaggio H7-H10 attorno).
for fp in list(board.GetFootprints()):
    if fp.GetReference() == 'VENT1':
        board.Remove(fp)
holes = [board.FindFootprintByReference(f'H{i}') for i in range(7, 11)]
cx = sum(h.GetPosition().x for h in holes) // 4
cy = sum(h.GetPosition().y for h in holes) // 4
side, height = FAN[0], FAN[1]
step_boxes(OUT / 'ingombro-ventola.step', [(-side / 2, -side / 2, 0.0, side / 2, side / 2, height)], 'ventola')
fan = pcbnew.FOOTPRINT(board)
fan.SetReference('VENT1')
fan.SetValue('Delta AFB0412VA-00')
fan.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)
fan.Reference().SetVisible(False)
fan.Value().SetVisible(False)
board.Add(fan)
fan.SetPosition(pcbnew.VECTOR2I(cx, cy))
fan.Flip(fan.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
set_model(fan, 'ingombro-ventola.step')
pcbnew.SaveBoard(str(PCB), board)
print('ingombri scritti in', OUT, ':', ', '.join(list(BOXES) + ['ventola']))
