"""Schema a blocchi preliminare della scheda madre del cruscotto (C3AI-CR-BL-001), D-028…D-030.

Rev. C: IMU LSM6DSO. Rev. B (D-031): ventola 12 V, NTC, dominio sempre acceso. Rev. A: architettura funzionale, connettori J1 (auto) e J2 (verso l'S3), ripartizione dei
GPIO del front-end. Proposta di progetto, non schema elettrico esecutivo.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

d = Sheet('C3AI-CR-BL-001 rev C — Scheda madre, schema a blocchi preliminare')
d.frame()
d.text(25, 20, 'SCHEDA MADRE DEL CRUSCOTTO — SCHEMA A BLOCCHI PRELIMINARE', 5, bold=True)
d.text(25, 25, 'Schema funzionale (IEC 61082-1): non usare per cablare. Pin del veicolo da manuali generici, '
               'da verificare (D-008); componenti proposti, non scelti né collaudati.', 2.5)

# --- Veicolo e connettore J1 -----------------------------------------------------
d.block(25, 35, 55, 30, 'Presa OBD C001 (retro)', ['via 16  + batteria', 'via 1   + dopo contatto',
        'via 4/5 massa', 'via 7   linea K'], ref='Veicolo')
d.block(25, 72, 55, 22, 'Quadro 0004 (18 vie NR)', ['vie 1/3  VAN 9004A/9005A', 'via 9    massa M0004',
        'via 7 XE1: NON collegare'], ref='Veicolo')
d.block(25, 101, 55, 22, 'Radio originale', ['uscite altoparlanti', 'anteriori Sx/Dx (a ponte)'], ref='Veicolo')
d.block(25, 130, 55, 15, 'Altoparlanti anteriori', ['Sx / Dx'], ref='Veicolo')
d.rect(88, 35, 12, 160, width=0.7)
d.text(94, 33, '-J1', 3.5, 'middle', True)
d.text(94, 200, 'connettore', 2.2, 'middle'); d.text(94, 203, 'multipolare', 2.2, 'middle')
for y in (47, 80, 108, 137):
    d.arrow((80, y), (88, y), both=True)

# --- Recinzione della scheda madre --------------------------------------------------
d.rect(105, 32, 200, 178, width=0.35, dash='12 3 0.5 3')
d.text(108, 37, '-A1  SCHEDA MADRE (circuito stampato dedicato, montaggio in fabbrica)', 3, bold=True)

# Alimentazione
d.block(110, 48, 58, 34, 'Ingresso 12 V', ['fusibile di ramo (F, nel cablaggio)', 'inversione polarità, TVS, filtro',
        'dominio sempre acceso: LDO a basso', 'consumo, ventola 12 V PWM (D-031)', 'mantenimento: MOSFET lato alto'], ref='-U1…U3')
d.block(110, 88, 58, 24, 'Riserva avviamento', ['diodo + supercondensatore', 'carica limitata', 'capacità da calcolare (D-030)'],
        ref='-C1')
d.block(110, 118, 58, 22, 'Convertitore 12 → 5 V', ['buck, ingresso ≥ 40 V, 5 V 2-3 A', '+ LDO 3,3 V basso consumo'],
        ref='-U4/U5')
d.arrow((100, 59), (110, 59))
d.arrow((168, 65), (176, 65)); d.arrow((139, 82), (139, 88)); d.arrow((139, 112), (139, 118))
d.arrow((168, 124), (176, 124))
d.text(172, 122.5, '3V3', 1.8, 'middle')
d.arrow((168, 132), (172, 132), (172, 156), (176, 156)); d.text(170.5, 145, '5 V', 1.8, 'end')

# Front-end
d.block(176, 48, 64, 86, 'Front-end ESP32', ['ESP32-WROOM-32E-H4/H8', '(senza PSRAM, −40…105 °C)', '',
        'GPIO16/17  UART2 K-line', 'GPIO34     VAN RX', 'GPIO21/22  I2C (IMU, RTC)',
        'GPIO25/33  UART1 verso S3', 'GPIO35     tensione batteria', 'GPIO39     segnale chiave',
        'GPIO13     mantenimento', 'GPIO4      LED di stato', 'GPIO26/14  ventola PWM/giri (D-031)',
        'GPIO36/32  NTC display/scheda', 'MicroSD opz. 18/19/23/27',
        '(stessi pin del logger 0.3.x)'], ref='-U6')
d.block(246, 48, 54, 18, 'Ricevitore VAN', ['SN65HVD230, solo RX', 'D a 3V3, nessuna 120 Ω'], ref='-U7')
d.block(246, 72, 54, 18, 'Interfaccia K-line', ['circuito KL-001 rev F', '2N5551 + LM2903B'], ref='-U8')
d.block(246, 96, 54, 22, 'IMU + RTC (opz.)', ['LSM6DSO 0x6A, fissaggio', 'rigido, assi in serigrafia', 'DS3231 0x68 opzionale'],
        ref='-U9/U10')
d.block(246, 124, 54, 18, 'Programmazione', ['USB-seriale + reset auto', 'o connettore 6 poli'], ref='-U11')
for y in (57, 81, 107, 131):
    d.arrow((246, y), (240, y), both=True)

# Segnali dal veicolo verso front-end e interfacce: canale superiore.
d.line((100, 42), (303, 42), (303, 81))
d.arrow((303, 57), (300, 57)); d.dot(303, 57)
d.arrow((303, 81), (300, 81))
d.arrow((208, 42), (208, 48)); d.dot(208, 42)
d.text(112, 40.8, 'VAN (quadro vie 1/3) · K-line (OBD via 7) · chiave (OBD via 1, verso GPIO39 protetto)', 2, 'start')

# Connettore verso l'S3 e audio
d.block(176, 146, 124, 20, 'Connettore -J2 verso ESP32-S3', ['P1: 5 V, GND  ·  P2: IO11 RX, IO12 TX, IO13 relè, IO19 riserva',
        'P6 Speak: uscita audio (funzione U1 da confermare)'], ref='-J2')
d.arrow((208, 134), (208, 146), both=True); d.text(210, 141, 'UART', 1.8)
d.block(176, 174, 124, 28, 'Commutazione audio (D-028)', ['relè doppio scambio per canale: a riposo radio → altoparlanti',
        'eccitato: uscita audio S3 → altoparlanti; mai a massa le uscite radio (a ponte)',
        'pilotaggio a transistor + diodo di ricircolo, comando dall\'S3, spento al reset'], ref='-K1/K2')
d.arrow((238, 166), (238, 174)); d.text(240, 171, 'audio + comando relè', 1.8)
d.arrow((100, 188), (176, 188), both=True); d.text(104, 186.5, 'radio ⇄ altoparlanti (4 fili per canale)', 2)

# --- ESP32-S3 ------------------------------------------------------------------
d.block(315, 146, 85, 48, 'ESP32-S3 8048S050', ['display 5″, IA, messaggi in flash', 'P1 ← 5 V', 'P2 ↔ UART, relè',
        'P6 → audio', 'nessun filo diretto al veicolo', '(D-029)'], ref='-A2')
d.arrow((300, 156), (315, 156), both=True)

# Note
d.notes(315, 40, 'NOTE', [
    '1  J1: connettore multipolare unico verso il cablaggio',
    '   auto (tipo da scegliere, es. Micro-Fit 3.0).',
    '2  Il fusibile di ramo sta nel cablaggio, vicino al',
    '   prelievo OBD via 16 (HW-FUSE-HOLDER).',
    '3  Riferimento di massa VAN: via 9 del quadro.',
    '4  VAN: quale filo sia DATA non è indicato dagli',
    '   schemi; prerequisiti D-022 bloccanti.',
    '5  Spento: consumo obiettivo < 1 mA (D-030).',
    '6  Front-end = logger 0.3.x senza OLED/STOP: stesso',
    '   formato dati per l\'addestramento dell\'IA.',
    '7  UART verso S3 su P2 (IO11/12): lascia IO17/18',
    '   all\'amplificatore U1 se confermato.',
], h=2.5, step=4.2)

d.title_block(title=['Scheda madre', 'schema a blocchi'], subtitle='Cruscotto digitale',
              doc_type='Schema a blocchi', status='PRELIMINARE · NON VERIFICATO',
              code='C3AI-CR-BL-001', rev='C', date='22/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione preliminare (D-028, D-029, D-030)', '20/10/2026'),
                         ('B', 'Ventola, NTC e dominio sempre acceso (D-031)', '21/10/2026'),
                         ('C', 'IMU LSM6DSO (HW-IMU-LSM6DSO) al posto di LSM6DS3', '22/10/2026')])
out = ROOT / 'disegni/sorgenti/CR-BL-001_scheda-madre-blocchi.svg'
out.write_text(d.svg('Schema a blocchi preliminare della scheda madre; proposta, non schema esecutivo.'), encoding='utf-8')
print(out)
