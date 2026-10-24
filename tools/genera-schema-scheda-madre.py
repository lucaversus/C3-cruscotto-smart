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
    assert '(extends' not in body, f'simbolo derivato non gestito: {lib_id}'
    pins = {}
    for p in re.finditer(r'\(pin \w+ \w+\s+\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(number "([^"]*)"', body, re.S):
        pins.setdefault(p.group(4), []).append((float(p.group(1)), float(p.group(2)), int(p.group(3))))
    return f'\t\t(symbol "{lib_id}"\n{body}\n\t\t)', pins


def check_fp(fp):
    lib, name = fp.split(':')
    assert (FPDIR / f'{lib}.pretty' / f'{name}.kicad_mod').is_file(), f'impronta non trovata: {fp}'
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


items = []         # testo S-expression già pronto
lib_defs = {}
PIN = {}           # 'R1.2' -> (x, y) assoluto
INTENT = {}        # 'R1.2' -> rete voluta
ends = Counter()   # estremi di fili e piedini, per i pallini di giunzione
n_parts = 0
_pwr = 0


def symbol(ref, lib_id, value, fp, x, y, rot=0, mirror=False, note='', nets=None, auto=False, txt=None):
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
    for num, ps in lpins.items():
        px, py, ang = ps[0]
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
    s = (f'\t(symbol (lib_id "{lib_id}") (at {fnum(x)} {fnum(y)} {rot}){m} (unit 1) (exclude_from_sim no) '
         f'(in_bom {"no" if hidden else "yes"}) (on_board {"no" if hidden else "yes"}) (dnp no) (uuid "{uid(ref)}")\n')
    s += prop('Reference', ref, *rpos, just, hide=hidden, angle=ang)
    s += prop('Value', value, *vpos, just, hide=hidden, angle=ang)
    s += prop('Footprint', fp, x, y, hide=True)
    s += prop('Datasheet', '', x, y, hide=True)
    s += prop('Description', note, x, y, hide=True)
    for num in lpins:
        s += f'\t\t(pin "{num}" (uuid "{uid(ref + "/pin/" + num)}"))\n'
    s += f'\t\t(instances (project "scheda-madre" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))\n\t)\n'
    items.append(s)
    if hidden:
        return pts
    n_parts += 1
    for num, (px, py, ang) in pts.items():
        PIN[f'{ref}.{num}'] = (px, py)
        net = (nets or {}).get(num, '__missing__')
        assert net != '__missing__', f'{ref}: piedino {num} senza rete'
        INTENT[f'{ref}.{num}'] = net
        ends[key((px, py))] += 1
        if net is None:
            items.append(f'\t(no_connect (at {fnum(px)} {fnum(py)}) (uuid "{uid(f"{ref}/nc/{num}")}"))\n')
        elif auto:
            out = (ang + 180 + rot) % 360
            dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[out]
            end = (px + 2.54 * dx, py + 2.54 * dy)
            wire((px, py), end)
            if net == 'GND':
                gnd(end, 0, rot={270: 0, 90: 180, 0: 90, 180: 270}[out])
            else:
                label(net, end, out)
    return pts


def P(p):
    return PIN[p] if isinstance(p, str) else p


def wire(*pts):
    """Polilinea ortogonale tra punti o piedini ('R1.2')."""
    pts = [P(p) for p in pts]
    for a, b in zip(pts, pts[1:]):
        assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6, f'filo non ortogonale {a} {b}'
        items.append(f'\t(wire (pts (xy {fnum(a[0])} {fnum(a[1])}) (xy {fnum(b[0])} {fnum(b[1])})) '
                     f'(stroke (width 0) (type default)) (uuid "{uid(f"w/{a}/{b}")}"))\n')
        ends[key(a)] += 1
        ends[key(b)] += 1


def label(net, p, direction=0):
    """Etichetta di rete; direction = verso del testo (0 destra, 90 su, 180 sinistra, 270 giù)."""
    x, y = P(p)
    just = 'left bottom' if direction in (0, 90) else 'right bottom'
    items.append(f'\t(label "{net}" (at {fnum(x)} {fnum(y)} {direction}) {effects(just)} '
                 f'(uuid "{uid(f"l/{net}/{x}/{y}")}"))\n')


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
                 f'{effects("left bottom", size=size)} (uuid "{uid(f"text/{t}")}"))\n')


R0805 = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C0805 = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
C1206 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
C1210 = 'Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder'


def R(ref, value, x, y, a, b, rot=0, note=''):
    """Resistenza: verticale (piedino 1 in alto) o, con rot=90, orizzontale (piedino 1 a sinistra)."""
    return symbol(ref, 'Device:R', value, R0805, x, y, rot, nets={'1': a, '2': b}, note=note)


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
wire('L1.2', 'C7.1', 'C8.1', 'R1.1', (368.3, 63.5))
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
wire('L2.2', 'C15.1', 'C16.1', 'C17.1', 'R9.1', (345.44, 170.18))
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
text(25.4, 246.38, 'Ventola 12 V (D-031), relè audio, front-end, VAN, K-line, IMU: fogli successivi. '
                   'Etichette con lo stesso nome sono collegate.', 1.27)

# Pallini di giunzione dove si incontrano almeno tre estremi.
for (x, y), n in sorted(ends.items()):
    if n >= 3:
        items.append(f'\t(junction (at {fnum(x)} {fnum(y)}) (diameter 0) (color 0 0 0 0) (uuid "{uid(f"j/{x}/{y}")}"))\n')

head = f'''(kicad_sch
\t(version 20250610)
\t(generator "genera-schema-scheda-madre")
\t(generator_version "10.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "Scheda madre cruscotto C3+AI - alimentazione")
\t\t(date "2026-10-24")
\t\t(rev "B")
\t\t(company "Cruscotto C3+AI")
\t\t(comment 1 "C3AI-CR-EL-001 rev B - proposta preliminare, non verificata")
\t\t(comment 2 "D-030, D-031, D-044, D-046")
\t\t(comment 3 "Generato da tools/genera-schema-scheda-madre.py")
\t)
\t(lib_symbols
'''
body = ''.join(d for d, _ in lib_defs.values())
OUT.write_text(head + body + '\n\t)\n' + ''.join(items) + '\t(sheet_instances (path "/" (page "1")))\n)\n',
               encoding='utf-8', newline='\n')
print(OUT, n_parts, 'componenti')


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
            got[f'{ref}.{pin}'] = None if name.startswith('unconnected-') else name
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
        if got_name is None or (got_name != n and not got_name.startswith('Net-(')):
            errors.append(f'{n}: voluto {sorted(pins)}, disegnato {sorted(have.get(n, set()))}')
    errors += [f'rete in più nel disegno: {n} {sorted(v)}' for n, v in have.items()
               if frozenset(v) not in {frozenset(w) for w in want.values()}]
    errors += [f'{p} dovrebbe essere libero, è su {got.get(p)}' for p, n in INTENT.items() if n is None and got.get(p)]
    assert not errors, 'reti diverse dal voluto:\n' + '\n'.join(errors)
    print('reti verificate sul netlist di KiCad:', len(want), 'reti, nessuna differenza')


verify()
