"""Schema di collegamento del banco logger (C3AI-DL-EL-003), GPIO letti da hardware.json.

Rev. B (D-024): IEC 61082-1 schema di collegamento, simboli IEC 60617, foglio ISO 5457 A3,
cartiglio ISO 7200, tabella dei collegamenti con fili numerati.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

PINS = json.loads((ROOT / 'data-logger/docs/hardware.json').read_text(encoding='utf-8'))['wiring_proposal']['pins']
g = {k: PINS[k] for k in ('kSda', 'kScl', 'kSck', 'kMiso', 'kMosi', 'kSdCs', 'kStopPin')}

d = Sheet('C3AI-DL-EL-003 rev B — Collegamenti banco logger')
d.frame()
d.text(25, 20, 'COLLEGAMENTI PER LA PROVA A BANCO DEL LOGGER — SCHEMA DI COLLEGAMENTO', 5, bold=True)
d.text(25, 25, f'Firmware 0.3.x, profilo esp32-hw394-logger. Alimentazione soltanto da USB. GPIO da hardware.json (proposta, non collaudo).', 2.5)

# -A1 ESP32: morsetti usati, in ordine logico (non la posizione sul connettore della scheda).
rows = [None] * 21
def put(i, pin, label): rows[i] = (pin, label)
put(0, '3V3', '3V3'); put(2, 'GND', 'GND')
put(5, f'D{g["kSdCs"]}', f'GPIO{g["kSdCs"]}'); put(7, f'D{g["kMosi"]}', f'GPIO{g["kMosi"]}')
put(9, f'D{g["kSck"]}', f'GPIO{g["kSck"]}'); put(11, f'D{g["kMiso"]}', f'GPIO{g["kMiso"]}')
put(14, f'D{g["kSda"]}', f'GPIO{g["kSda"]}'); put(16, f'D{g["kScl"]}', f'GPIO{g["kScl"]}')
put(20, f'D{g["kStopPin"]}', f'GPIO{g["kStopPin"]}')
right = [r if r else (None, None) for r in rows]
a1 = d.element(70, 40, 40, 125, '-A1', 'ESP32 HW-394 (30 pin)', pins_right=right, first=10, pitch=5,
               pins_bottom=[('USB', 'USB')], )
d.text(90, 100, 'HW-ESP32', 3.5, 'middle', True)
d.text(90, 105, 'ESP-32D', 2.5, 'middle')
usb = a1['USB']
d.wire(usb, (usb[0], 178)); d.text(usb[0] - 2, 182, '-X1  USB verso PC: alimentazione e seriale', 2.5, 'end')
# Alimentazione di -A1 verso i moduli: riferimenti di potenziale (IEC 61082-1).
d.wire(a1['3V3'], (120, 50)); d.supply_side(120, 50, '+3V3', 1)
d.wire(a1['GND'], (120, 60)); d.ground_side(120, 60, 1)

# Moduli con morsetti nell'ordine della serigrafia documentata in hardware.json.
X = 225
sd = d.element(X, 45, 40, 35, '-A2', 'Lettore MicroSD (HW-SD-MODULE)', pins_left=[
    ('', '3V3'), ('', 'CS'), ('', 'MOSI'), ('', 'CLK'), ('', 'MISO'), ('', 'GND')], first=5, pitch=5)
rtc = d.element(X, 100, 40, 35, '-A3', 'RTC DS3231 (HW-RTC)', pins_left=[
    ('', 'GND'), ('', 'VCC'), ('', 'SDA'), ('', 'SCL'), ('', 'SQW'), ('', '32K')], first=5, pitch=5)
oled = d.element(X, 150, 40, 25, '-A4', 'OLED I²C (HW-OLED)', pins_left=[
    ('', 'GND'), ('', 'VCC'), ('', 'SCL'), ('', 'SDA')], first=5, pitch=5)

def to_module(src, trunk_x, dst, wire_no):
    d.wire(src, (trunk_x, src[1]), (trunk_x, dst[1]), dst)
    d.text(dst[0] - 2, dst[1] - 0.8, wire_no, 2, 'end')

# Bus SPI: tronchi verticali crescenti verso il basso, senza incroci.
to_module(a1[f'GPIO{g["kSdCs"]}'], 150, sd['CS'], 'W3')
to_module(a1[f'GPIO{g["kMosi"]}'], 157.5, sd['MOSI'], 'W4')
to_module(a1[f'GPIO{g["kSck"]}'], 165, sd['CLK'], 'W5')
to_module(a1[f'GPIO{g["kMiso"]}'], 172.5, sd['MISO'], 'W6')

# Bus I²C condiviso: giunzioni a T con punto.
sda, scl = a1[f'GPIO{g["kSda"]}'], a1[f'GPIO{g["kScl"]}']
d.wire(sda, (185, sda[1])); d.dot(185, sda[1])
d.wire((185, sda[1]), (185, rtc['SDA'][1]), rtc['SDA']); d.text(rtc['SDA'][0] - 2, rtc['SDA'][1] - 0.8, 'W9', 2, 'end')
d.wire((185, sda[1]), (185, oled['SDA'][1]), oled['SDA']); d.text(oled['SDA'][0] - 2, oled['SDA'][1] - 0.8, 'W13', 2, 'end')
d.wire(scl, (195, scl[1])); d.dot(195, scl[1])
d.wire((195, scl[1]), (195, rtc['SCL'][1]), rtc['SCL']); d.text(rtc['SCL'][0] - 2, rtc['SCL'][1] - 0.8, 'W10', 2, 'end')
d.wire((195, scl[1]), (195, oled['SCL'][1]), oled['SCL']); d.text(oled['SCL'][0] - 2, oled['SCL'][1] - 0.8, 'W14', 2, 'end')
d.text(186, sda[1] - 1.5, 'SDA', 2.2); d.text(196, scl[1] - 1.5, 'SCL', 2.2)

# Alimentazione dei moduli: riferimenti +3V3 e massa, fili W1/W2, W7/W8, W11/W12 in tabella.
def power(pt, kind, wire_no):
    x = pt[0] - 7.5
    d.wire(pt, (x, pt[1]))
    if kind == 'vcc': d.supply_side(x, pt[1], '+3V3')
    else: d.ground_side(x, pt[1])
    d.text(pt[0] - 2, pt[1] - 0.8, wire_no, 2, 'end')
power(sd['3V3'], 'vcc', 'W1'); power(sd['GND'], 'gnd', 'W2')
power(rtc['VCC'], 'vcc', 'W7'); power(rtc['GND'], 'gnd', 'W8')
power(oled['VCC'], 'vcc', 'W11'); power(oled['GND'], 'gnd', 'W12')
for name in ('SQW', '32K'):
    p = rtc[name]; d.wire(p, (p[0] - 3, p[1])); d.not_connected(p[0] - 3, p[1])

# -S1 pulsante STOP normalmente aperto verso massa.
stop = a1[f'GPIO{g["kStopPin"]}']
d.wire(stop, (130, stop[1])); end = d.push_button_no(130, stop[1], '-S1', 'STOP (NO)')
d.wire(end, (147.5, stop[1])); d.ground(147.5, stop[1])
d.text(131, stop[1] + 7.5, 'W15 / W16', 2)

d.notes(285, 45, 'NOTE', [
    '1. Cablare a USB scollegata. Moduli a 3,3 V, masse comuni.',
    '2. Non usare VIN per alimentare i moduli al banco.',
    f'3. -S1: due contatti che si chiudono solo premendo. Pull-up interna',
    f'  attivata dal firmware su GPIO{g["kStopPin"]}.',
    '4. -A3: CR2032 fuori finché il ramo di ricarica non è disabilitato',
    '  (D-019). SQW e 32K non collegati (×).',
    '5. Ordine dei morsetti di -A2/-A3/-A4 come da serigrafia; -A1 in ordine',
    '  logico: collegare per nome (D23 = GPIO23), non per posizione.',
    '6. Scollegati per questa prova: MCP2515, VP230, interfaccia K-line',
    '  e tutti i fili dell\'auto.',
    '7. Tutti i riferimenti +3V3 sono il morsetto 3V3 di -A1; tutte le masse',
    '  il morsetto GND di -A1 (fili W1–W16 in tabella).',
    '8. Simboli IEC 60617; schema IEC 61082-1. Incrocio senza punto:',
    '  nessun contatto.',
], step=3.8)

conn = [
    ('W1', '-A1:3V3', '-A2:3V3', '+3V3'), ('W2', '-A1:GND', '-A2:GND', 'GND'),
    ('W3', f'-A1:D{g["kSdCs"]}', '-A2:CS', 'SPI CS'), ('W4', f'-A1:D{g["kMosi"]}', '-A2:MOSI', 'SPI MOSI'),
    ('W5', f'-A1:D{g["kSck"]}', '-A2:CLK', 'SPI SCK'), ('W6', f'-A1:D{g["kMiso"]}', '-A2:MISO', 'SPI MISO'),
    ('W7', '-A1:3V3', '-A3:VCC', '+3V3'), ('W8', '-A1:GND', '-A3:GND', 'GND'),
    ('W9', f'-A1:D{g["kSda"]}', '-A3:SDA', 'I²C SDA'), ('W10', f'-A1:D{g["kScl"]}', '-A3:SCL', 'I²C SCL'),
    ('W11', '-A1:3V3', '-A4:VCC', '+3V3'), ('W12', '-A1:GND', '-A4:GND', 'GND'),
    ('W13', f'-A1:D{g["kSda"]}', '-A4:SDA', 'I²C SDA'), ('W14', f'-A1:D{g["kScl"]}', '-A4:SCL', 'I²C SCL'),
    ('W15', f'-A1:D{g["kStopPin"]}', '-S1:1', 'STOP'), ('W16', '-A1:GND', '-S1:2', 'GND'),
]
d.parts_list(25, 192, conn, widths=(15, 35, 35, 30), heads=('Filo', 'Da', 'A', 'Segnale'))
d.text(25, 190, 'TABELLA DEI COLLEGAMENTI', 3.5, bold=True)
d.title_block(title=['Collegamenti banco', 'logger'], subtitle='Data Logger',
              doc_type='Schema di collegamento', status='PROPOSTO · NON COLLAUDATO',
              code='C3AI-DL-EL-003', rev='B', date='20/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione per firmware 0.3.0, moduli illustrati', '19/10/2026'),
                         ('B', 'Ridisegno IEC 61082-1 / IEC 60617 / ISO 5457 / ISO 7200; fili numerati (D-024)', '20/10/2026')])
out = ROOT / 'disegni/sorgenti/DL-EL-003_collegamenti-banco-logger.svg'
out.write_text(d.svg('Schema di collegamento IEC 61082-1 per la prova USB a banco; non collaudo fisico.'), encoding='utf-8')
print(out)
