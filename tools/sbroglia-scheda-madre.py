"""Sbroglio automatico della scheda madre con Freerouting (KiCad 10 + Freerouting 2.5 su Java 25).

Uso (con il Python di KiCad, dopo tools/genera-pcb-scheda-madre.py):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" tools/sbroglia-scheda-madre.py <java.exe> <freerouting.jar> [passate]
Freerouting 2.5.0 richiede Java 25 (es. Eclipse Temurin 25, anche in versione portatile .zip). La versione
CLI nativa per Windows 2.5.0 si blocca all'avvio dello sbroglio (errore di serializzazione): usare il .jar.
Passi: classi di rete (larghezze delle piste), piani di massa sulle due facce, esportazione Specctra
(.dsn), sbroglio con Freerouting, importazione delle piste (.ses), riempimento dei piani, salvataggio.
Freerouting (GPL-3) non è nel repository: si scarica dalla pagina delle release del progetto.
Il risultato è una prima stesura da controllare con il DRC e da rifinire, non uno sbroglio collaudato.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb'
# --pcb=<file>: lavora su una copia (più sbrogli in parallelo, poi si tiene il migliore).
for a in sys.argv:
    if a.startswith('--pcb='):
        PCB = Path(a[6:])
JAVA, JAR = Path(sys.argv[1]), Path(sys.argv[2])
PASSES = sys.argv[3] if len(sys.argv) > 3 else '25'
# --completa: riparte dalla scheda già sbrogliata, tiene piste e piani e cerca solo le connessioni mancanti.
COMPLETE = '--completa' in sys.argv
mm = pcbnew.FromMM

# Classi di rete: (nome, pista, distanza, via, foro, reti). Correnti stimate in scheda-madre.md.
CLASSES = [
    ('Potenza', 0.8, 0.2, 0.8, 0.4, ['VBAT_IN', 'VBAT_P', '+12V_F', 'S3_5V', 'SW_5V', '+12V_FAN',
                                      'SPK_*', 'RADIO_*', 'S3_SPK_*', 'SPK_SERIE']),
    ('5V', 0.6, 0.2, 0.7, 0.35, ['+5V', 'RELAY_COIL']),
    ('Medio', 0.3, 0.2, 0.6, 0.3, ['+3V3_AON', '+3V3_SW', '+3V3_USB', 'USB_VBUS', 'SW_3V3', 'KLINE', 'VAN_DATA*',
                                   'KEY_IN', 'U2_BOOT', 'U3_BOOT', 'CH_V3', 'GND']),
]

board = pcbnew.LoadBoard(str(PCB))
ds = board.GetDesignSettings()
ns = ds.m_NetSettings
default = ns.GetDefaultNetclass()
default.SetTrackWidth(mm(0.2))
default.SetClearance(mm(0.2))
default.SetViaDiameter(mm(0.6))
default.SetViaDrill(mm(0.3))
ns.ClearNetclassPatternAssignments()
for name, w, c, vd, vh, pats in CLASSES:
    nc = pcbnew.NETCLASS(name)
    nc.SetTrackWidth(mm(w))
    nc.SetClearance(mm(c))
    nc.SetViaDiameter(mm(vd))
    nc.SetViaDrill(mm(vh))
    ns.SetNetclass(name, nc)
    for p in pats:
        ns.SetNetclassPatternAssignment(p, name)
board.SynchronizeNetsAndNetClasses(True)

# Piani di massa: un rettangolo più grande della scheda, ritagliato dal contorno al riempimento.
if not COMPLETE:
    for z in list(board.Zones()):
        board.Remove(z)
gnd = board.FindNet('GND')
bb = board.GetBoardEdgesBoundingBox()
bb.Inflate(mm(2))
# Quattro strati (D-057): piano di massa continuo su In1 e riempimenti di massa su F e B. In2 resta libero per
# le piste e riceve il suo riempimento di massa dopo lo sbroglio. Con due soli strati Freerouting si fermava a
# 28-32 connessioni aperte.


def add_plane(layer, net):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(net.GetNetCode())
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)  # SMD pieni, raccordi termici solo sui fori passanti
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                 (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        ol.Append(x, y)
    board.Add(z)


if not COMPLETE:
    for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.B_Cu):
        add_plane(layer, gnd)

# Fascia vietata di 1,0 mm lungo il contorno e il foro della ventola: Freerouting tiene dal bordo una distanza
# più piccola dei 0,5 mm richiesti dalle regole della scheda.
outline = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(outline, False)
inner = pcbnew.SHAPE_POLY_SET(outline)
inner.Deflate(mm(1.2), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, mm(0.01))
ring = pcbnew.SHAPE_POLY_SET(outline)
ring.BooleanSubtract(inner)
edge = pcbnew.ZONE(board)
edge.SetIsRuleArea(True)
edge.SetDoNotAllowTracks(True)
edge.SetDoNotAllowVias(True)
edge.SetDoNotAllowZoneFills(False)
edge.SetDoNotAllowPads(False)
edge.SetDoNotAllowFootprints(False)
edge.SetLayerSet(pcbnew.LSET.AllCuMask())
edge.SetOutline(ring)
board.Add(edge)

with tempfile.TemporaryDirectory() as tmp:  # una cartella per processo: sbrogli paralleli indipendenti
    dsn, ses = Path(tmp) / 'scheda-madre.dsn', Path(tmp) / 'scheda-madre.ses'
    assert pcbnew.ExportSpecctraDSN(board, str(dsn)), 'esportazione DSN non riuscita'
    # In1 è il piano di massa (D-057): dichiarato come strato di alimentazione, Freerouting non vi traccia piste.
    text = dsn.read_text(encoding='utf-8')
    head, sep, rest = text.partition('(layer In1.Cu')
    assert sep, 'strato In1.Cu assente nel DSN'
    rest = rest.replace('(type signal)', '(type power)', 1)
    dsn.write_text(head + sep + rest, encoding='utf-8')
    cmd = [str(JAVA), '-jar', str(JAR), '--gui.enabled=false', '-de', str(dsn), '-do', str(ses),
           f'--router.autorouter.max_passes={PASSES}']
    cmd += ['--router.fanout.enabled=false'] if COMPLETE else []
    cmd += [a for a in sys.argv[4:] if a.startswith('--router.')]  # altre opzioni di Freerouting
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       stdin=subprocess.DEVNULL)
    log = [l for l in (r.stdout + r.stderr).splitlines() if ' INFO ' in l and ('pass #' in l or 'completed' in l)]
    print('\n'.join(log[-8:]))
    assert ses.is_file(), 'Freerouting non ha prodotto la sessione .ses:\n' + r.stderr[-2000:]
    assert pcbnew.ImportSpecctraSES(board, str(ses)), 'importazione SES non riuscita'
board.Remove(edge)  # la fascia serviva solo allo sbroglio: il DRC controlla la distanza dal bordo con le sue regole
if not COMPLETE:
    add_plane(pcbnew.In2_Cu, gnd)

# Via di cucitura della massa su una griglia di 4 mm, dove non toccano rame di altre reti: uniscono i
# piani delle due facce e le isole lasciate dalle piste.
import math
import importlib.util
spec = importlib.util.spec_from_file_location('ing', ROOT / 'tools/genera-ingombro-scheda-madre.py')
ing = importlib.util.module_from_spec(spec)
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(ing)
CX, CY = 148.5, 105.0
VIA_D, VIA_H, GAP = 0.6, 0.3, 0.25
segs, blobs, gnd_vias = [], [], []
for t in board.GetTracks():
    if t.GetNetCode() == gnd.GetNetCode():
        if t.GetClass() == 'PCB_VIA':
            gnd_vias.append((pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)))
        continue
    if t.GetClass() == 'PCB_VIA':
        blobs.append((pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y), pcbnew.ToMM(t.GetFrontWidth()) / 2))
    else:
        segs.append((pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y), pcbnew.ToMM(t.GetEnd().x),
                     pcbnew.ToMM(t.GetEnd().y), pcbnew.ToMM(t.GetWidth()) / 2))
boxes = []
for fp in board.GetFootprints():
    for pad in fp.Pads():
        bb = pad.GetBoundingBox()
        if pad.GetNetCode() != gnd.GetNetCode():
            boxes.append((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())))
    if fp.GetReference().startswith('H'):  # fori di fissaggio e della ventola: niente via vicino
        bb = fp.GetBoundingBox(False)
        boxes.append((pcbnew.ToMM(bb.GetLeft()) - 1, pcbnew.ToMM(bb.GetTop()) - 1, pcbnew.ToMM(bb.GetRight()) + 1, pcbnew.ToMM(bb.GetBottom()) + 1))


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L = dx * dx + dy * dy
    u = 0 if L == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L))
    return math.hypot(px - x1 - u * dx, py - y1 - u * dy)


n_st = 0
r = VIA_D / 2 + GAP
for gx in range(-88, 89, 4):
    for gy in range(11, 83, 4):
        if not all(ing.inside(gx + ox, gy + oy) for ox, oy in ((1.2, 0), (-1.2, 0), (0, 1.2), (0, -1.2))):
            continue
        if math.hypot(gx - ing.FAN_C[0], gy - ing.FAN_C[1]) < ing.FAN_HOLE / 2 + 2.5:
            continue
        px, py = CX + gx, CY + 46.0 - gy
        if any(b[0] - r < px < b[2] + r and b[1] - r < py < b[3] + r for b in boxes):
            continue
        if any(math.hypot(px - x, py - y) < r + rr for x, y, rr in blobs):
            continue
        if any(seg_dist(px, py, *sg[:4]) < r + sg[4] for sg in segs):
            continue
        if any(math.hypot(px - x, py - y) < 2.0 for x, y in gnd_vias):  # già cucito in un giro precedente
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(px), mm(py)))
        v.SetWidth(mm(VIA_D))
        v.SetDrill(mm(VIA_H))
        v.SetNetCode(gnd.GetNetCode())
        board.Add(v)
        n_st += 1
print('via di cucitura della massa:', n_st)
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())


def free_point(px, py):
    return (not any(b[0] - r < px < b[2] + r and b[1] - r < py < b[3] + r for b in boxes)
            and not any(math.hypot(px - x, py - y) < r + rr for x, y, rr in blobs)
            and not any(seg_dist(px, py, *sg[:4]) < r + sg[4] for sg in segs))


# Isole del piano di massa: in ogni pezzo staccato (non il più grande) una via verso il piano dell'altra faccia.
for giro in range(1):  # un solo passaggio: una via per isola
    added = 0
    for z in board.Zones():
        if z.GetIsRuleArea():
            continue
        layer = z.GetLayer()
        polys = z.GetFilledPolysList(layer)
        areas = [(polys.Outline(i).Area(), i) for i in range(polys.OutlineCount())]
        if len(areas) < 2:
            continue
        biggest = max(areas)[1]
        for area, i in areas:
            if i == biggest:
                continue
            ol = polys.Outline(i)
            bb = ol.BBox()
            done = False
            x = bb.GetLeft()
            while x < bb.GetRight() and not done:
                y = bb.GetTop()
                while y < bb.GetBottom() and not done:
                    pt = pcbnew.VECTOR2I(int(x), int(y))
                    if ol.PointInside(pt) and free_point(pcbnew.ToMM(x), pcbnew.ToMM(y)):
                        v = pcbnew.PCB_VIA(board)
                        v.SetPosition(pt)
                        v.SetWidth(mm(VIA_D))
                        v.SetDrill(mm(VIA_H))
                        v.SetNetCode(z.GetNetCode())
                        board.Add(v)
                        blobs.append((pcbnew.ToMM(x), pcbnew.ToMM(y), VIA_D / 2))
                        added += 1
                        done = True
                    y += mm(0.8)
                x += mm(0.8)
    print('giro', giro + 1, 'via nelle isole di massa:', added)
    if not added:
        break
    filler.Fill(board.Zones())
pcbnew.SaveBoard(str(PCB), board)
tracks = [t for t in board.GetTracks()]
print(PCB, len([t for t in tracks if t.GetClass() == 'PCB_TRACK']), 'piste,',
      len([t for t in tracks if t.GetClass() == 'PCB_VIA']), 'via')
