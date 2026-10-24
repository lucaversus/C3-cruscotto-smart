"""Schema elettrico della scheda madre (KiCad 10), foglio alimentazione: C3AI-CR-EL-001.

Uso (qualsiasi Python 3, nessuna libreria esterna):
  python tools/genera-schema-scheda-madre.py
Crea cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch con i simboli copiati dalle
librerie standard di KiCad 10 (cartella symbols dell'installazione). Ogni piedino ha un
tratto di filo e un'etichetta di rete: il collegamento è dato dai nomi, non dal disegno.
Valori da datasheet (TPS54360B fig. 32, LMR36510 tab. 8-1/8-3, LM74700-Q1): proposta non
verificata, da ricontrollare prima dell'ordine dei componenti (D-030, D-031, D-046).
Il file va rigenerato da qui: le modifiche fatte a mano in KiCad si perdono.
"""
from pathlib import Path
import math
import os
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch'
KICAD = Path(os.environ.get('KICAD10_SHARE', r'C:\Program Files\KiCad\10.0\share\kicad'))
SYM = KICAD / 'symbols'
FPDIR = KICAD / 'footprints'
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


# --- componenti del foglio --------------------------------------------------------------
R0805 = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C0805 = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
C1206 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
C1210 = 'Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder'

# (rif., simbolo, valore, impronta, x, y, rotazione, {piedino: rete}, nota)
# Rete None = piedino non collegato (croce); rete 'GND' = simbolo di massa.
PARTS = []


def part(ref, lib_id, value, fp, x, y, nets, rot=0, note=''):
    PARTS.append((ref, lib_id, value, fp, x, y, rot, nets, note))


def R(ref, value, x, y, a, b, note=''):
    part(ref, 'Device:R', value, R0805, x, y, {'1': a, '2': b}, note=note)


def C(ref, value, x, y, a, b, fp=C0805, note=''):
    part(ref, 'Device:C', value, fp, x, y, {'1': a, '2': b}, note=note)


# Ingresso dall'auto: J1 Micro-Fit 2x12 (D-044); vie dalla tabella bozza di scheda-madre.md.
J1_NETS = {1: 'VBAT_IN', 2: 'GND', 3: 'KEY_IN', 4: 'KLINE', 5: 'VAN_DATA', 6: 'VAN_DATAB', 7: 'VAN_GND_REF',
           8: 'RADIO_L_P', 9: 'RADIO_L_N', 10: 'SPK_L_P', 11: 'SPK_L_N', 12: 'RADIO_R_P', 13: 'RADIO_R_N',
           14: 'SPK_R_P', 15: 'SPK_R_N'}
part('J1', 'Connector_Generic:Conn_02x12_Top_Bottom', 'Micro-Fit 43045-2400 (D-044)',
     'Connector_Molex:Molex_Micro-Fit_3.0_43045-2400_2x12_P3.00mm_Horizontal', 45.72, 116.84,
     {str(i): J1_NETS.get(i) for i in range(1, 25)}, note='Vie 16-24 riserva; assegnazione bozza (D-044)')
part('#FLG01', 'power:PWR_FLAG', 'PWR_FLAG', '', 30.48, 167.64, {'1': 'VBAT_IN'})
part('#FLG02', 'power:PWR_FLAG', 'PWR_FLAG', '', 45.72, 167.64, {'1': 'GND'})

# Protezioni d'ingresso (-U1…U3, D-030): TVS bidirezionale, diodo ideale contro l'inversione, filtro.
part('D1', 'Device:D_TVS', 'SMCJ26CA', 'Diode_SMD:D_SMC', 81.28, 50.8, {'1': 'VBAT_IN', '2': 'GND'},
     note='Bidirezionale 26 V, blocca ~42 V: sotto i 60-65 V dei regolatori')
C('C1', '100nF 100V', 99.06, 50.8, 'VBAT_IN', 'GND')
part('U1', 'Power_Management:LM74700', 'LM74700-Q1', 'Package_TO_SOT_SMD:SOT-23-6', 139.7, 50.8,
     {'1': 'U1_VCAP', '2': 'GND', '3': 'VBAT_IN', '4': 'VBAT_P', '5': 'U1_GATE', '6': 'VBAT_IN'},
     note='Diodo ideale: blocca inversione e ritorno di corrente durante l\'avviamento')
C('C2', '100nF 25V', 175.26, 50.8, 'U1_VCAP', 'VBAT_IN')
part('Q1', 'Transistor_FET:IPD50R380CE', 'IPD50N06S4L-12 (60V, da confermare)', 'Package_TO_SOT_SMD:TO-252-2',
     139.7, 96.52, {'1': 'U1_GATE', '2': 'VBAT_P', '3': 'VBAT_IN'}, note='MOSFET N 60 V: S verso la batteria, D verso il carico')
part('C3', 'Device:C_Polarized', '220uF 50V', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', 175.26, 96.52,
     {'1': 'VBAT_P', '2': 'GND'}, note='Riserva per l\'avviamento (-C1), capacità da confermare')
part('FB1', 'Device:FerriteBead', 'ferrite >= 3A, 1206', 'Inductor_SMD:L_1206_3216Metric_Pad1.22x1.90mm_HandSolder',
     81.28, 93.98, {'1': 'VBAT_P', '2': '+12V_F'})
part('#FLG03', 'power:PWR_FLAG', 'PWR_FLAG', '', 99.06, 93.98, {'1': '+12V_F'})
part('#FLG04', 'power:PWR_FLAG', 'PWR_FLAG', '', 114.3, 93.98, {'1': 'VBAT_P'})

# Dominio principale: buck 12 -> 5 V 3,5 A per S3 e audio (-U4), acceso da chiave o mantenimento (D-030).
part('U2', 'Regulator_Switching:TPS54360DDA', 'TPS54360B', 'Package_SO:TI_SO-PowerPAD-8_ThermalVias', 254, 55.88,
     {'1': 'U2_BOOT', '2': '+12V_F', '3': 'EN_5V', '4': 'U2_RT', '5': 'FB_5V', '6': 'U2_COMP', '7': 'GND',
      '8': 'SW_5V', '9': 'GND'}, note='Valori dall\'esempio 5 V / 3,5 A del datasheet (fig. 32)')
C('C4', '2.2uF 100V', 205.74, 33.02, '+12V_F', 'GND', fp=C1210)
C('C5', '2.2uF 100V', 220.98, 33.02, '+12V_F', 'GND', fp=C1210)
C('C6', '100nF', 299.72, 33.02, 'U2_BOOT', 'SW_5V')
part('D2', 'Device:D_Schottky', 'B560C', 'Diode_SMD:D_SMC', 299.72, 60.96, {'1': 'SW_5V', '2': 'GND'})
part('L1', 'Device:L', '8.2uH Isat>=5A', 'Inductor_SMD:L_Bourns_SRR1260', 325.12, 33.02, {'1': 'SW_5V', '2': '+5V'},
     note='Es. Bourns SRR1260-8R2Y, da verificare corrente di saturazione')
C('C7', '47uF 10V', 325.12, 60.96, '+5V', 'GND', fp=C1210)
C('C8', '47uF 10V', 340.36, 60.96, '+5V', 'GND', fp=C1210)
R('R1', '53.6k', 355.6, 60.96, '+5V', 'FB_5V')
R('R2', '10.2k', 370.84, 60.96, 'FB_5V', 'GND')
R('R3', '162k', 205.74, 78.74, 'U2_RT', 'GND', note='600 kHz')
R('R4', '13.0k', 299.72, 86.36, 'U2_COMP', 'U2_CZ')
C('C9', '6.8nF', 314.96, 86.36, 'U2_CZ', 'GND')
C('C10', '39pF', 330.2, 86.36, 'U2_COMP', 'GND')
# Accensione: chiave (UVLO 8 V / 6,25 V con R5/R6) oppure GPIO13 del front-end (mantenimento).
part('D3', 'Device:D', '1N4148W', 'Diode_SMD:D_SOD-123', 213.36, 106.68, {'1': 'KEY_D', '2': 'KEY_IN'})
R('R5', '523k', 238.76, 106.68, 'KEY_D', 'EN_5V')
R('R6', '84.5k', 254, 106.68, 'EN_5V', 'GND')
part('D4', 'Device:D_Schottky', 'BAT54J', 'Diode_SMD:D_SOD-323F', 213.36, 127, {'1': 'HOLD_D', '2': 'PWR_HOLD'})
R('R7', '10k', 238.76, 127, 'HOLD_D', 'EN_5V')
R('R8', '100k', 254, 127, 'PWR_HOLD', 'GND', note='A riposo spento (GPIO13 flottante al reset)')

# Dominio sempre acceso: buck 12 -> 3,3 V 1 A, 26 uA a vuoto, front-end e sensori (-U5, D-031).
part('U3', 'Regulator_Switching:LMR36510ADDA', 'LMR36510',
     'Package_SO:Texas_HTSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias', 254, 185.42,
     {'1': 'GND', '2': '+12V_F', '3': '+12V_F', '4': None, '5': 'FB_3V3', '6': 'U3_VCC', '7': 'U3_BOOT',
      '8': 'SW_3V3', '9': 'GND'}, note='EN a VIN: sempre acceso; tabella 8-1/8-3 del datasheet')
C('C11', '2.2uF 100V', 205.74, 165.1, '+12V_F', 'GND', fp=C1210)
C('C12', '220nF 100V', 220.98, 165.1, '+12V_F', 'GND')
C('C13', '1uF', 236.22, 165.1, 'U3_VCC', 'GND')
C('C14', '100nF', 299.72, 165.1, 'U3_BOOT', 'SW_3V3')
part('L2', 'Device:L', '22uH Isat>=1.5A', 'Inductor_SMD:L_Bourns_SRN6045TA', 325.12, 165.1, {'1': 'SW_3V3', '2': '+3V3_AON'},
     note='Es. Bourns SRN6045TA-220M, da verificare')
C('C15', '22uF 10V', 314.96, 190.5, '+3V3_AON', 'GND', fp=C1206)
C('C16', '22uF 10V', 330.2, 190.5, '+3V3_AON', 'GND', fp=C1206)
C('C17', '22uF 10V', 345.44, 190.5, '+3V3_AON', 'GND', fp=C1206)
R('R9', '100k', 360.68, 190.5, '+3V3_AON', 'FB_3V3')
R('R10', '43.2k', 375.92, 190.5, 'FB_3V3', 'GND')

# Misure verso il front-end: segnale chiave (GPIO39) e tensione batteria (GPIO35), con limitatori.
R('R11', '100k', 81.28, 215.9, 'KEY_IN', 'KEY_SENSE')
R('R12', '22k', 96.52, 215.9, 'KEY_SENSE', 'GND', note='16 V -> 2,9 V')
C('C18', '100nF', 111.76, 215.9, 'KEY_SENSE', 'GND')
part('D5', 'Diode:BAT54S', 'BAT54S', 'Package_TO_SOT_SMD:SOT-23', 129.54, 215.9,
     {'1': 'GND', '2': '+3V3_AON', '3': 'KEY_SENSE'})
R('R13', '470k', 160.02, 215.9, 'VBAT_P', 'VBAT_SENSE')
R('R14', '100k', 175.26, 215.9, 'VBAT_SENSE', 'GND', note='16 V -> 2,8 V; 21 uA a 12 V')
C('C19', '100nF', 190.5, 215.9, 'VBAT_SENSE', 'GND')
part('D6', 'Diode:BAT54S', 'BAT54S', 'Package_TO_SOT_SMD:SOT-23', 208.28, 215.9,
     {'1': 'GND', '2': '+3V3_AON', '3': 'VBAT_SENSE'})

TEXTS = [
    (71.12, 25.4, 'INGRESSO 12 V E PROTEZIONI (D-030)'),
    (195.58, 17.78, 'DOMINIO PRINCIPALE 5 V 3,5 A: S3, AUDIO (accensione: chiave O mantenimento)'),
    (195.58, 147.32, 'DOMINIO SEMPRE ACCESO 3,3 V 1 A: FRONT-END, SENSORI (D-031)'),
    (71.12, 200.66, 'MISURE PER IL FRONT-END: KEY_SENSE -> GPIO39, VBAT_SENSE -> GPIO35, PWR_HOLD <- GPIO13'),
    (25.4, 236.22, 'Proposta preliminare, non verificata. Fusibile di ramo nel cablaggio (HW-FUSE-HOLDER). '
                   'Montaggio a mano (D-046): U2/U3 con piazzola esposta, saldatura dal retro attraverso i fori termici.'),
    (25.4, 241.3, 'Consumo a riposo stimato: U1 80 uA + U3 26 uA + partitori ~25 uA + front-end in sonno: < 1 mA (D-030), da misurare.'),
    (25.4, 246.38, 'Ventola 12 V (D-031), relè audio, front-end, VAN, K-line, IMU: fogli successivi. Reti con lo stesso nome sono collegate.'),
]


# --- scrittura -------------------------------------------------------------------------
def fnum(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def effects(justify='', hide=False, size=1.27):
    j = f' (justify {justify})' if justify else ''
    h = ' (hide yes)' if hide else ''
    return f'(effects (font (size {size} {size})){j}{h})'


def prop(name, value, x, y, justify='', hide=False):
    value = value.replace('\\', '\\\\').replace('"', '\\"')
    return (f'\t\t(property "{name}" "{value}" (at {fnum(x)} {fnum(y)} 0) '
            f'{"(hide yes) " if hide else ""}{effects(justify)})\n')


def transform(px, py, rot):
    a = math.radians(rot)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


out_items = []
lib_defs = {}
pwr_n = 0


def place_gnd(x, y, out_dir, key):
    global pwr_n
    pwr_n += 1
    rot = {270: 0, 90: 180, 0: 90, 180: 270}[out_dir]
    ref = f'#PWR{pwr_n:03d}'
    symbol_instance(ref, 'power:GND', 'GND', '', x, y, rot, key)


def symbol_instance(ref, lib_id, value, fp, x, y, rot, key, note='', pins=None):
    if lib_id not in lib_defs:
        lib_defs[lib_id] = lib_symbol(lib_id)
    _, lpins = lib_defs[lib_id]
    hidden = ref.startswith('#')
    pts = [(x + transform(px, py, rot)[0], y - transform(px, py, rot)[1]) for ps in lpins.values() for px, py, _ in ps]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if len(lpins) == 2 and max(xs) - min(xs) < 0.1:
        rpos, vpos, just = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27), 'left'
    elif len(lpins) == 2:
        rpos, vpos, just = (x, min(ys) - 3.81), (x, max(ys) + 3.81), ''
    else:
        rpos, vpos, just = (x, min(ys) - 6.35), (x, min(ys) - 3.81), ''
    s = (f'\t(symbol (lib_id "{lib_id}") (at {fnum(x)} {fnum(y)} {rot}) (unit 1) (exclude_from_sim no) '
         f'(in_bom {"no" if hidden else "yes"}) (on_board {"no" if hidden else "yes"}) (dnp no) (uuid "{uid(key)}")\n')
    s += prop('Reference', ref, *rpos, just, hide=hidden)
    s += prop('Value', value, *vpos, just, hide=hidden)
    s += prop('Footprint', fp, x, y, hide=True)
    s += prop('Datasheet', '', x, y, hide=True)
    s += prop('Description', note, x, y, hide=True)
    for num in lpins:
        s += f'\t\t(pin "{num}" (uuid "{uid(key + "/pin/" + num)}"))\n'
    s += (f'\t\t(instances (project "scheda-madre" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))\n\t)\n')
    out_items.append(s)


for ref, lib_id, value, fp, x, y, rot, nets, note in PARTS:
    if fp:
        check_fp(fp)
    symbol_instance(ref, lib_id, value, fp, x, y, rot, ref, note)
    _, lpins = lib_defs[lib_id]
    for num, plist in lpins.items():
        net = nets.get(num, '__missing__')
        assert net != '__missing__', f'{ref}: piedino {num} senza rete'
        for k, (px, py, pang) in enumerate(plist):
            tx, ty = transform(px, py, rot)
            x0, y0 = x + tx, y - ty
            if net is None:
                out_items.append(f'\t(no_connect (at {fnum(x0)} {fnum(y0)}) (uuid "{uid(f"{ref}/nc/{num}/{k}")}"))\n')
                continue
            if k > 0:
                continue  # piedini con lo stesso numero (es. massa ripetuta): uno basta
            out_dir = (pang + 180 + rot) % 360
            dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[out_dir]
            x1, y1 = x0 + 2.54 * dx, y0 + 2.54 * dy
            out_items.append(f'\t(wire (pts (xy {fnum(x0)} {fnum(y0)}) (xy {fnum(x1)} {fnum(y1)})) '
                             f'(stroke (width 0) (type default)) (uuid "{uid(f"{ref}/w/{num}")}"))\n')
            if net == 'GND':
                place_gnd(x1, y1, out_dir, f'{ref}/gnd/{num}')
                continue
            just = {0: 'left bottom', 90: 'left bottom', 180: 'right bottom', 270: 'right bottom'}[out_dir]
            out_items.append(f'\t(label "{net}" (at {fnum(x1)} {fnum(y1)} {out_dir}) {effects(just)} '
                             f'(uuid "{uid(f"{ref}/l/{num}")}"))\n')

for i, (x, y, t) in enumerate(TEXTS):
    size = 1.27 if y > 230 else 2.0
    out_items.append(f'\t(text "{t}" (exclude_from_sim no) (at {fnum(x)} {fnum(y)} 0) '
                     f'{effects("left bottom", size=size)} (uuid "{uid(f"text/{i}")}"))\n')

head = f'''(kicad_sch
\t(version 20250610)
\t(generator "genera-schema-scheda-madre")
\t(generator_version "10.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "Scheda madre cruscotto C3+AI - alimentazione")
\t\t(date "2026-10-24")
\t\t(rev "A")
\t\t(company "Cruscotto C3+AI")
\t\t(comment 1 "C3AI-CR-EL-001 rev A - proposta preliminare, non verificata")
\t\t(comment 2 "D-030, D-031, D-044, D-046")
\t\t(comment 3 "Generato da tools/genera-schema-scheda-madre.py")
\t)
\t(lib_symbols
'''
body = ''.join(d for d, _ in lib_defs.values())
text = head + body + '\n\t)\n' + ''.join(out_items) + '\t(sheet_instances (path "/" (page "1")))\n)\n'
OUT.write_text(text, encoding='utf-8', newline='\n')
print(OUT, len(PARTS), 'componenti')
