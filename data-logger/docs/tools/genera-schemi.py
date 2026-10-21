"""Genera C3AI-DL-EL-001 (storico) e C3AI-DL-BL-001 (schema a blocchi) — D-024.

IEC 61082-1 / IEC 60617, foglio ISO 5457 A3, cartiglio ISO 7200.
EL-001 conserva il contenuto della proposta iniziale (rev. D) ed è marcato
come sostituito da EL-003: non va usato per cablare.
"""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from iso_drawing import Sheet, THICK  # noqa: E402

PINS = json.loads((ROOT / 'hardware.json').read_text(encoding='utf-8'))['wiring_proposal']['pins']


def superseded_stamp(d, x, y, text):
    d.rect(x, y, 150, 18, width=THICK)
    d.text(x + 75, y + 8, 'DOCUMENTO SOSTITUITO — NON USARE', 5, 'middle', True)
    d.text(x + 75, y + 14, text, 2.5, 'middle')


# ---------------------------------------------------------------- EL-001 ---
d = Sheet('C3AI-DL-EL-001 rev E — Collegamenti proposta iniziale (storico)')
d.frame()
d.text(25, 20, 'COLLEGAMENTI DELLA PROPOSTA INIZIALE — SCHEMA DI COLLEGAMENTO (STORICO)', 5, bold=True)
d.text(25, 25, 'Contenuto invariato rispetto alla rev. D (firmware 0.1.0, pulsanti opzionali). Superato da D-015 e da C3AI-DL-EL-003.', 2.5)
superseded_stamp(d, 250, 35, 'Sostituito da C3AI-DL-EL-003 (collegamenti banco logger 0.3.x)')

rows = [None] * 21
def put(i, pin, label): rows[i] = (pin, label)
put(0, '3V3', '3V3'); put(2, 'GND', 'GND')
put(4, 'D21', 'GPIO21'); put(5, 'D22', 'GPIO22')
put(16, 'D18', 'GPIO18'); put(17, 'D23', 'GPIO23'); put(18, 'D19', 'GPIO19'); put(19, 'D27', 'GPIO27')
left = [None] * 21
left[14] = ('D32', 'GPIO32'); left[18] = ('D33', 'GPIO33')
a1 = d.element(95, 50, 40, 125, '-A1', 'ESP32 HW-394',
               pins_right=[r if r else (None, None) for r in rows],
               pins_left=[r if r else (None, None) for r in left], first=10, pitch=5)
d.wire(a1['3V3'], (145, 60)); d.supply_side(145, 60, '+3V3', 1)
d.wire(a1['GND'], (145, 70)); d.ground_side(145, 70, 1)
X = 235
rtc = d.element(X, 72.5, 40, 20, '-A2', 'RTC DS3231', pins_left=[('', 'VCC'), ('', 'SDA'), ('', 'SCL'), ('', 'GND')], first=2.5, pitch=5)
oled = d.element(X, 102.5, 40, 20, '-A3', 'OLED I²C', pins_left=[('', 'VCC'), ('', 'SDA'), ('', 'SCL'), ('', 'GND')], first=2.5, pitch=5)
sd = d.element(X, 132.5, 40, 30, '-A4', 'MicroSD SPI 3,3 V', pins_left=[('', '3V3'), ('', 'CLK'), ('', 'MOSI'), ('', 'MISO'), ('', 'CS'), ('', 'GND')], first=2.5, pitch=5)
for m in (rtc, oled):
    for name, kind in (('VCC', 'v'), ('GND', 'g')):
        p = m[name]; d.wire(p, (p[0] - 7.5, p[1]))
        (d.supply_side(p[0] - 7.5, p[1], '+3V3') if kind == 'v' else d.ground_side(p[0] - 7.5, p[1]))
for name, kind in (('3V3', 'v'), ('GND', 'g')):
    p = sd[name]; d.wire(p, (p[0] - 7.5, p[1]))
    (d.supply_side(p[0] - 7.5, p[1], '+3V3') if kind == 'v' else d.ground_side(p[0] - 7.5, p[1]))
sda, scl = a1['GPIO21'], a1['GPIO22']
assert sda[1] == rtc['SDA'][1] and scl[1] == rtc['SCL'][1]
d.wire(sda, rtc['SDA']); d.dot(180, sda[1]); d.wire((180, sda[1]), (180, oled['SDA'][1]), oled['SDA'])
d.wire(scl, rtc['SCL']); d.dot(190, scl[1]); d.wire((190, scl[1]), (190, oled['SCL'][1]), oled['SCL'])
for src, dst in (('GPIO18', 'CLK'), ('GPIO23', 'MOSI'), ('GPIO19', 'MISO'), ('GPIO27', 'CS')):
    assert a1[src][1] == sd[dst][1]
    d.wire(a1[src], sd[dst])
for src, ref, label in (('GPIO32', '-S1', 'PAGINA'), ('GPIO33', '-S2', 'CONFERMA')):
    p = a1[src]
    d.wire(p, (82.5, p[1])); end = d.push_button_no(72.5, p[1], ref, label)
    d.wire((72.5, p[1]), (60, p[1])); d.ground_side(60, p[1])
d.notes(25, 192, 'NOTE STORICHE', [
    '1. Proposta GPIO iniziale del 18/10/2026 per il futuro firmware; la 0.1.0 usava solo la seriale.',
    '2. -S1/-S2 pulsanti opzionali: sostituiti dal solo STOP su GPIO32 (D-015, EL-003).',
    '3. Collegamenti auto e alimentazione automotive: non trattati in questo documento.',
    '4. Per il cablaggio attuale usare esclusivamente C3AI-DL-EL-003.',
])
d.title_block(title=['Collegamenti proposta', 'iniziale (storico)'], subtitle='Data Logger',
              doc_type='Schema di collegamento', status='SOSTITUITO da EL-003',
              code='C3AI-DL-EL-001', rev='E', date='20/10/2026', sheet='1/1',
              revisions=[('B', 'Fili continui, cornice e cartiglio', '18/10/2026'),
                         ('C', 'Componenti illustrati', '18/10/2026'),
                         ('D', 'Note sui moduli CAN già presenti', '18/10/2026'),
                         ('E', 'Ridisegno IEC/ISO (D-024); marcato come sostituito da EL-003', '20/10/2026')])
(ROOT / 'schema-collegamenti.svg').write_text(d.svg('Documento storico, sostituito da C3AI-DL-EL-003.'), encoding='utf-8')

# ---------------------------------------------------------------- BL-001 ---
b = Sheet('C3AI-DL-BL-001 rev E — Architettura funzionale del Data Logger')
b.frame()
b.text(25, 20, 'ARCHITETTURA FUNZIONALE DEL DATA LOGGER — SCHEMA A BLOCCHI', 5, bold=True)
b.text(25, 25, 'Stato al 20/10/2026. Schema funzionale: non usare per cablare. Pin e protocolli del veicolo restano da verificare (D-008).', 2.5)

b.enclosure(28, 33, 70, 140, 'VEICOLO  Citroën C3 1.4 HDi')
b.block(33, 42, 60, 30, 'Presa OBD', ['Diagnosi motore', 'ISO 14230-4 KWP, fast init', '10,4 kbaud (da riscontrare)', 'Fronte libero (D-007)'], ref='K-line')
b.block(33, 82, 60, 30, 'Linea dietro al quadro', ['BSI Siemens Light 2001 VAN', 'VAN comfort 125 kbit/s', '(documentale, D-016/D-017)', 'Pin da identificare'], ref='VAN')
b.block(33, 135, 60, 30, 'Alimentazione 12 V', ['Punto di prelievo', 'da identificare', 'Fusibile 2 A (HW-FUSE-HOLDER)'], ref='12 V')

b.block(118, 42, 62, 30, 'Interfaccia K-line', ['2N5551 + LM2903B, isteresi', 'C3AI-DL-KL-001 rev G', 'Non montata · non collaudata'], ref='HW-KLINE-INTERFACE')
b.block(118, 82, 62, 30, 'Ricevitore VAN', ['SN65HVD230 (VP230), solo RX', 'Senza 120 Ω, TX a 3V3', 'Prerequisiti bloccanti'], ref='HW-CAN-VP230')
b.block(118, 135, 62, 30, 'Convertitore 12 V → 5 V', ['Uadme GYVRM-K240505', 'Candidato, non collaudato', 'Arresto con STOP (D-015)'], ref='HW-AUTO-POWER')

b.block(200, 60, 70, 65, 'ESP32 HW-394', ['Logger: sorgenti 0.3.1,', '0.3.0 caricata a banco', 'UART2 KWP: GPIO16 RX / 17 TX', 'RMT VAN: GPIO34', 'SPI SD: 18/19/23, CS 27', 'I²C: 21 SDA / 22 SCL', 'STOP: GPIO32', 'Nessuna radio attiva'], ref='HW-ESP32')
b.block(290, 42, 55, 22, 'MicroSD', ['CSV v2, sync 1 s', 'SPI 1 MHz predefinito'], ref='HW-SD-MODULE')
b.block(290, 72, 55, 22, 'RTC DS3231', ['Ancora oraria UTC', 'CR2032 dopo D-019'], ref='HW-RTC')
b.block(290, 102, 55, 22, 'OLED I²C', ['Stato, righe, perdite'], ref='HW-OLED')
b.block(290, 132, 55, 22, 'Pulsante STOP', ['NO verso massa', 'SALVATO prima di spegnere'], ref='HW-STOP-BUTTON')
b.block(355, 72, 50, 30, 'PC / analisi', ['USB: seriale, carico', 'Dataset per TinyML', '(fase successiva)'], ref='Esterno', dash='3 1.5')
b.block(200, 140, 70, 25, 'MCP2515 (non usato)', ['CS GPIO26 tenuto alto', 'Non decodifica VAN'], ref='HW-CAN-MCP2515', dash='3 1.5')

# Flussi di segnale (frecce piene) e di energia (tratto più spesso).
b.arrow((93, 57), (118, 57), both=True); b.text(105.5, 55.5, 'K', 2.5, 'middle')
b.arrow((93, 97), (118, 97)); b.text(105.5, 95.5, 'VAN', 2.5, 'middle')
b.arrow((180, 57), (190, 57), (190, 75), (200, 75), both=True); b.text(184, 70, 'UART', 2.2)
b.arrow((180, 97), (200, 97)); b.text(190, 95.5, 'RX', 2.2, 'middle')
b.arrow((270, 70), (280, 70), (280, 53), (290, 53), both=True); b.text(281, 62, 'SPI', 2.2)
b.arrow((270, 83), (290, 83), both=True); b.text(280, 81.5, 'I²C', 2.2, 'middle')
b.arrow((280, 83), (280, 113), (290, 113))
b.arrow((290, 143), (283, 143), (283, 120), (270, 120)); b.text(284.5, 135, 'GPIO', 2.2)
b.arrow((255, 60), (255, 36), (380, 36), (380, 72), both=True, dash='3 1.5')
b.text(318, 34.5, 'USB (banco): alimentazione e seriale', 2.2, 'middle')
b.arrow((93, 150), (118, 150), width=0.7); b.text(105.5, 148.5, '12 V', 2.5, 'middle')
b.arrow((180, 150), (190, 150), (190, 115), (200, 115), width=0.7); b.text(184, 133, '5 V', 2.5)

b.notes(25, 188, 'LEGENDA E NOTE', [
    'Freccia piena: flusso di segnale (doppia punta = bidirezionale). Linea spessa: alimentazione.',
    'Riquadro tratteggiato: elemento esterno o non usato. Recinzione a tratto e punto: veicolo.',
    'Sigle HW-xxx come in hardware.json. Nessun collegamento diretto veicolo → GPIO.',
    'Interfacce, alimentazione e punti di prelievo: proposte non collaudate (D-020, D-022).',
    'Dettagli: KL-001 (K-line), EL-003 (banco), protocolli-veicolo.md, alimentazione-spegnimento.md.',
])
b.title_block(title=['Architettura funzionale', 'del Data Logger'], subtitle='Data Logger',
              doc_type='Schema a blocchi', status='PRELIMINARE',
              code='C3AI-DL-BL-001', rev='E', date='21/10/2026', sheet='1/1',
              revisions=[('B', 'Cornice e cartiglio; stato aggiornato', '18/10/2026'),
                         ('C', 'Note sui moduli CAN già presenti', '18/10/2026'),
                         ('D', 'Ridisegno IEC 61082-1/ISO; aggiornato a KWP, VAN, logger 0.3.x (D-024)', '20/10/2026'),
                         ('E', 'Riferimento a KL-001 rev G; nessuna variazione funzionale', '21/10/2026')])
(ROOT / 'schema-sistema.svg').write_text(b.svg('Schema a blocchi funzionale preliminare, non schema di cablaggio.'), encoding='utf-8')

for f in ROOT.glob('*.svg'):
    ET.parse(f)
print('SVG generati e XML validato')
