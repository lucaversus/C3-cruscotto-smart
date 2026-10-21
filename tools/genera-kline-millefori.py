"""Disposizione su millefori del modulo K-line KL-001 rev F (C3AI-DL-KL-003).

Rev. A: vista dal lato componenti, passo 2,54 mm, scala 4:1. Ogni collegamento è un filo
(isolato se lungo, nudo o stagno se tra fori adiacenti) saldato sul lato saldature ai
piedini indicati. Il generatore verifica che i fili realizzino esattamente le reti dello
schema KL-001 rev F e che nessun foro sia usato da due elementi.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

COLS, ROWS = 24, 16                     # A..X, 1..16
PITCH, SCALE = 2.54, 4.0
OX, OY = 52.0, 50.0                     # foro A1 sul foglio
STEP = PITCH * SCALE
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWX'


def hole(ref):
    return LETTERS.index(ref[0]), int(ref[1:]) - 1


def P(ref):
    c, r = hole(ref)
    return OX + c * STEP, OY + r * STEP


# Reti dello schema KL-001 rev F (data-logger/docs/kline-autocostruita.md, netlist).
NET_COLOR = {
    'GND': '#000000', '+5V': '#d00000', '+3V3': '#ff8c00', 'TX_INV': '#c8a000',
    'RX_3V3': '#008000', 'RX_RAW': '#6cbf3a', 'VSENSE': '#00a0c0', 'VREF': '#8040c0',
    'VBENCH': '#d040a0', 'K': '#0040d0', 'BASE': '#8b5a2b',
}

# Componenti: sigla -> {piedino: (foro, rete)}
COMP = {
    'X1': {'1': ('A4', 'RX_3V3'), '2': ('A6', 'TX_INV'), '3': ('A8', '+5V'), '4': ('A10', '+3V3'), '5': ('A12', 'GND')},
    'X2': {'1': ('X5', 'K'), '2': ('X8', 'VBENCH'), '3': ('X11', 'GND')},
    'U1': {'8': ('L8', '+5V'), '7': ('M8', None), '6': ('N8', 'VREF'), '5': ('O8', 'GND'),
           '1': ('L11', 'RX_RAW'), '2': ('M11', 'VREF'), '3': ('N11', 'VSENSE'), '4': ('O11', 'GND')},
    'C1': {'1': ('K9', '+5V'), '2': ('K10', 'GND')},
    'C2': {'+': ('J9', '+5V'), '-': ('J10', 'GND')},
    'R9': {'a': ('C4', 'RX_3V3'), 'b': ('G4', 'RX_RAW')},
    'R8': {'a': ('C10', '+3V3'), 'b': ('G10', 'RX_RAW')},
    'R10': {'a': ('H13', 'RX_RAW'), 'b': ('L13', 'VSENSE')},
    'R4': {'a': ('Q11', 'VSENSE'), 'b': ('U11', 'K')},
    'R5': {'a': ('Q13', 'VSENSE'), 'b': ('U13', 'GND')},
    'R6': {'a': ('Q3', 'VREF'), 'b': ('U3', 'VBENCH')},
    'R7': {'a': ('Q4', 'VREF'), 'b': ('U4', 'GND')},
    'R1': {'a': ('Q6', 'TX_INV'), 'b': ('U6', 'BASE')},
    'R2': {'a': ('U7', 'BASE'), 'b': ('U9', 'GND')},
    'Q1': {'C': ('W5', 'K'), 'B': ('W6', 'BASE'), 'E': ('W7', 'GND')},
}
BODIES = [f'{c}{r}' for c in 'LMNO' for r in (9, 10)]     # interno dello zoccolo U1

# Bus nudo di massa (stagno o filo nudo lungo la fila 16).
BUSES = [('GND', [f'{LETTERS[c]}16' for c in range(0, COLS)])]

# Fili sotto lo zoccolo (lato saldature), fissati a mano.
FIXED = [('VREF', ['M11', 'M9', 'N9', 'N8']), ('GND', ['O11', 'O8']),
         ('+5V', ['A8', 'J8']), ('+5V', ['J8', 'K8']), ('+5V', ['K8', 'L8']), ('GND', ['O11', 'O16'])]
NET_ORDER = ['VREF', '+5V', 'RX_3V3', 'TX_INV', '+3V3', 'RX_RAW', 'VSENSE', 'VBENCH', 'BASE', 'K', 'GND']


def route():
    """Instrada ogni rete con fili ortogonali che non si toccano né si sovrappongono."""
    from collections import deque
    owner = {}                       # cella -> rete (piedini, bus, fili)
    nodes = {}                       # rete -> celle a cui saldare (piedini, bus, estremi dei fili)
    blocked = set()
    for comp, pins in COMP.items():
        for pin, (h, net) in pins.items():
            owner[hole(h)] = net or 'NC'
            if net:
                nodes.setdefault(net, set()).add(hole(h))
        if comp.startswith('R'):
            (c1, r1), (c2, r2) = hole(pins['a'][0]), hole(pins['b'][0])
            if r1 == r2:
                blocked |= {(c, r1) for c in range(min(c1, c2) + 1, max(c1, c2))}
            else:
                blocked |= {(c1, r) for r in range(min(r1, r2) + 1, max(r1, r2))}
    blocked |= {hole(h) for h in BODIES}
    for net, holes in BUSES:
        for h in holes:
            owner[hole(h)] = net
            nodes.setdefault(net, set()).add(hole(h))
    wires = [(net, list(path)) for net, path in FIXED]
    used = {}                        # cella -> 'h', 'v' o 'both' (fili che la attraversano)
    for net, path in FIXED:
        nodes[net] |= {hole(path[0]), hole(path[-1])}
        pts = [hole(h) for h in path]
        for (c1, r1), (c2, r2) in zip(pts, pts[1:]):
            cells = [(c, r1) for c in range(min(c1, c2), max(c1, c2) + 1)] if r1 == r2 else                     [(c1, r) for r in range(min(r1, r2), max(r1, r2) + 1)]
            for c in cells:
                if c in (pts[0], pts[-1]) or c in owner:
                    continue
                o = 'h' if r1 == r2 else 'v'
                used[c] = 'both' if (c in used and used[c] != o) or c in pts else o

    def connected(net):
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                x = parent[x]
            return x
        for n, holes in BUSES:
            if n == net:
                for a, b in zip(holes, holes[1:]):
                    parent[find(hole(a))] = find(hole(b))
        for n, path in wires:
            if n == net:
                parent[find(hole(path[0]))] = find(hole(path[-1]))
        return find

    for net in NET_ORDER:
        pins = sorted(h for comp in COMP.values() for h, n in comp.values() if n == net)
        while True:
            find = connected(net)
            bus = [h for n, holes in BUSES if n == net for h in holes]
            main = find(hole(bus[0])) if bus else find(hole(pins[0]))
            rest = [h for h in pins if find(hole(h)) != main]
            if not rest:
                break
            start = rest[0]
            s0 = hole(start)
            targets = {c for c in nodes[net] if find(c) == main}
            # Ricerca in ampiezza su (cella, direzione): si può attraversare un filo di
            # un'altra rete solo ad angolo retto e senza svoltare nell'incrocio.
            start_state = (s0, None)
            prev = {start_state: None}
            q = deque([start_state])
            found = None
            while q:
                cur, d0 = q.popleft()
                if cur in targets and cur != s0:
                    found = (cur, d0)
                    break
                crossing = cur in used and cur != s0
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    d1 = 'h' if dc else 'v'
                    if crossing and d1 != d0:
                        continue
                    nxt = (cur[0] + dc, cur[1] + dr)
                    if not (0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS):
                        continue
                    state = (nxt, d1)
                    if state in prev or nxt in blocked:
                        continue
                    if nxt in owner and (owner[nxt] != net or nxt not in targets):
                        continue
                    if nxt in used and (used[nxt] == 'both' or used[nxt] == d1 or nxt in targets):
                        continue
                    prev[state] = (cur, d0)
                    q.append(state)
            assert found, f'instradamento impossibile per {net} da {start}'
            cells = []
            st = found
            while st is not None:
                cells.append(st[0])
                st = prev[st]
            cells.reverse()
            pts = [cells[0]]
            for a_, b_, c_ in zip(cells, cells[1:], cells[2:]):
                if (a_[0] == b_[0] == c_[0]) or (a_[1] == b_[1] == c_[1]):
                    continue
                pts.append(b_)
            pts.append(cells[-1])
            turns = set(pts)
            for a_, b_ in zip(cells, cells[1:]):
                pass
            for i, c in enumerate(cells[1:-1], start=1):
                o = 'h' if cells[i - 1][1] == c[1] == cells[i + 1][1] else ('v' if cells[i - 1][0] == c[0] == cells[i + 1][0] else 'both')
                if c in turns:
                    o = 'both'
                used[c] = 'both' if (c in used and used[c] != o) else o
            nodes[net] |= {cells[0], cells[-1]}
            wires.append((net, [f'{LETTERS[x]}{y + 1}' for x, y in pts]))
    return wires


WIRES = route()


def verify():
    """Reti realizzate dai fili e dai bus = reti dello schema; un solo uso per foro."""
    owner = {}
    for comp, pins in COMP.items():
        for pin, (h, _) in pins.items():
            assert h not in owner, f'foro {h} usato da {owner[h]} e {comp}:{pin}'
            owner[h] = f'{comp}:{pin}'
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    pin_net = {h: net for pins in COMP.values() for h, net in pins.values()}
    for net, holes in BUSES:
        for h in holes:
            if h in pin_net:
                assert pin_net[h] == net, f'bus {net} sul foro {h} della rete {pin_net[h]}'
        for a, b in zip(holes, holes[1:]):
            union(a, b)
    for net, path in WIRES:
        for end in (path[0], path[-1]):
            if end in pin_net:
                assert pin_net[end] == net, f'filo {net} su {end} della rete {pin_net[end]}'
        union(path[0], path[-1])
    groups = {}
    for h, net in pin_net.items():
        if net is None:
            continue
        groups.setdefault(net, set()).add(find(h))
    for net, roots in groups.items():
        assert len(roots) == 1, f'rete {net} divisa in {len(roots)} parti'
    roots = {net: next(iter(r)) for net, r in groups.items()}
    assert len(set(roots.values())) == len(roots), 'due reti diverse collegate insieme'
    # Leggibilità: nessun tratto sovrapposto a un tratto di altra rete e nessun filo che
    # passi su un piedino di altra rete (eccetto sotto lo zoccolo U1, lato saldature).
    under_socket = {f'{c}{r}' for c in 'LMNO' for r in (9, 10)}
    segs = []
    for net, path in WIRES:
        for a, b in zip(path, path[1:]):
            segs.append((net, hole(a), hole(b)))
    for net, holes in BUSES:
        segs.append((net, hole(holes[0]), hole(holes[-1])))

    def cells(a, b):
        (c1, r1), (c2, r2) = a, b
        if c1 == c2:
            return {(c1, r) for r in range(min(r1, r2), max(r1, r2) + 1)}
        if r1 == r2:
            return {(c, r1) for c in range(min(c1, c2), max(c1, c2) + 1)}
        raise AssertionError(f'tratto non ortogonale {a} {b}')
    for i, (n1, a1, b1) in enumerate(segs):
        for n2, a2, b2 in segs[i + 1:]:
            if n1 == n2:
                continue
            both_h = a1[1] == b1[1] and a2[1] == b2[1] and a1[1] == a2[1]
            both_v = a1[0] == b1[0] and a2[0] == b2[0] and a1[0] == a2[0]
            if (both_h or both_v) and len(cells(a1, b1) & cells(a2, b2)) > 0:
                raise AssertionError(f'tratti sovrapposti {n1} {a1}-{b1} e {n2} {a2}-{b2}')
    pins = {hole(h): net for h, net in pin_net.items()}
    for n, a, b in segs:
        for cell in cells(a, b):
            other = pins.get(cell)
            name = f'{LETTERS[cell[0]]}{cell[1] + 1}'
            if other is not None and other != n and name not in under_socket:
                raise AssertionError(f'filo {n} passa sul piedino {name} della rete {other}')
            if other is None and cell in pins and name not in under_socket:
                raise AssertionError(f'filo {n} passa sul piedino libero {name}')
    return len(WIRES)


def resistor_bands(ohms, precise):
    colors = ['#000000', '#8b4513', '#ff0000', '#ff8c00', '#ffd700', '#008000', '#0000ff', '#8a2be2', '#808080', '#ffffff']
    digits = 3 if precise else 2
    s = f'{ohms:.{digits}g}'.replace('.', '')
    mant = int(f'{ohms:.{digits}e}'.split('e')[0].replace('.', ''))
    exp = int(f'{ohms:.{digits}e}'.split('e')[1]) - (digits - 1)
    bands = [colors[int(ch)] for ch in str(mant).zfill(digits)] + [colors[exp] if exp >= 0 else '#d4af37']
    bands.append('#8b4513' if precise else '#d4af37')   # tolleranza 1% marrone, 5% oro
    return bands


RES = {'R1': (330, False), 'R2': (47000, False), 'R4': (68000, True), 'R5': (10000, True), 'R6': (150000, True),
       'R7': (10000, True), 'R8': (4700, True), 'R9': (1000, False), 'R10': (330000, True)}
RES_LABEL = {'R1': '330 Ω', 'R2': '47 kΩ', 'R4': '68 kΩ 1%', 'R5': '10 kΩ 1%', 'R6': '150 kΩ 1%', 'R7': '10 kΩ 1%',
             'R8': '4,7 kΩ 1%', 'R9': '1 kΩ', 'R10': '330 kΩ 1%'}


def draw():
    n = verify()
    d = Sheet('C3AI-DL-KL-003 rev A — K-line su millefori')
    d.frame()
    d.text(25, 20, 'MODULO K-LINE KL-001 REV F — DISPOSIZIONE SU MILLEFORI (VISTA LATO COMPONENTI, SCALA 4:1)', 5, bold=True)
    d.text(25, 25, f'Basetta a fori isolati passo 2,54 mm, {COLS} × {ROWS} fori. Disposizione verificata dal generatore: '
                   f'{n} fili realizzano esattamente le reti dello schema KL-001 rev F. Prototipo da banco, non collaudato.', 2.5)
    # Basetta e fori
    x0, y0 = OX - STEP * 0.8, OY - STEP * 0.8
    d.raw(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{(COLS - 1 + 1.6) * STEP:.2f}" height="{(ROWS - 1 + 1.6) * STEP:.2f}" '
          f'rx="2" fill="#e9d8a6" stroke="#000" stroke-width="0.5"/>')
    for c in range(COLS):
        d.text(OX + c * STEP, y0 - 1.5, LETTERS[c], 2.5, 'middle', True)
    for r in range(ROWS):
        d.text(x0 + 2.2, OY + r * STEP + 0.8, str(r + 1), 2.2, 'middle', True)
        d.text(x0 + (COLS - 1 + 1.6) * STEP - 2.2, OY + r * STEP + 0.8, str(r + 1), 2.2, 'middle', True)
        for c in range(COLS):
            d.raw(f'<circle cx="{OX + c * STEP:.2f}" cy="{OY + r * STEP:.2f}" r="1.6" fill="#c08040" stroke="#7a4a1a" stroke-width="0.2"/>'
                  f'<circle cx="{OX + c * STEP:.2f}" cy="{OY + r * STEP:.2f}" r="0.55" fill="#ffffff"/>')
    # Bus
    for net, holes in BUSES:
        (xa, ya), (xb, yb) = P(holes[0]), P(holes[-1])
        d.raw(f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" y2="{yb:.2f}" stroke="#909090" stroke-width="2.2" stroke-linecap="round"/>'
              f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" y2="{yb:.2f}" stroke="{NET_COLOR[net]}" stroke-width="0.6" stroke-dasharray="2 2"/>')
    # Fili
    for net, path in WIRES:
        pts = ' '.join(f'{P(h)[0]:.2f},{P(h)[1]:.2f}' for h in path)
        d.raw(f'<polyline points="{pts}" fill="none" stroke="{NET_COLOR[net]}" stroke-width="1.4" '
              f'stroke-linejoin="round" stroke-linecap="round" opacity="0.9"/>')
        for end in (path[0], path[-1]):
            x, y = P(end)
            d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.0" fill="{NET_COLOR[net]}" stroke="#000" stroke-width="0.2"/>')
    # Resistenze
    for ref, (ohms, precise) in RES.items():
        (xa, ya), (xb, yb) = P(COMP[ref]['a'][0]), P(COMP[ref]['b'][0])
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        horizontal = abs(ya - yb) < 0.1
        w, h = (12, 4.2) if horizontal else (4.2, 12)
        d.raw(f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" y2="{yb:.2f}" stroke="#606060" stroke-width="0.6"/>')
        d.raw(f'<rect x="{mx - w / 2:.2f}" y="{my - h / 2:.2f}" width="{w}" height="{h}" rx="1.8" fill="{"#8fb8e8" if precise else "#e8d2a0"}" stroke="#000" stroke-width="0.3"/>')
        bands = resistor_bands(ohms, precise)
        for i, col in enumerate(bands):
            off = -4 + i * (8 / (len(bands) - 1))
            if horizontal:
                d.raw(f'<rect x="{mx + off - 0.45:.2f}" y="{my - h / 2:.2f}" width="0.9" height="{h}" fill="{col}"/>')
            else:
                d.raw(f'<rect x="{mx - w / 2:.2f}" y="{my + off - 0.45:.2f}" width="{w}" height="0.9" fill="{col}"/>')
        tx, ty = (mx, my - 3.4) if horizontal else (mx + 3.5, my)
        d.text(tx, ty, f'{ref} {RES_LABEL[ref]}', 2.2, 'middle' if horizontal else 'start', True)
    # U1: zoccolo DIP-8 con adattatore (tacca a sinistra, piedino 1 in basso a sinistra)
    (xa, ya), (xb, yb) = P(COMP['U1']['8'][0]), P(COMP['U1']['4'][0])
    d.raw(f'<rect x="{xa - 3:.2f}" y="{ya - 3:.2f}" width="{xb - xa + 6:.2f}" height="{yb - ya + 6:.2f}" rx="1" fill="#303030" stroke="#000" stroke-width="0.4"/>')
    d.raw(f'<path d="M{xa - 3:.2f} {(ya + yb) / 2 - 2:.2f} a2 2 0 0 1 0 4" fill="#e9d8a6" stroke="#000" stroke-width="0.3"/>')
    d.raw(f'<text x="{(xa + xb) / 2:.2f}" y="{(ya + yb) / 2 - 1:.2f}" font-size="2.8" text-anchor="middle" font-weight="bold" fill="#ffffff" font-family="Arial">U1 LM2903B</text>')
    d.raw(f'<text x="{(xa + xb) / 2:.2f}" y="{(ya + yb) / 2 + 3:.2f}" font-size="2" text-anchor="middle" fill="#ffffff" font-family="Arial">su adattatore SOIC-8 → DIP-8</text>')
    for pin, (h, _) in COMP['U1'].items():
        x, y = P(h)
        d.raw(f'<rect x="{x - 1.3:.2f}" y="{y - 1.3:.2f}" width="2.6" height="2.6" fill="#d0d0d0" stroke="#000" stroke-width="0.2"/>')
        d.raw(f'<text x="{x:.2f}" y="{y + 0.8:.2f}" font-size="2.2" text-anchor="middle" font-weight="bold" font-family="Arial">{pin}</text>')
    # Condensatori
    for ref, shape in (('C1', 'disc'), ('C2', 'elec')):
        holes = list(COMP[ref].values())
        (x1, y1), (x2, y2) = P(holes[0][0]), P(holes[1][0])
        cx, cy = (x1 + x2) / 2 - 3.6, (y1 + y2) / 2
        if shape == 'disc':
            d.raw(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="2.4" ry="3.4" fill="#e0a020" stroke="#000" stroke-width="0.3"/>')
            d.text(cx + 2, cy + 8.5, 'C1 100 nF', 2.2, 'middle', True)
        else:
            d.raw(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="3.2" fill="#203080" stroke="#000" stroke-width="0.3"/>'
                  f'<rect x="{cx - 3.2:.2f}" y="{cy + 0.8:.2f}" width="6.4" height="1.2" fill="#c0c0c0"/>')
            d.text(cx - 4.5, cy + 1, 'C2 10 µF', 2.2, 'end', True)
            d.text(cx - 4.5, cy + 4, '(− in basso)', 2, 'end')
        for (h, _) in holes:
            x, y = P(h)
            d.raw(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="#606060" stroke-width="0.5"/>')
    # Q1 TO-92, piedini in colonna
    hs = [P(h) for h, _ in COMP['Q1'].values()]
    xq = hs[0][0]
    # Lato piatto a destra (verso -X2), parte arrotondata a sinistra.
    d.raw(f'<path d="M{xq + 2.5:.2f} {hs[0][1] - 3:.2f} L{xq + 2.5:.2f} {hs[-1][1] + 3:.2f} '
          f'A 5 {(hs[-1][1] - hs[0][1]) / 2 + 3:.2f} 0 0 1 {xq + 2.5:.2f} {hs[0][1] - 3:.2f} Z" fill="#202020" stroke="#000" stroke-width="0.3" opacity="0.92"/>')
    for pin, (h, _) in COMP['Q1'].items():
        x, y = P(h)
        d.raw(f'<text x="{x - 1.4:.2f}" y="{y + 0.9:.2f}" font-size="2.4" text-anchor="end" font-weight="bold" fill="#ffffff" font-family="Arial">{pin}</text>')
    d.text(xq - 6.5, hs[1][1] - 1, 'Q1 2N5551', 2.4, 'end', True)
    d.text(xq - 6.5, hs[1][1] + 2.2, '(E-B-C dal datasheet)', 2, 'end')
    # Morsettiere
    for ref, label in (('X1', ['1 RX→GPIO16', '2 TX←GPIO17', '3 +5V', '4 +3V3', '5 GND']),
                       ('X2', ['1 K', '2 VBENCH', '3 GND'])):
        holes = [h for h, _ in COMP[ref].values()]
        xs = [P(h)[0] for h in holes]; ys = [P(h)[1] for h in holes]
        left = ref == 'X1'
        bx = min(xs) - 3.75
        d.raw(f'<rect x="{bx:.2f}" y="{min(ys) - 3:.2f}" width="7.5" height="{max(ys) - min(ys) + 6:.2f}" fill="#2e8b57" stroke="#000" stroke-width="0.3"/>')
        for (h, _), text in zip(COMP[ref].values(), label):
            x, y = P(h)
            d.raw(f'<circle cx="{bx + 3.75:.2f}" cy="{y:.2f}" r="2" fill="#c0c0c0" stroke="#000" stroke-width="0.3"/>')
            edge = x0 if left else x0 + (COLS - 1 + 1.6) * STEP
            d.text(edge - 1.5 if left else edge + 1.5, y + 1, text, 2.4, 'end' if left else 'start', True)
        d.text(bx + 3.75, min(ys) - 4.5, f'-{ref}', 3, 'middle', True)
    # Legenda reti
    LX, LY = 334, 46
    d.text(LX, LY, 'COLORI DEI FILI (RETI)', 3.5, bold=True)
    for i, (net, col) in enumerate(NET_COLOR.items()):
        y = LY + 5 + i * 5
        d.raw(f'<line x1="{LX:.2f}" y1="{y - 1:.2f}" x2="{LX + 10:.2f}" y2="{y - 1:.2f}" stroke="{col}" stroke-width="1.6"/>')
        d.text(LX + 13, y, net, 2.6)
    d.notes(LX, LY + 70, 'COME LEGGERE', [
        'Pallino colorato = saldatura del filo',
        'sul piedino o sul foro.',
        'Incrocio di fili senza pallino = nessun',
        'contatto (fili isolati).',
        'Grigio tratteggiato = bus di massa nudo',
        '(fila 16), stagno o filo nudo.',
        'Resistenze 1% in azzurro, 5% in beige;',
        'bande colorate come sul componente.',
        'R3 (510 Ω 1 W) NON va sulla basetta:',
        'solo simulatore esterno (D-018).',
    ], h=2.4, step=4.0)
    d.notes(LX, LY + 120, 'ORDINE DI MONTAGGIO', [
        '1 Fili e bus di massa, poi resistenze.',
        '2 Zoccolo U1 (tacca a sinistra), C1, C2 (polarità).',
        '3 Q1 per ultimo, orientato col datasheet.',
        '4 Morsettiere X1 e X2.',
        '5 Controllo a vista e continuità a',
        '  circuito spento PRIMA dell\'adattatore U1.',
    ], h=2.4, step=4.0)
    # Elenco dei fili (estremi da saldare), in due colonne
    d.text(25, 214, 'ELENCO DEI FILI (estremi da saldare; percorso come nel disegno)', 3.2, bold=True)
    half = (len(WIRES) + 1) // 2
    for i, (net, path) in enumerate(WIRES):
        col, row = divmod(i, half)
        x, y = 25 + col * 100, 219.5 + row * 3.3
        d.raw(f'<line x1="{x:.2f}" y1="{y - 0.9:.2f}" x2="{x + 5:.2f}" y2="{y - 0.9:.2f}" stroke="{NET_COLOR[net]}" stroke-width="1.4"/>')
        pts = [hole(h) for h in path]
        under = any((c, r) in {hole(b) for b in BODIES} for (c1, r1), (c2, r2) in zip(pts, pts[1:])
                    for c in range(min(c1, c2), max(c1, c2) + 1) for r in range(min(r1, r2), max(r1, r2) + 1))
        note = ' (sotto lo zoccolo, lato saldature)' if under else ''
        d.text(x + 7, y, f'{i + 1:2d}  {net:7s} {path[0]} → {path[-1]}{note}', 2.3)
    d.title_block(title=['K-line su', 'millefori'], subtitle='Data Logger',
                  doc_type='Disposizione di montaggio', status='PROPOSTO · NON COLLAUDATO',
                  code='C3AI-DL-KL-003', rev='A', date='22/10/2026', sheet='1/1',
                  revisions=[('A', 'Prima emissione da KL-001 rev F; reti verificate dal generatore', '22/10/2026')])
    out = ROOT / 'disegni/sorgenti/DL-KL-003_kline-millefori.svg'
    out.write_text(d.svg('Disposizione dei componenti del modulo K-line KL-001 rev F su millefori; prototipo non collaudato.'),
                   encoding='utf-8')
    print(out, 'fili', n)


if __name__ == '__main__':
    draw()
