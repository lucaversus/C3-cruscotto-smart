from pathlib import Path
from itertools import product

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from iso_drawing import Sheet
# Static bounds only: no SPICE simulation, dynamic or automotive qualification.
# Rev. E: R10 positive feedback from OUT1 (pin 1) to IN1+ (VSENSE) gives hysteresis.
# Output high = R8 pull-up to 3V3 (3.135-3.465 V); output low = 0-0.4 V (LM2903B VOL).
# Thresholds are the K voltages at which VSENSE crosses VREF in each output state.
R10=330000
def vsense(k,r4,r5,r10,vout,r8=None):
    # Node VSENSE fed by K through R4, GND through R5, output through R10.
    # Output high: R8 to 3V3 in series with R10 (ESP32 input through R9 neglected).
    rfb=r10+(r8 or 0)
    return (k/r4+vout/rfb)/(1/r4+1/r5+1/rfb)
def k_at(vref,r4,r5,r10,vout,r8=None):
    rfb=r10+(r8 or 0)
    return (vref*(1/r4+1/r5+1/rfb)-vout/rfb)*r4
falling=[];rising=[];hyst=[]
for a,b,c,d,e,f in product((.99,1.01), repeat=6):
    r4,r5,r6,r7,r10,r8=68000*a,10000*b,150000*c,10000*d,R10*e,4700*f
    for supply in (9,16):
        vref=supply*r7/(r6+r7)
        for offset in (-.003,.003):
            for v3 in (3.135,3.465):
                for vol in (0,.4):
                    kl=k_at(vref+offset,r4,r5,r10,v3,r8)   # K falling, output high
                    kh=k_at(vref+offset,r4,r5,r10,vol)     # K rising, output low
                    falling.append(kl/supply);rising.append(kh/supply);hyst.append(kh-kl)
thresholds=falling+rising
assert min(thresholds)>.3 and max(thresholds)<.7
assert min(hyst)>.4, 'hysteresis below 0.4 V at K'
max_input=vsense(16,67320,10100,R10*.99,3.465,4700*.99)
assert max_input < 4.75-2
base_min=(2.5-1.2)/(330*1.05)-1.2/(47000*.95)
collector_max=16/(510*.95)  # rev G: R3 5 % (D-036)
assert collector_max/base_min<10
print(f"DC model: falling/VBAT={min(falling):.4f}..{max(falling):.4f}; rising/VBAT={min(rising):.4f}..{max(rising):.4f}; hysteresis_K={min(hyst):.3f}..{max(hyst):.3f}V; input_max={max_input:.3f}V; forced_beta_max={collector_max/base_min:.2f}; R3_power_max={16**2/(510*.95):.3f}W")



def it(v, n): return f'{v:.{n}f}'.replace('.', ',')

# --- Disegno C3AI-DL-KL-001 rev G (D-024, D-036): IEC 60617 / IEC 61082-1, foglio ISO 5457 A3 ---
d = Sheet('C3AI-DL-KL-001 rev G — Interfaccia K-line autocostruita')
d.frame()
d.text(25, 20, 'INTERFACCIA K-LINE AUTOCOSTRUITA — SCHEMA ELETTRICO', 5, bold=True)
d.text(25, 25, 'Prototipo da banco, non collaudato. Nessun collegamento al veicolo autorizzato da questo documento.', 2.5)

d.enclosure(65, 30, 265, 152, '-A1  Modulo interfaccia K-line')
# Morsetti verso ESP32 (X1) e verso la linea (X2), sul confine del modulo.
d.terminal(65, 40, '-X1:1', 'RX_3V3 → ESP32 GPIO16')
d.terminal(65, 140, '-X1:2', 'TX_INV ← ESP32 GPIO17')
d.terminal(65, 155, '-X1:3', '+5V'); d.terminal(65, 162.5, '-X1:4', '+3V3'); d.terminal(65, 170, '-X1:5', 'GND')
d.wire((65.9, 155), (75, 155)); d.net_label(75, 155, '+5V', 'start')
d.wire((65.9, 162.5), (75, 162.5)); d.net_label(75, 162.5, '+3V3', 'start')
d.wire((65.9, 170), (75, 170)); d.ground(75, 170)
d.terminal(330, 115, '-X2:1', 'K', side='right')
d.terminal(330, 140, '-X2:2', 'VBENCH (riferimento)', side='right')
d.terminal(330, 155, '-X2:3', 'GND', side='right')
d.wire((329.1, 140), (320, 140)); d.net_label(320, 140, 'VBENCH')
d.wire((329.1, 155), (320, 155)); d.ground(320, 155)

# Ricezione: K -> R4/R5 -> U1A (+); VREF su (-); uscita a collettore aperto.
plus, minus, out = d.amplifier(200, 75, 'U1A', {'in+': '3', 'in-': '2', 'out': '1'})
d.wire((147.5, 115), (147.5, 80))
d.resistor(147.5, 80, 172.5, 80, 'R4', '68 kΩ')
d.wire((172.5, 80), plus)
d.dot(182.5, 80); d.resistor(182.5, 80, 182.5, 100, 'R5', '10 kΩ', 'left'); d.ground(182.5, 100)
d.wire(minus, (195, 85)); d.net_label(196.5, 85, 'VREF')
# Isteresi: R10 da uscita a ingresso +.
d.dot(190, 80); d.wire((190, 80), (190, 60), (205, 60))
d.resistor(205, 60, 230, 60, 'R10', '330 kΩ')
d.wire(out, (262.5, 82.5)); d.dot(230, 82.5); d.wire((230, 82.5), (230, 60))
d.text(206, 66, 'isteresi', 2.2)
d.dot(242.5, 82.5); d.resistor(242.5, 82.5, 242.5, 62.5, 'R8', '4,7 kΩ'); d.supply(242.5, 62.5, '+3V3')
d.text(232, 87, 'RX_RAW', 2.2)
d.wire((262.5, 82.5), (262.5, 40), (92.5, 40))
d.resistor(92.5, 40, 72.5, 40, 'R9', '1 kΩ'); d.wire((72.5, 40), (65.9, 40))

# Trasmissione: TX_INV -> R1 -> base Q1; R2 base-massa; collettore su K.
d.wire((65.9, 140), (70, 140)); d.resistor(70, 140, 85, 140, 'R1', '330 Ω')
d.wire((85, 140), (105, 140))
d.dot(90, 140); d.resistor(90, 140, 90, 160, 'R2', '47 kΩ'); d.ground(90, 160)
c, e = d.npn(105, 140, 'Q1', '2N5551')
d.wire(c, (c[0], 115), (329.1, 115)); d.dot(147.5, 115)
d.wire(e, (e[0], 152.5)); d.ground(e[0], 152.5)
d.text(150, 113, 'K', 2.5, bold=True)

# Riferimento VREF dal partitore R6/R7 su VBENCH.
d.supply(260, 125, 'VBENCH'); d.resistor(260, 125, 260, 142.5, 'R6', '150 kΩ', 'left')
d.wire((260, 142.5), (260, 145)); d.dot(260, 145); d.wire((260, 145), (270, 145)); d.net_label(270, 145, 'VREF', 'start')
d.resistor(260, 145, 260, 165, 'R7', '10 kΩ', 'left'); d.ground(260, 165)

# Sezione inutilizzata U1B: ingressi a potenziale definito, uscita libera.
p2, m2, o2 = d.amplifier(200, 125, 'U1B', {'in+': '5', 'in-': '6', 'out': '7'})
d.wire(p2, (180, 130), (180, 140)); d.ground(180, 140)
d.wire(m2, (195, 135)); d.net_label(196.5, 135, 'VREF')
d.wire(o2, (217.5, 132.5)); d.not_connected(217.5, 132.5)

# Alimentazione di U1 (unità separata U1C) e disaccoppiamento.
top, bottom = d.power_unit(270, 60, 'U1C', '8', '4')
d.wire(top, (275, 52.5), (310, 52.5)); d.supply(275, 52.5, '+5V'); d.dot(275, 52.5)
d.ground(bottom[0], bottom[1])
d.dot(292.5, 52.5); d.wire((292.5, 52.5), (292.5, 57.5)); d.capacitor(292.5, 57.5, 72.5, 'C1', '100 nF'); d.ground(292.5, 72.5)
d.wire((310, 52.5), (310, 57.5)); d.capacitor(310, 57.5, 72.5, 'C2', '10 µF 16 V', polarized=True); d.ground(310, 72.5)

# Simulatore esterno da banco: non fa parte del modulo.
d.enclosure(352.5, 92, 52.5, 80, '-A2  Simulatore linea')
d.text(355, 178, 'solo banco, esterno ad -A1', 2.2)
d.wire((330.9, 115), (375, 115)); d.resistor(375, 115, 375, 100, 'R3', '510 Ω 1 W')
d.supply(375, 100, 'VBENCH')
d.wire((330.9, 140), (385, 140)); d.supply(385, 140, 'VBENCH')
d.wire((330.9, 155), (385, 155)); d.ground(385, 155)
d.text(355, 166, '-G1 alimentatore 9–16 V', 2.2); d.text(355, 169.5, 'limitato in corrente', 2.2)

parts = [
    ('1', 'Q1', '1', 'NPN 2N5551, TO-92', 'Piedinatura E/B/C secondo produttore'),
    ('2', 'U1', '1', 'Doppio comparatore LM2903B, SOIC-8', 'Adattatore SOIC-8 → DIP-8 e zoccolo'),
    ('3', 'R1', '1', '330 Ω, 0,25 W, 5 %', ''),
    ('4', 'R2', '1', '47 kΩ, 0,25 W, 5 %', 'Q1 spento con GPIO flottante'),
    ('5', 'R4', '1', '68 kΩ, 0,25 W, 1 %', 'Partitore K'),
    ('6', 'R5, R7', '2', '10 kΩ, 0,25 W, 1 %', ''),
    ('7', 'R6', '1', '150 kΩ, 0,25 W, 1 %', 'Riferimento da VBENCH'),
    ('8', 'R8', '1', '4,7 kΩ, 0,25 W, 1 %', 'Richiamo uscita a +3V3'),
    ('9', 'R9', '1', '1 kΩ, 0,25 W', 'Serie verso ESP32'),
    ('10', 'R10', '1', '330 kΩ, 0,25 W, 1 %', 'Isteresi (rev E, D-022)'),
    ('11', 'C1', '1', '100 nF, ceramico', 'Vicino ai pin 8 e 4 di U1'),
    ('12', 'C2', '1', '10 µF, 16 V, elettrolitico', 'Rispettare la polarità'),
    ('13', 'R3', '1', '510 Ω, 1 W, 5 %', 'Solo -A2 simulatore, non nel modulo'),
    ('14', '—', '1 ins.', 'Millefori, morsetti, fili', ''),
]
d.parts_list(25, 192, parts, widths=(10, 15, 11, 62, 82))
d.notes(212, 196, 'NOTE', [
    '1. Modello DC (tolleranze 1 %, offset ±3 mV, VBENCH 9–16 V): soglia in discesa',
    f'\u2003\u2003{it(min(falling), 3)}–{it(max(falling), 3)} VBENCH, in salita {it(min(rising), 3)}–{it(max(rising), 3)} VBENCH;'
    f' isteresi {it(min(hyst), 2)}–{it(max(hyst), 2)} V. Nessuna simulazione dinamica.',
    '2. UART 10 400 baud 8N1: TX invertito (TX basso = linea rilasciata), RX non invertito.',
    '3. U1B inutilizzato: ingressi a potenziale definito, uscita 7 non collegata (×).',
    '4. Protezioni automotive (inversione, transitori, load dump, ESD) NON comprese.',
    '5. Simboli IEC 60617, schema IEC 61082-1. Incrocio senza punto: nessun contatto.',
    '\u2003\u2003Sigle con lettere di uso corrente (Q, U) coerenti con distinta e firmware.',
], step=3.6)
d.title_block(title=['Interfaccia K-line', 'autocostruita'], subtitle='Data Logger',
              doc_type='Schema elettrico', status='NON COLLAUDATO · solo banco',
              code='C3AI-DL-KL-001', rev='G', date='21/10/2026', sheet='1/1',
              revisions=[('D', 'Porte esterne evidenziate; nessuna variazione elettrica', '18/10/2026'),
                         ('E', 'Aggiunta R10 per isteresi del comparatore (D-022)', '20/10/2026'),
                         ('F', 'Ridisegno secondo IEC 60617 / IEC 61082-1 / ISO 5457 / ISO 7200 (D-024)', '20/10/2026'),
                         ('G', 'R3 con tolleranza 5 % (D-036); reti e valori invariati', '21/10/2026')])
(ROOT/'schema-kline-banco.svg').write_text(d.svg('Schema elettrico IEC 61082-1 dell\'interfaccia K-line da banco; non collaudato.'), encoding='utf-8')
