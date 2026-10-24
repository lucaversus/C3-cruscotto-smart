"""Schema elettrico della scheda madre (KiCad 10), foglio alimentazione: C3AI-CR-EL-001.

Uso (qualsiasi Python 3, nessuna libreria esterna):
  python tools/genera-schema-scheda-madre.py
Crea cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch con i simboli copiati dalle
librerie standard di KiCad 10 (cartella symbols dell'installazione). Dentro ogni blocco i
collegamenti sono fili disegnati; le etichette restano per le reti che vanno ad altri blocchi
o fogli. Le reti volute sono scritte accanto a ogni componente: se kicad-cli è disponibile,
il netlist esportato da KiCad viene confrontato con queste e ogni differenza blocca.
Valori da datasheet (TPS54360B fig. 32, LMR36510 tab. 8-1/8-3, LM74700-Q1): proposta non
verificata, da ricontrollare prima dell'ordine dei componenti (D-030, D-031, D-046).
Il file va rigenerato da qui: le modifiche fatte a mano in KiCad si perdono.
"""
from pathlib import Path
from collections import Counter
import math
import os
import re
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch'
KICAD = Path(os.environ.get('KICAD10_SHARE', r'C:\Program Files\KiCad\10.0\share\kicad'))
SYM = KICAD / 'symbols'
FPDIR = KICAD / 'footprints'
KICAD_CLI = KICAD.parents[1] / 'bin' / 'kicad-cli.exe'
NS = uuid.UUID('6b1c3a52-7e0e-4d55-9c1e-c3a1c3a1c3a1')
ROOT_UUID = str(uuid.uuid5(NS, 'root'))


def uid(key):
    return str(uuid.uuid5(NS, key))


# --- librerie --------------------------------------------------------------------------
_libs = {}


def lib_symbol(lib_id):
    lib, name = lib_id.split(':')
    if lib not in _libs:
        _libs[lib] = (SYM / f'{lib}.kicad_sym').read_text(encoding='utf-8')
    m = re.search(r'\n\t\(symbol "%s"\n(.*?)\n\t\)' % re.escape(name), _libs[lib], re.S)
    assert m, f'simbolo non trovato: {lib_id}'
    body = m.group(1)
    ext = re.search(r'\(extends "([^"]+)"\)', body)
    if ext:  # simbolo derivato: disegno e piedini del padre, proprietà del figlio (come salva KiCad)
        parent = ext.group(1)
        pm = re.search(r'\n\t\(symbol "%s"\n(.*?)\n\t\)' % re.escape(parent), _libs[lib], re.S)
        assert pm, f'simbolo padre non trovato: {parent}'
        def props(text):  # blocchi (property ...) completi, con le parentesi bilanciate
            out = {}
            for mm in re.finditer(r'\(property "([^"]+)"', text):
                depth, i = 0, mm.start()
                while True:
                    depth += {'(': 1, ')': -1}.get(text[i], 0)
                    i += 1
                    if depth == 0:
                        break
                out[mm.group(1)] = (mm.start(), i)
            return out
        pbody = pm.group(1).replace(f'(symbol "{parent}_', f'(symbol "{name}_')
        child = {k: body[a:b] for k, (a, b) in props(body).items()}
        parent_props = props(pbody)
        for k, (a, b) in sorted(parent_props.items(), key=lambda t: -t[1][0]):
            if k in child:
                pbody = pbody[:a] + child.pop(k) + pbody[b:]
        if child:  # proprietà presenti solo nel figlio: dopo l'ultima del padre
            end = max(b for _, b in props(pbody).values())
            pbody = pbody[:end] + ''.join('\n\t\t' + v for v in child.values()) + pbody[end:]
        body = pbody
    pins = {}
    units = [(mm.start(), int(mm.group(1))) for mm in re.finditer(r'\(symbol "%s_(\d+)_\d+"' % re.escape(name), body)]
    for p in re.finditer(r'\(pin \w+ \w+\s+\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(number "([^"]*)"', body, re.S):
        unit = [u for pos, u in units if pos < p.start()][-1]  # unità del sottosimbolo che contiene il piedino
        pins.setdefault(p.group(4), []).append((float(p.group(1)), float(p.group(2)), int(p.group(3)), unit))
    return f'\t\t(symbol "{lib_id}"\n{body}\n\t\t)', pins


def check_fp(fp):
    lib, name = fp.split(':')
    base = OUT.parent if lib == 'scheda-madre' else FPDIR  # libreria del progetto (fp-lib-table) o standard
    assert (base / f'{lib}.pretty' / f'{name}.kicad_mod').is_file(), f'impronta non trovata: {fp}'
    return fp


# --- primitive del disegno -------------------------------------------------------------
def fnum(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def key(p):
    return (round(p[0], 3), round(p[1], 3))


def effects(justify='', hide=False, size=1.27):
    j = f' (justify {justify})' if justify else ''
    h = ' (hide yes)' if hide else ''
    return f'(effects (font (size {size} {size})){j}{h})'


def prop(name, value, x, y, justify='', hide=False, angle=0):
    value = value.replace('\\', '\\\\').replace('"', '\\"')
    return (f'\t\t(property "{name}" "{value}" (at {fnum(x)} {fnum(y)} {angle}) '
            f'{"(hide yes) " if hide else ""}{effects(justify)})\n')


def transform(px, py, rot, mirror):
    a = math.radians(rot)
    x, y = px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)
    return (-x if mirror else x), y


SHEETS = []        # fogli del progetto, il primo è la radice
items = []         # testo S-expression del foglio corrente
lib_defs = {}
CUR = ''           # file del foglio corrente (anche prefisso degli identificativi)
CUR_PATH = ''      # percorso gerarchico per le istanze dei simboli
PIN = {}           # 'R1.2' -> (x, y) assoluto
PINOUT = {}        # 'R1.2' -> direzione verso l'esterno del simbolo (0, 90, 180, 270)
INTENT = {}        # 'R1.2' -> rete voluta
ends = Counter()   # estremi di fili e piedini, per i pallini di giunzione
n_parts = 0
_pwr = 0


def begin_sheet(file, title, code, rev, decisions, sheet_uuid=None):
    """Apre un foglio: la radice (sheet_uuid None) o un sottofoglio richiamato dalla radice."""
    global items, lib_defs, ends, CUR, CUR_PATH
    sh = dict(file=file, title=title, code=code, rev=rev, decisions=decisions, uuid=sheet_uuid or ROOT_UUID,
              items=[], lib_defs={}, ends=Counter())
    SHEETS.append(sh)
    items, lib_defs, ends, CUR = sh['items'], sh['lib_defs'], sh['ends'], file
    CUR_PATH = f'/{ROOT_UUID}' + (f'/{sheet_uuid}' if sheet_uuid else '')


def sheet_box(file, name, x, y, w, h, page):
    """Riquadro di un sottofoglio nella radice; restituisce il suo identificativo."""
    su = uid(f'sheet/{file}')
    items.append(f'\t(sheet (at {fnum(x)} {fnum(y)}) (size {fnum(w)} {fnum(h)}) (exclude_from_sim no) (in_bom yes) '
                 f'(on_board yes) (dnp no) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) '
                 f'(uuid "{su}")\n'
                 + prop('Sheetname', name, x, y - 0.7, 'left bottom')
                 + prop('Sheetfile', file, x, y + h + 0.6, 'left top')
                 + f'\t\t(instances (project "scheda-madre" (path "/{ROOT_UUID}" (page "{page}"))))\n\t)\n')
    return su


def symbol(ref, lib_id, value, fp, x, y, rot=0, mirror=False, note='', nets=None, auto=False, txt=None, unit=1):
    """Posa un simbolo. nets = {piedino: rete voluta}; None = non collegato (croce).
    auto=True: ogni piedino riceve un tratto e un'etichetta (connettori verso altri fogli)."""
    global n_parts
    if fp:
        check_fp(fp)
    if lib_id not in lib_defs:
        lib_defs[lib_id] = lib_symbol(lib_id)
    _, lpins = lib_defs[lib_id]
    hidden = ref.startswith('#')
    pts = {}
    lpins = {n: [q for q in ps if q[3] in (0, unit)] for n, ps in lpins.items()}  # piedini di questa unità
    lpins = {n: ps for n, ps in lpins.items() if ps}
    for num, ps in lpins.items():
        px, py, ang, _ = ps[0]
        tx, ty = transform(px, py, rot, mirror)
        pts[num] = (x + tx, y - ty, ang)
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    if len(lpins) == 2 and max(xs) - min(xs) < 0.1:
        rpos, vpos, just = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27), 'left'
    elif len(lpins) == 2:
        rpos, vpos, just = (x, min(ys) - 3.81), (x, max(ys) + 3.81), ''
    else:
        rpos, vpos, just = (x, min(ys) - 6.35), (x, min(ys) - 3.81), ''
    if txt:  # posizione dei testi scelta a mano: ((dx, dy) riferimento, (dx, dy) valore, allineamento)
        (rdx, rdy), (vdx, vdy), just = txt
        rpos, vpos = (x + rdx, y + rdy), (x + vdx, y + vdy)
    ang = 90 if rot in (90, 270) else 0  # testi orizzontali e non capovolti anche sui simboli ruotati
    m = ' (mirror y)' if mirror else ''
    s = (f'\t(symbol (lib_id "{lib_id}") (at {fnum(x)} {fnum(y)} {rot}){m} (unit {unit}) (exclude_from_sim no) '
         f'(in_bom {"no" if hidden else "yes"}) (on_board {"no" if hidden else "yes"}) (dnp no) (uuid "{uid(ref if unit == 1 else f"{ref}/{unit}")}")\n')
    s += prop('Reference', ref, *rpos, just, hide=hidden, angle=ang)
    s += prop('Value', value, *vpos, just, hide=hidden, angle=ang)
    s += prop('Footprint', fp, x, y, hide=True)
    s += prop('Datasheet', '', x, y, hide=True)
    s += prop('Description', note, x, y, hide=True)
    for num in lpins:
        s += f'\t\t(pin "{num}" (uuid "{uid(ref + "/pin/" + num)}"))\n'
    s += f'\t\t(instances (project "scheda-madre" (path "{CUR_PATH}" (reference "{ref}") (unit {unit}))))\n\t)\n'
    items.append(s)
    if hidden:
        return pts
    n_parts += 1
    for num, (px, py, ang) in pts.items():
        PIN[f'{ref}.{num}'] = (px, py)
        out = (ang + 180 + rot) % 360
        PINOUT[f'{ref}.{num}'] = (180 - out) % 360 if mirror and out in (0, 180) else out
        net = (nets or {}).get(num, '__missing__')
        assert net != '__missing__', f'{ref}: piedino {num} senza rete'
        # Piedini sovrapposti scritti come "[1,15,38,39]": nel netlist compaiono uno per uno.
        for single in num.strip('[]').split(','):
            INTENT[f'{ref}.{single}'] = net
        ends[key((px, py))] += 1
        if net is None:
            items.append(f'\t(no_connect (at {fnum(px)} {fnum(py)}) (uuid "{uid(f"{CUR}/{ref}/nc/{num}")}"))\n')
        elif auto:
            tag(f'{ref}.{num}')
    return pts


def tag(pin):
    """Tratto di filo verso l'esterno del piedino con etichetta della sua rete (o simbolo di massa)."""
    x, y = PIN[pin]
    out, net = PINOUT[pin], INTENT[pin]
    dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[out]
    end = (x + 2.54 * dx, y + 2.54 * dy)
    wire((x, y), end)
    if net == 'GND':
        gnd(end, 0, rot={270: 0, 90: 180, 0: 90, 180: 270}[out])
    else:
        label(net, end, out)


def P(p):
    return PIN[p] if isinstance(p, str) else p


def wire(*pts):
    """Polilinea ortogonale tra punti o piedini ('R1.2')."""
    pts = [P(p) for p in pts]
    for a, b in zip(pts, pts[1:]):
        assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6, f'filo non ortogonale {a} {b}'
        assert key(a) != key(b), f'filo di lunghezza nulla in {a}'
        items.append(f'\t(wire (pts (xy {fnum(a[0])} {fnum(a[1])}) (xy {fnum(b[0])} {fnum(b[1])})) '
                     f'(stroke (width 0) (type default)) (uuid "{uid(f"{CUR}/w/{a}/{b}")}"))\n')
        ends[key(a)] += 1
        ends[key(b)] += 1


def label(net, p, direction=0):
    """Etichetta globale di rete, valida in tutti i fogli; direction = verso del testo
    (0 destra, 90 su, 180 sinistra, 270 giù)."""
    x, y = P(p)
    just = 'left' if direction in (0, 90) else 'right'
    items.append(f'\t(global_label "{net}" (shape passive) (at {fnum(x)} {fnum(y)} {direction}) '
                 f'(fields_autoplaced yes) {effects(just)} (uuid "{uid(f"{CUR}/l/{net}/{x}/{y}")}")\n'
                 f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {fnum(x)} {fnum(y)} 0) '
                 f'{effects(just, hide=True)}))\n')


def gnd(p, down=2.54, rot=0):
    """Simbolo di massa sotto il punto (con un tratto di filo se down > 0), o ruotato verso l'esterno."""
    global _pwr
    x, y = P(p)
    if down:
        wire((x, y), (x, y + down))
        y += down
    _pwr += 1
    symbol(f'#PWR{_pwr:03d}', 'power:GND', 'GND', '', x, y, rot)
    ends[key((x, y))] += 1


def flag(net, p):
    global _pwr
    x, y = P(p)
    _pwr += 1
    symbol(f'#FLG{_pwr:03d}', 'power:PWR_FLAG', 'PWR_FLAG', '', x, y)
    ends[key((x, y))] += 1


def text(x, y, t, size=2.0):
    items.append(f'\t(text "{t}" (exclude_from_sim no) (at {fnum(x)} {fnum(y)} 0) '
                 f'{effects("left bottom", size=size)} (uuid "{uid(f"{CUR}/text/{t}")}"))\n')


R0805 = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C0805 = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
C1206 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
C1210 = 'Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder'


def R(ref, value, x, y, a, b, rot=0, note='', txt=None):
    """Resistenza: verticale (piedino 1 in alto) o, con rot=90, orizzontale (piedino 1 a sinistra)."""
    return symbol(ref, 'Device:R', value, R0805, x, y, rot, nets={'1': a, '2': b}, note=note, txt=txt)


def C(ref, value, x, y, a, b, fp=C0805, rot=0, note=''):
    return symbol(ref, 'Device:C', value, fp, x, y, rot, nets={'1': a, '2': b}, note=note)


def shunt(ref, value, x, top, net, fp=C0805, kind='C', note=''):
    """Componente verticale tra una linea (piedino 1 a quota top) e massa."""
    f = C if kind == 'C' else R
    if kind == 'C':
        f(ref, value, x, top + 3.81, net, 'GND', fp=fp, note=note)
    else:
        f(ref, value, x, top + 3.81, net, 'GND', note=note)
    gnd(f'{ref}.2', 0)


begin_sheet('scheda-madre.kicad_sch', 'Scheda madre cruscotto C3+AI - alimentazione', 'C3AI-CR-EL-001', 'C',
            'D-030, D-031, D-044, D-046, D-047, D-048')
FE_SHEET = sheet_box('front-end.kicad_sch', 'Front-end', 279.4, 205.74, 38.1, 12.7, 2)
VEH_SHEET = sheet_box('interfacce-veicolo.kicad_sch', 'Interfacce veicolo', 279.4, 228.6, 38.1, 12.7, 3)
SENS_SHEET = sheet_box('sensori-memoria.kicad_sch', 'Sensori e memoria', 332.74, 205.74, 38.1, 12.7, 4)

# === J1: connettore verso l'auto (D-044), vie dalla tabella bozza di scheda-madre.md ======
J1_NETS = {1: 'VBAT_IN', 2: 'GND', 3: 'KEY_IN', 4: 'KLINE', 5: 'VAN_DATA', 6: 'VAN_DATAB', 7: 'VAN_GND_REF',
           8: 'RADIO_L_P', 9: 'RADIO_L_N', 10: 'SPK_L_P', 11: 'SPK_L_N', 12: 'RADIO_R_P', 13: 'RADIO_R_N',
           14: 'SPK_R_P', 15: 'SPK_R_N'}
symbol('J1', 'Connector_Generic:Conn_02x12_Top_Bottom', 'Micro-Fit 43045-2400 (D-044)',
       'Connector_Molex:Molex_Micro-Fit_3.0_43045-2400_2x12_P3.00mm_Horizontal', 45.72, 116.84,
       nets={str(i): J1_NETS.get(i) for i in range(1, 25)}, auto=True,
       note='Vie 16-24 riserva; assegnazione bozza (D-044)')
wire((30.48, 160.02), (30.48, 165.1))
flag('VBAT_IN', (30.48, 160.02))
label('VBAT_IN', (30.48, 165.1), 270)
flag('GND', (45.72, 160.02))
gnd((45.72, 160.02))

# === Ingresso 12 V e protezioni (-U1…U3, D-030) =======================================
Y = 45.72  # linea di alimentazione
symbol('D1', 'Device:D_TVS', 'SMCJ26CA', 'Diode_SMD:D_SMC', 83.82, Y + 3.81, rot=270,
       nets={'1': 'VBAT_IN', '2': 'GND'}, txt=((-2.54, -1.27), (-2.54, 1.27), 'right'), note='Bidirezionale 26 V, blocca ~42 V: sotto i 60-65 V dei regolatori')
gnd('D1.2', 0)
shunt('C1', '100nF 100V', 91.44, Y, 'VBAT_IN')
symbol('Q1', 'Transistor_FET:IPD50R380CE', 'IPD50N06S4L-12 (da confermare)', 'Package_TO_SOT_SMD:TO-252-2',
       121.92, Y + 2.54, rot=90, mirror=True, nets={'1': 'U1_GATE', '2': 'VBAT_P', '3': 'VBAT_IN'},
       txt=((0, -10.16), (0, -7.62), ''),
       note='MOSFET N 60 V: S verso la batteria, D verso il carico')
symbol('U1', 'Power_Management:LM74700', 'LM74700-Q1', 'Package_TO_SOT_SMD:SOT-23-6', 121.92, 68.58,
       txt=((8.89, 13.97), (8.89, 16.51), 'left'),
       nets={'1': 'U1_VCAP', '2': 'GND', '3': 'VBAT_IN', '4': 'VBAT_P', '5': 'U1_GATE', '6': 'VBAT_IN'},
       note='Diodo ideale: blocca inversione e ritorno di corrente durante l\'avviamento')
gnd('U1.2', 0)
C('C2', '100nF 25V', 101.6, 66.04, 'VBAT_IN', 'U1_VCAP', rot=90)
wire('C2.2', (106.68, 66.04), (106.68, 71.12), 'U1.1')
wire('U1.3', (97.79, 73.66), 'C2.1')
wire('C2.1', (97.79, Y))
wire('Q1.1', 'U1.5')
wire('U1.6', (114.3, Y))
wire('U1.4', (129.54, Y))
symbol('C3', 'Device:C_Polarized', '220uF 50V', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', 139.7, Y + 3.81,
       nets={'1': 'VBAT_P', '2': 'GND'}, note='Riserva per l\'avviamento (-C1), capacità da confermare')
gnd('C3.2', 0)
symbol('FB1', 'Device:FerriteBead', 'ferrite >= 3A, 1206', 'Inductor_SMD:L_1206_3216Metric_Pad1.22x1.90mm_HandSolder',
       157.48, Y, rot=90, nets={'1': 'VBAT_P', '2': '+12V_F'})
wire((78.74, Y), 'D1.1', 'C1.1', (97.79, Y), (114.3, Y), 'Q1.3')
wire('Q1.2', (129.54, Y), (134.62, Y), 'C3.1', (149.86, Y), 'FB1.1')
wire('FB1.2', (165.1, Y), (170.18, Y))
label('VBAT_IN', (78.74, Y), 180)
wire((134.62, Y), (134.62, Y - 5.08))
label('VBAT_P', (134.62, Y - 5.08), 90)
flag('VBAT_P', (149.86, Y))
flag('+12V_F', (165.1, Y))
label('+12V_F', (170.18, Y), 0)

# === Dominio principale 5 V 3,5 A (-U4): acceso da chiave O mantenimento (D-030) =======
Y5 = 40.64  # +12V_F in ingresso
symbol('U2', 'Regulator_Switching:TPS54360DDA', 'TPS54360B', 'Package_SO:TI_SO-PowerPAD-8_ThermalVias', 254, 63.5,
       nets={'1': 'U2_BOOT', '2': '+12V_F', '3': 'EN_5V', '4': 'U2_RT', '5': 'FB_5V', '6': 'U2_COMP', '7': 'GND',
             '8': 'SW_5V', '9': 'GND'}, note='Valori dall\'esempio 5 V / 3,5 A del datasheet (fig. 32)')
gnd('U2.7', 0)
gnd('U2.9', 0)
shunt('C4', '2.2uF 100V', 205.74, Y5, '+12V_F', fp=C1210)
shunt('C5', '2.2uF 100V', 220.98, Y5, '+12V_F', fp=C1210)
label('+12V_F', (198.12, Y5), 180)
wire((198.12, Y5), 'C4.1', 'C5.1', (238.76, Y5), (238.76, 58.42), 'U2.2')
shunt('R3', '162k', 233.68, 63.5, 'U2_RT', kind='R', note='600 kHz')
wire('U2.4', 'R3.1')
# Accensione: chiave tramite D3 e partitore R5/R6 (avvio ~8 V, arresto ~6,3 V) o GPIO13 tramite D4/R7.
wire('U2.3', (238.76, 71.12), (238.76, 88.9), (238.76, 101.6))
R('R5', '523k', 228.6, 88.9, 'KEY_D', 'EN_5V', rot=90)
symbol('D3', 'Device:D', '1N4148W', 'Diode_SMD:D_SOD-123', 215.9, 88.9, rot=180, nets={'1': 'KEY_D', '2': 'KEY_IN'})
wire('D3.1', 'R5.1')
wire('R5.2', (238.76, 88.9))
wire('D3.2', (209.55, 88.9))
label('KEY_IN', (209.55, 88.9), 180)
R('R7', '10k', 228.6, 101.6, 'HOLD_D', 'EN_5V', rot=90)
symbol('D4', 'Device:D_Schottky', 'BAT54J', 'Diode_SMD:D_SOD-323F', 215.9, 101.6, rot=180,
       nets={'1': 'HOLD_D', '2': 'PWR_HOLD'})
wire('D4.1', 'R7.1')
wire('R7.2', (238.76, 101.6))
R('R6', '84.5k', 238.76, 105.41, 'EN_5V', 'GND')
gnd('R6.2', 0)
R('R8', '100k', 205.74, 105.41, 'PWR_HOLD', 'GND', note='A riposo spento (GPIO13 flottante al reset)')
gnd('R8.2', 0)
wire('D4.2', 'R8.1', (200.66, 101.6))
label('PWR_HOLD', (200.66, 101.6), 180)
# Bootstrap, commutazione, diodo, induttanza e uscita.
C('C6', '100nF', 271.78, 54.61, 'U2_BOOT', 'SW_5V')
wire('U2.1', (266.7, 58.42), (266.7, 48.26), (271.78, 48.26), 'C6.1')
wire('C6.2', (271.78, 63.5))
symbol('D2', 'Device:D_Schottky', 'B560C', 'Diode_SMD:D_SMC', 302.26, 67.31, rot=270, nets={'1': 'SW_5V', '2': 'GND'})
gnd('D2.2', 0)
symbol('L1', 'Device:L', '8.2uH Isat>=5A', 'Inductor_SMD:L_Bourns_SRR1260', 318.77, 63.5, rot=90,
       nets={'1': 'SW_5V', '2': '+5V'}, note='Es. Bourns SRR1260-8R2Y, da verificare corrente di saturazione')
wire('U2.8', (271.78, 63.5), 'D2.1', 'L1.1')
shunt('C7', '47uF 10V', 330.2, 63.5, '+5V', fp=C1210)
shunt('C8', '47uF 10V', 342.9, 63.5, '+5V', fp=C1210)
R('R1', '53.6k', 355.6, 67.31, '+5V', 'FB_5V')
R('R2', '10.2k', 355.6, 80.01, 'FB_5V', 'GND')
gnd('R2.2', 0)
wire('L1.2', 'C7.1', 'C8.1', 'R1.1', (363.22, 63.5), (368.3, 63.5))
flag('+5V', (363.22, 63.5))
label('+5V', (368.3, 63.5), 0)
wire('R1.2', (355.6, 73.66), 'R2.1')
wire('U2.5', (266.7, 71.12), (266.7, 99.06), (363.22, 99.06), (363.22, 73.66), (355.6, 73.66))
# Compensazione.
C('C10', '39pF', 276.86, 69.85, 'U2_COMP', 'GND')
gnd('C10.2', 0)
R('R4', '13.0k', 287.02, 69.85, 'U2_COMP', 'U2_CZ')
C('C9', '6.8nF', 287.02, 80.01, 'U2_CZ', 'GND')
gnd('C9.2', 0)
wire('U2.6', 'C10.1', 'R4.1')
wire('R4.2', 'C9.1')

# === Dominio sempre acceso 3,3 V 1 A (-U5, D-031) =====================================
Y3 = 152.4
symbol('U3', 'Regulator_Switching:LMR36510ADDA', 'LMR36510',
       'Package_SO:Texas_HTSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias', 254, 172.72,
       nets={'1': 'GND', '2': '+12V_F', '3': '+12V_F', '4': None, '5': 'FB_3V3', '6': 'U3_VCC', '7': 'U3_BOOT',
             '8': 'SW_3V3', '9': 'GND'}, note='EN a VIN: sempre acceso; tabella 8-1/8-3 del datasheet')
gnd('U3.1', 0)
gnd('U3.9', 0)
shunt('C11', '2.2uF 100V', 205.74, Y3, '+12V_F', fp=C1210)
shunt('C12', '220nF 100V', 220.98, Y3, '+12V_F')
label('+12V_F', (198.12, Y3), 180)
wire((198.12, Y3), 'C11.1', 'C12.1', (238.76, Y3), (238.76, 167.64), 'U3.2')
wire('U3.3', (238.76, 172.72), (238.76, 167.64))
shunt('C13', '1uF', 233.68, 177.8, 'U3_VCC')
wire('U3.6', 'C13.1')
C('C14', '100nF', 271.78, 166.37, 'U3_BOOT', 'SW_3V3')
wire('U3.7', (266.7, 167.64), (266.7, 160.02), (271.78, 160.02), 'C14.1')
symbol('L2', 'Device:L', '22uH Isat>=1.5A', 'Inductor_SMD:L_Bourns_SRN6045TA', 281.94, 170.18, rot=90,
       nets={'1': 'SW_3V3', '2': '+3V3_AON'}, note='Es. Bourns SRN6045TA-220M, da verificare')
wire('U3.8', 'C14.2', 'L2.1')
for ref, x in (('C15', 294.64), ('C16', 307.34), ('C17', 320.04)):
    shunt(ref, '22uF 10V', x, 170.18, '+3V3_AON', fp=C1206)
R('R9', '100k', 332.74, 173.99, '+3V3_AON', 'FB_3V3')
R('R10', '43.2k', 332.74, 186.69, 'FB_3V3', 'GND')
gnd('R10.2', 0)
wire('L2.2', 'C15.1', 'C16.1', 'C17.1', 'R9.1', (340.36, 170.18), (345.44, 170.18))
flag('+3V3_AON', (340.36, 170.18))
label('+3V3_AON', (345.44, 170.18), 0)
wire('R9.2', (332.74, 180.34), 'R10.1')
wire('U3.5', (266.7, 175.26), (266.7, 195.58), (340.36, 195.58), (340.36, 180.34), (332.74, 180.34))

# === Misure per il front-end: chiave (GPIO39) e batteria (GPIO35) ======================
for (src, rtop, rbot, cap, dio, x0, rv, out, note) in (
        ('KEY_IN', 'R11', 'R12', 'C18', 'D5', 80.01, ('100k', '22k'), 'KEY_SENSE', '16 V -> 2,9 V'),
        ('VBAT_P', 'R13', 'R14', 'C19', 'D6', 160.02, ('470k', '100k'), 'VBAT_SENSE', '16 V -> 2,8 V; 21 uA a 12 V')):
    ym = 210.82
    R(rtop, rv[0], x0 + 8.89, ym, src, out, rot=90)
    shunt(rbot, rv[1], x0 + 19.05, ym, out, kind='R', note=note)
    shunt(cap, '100nF', x0 + 26.67, ym, out)
    symbol(dio, 'Diode:BAT54S', 'BAT54S', 'Package_TO_SOT_SMD:SOT-23', x0 + 44.45, ym + 5.08, rot=180,
           nets={'1': 'GND', '2': '+3V3_AON', '3': out})
    gnd(f'{dio}.1')
    wire(f'{dio}.2', (x0 + 36.83, ym + 10.16))
    label('+3V3_AON', (x0 + 36.83, ym + 10.16), 270)
    wire((x0, ym), f'{rtop}.1')
    label(src, (x0, ym), 180)
    wire(f'{rtop}.2', f'{rbot}.1', f'{cap}.1', f'{dio}.3', (x0 + 57.15, ym))
    label(out, (x0 + 57.15, ym), 0)

text(71.12, 30.48, 'INGRESSO 12 V E PROTEZIONI (D-030)')
text(195.58, 27.94, 'DOMINIO PRINCIPALE 5 V 3,5 A: S3, AUDIO (accensione: chiave O mantenimento)')
text(195.58, 142.24, 'DOMINIO SEMPRE ACCESO 3,3 V 1 A: FRONT-END, SENSORI (D-031)')
text(71.12, 198.12, 'MISURE PER IL FRONT-END: KEY_SENSE -> GPIO39, VBAT_SENSE -> GPIO35, PWR_HOLD <- GPIO13')
text(25.4, 236.22, 'Proposta preliminare, non verificata. Fusibile di ramo nel cablaggio (HW-FUSE-HOLDER). '
                   'Montaggio a mano (D-046): U2/U3 con piazzola esposta, saldatura dal retro attraverso i fori termici.', 1.27)
text(25.4, 241.3, 'Consumo a riposo stimato: U1 80 uA + U3 26 uA + partitori ~25 uA + front-end in sonno: < 1 mA (D-030), '
                  'da misurare.', 1.27)
text(25.4, 246.38, 'Sottofogli: front-end, interfacce veicolo, sensori e memoria. Collegamento con l’S3 e relè audio: '
                   'da disegnare dopo il rilievo dei connettori della S3. Etichette con lo stesso nome sono collegate.', 1.27)


# ======================================================================================
# Foglio 2: front-end ESP32 (C3AI-CR-EL-002; D-029, D-031, D-033, D-039)
# ======================================================================================
begin_sheet('front-end.kicad_sch', 'Scheda madre cruscotto C3+AI - front-end ESP32', 'C3AI-CR-EL-002', 'A',
            'D-029, D-031, D-033, D-039, D-046', sheet_uuid=FE_SHEET)
SOT23 = 'Package_TO_SOT_SMD:SOT-23'
NPN = 'Transistor_BJT:MMBT3904'

# --- Modulo ESP32-WROOM-32E: GPIO della tabella di scheda-madre.md (come il logger 0.3.x) ---
FE = {'2': '+3V3_AON', '[1,15,38,39]': 'GND', '3': 'FE_EN',
      '4': 'NTC_DISP', '5': 'KEY_SENSE', '6': 'VAN_RX', '7': 'VBAT_SENSE', '8': 'NTC_PCB', '9': 'FE_RX',
      '10': 'FE_TX', '11': 'FAN_PWM', '12': 'SD_CS', '13': 'FAN_TACH', '14': None, '16': 'PWR_HOLD',
      '23': None, '24': 'FAN_EN', '25': 'FE_IO0', '26': 'FE_LED', '27': 'KL_RX', '28': 'KL_TX', '29': None,
      '30': 'SD_SCK', '31': 'SD_MISO', '33': 'I2C_SDA', '34': 'FE_U0RXD', '35': 'FE_U0TXD', '36': 'I2C_SCL',
      '37': 'SD_MOSI'}
FE.update({n: None for n in ('17', '18', '19', '20', '21', '22', '32')})
symbol('U4', 'RF_Module:ESP32-WROOM-32E', 'ESP32-WROOM-32E-H4', 'RF_Module:ESP32-WROOM-32E', 203.2, 116.84,
       nets=FE, txt=((0, 43.18), (0, 45.72), ''), note='HW-FE-MODULE: variante H4/H8 (-40...+105 C), senza PSRAM; montaggio a mano (D-046)')
for n, net in FE.items():
    if net and n not in ('[1,15,38,39]', '2', '3'):
        tag(f'U4.{n}')
gnd('U4.[1,15,38,39]', 0)
shunt('C20', '22uF 10V', 213.36, 73.66, '+3V3_AON', fp=C1206)
shunt('C21', '100nF', 223.52, 73.66, '+3V3_AON')
wire('U4.2', (203.2, 73.66), 'C20.1', 'C21.1', (233.68, 73.66))
label('+3V3_AON', (233.68, 73.66), 0)
# EN: 10k + 1 uF (ritardo all'accensione raccomandato da Espressif), pulsante RESET, reset automatico.
R('R15', '10k', 172.72, 82.55, '+3V3_AON', 'FE_EN')
wire('R15.1', (172.72, 76.2))
label('+3V3_AON', (172.72, 76.2), 90)
shunt('C22', '1uF', 165.1, 86.36, 'FE_EN')
symbol('SW3', 'Switch:SW_Push', 'RESET', 'Button_Switch_THT:SW_PUSH_6mm', 157.48, 91.44, rot=90,
       nets={'1': 'GND', '2': 'FE_EN'}, txt=((0, 10.16), (0, 12.7), ''))
gnd('SW3.1', 0)
symbol('Q6', NPN, 'MMBT3904', SOT23, 147.32, 91.44, nets={'1': 'Q6_B', '2': 'CH_RTS', '3': 'FE_EN'},
       txt=((-5.08, -5.08), (-5.08, -2.54), 'right'))
wire('U4.3', 'R15.2', 'C22.1', 'SW3.2', 'Q6.3')
tag('Q6.2')
R('R35', '10k', 134.62, 91.44, 'CH_DTR', 'Q6_B', rot=90)
wire('R35.2', 'Q6.1')
wire('R35.1', (128.27, 91.44))
label('CH_DTR', (128.27, 91.44), 180)
symbol('Q7', NPN, 'MMBT3904', SOT23, 147.32, 127, nets={'1': 'Q7_B', '2': 'CH_DTR', '3': 'FE_IO0'},
       txt=((-5.08, -5.08), (-5.08, -2.54), 'right'))
tag('Q7.3')
tag('Q7.2')
R('R36', '10k', 134.62, 127, 'CH_RTS', 'Q7_B', rot=90)
wire('R36.2', 'Q7.1')
wire('R36.1', (128.27, 127))
label('CH_RTS', (128.27, 127), 180)

# --- Programmazione a banco: USB-C + CH340C alimentato solo dalla USB (nessun consumo in auto) ---
symbol('J3', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C (solo a banco)',
       'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', 35.56, 66.04,
       nets={'A4': 'USB_VBUS', 'A9': 'USB_VBUS', 'B4': 'USB_VBUS', 'B9': 'USB_VBUS', 'A5': 'USB_CC1',
             'B5': 'USB_CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DM', 'B7': 'USB_DM', 'A8': None,
             'B8': None, 'A1': 'GND', 'B1': 'GND', 'A12': 'GND', 'B12': 'GND', 'SH': 'GND'},
       note='Passo 0,5 mm: saldatura a trascinamento con flussante')
gnd('J3.A1', 0)
gnd('J3.SH', 0)
symbol('U5', 'Regulator_Linear:AP2112K-3.3', 'AP2112K-3.3', 'Package_TO_SOT_SMD:SOT-23-5', 76.2, 43.18,
       nets={'1': 'USB_VBUS', '2': 'GND', '3': 'USB_VBUS', '4': None, '5': '+3V3_USB'})
gnd('U5.2', 0)
shunt('C25', '1uF', 60.96, 40.64, 'USB_VBUS')
shunt('C26', '1uF', 86.36, 40.64, '+3V3_USB')
shunt('C27', '100nF', 104.14, 40.64, '+3V3_USB')
wire('J3.A4', (55.88, 50.8), (55.88, 45.72), (55.88, 40.64), 'C25.1', 'U5.1')
wire('U5.3', 'U5.1')
flag('USB_VBUS', (55.88, 45.72))
symbol('U6', 'Interface_USB:CH340C', 'CH340C', 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', 93.98, 66.04,
       nets={'1': 'GND', '2': 'CH_TXD', '3': 'CH_RXD', '4': 'CH_V3', '5': 'USB_DP', '6': 'USB_DM', '7': None,
             '8': None, '9': None, '10': None, '11': None, '12': None, '13': 'CH_DTR', '14': 'CH_RTS',
             '15': None, '16': '+3V3_USB'}, txt=((0, 20.32), (0, 22.86), ''))
gnd('U6.1', 0)
wire('U5.5', 'C26.1', (91.44, 40.64), (93.98, 40.64), 'C27.1')
wire((91.44, 40.64), 'U6.16')
R('R37', '0', 93.98, 46.99, '+3V3_USB', 'CH_V3', note='V3 collegato a VCC: CH340C alimentato a 3,3 V (datasheet)')
wire((93.98, 40.64), 'R37.1')
R('R31', '5.1k', 58.42, 58.42, 'USB_CC2', 'GND', rot=90, txt=((0, 2.54), (0, 5.08), ''))
gnd('R31.2', 0)
wire('J3.B5', 'R31.1')
R('R32', '5.1k', 66.04, 55.88, 'USB_CC1', 'GND', rot=90, txt=((0, -5.08), (0, -2.54), ''))
gnd('R32.2', 0)
wire('J3.A5', 'R32.1')
wire('J3.A7', (53.34, 63.5), (53.34, 66.04))
wire('J3.B7', (53.34, 66.04), 'U6.6')
wire('J3.A6', (55.88, 68.58), (55.88, 71.12), 'J3.B6')
wire((55.88, 68.58), (78.74, 68.58), (78.74, 63.5), 'U6.5')  # incrocia D- senza collegarsi
# Resistenze in serie: la UART0 del modulo non alimenta il CH340 spento attraverso i suoi diodi.
R('R33', '4.7k', 111.76, 55.88, 'CH_TXD', 'FE_U0RXD', rot=90, txt=((0, -5.08), (0, -2.54), ''))
R('R34', '4.7k', 111.76, 58.42, 'CH_RXD', 'FE_U0TXD', rot=90, txt=((0, 2.54), (0, 5.08), ''))
wire('U6.2', 'R33.1')
wire('U6.3', 'R34.1')
wire('R33.2', (120.65, 55.88))
label('FE_U0RXD', (120.65, 55.88), 0)
wire('R34.2', (120.65, 58.42))
label('FE_U0TXD', (120.65, 58.42), 0)
tag('U6.13')
tag('U6.14')

# --- Avvio, LED, I2C, collegamento con l'S3 -------------------------------------------
X0 = 256.54
label('FE_IO0', (X0, 60.96), 180)
R('R16', '10k', X0 + 7.62, 57.15, '+3V3_AON', 'FE_IO0')
symbol('SW4', 'Switch:SW_Push', 'BOOT', 'Button_Switch_THT:SW_PUSH_6mm', X0 + 15.24, 66.04, rot=90,
       nets={'1': 'GND', '2': 'FE_IO0'}, txt=((0, 10.16), (0, 12.7), ''))
gnd('SW4.1', 0)
wire((X0, 60.96), 'R16.2', 'SW4.2')
wire('R16.1', (X0 + 7.62, 50.8))
label('+3V3_AON', (X0 + 7.62, 50.8), 90)
label('FE_LED', (X0, 81.28), 180)
R('R17', '1k', X0 + 10.16, 81.28, 'FE_LED', 'LED_A', rot=90)
symbol('D7', 'Device:LED', 'verde', 'LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder', X0 + 25.4, 81.28,
       rot=180, nets={'1': 'GND', '2': 'LED_A'})
wire((X0, 81.28), 'R17.1')
wire('R17.2', 'D7.2')
wire('D7.1', (X0 + 31.75, 81.28))
gnd((X0 + 31.75, 81.28))
label('+3V3_AON', (X0, 96.52), 180)
R('R18', '4.7k', X0 + 10.16, 100.33, '+3V3_AON', 'I2C_SDA')
R('R19', '4.7k', X0 + 20.32, 100.33, '+3V3_AON', 'I2C_SCL')
wire((X0, 96.52), 'R18.1', 'R19.1')
for r in ('R18', 'R19'):
    tag(f'{r}.2')
# Collegamento seriale con l'S3 (fe_link): 1k in serie limitano la corrente verso l'S3 spenta.
label('FE_TX', (X0, 121.92), 180)
R('R20', '1k', X0 + 10.16, 121.92, 'FE_TX', 'LINK_FE2S3', rot=90)
wire((X0, 121.92), 'R20.1')
wire('R20.2', (X0 + 20.32, 121.92))
label('LINK_FE2S3', (X0 + 20.32, 121.92), 0)
label('FE_RX', (X0, 132.08), 180)
R('R21', '1k', X0 + 10.16, 132.08, 'FE_RX', 'LINK_S32FE', rot=90)
wire((X0, 132.08), 'R21.1')
wire('R21.2', (X0 + 20.32, 132.08))
label('LINK_S32FE', (X0 + 20.32, 132.08), 0)

# --- Temperature: NTC 100k sulla scheda (GPIO32) e vicino al display (GPIO36), 16 uA ciascuna ---
R('R22', '100k', X0 + 5.08, 151.13, '+3V3_AON', 'NTC_PCB')
wire('R22.1', (X0 + 5.08, 144.78))
label('+3V3_AON', (X0 + 5.08, 144.78), 90)
symbol('RT1', 'Device:Thermistor_NTC', 'NTC 100k B3950', R0805, X0 + 5.08, 158.75, nets={'1': 'NTC_PCB', '2': 'GND'},
       txt=((-3.81, -1.27), (-3.81, 1.27), 'right'))
gnd('RT1.2', 0)
shunt('C23', '100nF', X0 + 12.7, 154.94, 'NTC_PCB')
wire('R22.2', 'C23.1', (X0 + 20.32, 154.94))
label('NTC_PCB', (X0 + 20.32, 154.94), 0)
R('R23', '100k', X0 + 63.5, 151.13, '+3V3_AON', 'NTC_DISP')
wire('R23.1', (X0 + 63.5, 144.78))
label('+3V3_AON', (X0 + 63.5, 144.78), 90)
shunt('C24', '100nF', X0 + 71.12, 154.94, 'NTC_DISP')
symbol('J5', 'Connector_Generic:Conn_01x02', 'NTC display', 'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',
       X0 + 86.36, 154.94, nets={'1': 'NTC_DISP', '2': 'GND'}, note='NTC 100k incollata vicino al display')
wire('R23.2', 'C24.1', 'J5.1')
wire('J5.2', (X0 + 78.74, 157.48))
gnd((X0 + 78.74, 157.48))
wire('R23.2', (X0 + 55.88, 154.94))
label('NTC_DISP', (X0 + 55.88, 154.94), 180)

# --- Ventola 12 V (D-031): alimentazione staccata da Q3 a riposo, velocità PWM, giri ---------
label('+12V_F', (X0, 185.42), 180)
symbol('Q3', 'Transistor_FET:AO3401A', 'ZXMP6A13F (P 60 V)', SOT23, X0 + 22.86, 187.96, rot=90, mirror=True,
       nets={'1': 'Q3_G', '2': '+12V_F', '3': '+12V_FAN'}, txt=((0, -10.16), (0, -7.62), ''),
       note='P-MOSFET 60 V: la linea +12V_F arriva fino a ~42 V con il TVS')
R('R24', '6.8k', X0 + 12.7, 189.23, '+12V_F', 'Q3_G', note='Vgs -5,7 V a 14 V, -17 V a 42 V')
R('R25', '10k', X0 + 22.86, 196.85, 'Q3_G', 'Q4_C')
symbol('Q4', NPN, 'MMBTA06 (80 V)', SOT23, X0 + 20.32, 205.74, nets={'1': 'Q4_B', '2': 'GND', '3': 'Q4_C'},
       txt=((5.08, -1.27), (5.08, 1.27), 'left'))
gnd('Q4.2', 0)
wire((X0, 185.42), 'R24.1', 'Q3.2')
wire('R24.2', 'Q3.1')
R('R26', '10k', X0 + 2.54, 205.74, 'FAN_EN', 'Q4_B', rot=90)
R('R27', '100k', X0 + 10.16, 209.55, 'Q4_B', 'GND', note='Tiene la ventola spenta al reset (e GPIO2 basso)')
gnd('R27.2', 0)
wire((X0 - 5.08, 205.74), 'R26.1')
label('FAN_EN', (X0 - 5.08, 205.74), 180)
wire('R26.2', 'R27.1', 'Q4.1')
symbol('J4', 'Connector_Generic:Conn_01x04', 'Ventola Delta AFB0412VA-00 (D-052)', 'Connector:FanPinHeader_1x04_P2.54mm_Vertical',
       X0 + 68.58, 187.96, nets={'1': 'GND', '2': '+12V_FAN', '3': 'FAN_SENSE', '4': 'FAN_CTRL'},
       note='Fili Delta: nero GND, rosso +12V, blu giri, giallo PWM')
wire('Q3.3', (X0 + 50.8, 185.42), (X0 + 50.8, 187.96), 'J4.2')
for n in ('1', '3', '4'):
    tag(f'J4.{n}')
# Giri: uscita a collettore aperto della ventola, pull-up a 3,3 V e 1k in serie verso GPIO14.
label('FAN_SENSE', (X0 + 81.28, 210.82), 180)
R('R28', '10k', X0 + 88.9, 207.01, '+3V3_AON', 'FAN_SENSE')
R('R29', '1k', X0 + 99.06, 210.82, 'FAN_SENSE', 'FAN_TACH', rot=90)
wire((X0 + 81.28, 210.82), 'R28.2', 'R29.1')
wire('R28.1', (X0 + 88.9, 200.66))
label('+3V3_AON', (X0 + 88.9, 200.66), 90)
wire('R29.2', (X0 + 109.22, 210.82))
label('FAN_TACH', (X0 + 109.22, 210.82), 0)
# Velocità: ingresso PWM della ventola a 4 fili pilotato a collettore aperto (logica invertita).
symbol('Q5', NPN, 'MMBT3904', SOT23, X0 + 91.44, 236.22, nets={'1': 'Q5_B', '2': 'GND', '3': 'FAN_CTRL'},
       txt=((5.08, -1.27), (5.08, 1.27), 'left'))
gnd('Q5.2', 0)
tag('Q5.3')
R('R30', '1k', X0 + 78.74, 236.22, 'FAN_PWM', 'Q5_B', rot=90)
wire('R30.2', 'Q5.1')
wire((X0 + 68.58, 236.22), 'R30.1')
label('FAN_PWM', (X0 + 68.58, 236.22), 180)

text(25.4, 27.94, 'PROGRAMMAZIONE A BANCO: USB-C + CH340C, alimentati solo dalla USB')
text(124.46, 76.2, 'RESET AUTOMATICO (DTR/RTS)', 1.5)
text(160.02, 60.96, 'FRONT-END ESP32-WROOM-32E (D-029)')
text(X0 + 12.7, 43.18, 'AVVIO, LED, I2C, COLLEGAMENTO CON L\'S3')
text(X0 + 10.16, 139.7, 'TEMPERATURE: NTC 100k (D-031)')
text(X0 - 10.16, 172.72, 'VENTOLA 12 V A 4 FILI (D-031)')
text(25.4, 236.22, 'Proposta preliminare, non verificata. GPIO dalla tabella di cruscotto/docs/scheda-madre.md; '
                   'GPIO2 (accensione ventola) nuovo, pin di avvio: deve restare basso al reset (R27).', 1.27)
text(25.4, 241.3, 'USB-C e CH340C solo per la programmazione a banco; in auto aggiornamenti via S3 (D-039). '
                  'K-line, VAN, IMU, RTC, MicroSD e collegamento all\'S3 (J2): fogli successivi.', 1.27)
text(25.4, 246.38, 'Etichette con lo stesso nome sono collegate, anche tra fogli diversi.', 1.27)

# ======================================================================================
# Foglio 3: interfacce veicolo, K-line e VAN (C3AI-CR-EL-003; D-008, D-022, D-033)
# ======================================================================================
begin_sheet('interfacce-veicolo.kicad_sch', 'Scheda madre cruscotto C3+AI - interfacce veicolo', 'C3AI-CR-EL-003',
            'B', 'D-008, D-022, D-029, D-033, D-046, D-051', sheet_uuid=VEH_SHEET)
SOIC8 = 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'

# --- K-line: circuito KL-001 rev F (data-logger/docs/kline-autocostruita.md) con protezioni ---
YK = 50.8
label('KLINE', (30.48, YK), 180)
symbol('D8', 'Device:D_TVS', 'SMBJ26CA', 'Diode_SMD:D_SMB', 40.64, YK + 3.81, rot=270,
       nets={'1': 'KLINE', '2': 'GND'}, note='Aggiunta per l\'auto: transitori sulla linea K')
gnd('D8.2', 0)
symbol('D9', 'Device:D', '1N4148W', 'Diode_SMD:D_SOD-123', 55.88, 58.42, rot=90, nets={'1': 'KL_COLL', '2': 'KLINE'}, txt=((-2.54, -1.27), (-2.54, 1.27), 'right'),
       note='Aggiunta per l\'auto: con la linea negativa il transistor non conduce al contrario')
symbol('Q8', NPN, 'MMBT5551', SOT23, 53.34, 67.31, nets={'1': 'KL_BASE', '2': 'GND', '3': 'KL_COLL'},
       txt=((5.08, -1.27), (5.08, 1.27), 'left'), note='Versione SMD del 2N5551 della rev F')
gnd('Q8.2', 0)
R('R38', '330', 40.64, 67.31, 'KL_TX', 'KL_BASE', rot=90, txt=((0, -5.08), (0, -2.54), ''))
R('R39', '47k', 46.99, 71.12, 'KL_BASE', 'GND', txt=((-2.54, -1.27), (-2.54, 1.27), 'right'))
gnd('R39.2', 0)
wire('R38.2', 'R39.1', 'Q8.1')
wire((30.48, 67.31), 'R38.1')
label('KL_TX', (30.48, 67.31), 180)
R('R40', '68k', 81.28, 54.61, 'KLINE', 'KL_VSENSE')
R('R41', '10k', 81.28, 62.23, 'KL_VSENSE', 'GND')
gnd('R41.2', 0)
wire((30.48, YK), 'D8.1', (55.88, YK), 'R40.1')
wire('D9.2', (55.88, YK))
symbol('U7', 'Comparator:LM2903', 'LM2903B', SOIC8, 101.6, 60.96, unit=1,
       nets={'1': 'KL_RAW', '2': 'KL_VREF', '3': 'KL_VSENSE'}, txt=((0, 7.62), (0, 10.16), ''))
wire('R40.2', (88.9, 58.42), 'U7.3')
R('R42', '150k', 83.82, 76.2, 'KEY_IN', 'KL_VREF', rot=90,
  note='Soglia riferita alla linea chiave invece che alla batteria: nessun consumo a riposo')
R('R43', '10k', 91.44, 80.01, 'KL_VREF', 'GND')
gnd('R43.2', 0)
wire('U7.2', (91.44, 63.5), 'R43.1')
wire('R42.2', (91.44, 76.2), (96.52, 76.2))
label('KL_VREF', (96.52, 76.2), 0)
wire('R42.1', (76.2, 76.2))
label('KEY_IN', (76.2, 76.2), 180)
R('R44', '330k', 101.6, 48.26, 'KL_VSENSE', 'KL_RAW', rot=90, note='Isteresi (D-022)')
wire((88.9, 58.42), (88.9, 48.26), 'R44.1')
wire('R44.2', (114.3, 48.26), (114.3, 60.96), 'U7.1')
R('R45', '4.7k', 121.92, 57.15, '+3V3_AON', 'KL_RAW')
wire('R45.1', (121.92, 50.8))
label('+3V3_AON', (121.92, 50.8), 90)
R('R46', '1k', 132.08, 60.96, 'KL_RAW', 'KL_RX', rot=90)
wire((114.3, 60.96), 'R45.2', 'R46.1')
wire('R46.2', (142.24, 60.96))
label('KL_RX', (142.24, 60.96), 0)
# Seconda metà del comparatore non usata (come rev F) e alimentazione dal 5 V principale.
symbol('U7', 'Comparator:LM2903', 'LM2903B', SOIC8, 101.6, 91.44, unit=2,
       nets={'5': 'GND', '6': 'KL_VREF', '7': None}, txt=((0, 7.62), (0, 10.16), ''))
tag('U7.5')
tag('U7.6')
symbol('U7', 'Comparator:LM2903', 'LM2903B', SOIC8, 101.6, 116.84, unit=3, nets={'4': 'GND', '8': '+5V'},
       txt=((5.08, -1.27), (5.08, 1.27), 'left'))
gnd('U7.4', 0)
shunt('C28', '100nF', 106.68, 104.14, '+5V')
symbol('C29', 'Device:C_Polarized', '10uF 16V', 'Capacitor_SMD:CP_Elec_4x5.4', 116.84, 107.95,
       nets={'1': '+5V', '2': 'GND'})
gnd('C29.2', 0)
wire('U7.8', (99.06, 104.14), 'C28.1', 'C29.1', (124.46, 104.14))
label('+5V', (124.46, 104.14), 0)

# --- VAN: modulo blu SN65HVD230 (HW-CAN-VP230) su file di pin, sola ricezione (D-051) ----
HDR = 'Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical'
symbol('J8', 'Connector_Generic:Conn_01x04', 'Modulo VAN: 3.3V GND RX TX', HDR % 4, 231.14, 66.04,
       nets={'1': '+3V3_SW', '2': 'GND', '3': 'VAN_RX', '4': '+3V3_SW'}, txt=((0, 10.16), (0, 12.7), ''),
       note='Modulo con resistenza 121 rimossa (VAN-M002); TX al 3,3 V sulla scheda: trasmettitore sempre recessivo')
shunt('C30', '100nF', 213.36, 53.34, '+3V3_SW')
wire((205.74, 53.34), 'C30.1', (220.98, 53.34), (220.98, 63.5), 'J8.1')
label('+3V3_SW', (205.74, 53.34), 180)
tag('J8.2')
tag('J8.4')
R('R47', '100k', 208.28, 72.39, 'VAN_RX', 'GND', txt=((-2.54, -1.27), (-2.54, 1.27), 'right'),
  note='GPIO34 non ha resistenze interne: livello definito con il modulo spento')
gnd('R47.2', 0)
wire('J8.3', 'R47.1', (200.66, 68.58))
label('VAN_RX', (200.66, 68.58), 180)
symbol('J9', 'Connector_Generic:Conn_01x02', 'Modulo VAN: CANH CANL', HDR % 2, 309.88, 66.04,
       nets={'1': 'VAN_DATA', '2': 'VAN_DATAB'}, note='Interasse con J8 da misurare sul modulo')
symbol('D10', 'Power_Protection:NUP2105L', 'NUP2105L', SOT23, 284.48, 67.31, rot=90,
       nets={'1': 'VAN_DATAB', '2': 'VAN_DATA', '3': 'GND'}, txt=((0, -7.62), (0, -5.08), ''),
       note='Protezione dai transitori sulle due linee VAN')
tag('D10.3')
wire((269.24, 64.77), (274.32, 64.77), 'D10.2')
wire((274.32, 64.77), (274.32, 58.42), (302.26, 58.42), (302.26, 66.04), 'J9.1')
label('VAN_DATA', (269.24, 64.77), 180)
wire((269.24, 69.85), (276.86, 69.85), 'D10.1')
wire((276.86, 69.85), (276.86, 76.2), (299.72, 76.2), (299.72, 68.58), 'J9.2')
label('VAN_DATAB', (269.24, 69.85), 180)
# 3,3 V acceso con il dominio principale: VAN solo a quadro acceso, nessun consumo a riposo.
symbol('U9', 'Regulator_Linear:AP2112K-3.3', 'AP2112K-3.3', 'Package_TO_SOT_SMD:SOT-23-5', 233.68, 104.14,
       nets={'1': '+5V', '2': 'GND', '3': '+5V', '4': None, '5': '+3V3_SW'})
gnd('U9.2', 0)
shunt('C31', '1uF', 218.44, 101.6, '+5V')
shunt('C32', '1uF', 248.92, 101.6, '+3V3_SW')
wire((210.82, 101.6), 'C31.1', 'U9.1')
label('+5V', (210.82, 101.6), 180)
wire('U9.3', 'U9.1')
wire('U9.5', 'C32.1', (256.54, 101.6))
label('+3V3_SW', (256.54, 101.6), 0)

text(25.4, 33.02, 'K-LINE: KL-001 REV F CON PROTEZIONI PER L\'AUTO (D-008, D-022)')
text(198.12, 33.02, 'VAN: MODULO BLU SN65HVD230, SOLA RICEZIONE (D-022, D-051)')
text(198.12, 91.44, '3,3 V PER IL VAN, ACCESO CON IL DOMINIO PRINCIPALE', 1.5)
text(25.4, 236.22, 'Proposta preliminare, non verificata. Nessun collegamento all\'auto prima dei prerequisiti D-022 e '
                   'della verifica dei pin (D-008). Ordine DATA / DATA B del VAN da verificare.', 1.27)
text(25.4, 241.3, 'K-line: rispetto alla rev F aggiunti TVS D8 e diodo D9; soglia R42 dalla linea chiave. '
                  'Protezione dal corto della linea K verso la batteria durante la trasmissione: da studiare.', 1.27)
text(25.4, 246.38, 'Etichette con lo stesso nome sono collegate, anche tra fogli diversi.', 1.27)

# ======================================================================================
# Foglio 4: sensori e memoria, IMU su modulo, RTC, MicroSD (C3AI-CR-EL-004; D-033, D-046)
# ======================================================================================
begin_sheet('sensori-memoria.kicad_sch', 'Scheda madre cruscotto C3+AI - sensori e memoria', 'C3AI-CR-EL-004', 'B',
            'D-019, D-033, D-046, D-051', sheet_uuid=SENS_SHEET)

# --- IMU su modulo STEVAL-MKI196V1 (LSM6DSO) in zoccolo DIL-24: I2C a 0x6A (SA0 a massa) ---
IMU = {'1': '+3V3_AON', '2': '+3V3_AON', '13': 'GND', '19': '+3V3_AON', '20': 'I2C_SCL', '21': 'I2C_SDA',
       '22': 'GND'}
symbol('J6', 'Connector_Generic:Conn_02x12_Top_Bottom', 'STEVAL-MKI196V1 (DIL-24)',
       'scheda-madre:ST_DIL24_Adapter_W15.0mm', 60.96, 88.9, nets={str(i): IMU.get(str(i)) for i in range(1, 25)},
       auto=True, note='HW-IMU-LSM6DSO; piedinatura ST DB3714 rev 1; file di pin a 15,0 mm (Gerber ST), due strip femmina 1x12')
shunt('C33', '100nF', 45.72, 124.46, '+3V3_AON')
wire((35.56, 124.46), 'C33.1')
label('+3V3_AON', (35.56, 124.46), 180)

# --- RTC DS3231SN (facoltativo, -U10): pila CR2032 non ricaricata (D-019) -----------------
RTC = {'1': None, '2': '+3V3_AON', '3': None, '4': None, '14': 'RTC_VBAT', '15': 'I2C_SDA', '16': 'I2C_SCL'}
RTC.update({str(n): 'GND' for n in range(5, 14)})  # 5-12 da collegare a massa secondo il datasheet DS3231
symbol('U10', 'Timer_RTC:DS3231M', 'DS3231SN', 'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm', 165.1, 81.28, nets=RTC,
       txt=((5.08, 12.7), (5.08, 15.24), 'left'), note='Stessa piedinatura del DS3231SN del logger (HW-RTC)')
gnd('U10.5', 0)
tag('U10.15')
tag('U10.16')
shunt('C34', '100nF', 154.94, 63.5, '+3V3_AON')
wire((147.32, 63.5), 'C34.1', (162.56, 63.5), 'U10.2')
label('+3V3_AON', (147.32, 63.5), 180)
symbol('BT1', 'Device:Battery_Cell', 'CR2032', 'Battery:BatteryHolder_Keystone_3034_1x20mm', 175.26, 71.12,
       nets={'1': 'RTC_VBAT', '2': 'GND'}, note='HW-RTC-BATTERY, da procurare')
gnd('BT1.2', 0)
wire('U10.14', (165.1, 66.04), 'BT1.1')
flag('RTC_VBAT', (165.1, 66.04))

# --- MicroSD (facoltativa): modulo HW-SD-MODULE su fila di pin (D-051), SPI come il logger ---
symbol('J7', 'Connector_Generic:Conn_01x06', 'Modulo MicroSD: 3V3 CS MOSI CLK MISO GND',
       'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', 264.16, 81.28,
       nets={'1': '+3V3_SW', '2': 'SD_CS', '3': 'SD_MOSI', '4': 'SD_SCK', '5': 'SD_MISO', '6': 'GND'}, auto=True,
       note='Spento a riposo: il firmware deve tenere basse le linee SPI quando il 3,3 V a quadro è spento')
X4 = 228.6
label('+3V3_SW', (X4 - 7.62, 116.84), 180)
R('R49', '10k', X4, 120.65, '+3V3_SW', 'SD_CS', note='Scheda deselezionata durante l’avvio')
tag('R49.2')
shunt('C35', '10uF', X4 + 10.16, 116.84, '+3V3_SW', fp=C1206)
shunt('C36', '100nF', X4 + 20.32, 116.84, '+3V3_SW')
wire((X4 - 7.62, 116.84), 'R49.1', 'C35.1', 'C36.1')

text(25.4, 45.72, 'IMU SU MODULO DIL-24 (D-033, D-046)')
text(25.4, 50.8, 'STEVAL-MKI196V1, LSM6DSO, I2C 0x6A', 1.5)
text(142.24, 45.72, 'RTC DS3231SN (FACOLTATIVO) CON CR2032')
text(215.9, 45.72, 'MICROSD (FACOLTATIVA): MODULO SU FILA DI PIN (D-051)')
text(215.9, 106.68, 'PULL-UP DI CS E CONDENSATORI DEL MODULO MICROSD', 1.5)
text(25.4, 236.22, 'Proposta preliminare, non verificata. Pull-up I2C sul foglio del front-end. '
                   'Piedinatura del modulo IMU da riscontrare sulla serigrafia all’arrivo (HW-IMU-LSM6DSO).', 1.27)
text(25.4, 241.3, 'IMU e RTC sul 3,3 V sempre acceso (consumi a riposo di pochi uA); MicroSD sul 3,3 V acceso a quadro. '
                  'Pila dell’RTC non ricaricata (D-019).', 1.27)
text(25.4, 246.38, 'Etichette con lo stesso nome sono collegate, anche tra fogli diversi.', 1.27)

# === scrittura dei fogli ===============================================================
for sh in SHEETS:
    for (x, y), n in sorted(sh['ends'].items()):  # pallini dove si incontrano almeno tre estremi
        if n >= 3:
            j = uid(f"{sh['file']}/j/{x}/{y}")
            sh['items'].append(f'\t(junction (at {fnum(x)} {fnum(y)}) (diameter 0) (color 0 0 0 0) (uuid "{j}"))\n')
    head = (f'(kicad_sch\n\t(version 20250610)\n\t(generator "genera-schema-scheda-madre")\n'
            f'\t(generator_version "10.0")\n\t(uuid "{sh["uuid"]}")\n\t(paper "A3")\n\t(title_block\n'
            f'\t\t(title "{sh["title"]}")\n\t\t(date "2026-10-24")\n\t\t(rev "{sh["rev"]}")\n'
            f'\t\t(company "Cruscotto C3+AI")\n'
            f'\t\t(comment 1 "{sh["code"]} rev {sh["rev"]} - proposta preliminare, non verificata")\n'
            f'\t\t(comment 2 "{sh["decisions"]}")\n'
            f'\t\t(comment 3 "Generato da tools/genera-schema-scheda-madre.py")\n\t)\n\t(lib_symbols\n')
    body = ''.join(d for d, _ in sh['lib_defs'].values())
    tail = '\t(sheet_instances (path "/" (page "1")))\n' if sh is SHEETS[0] else ''
    (OUT.parent / sh['file']).write_text(head + body + '\n\t)\n' + ''.join(sh['items']) + tail + ')\n',
                                         encoding='utf-8', newline='\n')
print(OUT.parent, len(SHEETS), 'fogli,', n_parts, 'componenti')


# --- confronto con il netlist di KiCad ---------------------------------------------------
def verify():
    if not KICAD_CLI.is_file():
        print('kicad-cli non trovato: confronto delle reti saltato')
        return
    with tempfile.TemporaryDirectory() as tmp:
        net = Path(tmp) / 'n.net'
        subprocess.run([str(KICAD_CLI), 'sch', 'export', 'netlist', '-o', str(net), str(OUT)],
                       check=True, capture_output=True)
        t = net.read_text(encoding='utf-8')
    got = {}
    for blk in re.split(r'\n\s*\(net\b', t[t.index('(nets'):])[1:]:
        name = re.search(r'\(name "([^"]+)"', blk).group(1).lstrip('/')
        for ref, pin in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', blk):
            got[f'{ref}.{pin}'] = None if 'unconnected-(' in name else name
    want = {}
    for p, n in INTENT.items():
        want.setdefault(n, set()).add(p) if n else None
    have = {}
    for p, n in got.items():
        if n:
            have.setdefault(n, set()).add(p)
    # Le reti senza etichetta prendono da KiCad un nome automatico (Net-(...)): si confrontano
    # per composizione; quelle con etichetta anche per nome.
    have_sets = {frozenset(v): n for n, v in have.items()}
    errors = []
    for n, pins in want.items():
        got_name = have_sets.get(frozenset(pins))
        if got_name is None or (got_name != n and 'Net-(' not in got_name):
            errors.append(f'{n}: voluto {sorted(pins)}, disegnato {sorted(have.get(n, set()))}')
    errors += [f'rete in più nel disegno: {n} {sorted(v)}' for n, v in have.items()
               if frozenset(v) not in {frozenset(w) for w in want.values()}]
    errors += [f'{p} dovrebbe essere libero, è su {got.get(p)}' for p, n in INTENT.items() if n is None and got.get(p)]
    assert not errors, 'reti diverse dal voluto:\n' + '\n'.join(errors)
    print('reti verificate sul netlist di KiCad:', len(want), 'reti, nessuna differenza')


verify()
