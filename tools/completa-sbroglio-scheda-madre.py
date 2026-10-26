"""Completamento dello sbroglio della scheda madre: traccia i collegamenti lasciati aperti da Freerouting.

Uso (con il Python di KiCad, dopo tools/sbroglia-scheda-madre.py):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" tools/completa-sbroglio-scheda-madre.py [--pcb=<file>]
Per ogni rete con piedini non ancora collegati cerca un percorso libero (A*) su griglia di 0,05 mm negli
strati F, In2 e B (In1 resta piano di massa continuo, D-057), con via passanti dove serve, rispettando
larghezza della classe di rete, distanza minima e distanza dal bordo. Prima toglie le piste che violano la
distanza dal bordo o la larghezza minima e le ritraccia; mette una via verso In1 nelle isole dei riempimenti
di massa. Poi riempie i piani e ripete finché restano collegamenti aperti.
Il risultato va sempre controllato con il DRC di KiCad: è uno sbroglio generato, non collaudato.
"""
from pathlib import Path
import heapq
import json
import math
import subprocess
import sys

import numpy as np
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb'
for a in sys.argv[1:]:
    if a.startswith('--pcb='):
        PCB = Path(a[6:])
G = 0.05                 # passo della griglia, mm
MARGIN = 0.05            # margine per la discretizzazione (centro cella e percorso)
CLEAR = 0.2 + MARGIN     # distanza minima tra rame di reti diverse
EDGE_MIN = 0.3           # distanza minima dal bordo (regole della scheda)
EDGE = EDGE_MIN + MARGIN
VIA_COST = 24.0          # una via vale 1,2 mm di pista
WINDOW = 25.0            # finestra di ricerca attorno al gruppo da collegare, mm (poi tutta la scheda)
LAYERS = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
ROUTE = [0, 2, 3]        # indici in LAYERS su cui si traccia
LAYER_COST = {0: 1.15, 2: 1.0, 3: 1.15}   # In2 preferito: lascia integri i riempimenti di massa esterni
mm, nm = pcbnew.FromMM, pcbnew.ToMM

board = pcbnew.LoadBoard(str(PCB))
bb = board.GetBoardEdgesBoundingBox()
X0, Y0 = float(nm(bb.GetLeft()) - 1), float(nm(bb.GetTop()) - 1)
NX, NY = int((nm(bb.GetWidth()) + 2) / G) + 1, int((nm(bb.GetHeight()) + 2) / G) + 1
XS = X0 + np.arange(NX) * G
YS = Y0 + np.arange(NY) * G


def sub(x0, y0, x1, y1):
    i0, j0 = max(0, int((x0 - X0) / G) - 1), max(0, int((y0 - Y0) / G) - 1)
    i1, j1 = min(NX, int((x1 - X0) / G) + 2), min(NY, int((y1 - Y0) / G) + 2)
    return i0, j0, i1, j1


def poly_mask(pts, x0, y0, x1, y1):
    """Celle (sottogriglia) dentro il poligono pts, regola pari-dispari."""
    i0, j0, i1, j1 = sub(x0, y0, x1, y1)
    X, Y = np.meshgrid(XS[i0:i1], YS[j0:j1])
    inside = np.zeros(X.shape, bool)
    n = len(pts)
    for k in range(n):
        xa, ya = pts[k]
        xb, yb = pts[(k + 1) % n]
        if ya == yb:
            continue
        c = (ya > Y) != (yb > Y)
        xi = xa + (Y - ya) * (xb - xa) / (yb - ya)
        inside ^= c & (X < xi)
    return (i0, j0, i1, j1), inside


def seg_mask(xa, ya, xb, yb, r):
    i0, j0, i1, j1 = sub(min(xa, xb) - r, min(ya, yb) - r, max(xa, xb) + r, max(ya, yb) + r)
    X, Y = np.meshgrid(XS[i0:i1], YS[j0:j1])
    dx, dy = xb - xa, yb - ya
    L = dx * dx + dy * dy
    u = np.zeros(X.shape) if L == 0 else np.clip(((X - xa) * dx + (Y - ya) * dy) / L, 0, 1)
    return (i0, j0, i1, j1), np.hypot(X - xa - u * dx, Y - ya - u * dy) <= r


def chain_pts(ch):
    return [(nm(ch.CPoint(k).x), nm(ch.CPoint(k).y)) for k in range(ch.PointCount())]


def item_masks(it, grow=0.0):
    """(indice strato, finestra, maschera) del rame dell'elemento, allargato di grow mm."""
    out = []
    if it.GetClass() == 'PCB_TRACK':
        if it.GetLayer() in LAYERS:
            s, e = it.GetStart(), it.GetEnd()
            w, m = seg_mask(nm(s.x), nm(s.y), nm(e.x), nm(e.y), nm(it.GetWidth()) / 2 + grow)
            out.append((LAYERS.index(it.GetLayer()), w, m))
        return out
    if it.GetClass() == 'PCB_VIA':
        p = it.GetPosition()
        w, m = seg_mask(nm(p.x), nm(p.y), nm(p.x), nm(p.y), nm(it.GetFrontWidth()) / 2 + grow)
        return [(li, w, m) for li in range(4)]
    for li, L in enumerate(LAYERS):  # piazzola
        if not it.IsOnLayer(L):
            continue
        ps = pcbnew.SHAPE_POLY_SET()
        it.TransformShapeToPolygon(ps, L, mm(grow), mm(0.005), pcbnew.ERROR_OUTSIDE)
        for o in range(ps.OutlineCount()):
            pts = chain_pts(ps.Outline(o))
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            w, m = poly_mask(pts, min(xs), min(ys), max(xs), max(ys))
            out.append((li, w, m))
    return out


def paint(grid, li, w, m, value):
    i0, j0, i1, j1 = w
    grid[li, j0:j1, i0:i1][m] = value


DISKS = {}


def disk(r):
    n = int(math.ceil(r / G))
    if n not in DISKS:
        DISKS[n] = [(dx, dy) for dx in range(-n, n + 1) for dy in range(-n, n + 1) if math.hypot(dx, dy) <= n]
    return DISKS[n]


def dilate(mask, r):
    """Dilatazione con un disco di raggio r (mm), qualunque sia la forma della maschera."""
    h, w = mask.shape
    out = mask.copy()
    for dx, dy in disk(r):
        sx0, sx1 = max(0, dx), w + min(0, dx)
        sy0, sy1 = max(0, dy), h + min(0, dy)
        if sx1 > sx0 and sy1 > sy0:
            out[sy0:sy1, sx0:sx1] |= mask[sy0 - dy:sy1 - dy, sx0 - dx:sx1 - dx]
    return out


# --- Contorno: celle fuori scheda (comprende il foro della ventola) e segmenti per la distanza esatta --------
outline = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(outline, False)
inside = np.zeros((NY, NX), bool)
EDGE_SEGS = []
for o in range(outline.OutlineCount()):
    chains = [chain_pts(outline.Outline(o))] + [chain_pts(outline.Hole(o, h)) for h in range(outline.HoleCount(o))]
    for k, pts in enumerate(chains):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        (i0, j0, i1, j1), m = poly_mask(pts, min(xs), min(ys), max(xs), max(ys))
        if k == 0:
            inside[j0:j1, i0:i1] |= m
        else:
            inside[j0:j1, i0:i1] &= ~m
        EDGE_SEGS += [(pts[q], pts[(q + 1) % len(pts)]) for q in range(len(pts))]
OUTSIDE = ~inside
ES = np.array([[a[0], a[1], b[0], b[1]] for a, b in EDGE_SEGS])


def seg_seg_dist(xa, ya, xb, yb):
    """Distanza minima tra il segmento (a, b) e il contorno della scheda."""
    def pt_seg(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        L = dx * dx + dy * dy
        u = np.where(L == 0, 0, np.clip(((px - x1) * dx + (py - y1) * dy) / np.where(L == 0, 1, L), 0, 1))
        return np.hypot(px - x1 - u * dx, py - y1 - u * dy)
    x1, y1, x2, y2 = ES.T
    d = np.minimum.reduce([pt_seg(xa, ya, x1, y1, x2, y2), pt_seg(xb, yb, x1, y1, x2, y2),
                           pt_seg(x1, y1, xa, ya, xb, yb), pt_seg(x2, y2, xa, ya, xb, yb)])
    return float(d.min())


COP = np.zeros((4, NY, NX), np.int32)   # numero di rete per cella e strato; -1 = vietato


def netclass(code):
    net = board.FindNet(code)
    nc = board.GetDesignSettings().m_NetSettings.GetEffectiveNetClass(net.GetNetname())
    return nm(nc.GetTrackWidth()), nm(nc.GetViaDiameter()), nm(nc.GetViaDrill())


def build_copper():
    OWN_AXIS.clear()
    COP[:] = 0
    for fp in board.GetFootprints():
        for p in fp.Pads():
            code = p.GetNetCode() if p.GetNetCode() > 0 else -1  # fori di fissaggio e piedini senza rete
            for li, w, m in item_masks(p, G / 2):  # celle non allineate al rame: mezza cella in più
                paint(COP, li, w, m, code)
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:  # foro senza rame: vietato su tutti gli strati
                c = p.GetPosition()
                w, m = seg_mask(nm(c.x), nm(c.y), nm(c.x), nm(c.y), nm(p.GetDrillSize().x) / 2 + 0.05)
                for li in range(4):
                    paint(COP, li, w, m, -1)
    for t in board.GetTracks():
        for li, w, m in item_masks(t, G / 2):
            paint(COP, li, w, m, t.GetNetCode())


REMOVED = []  # riferimenti tenuti in vita: liberarli dopo board.Remove fa cadere pcbnew


def remove_bad_tracks():
    """Piste e via troppo vicine al bordo o più strette del minimo: tolte, saranno ritracciate."""
    min_w = nm(board.GetDesignSettings().m_TrackMinWidth)
    bad = []
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition()
            if seg_seg_dist(nm(p.x), nm(p.y), nm(p.x), nm(p.y)) < EDGE_MIN + nm(t.GetFrontWidth()) / 2 - 1e-4:
                bad.append(t)
            continue
        s, e = t.GetStart(), t.GetEnd()
        if (nm(t.GetWidth()) < min_w - 1e-6
                or seg_seg_dist(nm(s.x), nm(s.y), nm(e.x), nm(e.y)) < EDGE_MIN + nm(t.GetWidth()) / 2 - 1e-4):
            bad.append(t)
    for t in bad:
        board.Remove(t)
    REMOVED.extend(bad)
    return len(bad)


def clusters(code):
    """Gruppi di elementi della rete già collegati tra loro (connettività di KiCad, piani compresi)."""
    c = board.GetConnectivity()
    its = [p for fp in board.GetFootprints() for p in fp.Pads() if p.GetNetCode() == code]
    its += [t for t in board.GetTracks() if t.GetNetCode() == code]
    index = {x.m_Uuid.AsString(): k for k, x in enumerate(its)}
    left, out = set(range(len(its))), []
    while left:
        k = left.pop()
        cl = {k}
        for x in c.GetConnectedItems(its[k]):
            j = index.get(x.m_Uuid.AsString())
            if j is not None and j in left:
                cl.add(j)
                left.discard(j)
        out.append([its[j] for j in cl])
    return out


def cluster_mask(items):
    m = np.zeros((4, NY, NX), bool)
    for it in items:
        for li, w, mk in item_masks(it):
            i0, j0, i1, j1 = w
            m[li, j0:j1, i0:i1] |= mk
    return m


class LazyMasks(dict):
    """Maschere per rete calcolate alla prima richiesta e azzerate quando cambia il rame."""
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def __missing__(self, code):
        self[code] = self.fn(code)
        return self[code]


def pad_extensions(code):
    """Piazzole SMD strette (passo fine) della rete prolungate di 0,4 mm lungo l'asse lungo, per l'uscita in linea."""
    m = np.zeros((4, NY, NX), bool)
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() != code or p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            L = LAYERS.index(p.GetLayer()) if p.GetLayer() in LAYERS else (3 if fp.IsFlipped() else 0)
            sx, sy = nm(p.GetSize(p.GetLayer() if p.GetLayer() in LAYERS else pcbnew.F_Cu).x),                 nm(p.GetSize(p.GetLayer() if p.GetLayer() in LAYERS else pcbnew.F_Cu).y)
            if min(sx, sy) > 0.45:
                continue
            a = math.radians(p.GetOrientationDegrees())
            ux, uy = (math.cos(a), -math.sin(a)) if sx > sy else (math.sin(a), math.cos(a))
            half = max(sx, sy) / 2 + 0.4
            c = p.GetPosition()
            cx, cy = nm(c.x), nm(c.y)
            w, mk = seg_mask(cx - ux * half, cy - uy * half, cx + ux * half, cy + uy * half, min(sx, sy) / 2 + G / 2)
            i0, j0, i1, j1 = w
            m[L, j0:j1, i0:i1] |= mk
    return m


def track_axes(code):
    """Celle sull'asse delle piste della rete (entro tre quarti di cella)."""
    m = np.zeros((4, NY, NX), bool)
    for t in board.GetTracks():
        if t.GetNetCode() == code and t.GetClass() == 'PCB_TRACK' and t.GetLayer() in LAYERS:
            s, e = t.GetStart(), t.GetEnd()
            w, mk = seg_mask(nm(s.x), nm(s.y), nm(e.x), nm(e.y), 0.75 * G)
            i0, j0, i1, j1 = w
            m[LAYERS.index(t.GetLayer()), j0:j1, i0:i1] |= mk
    return m


OWN_EXT = LazyMasks(pad_extensions)
FINE = np.zeros((4, NY, NX), bool)   # rame delle piazzole a passo fine di tutte le reti
for _fp in board.GetFootprints():
    for _p in _fp.Pads():
        if _p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and min(nm(_p.GetSize(pcbnew.F_Cu).x), nm(_p.GetSize(pcbnew.F_Cu).y)) <= 0.45:
            for _li, _w, _m in item_masks(_p, G / 2):
                _i0, _j0, _i1, _j1 = _w
                FINE[_li, _j0:_j1, _i0:_i1] |= _m
OWN_AXIS = LazyMasks(track_axes)


NEIGH = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
         (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]


def route(code, src, dst, width, via_d, window, layers=None, via_goal=None):
    """A* da src a dst dentro la finestra; restituisce [(strato, i, j)] in coordinate di griglia o None.

    Con via_goal (maschera della scheda) l'arrivo è un punto di via libero dentro la maschera, sugli strati dati.
    """
    layers = layers or ROUTE
    wi0, wj0, wi1, wj1 = window
    cop = COP[:, wj0:wj1, wi0:wi1]
    s_m, d_m = src[:, wj0:wj1, wi0:wi1], dst[:, wj0:wj1, wi0:wi1]
    out_w = OUTSIDE[wj0:wj1, wi0:wi1]
    H, W = out_w.shape
    other = (cop != 0) & (cop != code)
    hw = width / 2
    free = {}
    for li in layers:
        f = ~(dilate(other[li], CLEAR + hw) | dilate(out_w, EDGE + hw))
        # Dentro il rame della stessa rete (piazzole prolungate in asse a passo fine) se la pista non ne
        # sporge, e lungo l'asse delle sue piste: lì la distanza dalle altre reti è già quella del rame esistente.
        edge_ok = ~dilate(out_w, EDGE + hw)
        ext = OWN_EXT[code][li][wj0:wj1, wi0:wi1] & ~dilate(other[li] & ~FINE[li, wj0:wj1, wi0:wi1], CLEAR + hw)  # oltre la piazzola niente altro rame
        own = (cop[li] == code) | ext
        # il rame dipinto è allargato di mezza cella: erosione di hw + G/2 perché la pista non sporga
        free[li] = (f | (own & ~dilate(~own, hw + G / 2) & edge_ok)
                    | (OWN_AXIS[code][li][wj0:wj1, wi0:wi1] & edge_ok))
    via_ok = ~dilate(out_w, EDGE + via_d / 2)
    for li in range(4):
        via_ok &= ~dilate(other[li], CLEAR + via_d / 2)
    starts = [(li, int(i), int(j)) for li in layers for j, i in zip(*np.nonzero(s_m[li] & free[li]))]
    if via_goal is None:
        goal = {li: d_m[li] & free[li] & ~s_m[li] for li in layers}
    else:
        goal = {li: via_goal[wj0:wj1, wi0:wi1] & via_ok & free[li] for li in layers}
    if not starts or not any(g.any() for g in goal.values()):
        return None
    gj, gi = np.nonzero(np.any(np.stack([goal[li] for li in layers]), axis=0))
    gx0, gx1, gy0, gy1 = int(gi.min()), int(gi.max()), int(gj.min()), int(gj.max())

    def h(i, j):
        return math.hypot(max(gx0 - i, 0, i - gx1), max(gy0 - j, 0, j - gy1))

    best, prev, heap = {}, {}, []
    for s in starts:
        best[s] = 0.0
        prev[s] = None
        heapq.heappush(heap, (h(s[1], s[2]), 0.0, s))
    n = 0
    while heap:
        f, g, s = heapq.heappop(heap)
        if g > best.get(s, 1e18):
            continue
        li, i, j = s
        if goal[li][j, i]:
            path = []
            while s is not None:
                path.append((s[0], s[1] + wi0, s[2] + wj0))
                s = prev[s]
            return path[::-1]
        n += 1
        if n > 4_000_000:
            return None
        fr = free[li]
        for di, dj, c in NEIGH:
            ni, nj = i + di, j + dj
            if 0 <= ni < W and 0 <= nj < H and fr[nj, ni]:
                t = (li, ni, nj)
                ng = g + c * LAYER_COST[li]
                if ng < best.get(t, 1e18):
                    best[t] = ng
                    prev[t] = s
                    heapq.heappush(heap, (ng + h(ni, nj), ng, t))
        if via_ok[j, i]:
            for l2 in layers:
                if l2 != li and free[l2][j, i]:
                    t = (l2, i, j)
                    ng = g + VIA_COST
                    if ng < best.get(t, 1e18):
                        best[t] = ng
                        prev[t] = s
                        heapq.heappush(heap, (ng + h(i, j), ng, t))
    return None


def windows(src):
    """Finestra attorno al gruppo da collegare, poi tutta la scheda."""
    _, js, is_ = np.nonzero(src)
    n = int(WINDOW / G)
    return [(max(0, int(is_.min()) - n), max(0, int(js.min()) - n), min(NX, int(is_.max()) + n + 1),
             min(NY, int(js.max()) + n + 1)), (0, 0, NX, NY)]


def add_path(code, path, width, via_d, via_h):
    """Converte il percorso in piste (tratti rettilinei) e via; aggiorna la mappa del rame."""
    pt = lambda i, j: pcbnew.VECTOR2I(mm(float(X0 + i * G)), mm(float(Y0 + j * G)))
    new = []
    k = 0
    while k < len(path) - 1:
        li, i, j = path[k]
        if path[k + 1][0] != li:  # cambio di strato: via (una sola per punto)
            here = pt(i, j)
            if not any(t.GetClass() == 'PCB_VIA' and t.GetPosition() == here for t in board.GetTracks()):
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(here)
                v.SetWidth(mm(via_d))
                v.SetDrill(mm(via_h))
                v.SetNetCode(code)
                board.Add(v)
                new.append(v)
            while k < len(path) - 1 and path[k + 1][1:] == (i, j):
                k += 1
            continue
        d = (path[k + 1][1] - i, path[k + 1][2] - j)
        m = k + 1
        while (m < len(path) - 1 and path[m + 1][0] == li
               and (path[m + 1][1] - path[m][1], path[m + 1][2] - path[m][2]) == d):
            m += 1
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pt(i, j))
        t.SetEnd(pt(path[m][1], path[m][2]))
        t.SetWidth(mm(width))
        t.SetLayer(LAYERS[li])
        t.SetNetCode(code)
        board.Add(t)
        new.append(t)
        k = m
    for it in new:
        for li, w, m in item_masks(it, G / 2):
            paint(COP, li, w, m, code)
    OWN_AXIS.pop(code, None)
    return new


def fill():
    pcbnew.ZONE_FILLER(board).Fill(ZONES)


def stitch_islands():
    """Isole dei riempimenti di massa senza via: una via verso il piano continuo In1 in ciascuna."""
    gnd = board.FindNet('GND').GetNetCode()
    width, via_d, via_h = netclass(gnd)
    vias = [(nm(t.GetPosition().x), nm(t.GetPosition().y)) for t in board.GetTracks()
            if t.GetClass() == 'PCB_VIA' and t.GetNetCode() == gnd]
    added = 0
    for z in ZONES:
        if z.GetIsRuleArea() or z.GetNetCode() != gnd or z.GetLayer() == pcbnew.In1_Cu:
            continue
        polys = z.GetFilledPolysList(z.GetLayer())
        areas = [(polys.Outline(i).Area(), i) for i in range(polys.OutlineCount())]
        if len(areas) < 2:
            continue
        biggest = max(areas)[1]
        for _, i in areas:
            ol = polys.Outline(i)
            if i == biggest or any(ol.PointInside(pcbnew.VECTOR2I(mm(x), mm(y))) for x, y in vias):
                continue
            pts = chain_pts(ol)
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            (i0, j0, i1, j1), m = poly_mask(pts, min(xs), min(ys), max(xs), max(ys))
            cop = COP[:, j0:j1, i0:i1]
            ok = m & ~dilate(~m, via_d / 2 + G) & ~dilate(OUTSIDE[j0:j1, i0:i1], EDGE + via_d / 2)
            for li in range(4):
                ok &= ~dilate((cop[li] != 0) & (cop[li] != gnd), CLEAR + via_d / 2)
            cand = np.argwhere(ok)
            if not len(cand):
                continue
            j, i = cand[len(cand) // 2]
            x, y = float(X0 + (i0 + i) * G), float(Y0 + (j0 + j) * G)
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            v.SetWidth(mm(via_d))
            v.SetDrill(mm(via_h))
            v.SetNetCode(gnd)
            board.Add(v)
            vias.append((x, y))
            for li, w, mk in item_masks(v, G / 2):
                paint(COP, li, w, mk, gnd)
            added += 1
    return added


# Uscita fissa dei piedini della USB-C HRO TYPE-C-31-M-12 (passo 0,5 mm, VBUS accanto ai perni di plastica). D+ e D- sono alternati
# (B7 D-, A6 D+, A7 D-, B6 D+): sullo stesso strato le coppie si incrocerebbero, quindi ogni piedino scende
# fino a una via sfalsata e le coppie si uniscono sugli altri strati. Coordinate (dx, dy) in mm rispetto al
# centro in x di A6 e al fondo delle piazzole; distanze verificate a mano: 0,2 mm tra rame, 0,8 mm tra le via.
USB_C_FANOUT = {
    'A4': ([(-1.95, 0.21), (-1.95, 1.36), (-2.25, 1.66)], True),   # VBUS sinistro: accanto al perno, poi via
    'A5': ([(-1.0, 0.36), (-1.5, 0.86), (-1.5, 2.36)], True),     # CC1
    'B7': ([(-0.5, 0.66), (-0.8, 0.96), (-0.8, 1.46)], True),     # D-
    'A6': ([(0.0, 2.56)], True),                                  # D+
    'A7': ([(0.5, 1.61), (0.75, 1.86)], True),                    # D-
    'B6': ([(1.0, 0.81), (1.3, 1.11)], True),                     # D+
    'B5': ([(2.0, 1.91), (1.75, 2.16)], True),                    # CC2
    'A9': ([(2.7, 0.11), (2.45, 0.36), (2.45, 2.76)], True),      # VBUS destro: accanto al perno, poi via
}


def usb_c_fanout():
    placed = 0
    for fp in board.GetFootprints():
        if not fp.GetFPID().GetLibItemName().wx_str().startswith('USB_C_Receptacle_HRO_TYPE-C-31-M-12'):
            continue
        pads = {p.GetNumber(): p for p in fp.Pads()}
        a6 = pads['A6']
        x0 = nm(a6.GetPosition().x)
        y0 = nm(a6.GetPosition().y) + nm(a6.GetSize(pcbnew.F_Cu).y) / 2
        codes = {pads[n].GetNetCode() for n in USB_C_FANOUT}
        olds = [t for t in board.GetTracks() if t.GetNetCode() in codes]
        for t in olds:
            board.Remove(t)
        REMOVED.extend(olds)
        new = []
        for num, (pts, via) in USB_C_FANOUT.items():
            p = pads[num]
            code = p.GetNetCode()
            width, via_d, via_h = netclass(code)
            chain = [(nm(p.GetPosition().x), nm(p.GetPosition().y))] + [(x0 + dx, y0 + dy) for dx, dy in pts]
            for (xa, ya), (xb, yb) in zip(chain, chain[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
                t.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
                t.SetWidth(mm(0.2))
                t.SetLayer(p.GetLayer())
                t.SetNetCode(code)
                board.Add(t)
                new.append(t)
            if via:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(mm(chain[-1][0]), mm(chain[-1][1])))
                v.SetWidth(mm(via_d))
                v.SetDrill(mm(via_h))
                v.SetNetCode(code)
                board.Add(v)
                new.append(v)
        RIPPED.update(pads[n].GetNetCode() for n in USB_C_FANOUT)  # l'uscita fissa non va tolta come ostacolo
        # Piste di altre reti troppo vicine all'uscita (non la massa): tolte, saranno ritracciate.
        build_copper()
        near = np.zeros((NY, NX), bool)
        for it in new:
            for li, w, m in item_masks(it, 0.7):
                i0, j0, i1, j1 = w
                near[j0:j1, i0:i1] |= m
        gnd = board.FindNet('GND').GetNetCode()
        hit = {int(v) for li in range(4) for v in np.unique(COP[li][near])} - {0, -1, gnd} - codes
        olds = [t for t in board.GetTracks() if t.GetNetCode() in hit]
        for t in olds:
            board.Remove(t)
        REMOVED.extend(olds)
        placed += len(new)
    build_copper()
    return placed


removed = remove_bad_tracks()
print('piste tolte (bordo o larghezza):', removed)
ZONES = [z for z in board.Zones()]
RIPPED = set()  # reti tolte e ritracciate da capo (una volta sola)
PRIORITY = []   # reti rimaste bloccate: nel giro successivo si tracciano per prime
board.BuildConnectivity()
print('uscita fissa della USB-C, piste e via:', usb_c_fanout(), flush=True)
def route_all(rounds=6):
    """Giri di sbroglio finché restano collegamenti aperti o isole da cucire."""
    for giro in range(rounds):
        fill()
        board.BuildConnectivity()
        build_copper()
        todo = []
        for code in sorted({p.GetNetCode() for fp in board.GetFootprints() for p in fp.Pads() if p.GetNetCode() > 0}):
            cls = clusters(code)
            if len(cls) > 1:
                todo.append((code, cls))
        todo.sort(key=lambda t: t[0] not in PRIORITY)
        missing = sum(len(c) - 1 for _, c in todo)
        isl = stitch_islands()
        print(f'giro {giro + 1}: collegamenti aperti {missing}, via nelle isole di massa {isl}', flush=True)
        if not missing and not isl:
            break
        done = failed = 0
        for code, cls in todo:
            width, via_d, via_h = netclass(code)
            name = board.FindNet(code).GetNetname()
            has_pad = lambda cl: any(it.GetClass() == 'PAD' for it in cl)
            cls.sort(key=lambda cl: (has_pad(cl), len(cl)), reverse=True)
            main = cluster_mask(cls[0])
            for small in cls[1:]:
                if not has_pad(small):  # pezzi di pista o via staccati da tutto: si tolgono
                    for it in small:
                        board.Remove(it)
                    REMOVED.extend(small)
                    build_copper()
                    done += 1
                    continue
                src = cluster_mask(small)
                path = None
                # prima la larghezza della classe, poi la minima di segnale per uscire da piazzole strette
                for w, vd, vh in [(width, via_d, via_h)] + ([(0.2, 0.6, 0.3)] if width > 0.2 else []):
                    for win in windows(src):
                        path = route(code, src, main, w, vd, win)
                        if path is not None:
                            break
                    if path is not None:
                        add_path(code, path, w, vd, vh)
                        break
                if path is None:
                    failed += 1
                    p0 = small[0].GetPosition()
                    print(f'  {name}: percorso non trovato da ({nm(p0.x):.2f}; {nm(p0.y):.2f}),'
                          f' {len(small)} elementi', flush=True)
                    # Rete bloccata: si tolgono le sue piste e quelle delle reti di segnale che la chiudono nel
                    # raggio di 1,5 mm dai due capi; nel giro successivo si traccia prima lei, poi le altre.
                    ends = np.any(src, axis=0) | (np.any(main, axis=0) if name != 'GND' else False)
                    near = dilate(ends, 1.5)  # attorno a entrambi i capi (per la massa solo il gruppo staccato)
                    blockers = {int(v) for li in ROUTE for v in np.unique(COP[li][near])} - {0, -1, code}
                    blockers = {b for b in blockers if b not in RIPPED and netclass(b)[0] <= 0.25
                                and sum(t.GetNetCode() == b for t in board.GetTracks()) <= 60}
                    rip = ({code} if name != 'GND' and code not in RIPPED else set()) | blockers
                    if rip:
                        RIPPED.update(rip)
                        PRIORITY.append(code)
                        olds = [t for t in board.GetTracks() if t.GetNetCode() in rip]
                        for t in olds:
                            board.Remove(t)
                        REMOVED.extend(olds)
                        names = ', '.join(board.FindNet(b).GetNetname() for b in sorted(rip))
                        print(f'  tolte {len(olds)} piste e via di {names}: da ritracciare', flush=True)
                        build_copper()
                        done += 1
                    break
                main |= src
                done += 1
        print(f'  tracciati {done}, non riusciti {failed}', flush=True)
        if not done and not isl:
            break


DRC_FIX = {'clearance', 'shorting_items', 'copper_edge_clearance', 'track_width', 'hole_clearance',
           'hole_to_hole', 'holes_co_located', 'tracks_crossing', 'via_diameter', 'annular_width',
           'track_dangling', 'via_dangling'}   # anche gli avvisi: fori troppo vicini, tratti e via morti


def drc_bad_items():
    """Piste e via coinvolte in errori o avvisi del DRC di KiCad (distanze, corti, bordo, fori, tratti morti)."""
    pcbnew.SaveBoard(str(PCB), board)
    out = PCB.with_suffix('.drc.json')
    cli = Path(sys.executable).parent / 'kicad-cli.exe'
    subprocess.run([str(cli), 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', str(out), str(PCB)],
                   capture_output=True, text=True)
    data = json.loads(out.read_text(encoding='utf-8'))
    out.unlink()
    uuids = {it['uuid'] for v in data.get('violations', []) if v.get('type') in DRC_FIX for it in v.get('items', [])}
    return [t for t in board.GetTracks() if t.m_Uuid.AsString() in uuids]


route_all()
# Controllo finale con il DRC di KiCad: piste e via in errore (anche lasciate da Freerouting) tolte e ritracciate.
for prova in range(6):
    fill()
    bad = drc_bad_items()
    print(f'DRC: {len(bad)} piste e via in errore', flush=True)
    if not bad:
        break
    for t in bad:
        board.Remove(t)
    REMOVED.extend(bad)
    route_all()
fill()
pcbnew.SaveBoard(str(PCB), board)
print(PCB)
