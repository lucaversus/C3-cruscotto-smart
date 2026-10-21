"""Istruzione di prova sulla presa diagnosi (C3AI-CR-PR-001), D-029 / D-030.

Rev. A: vista frontale della presa C001 secondo SAE J1962 / ISO 15031-3, vie da
misurare evidenziate, sequenza di prova e tabella dei risultati da compilare.
Piedinatura dal manuale MAN-017 PDF 2 (pag. 91): non ancora misurata sulla vettura.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-logger/docs/tools'))
from iso_drawing import Sheet  # noqa: E402

FUNCTION = {
    1: '+ dopo contatto', 4: 'massa scocca', 5: 'massa scocca', 7: 'linea K motore',
    11: 'linea K3 BSI', 12: 'linea K4 ABS/ESP', 16: '+ batteria',
}
MEASURE = {1, 4, 5, 16}
FORBIDDEN = {7, 11, 12}

d = Sheet('C3AI-CR-PR-001 rev A — Prova presa diagnosi')
d.frame()
d.text(25, 20, 'PROVA SULLA PRESA DIAGNOSI (OBD) — ALIMENTAZIONE, SEGNALE CHIAVE E CALO ALL\'AVVIAMENTO', 5, bold=True)
d.text(25, 25, 'Scopo: verificare le vie 16 (+ batteria) e 1 (+ dopo contatto) previste per il cruscotto (D-030) '
               'e misurare la tensione minima durante l\'avviamento.', 2.5)

# --- Vista frontale della presa (lato di innesto dello strumento) -------------------
cx, top = 108.0, 48.0
pitch, row_gap = 18.0, 30.0
wt, wb, hh = 8 * pitch + 16, 8 * pitch + 2, row_gap + 30
d.text(cx, top - 4, 'PRESA C001 — VISTA FRONTALE (lato dove si innesta lo strumento)', 3.5, 'middle', True)
# Contorno trapezoidale: lato lungo in alto (vie 1-8), lato corto in basso (vie 9-16).
d.line((cx - wt / 2, top), (cx + wt / 2, top), (cx + wb / 2 + 4, top + hh), (cx - wb / 2 - 4, top + hh),
       (cx - wt / 2, top), width=0.7)
for row, first in ((0, 1), (1, 9)):
    y = top + 15 + row * row_gap
    for i in range(8):
        n = first + i
        x = cx - 3.5 * pitch + i * pitch
        if n in MEASURE:
            d.circle(x, y, 6.0, fill='#bfe8bf', width=0.7)
        elif n in FORBIDDEN:
            d.circle(x, y, 6.0, fill='#f6b8b8', width=0.7)
            d.line((x - 4, y - 4), (x + 4, y + 4), width=0.7); d.line((x - 4, y + 4), (x + 4, y - 4), width=0.7)
        else:
            d.circle(x, y, 4.0, fill='white', width=0.35)
        d.text(x, y + (row and 12 or -8.5), str(n), 5, 'middle', True)

# Legenda dei colori
ly = top + hh + 12
d.circle(40, ly, 2.5, fill='#bfe8bf', width=0.7); d.text(45, ly + 1.2, 'Via da misurare (puntali solo qui)', 3.5)
d.circle(120, ly, 2.5, fill='#f6b8b8', width=0.7); d.text(125, ly + 1.2, 'NON TOCCARE: vie 7, 11, 12', 3.5, bold=True)
d.text(30, ly + 9, 'I numeri sono stampati sulla presa, spesso in piccolo: confrontarli con il disegno', 3)
d.text(30, ly + 13.5, 'prima di misurare. Se la presa è capovolta, il lato lungo (vie 1-8) resta il riferimento.', 3)

# Funzioni dichiarate dal manuale
d.notes(30, ly + 25, 'FUNZIONI DELLE VIE SECONDO IL MANUALE (MAN-017 PDF 2, pag. 91)',
        [f'Via {n:>2}: {FUNCTION[n]}' for n in sorted(FUNCTION)] +
        ['Vie non elencate: non collegate secondo il manuale.',
         'La via 1 "+ dopo contatto" non è standard OBD: da confermare con questa prova.'], h=3, step=4.6)

# --- Sequenza di prova ----------------------------------------------------------------
X = 215
d.notes(X, 45, 'STRUMENTO E PREPARAZIONE', [
    'Multimetro UNI-T UT210E (HW-MULTIMETER), funzione V DC (tensione continua).',
    'Usare i puntali, non la pinza amperometrica. Nessun altro strumento collegato alla presa.',
    'Puntale NERO sempre sulla via 4 (in alternativa via 5).',
], h=3, step=4.6)
d.notes(X, 70, 'SEQUENZA', [
    'P1  Chiave tolta: ROSSO su via 16 → atteso circa 12 V.',
    'P2  Chiave tolta: ROSSO su via 1 → atteso circa 0 V.',
    'P3  Chiave su marcia (quadro acceso, motore spento): ROSSO su via 1 → atteso circa 12 V.',
    'P4  Chiave su marcia: ROSSO su via 16 → atteso circa 12 V.',
    'P5  ROSSO su via 16, avviare il motore: annotare il valore più basso visto.',
    '     Serve una seconda persona o il tester fissato: non guidare con i puntali in mano.',
    'P6  Motore acceso al minimo: ROSSO su via 16 → atteso circa 13,5-14,5 V (alternatore).',
], h=3, step=4.6)
d.notes(X, 113, 'SICUREZZA', [
    'Toccare solo le vie 1, 4, 5, 16. Non cortocircuitare contatti vicini con la punta.',
    'Non misurare le vie 7, 11, 12 né i fili multiplex del quadro (MAN-017 PDF 3).',
    'Il tester è lento: non coglie cali di pochi millisecondi. Il valore di P5 è indicativo.',
], h=3, step=4.6)

# Tabella risultati da compilare (righe dall'alto verso il basso: P1 ... P6).
rows = [
    ('P6', 'via 16', 'motore acceso', '13,5-14,5 V', ''),
    ('P5', 'via 16', 'avviamento: minimo', '—', ''),
    ('P4', 'via 16', 'chiave su marcia', '~12 V', ''),
    ('P3', 'via 1', 'chiave su marcia', '~12 V', ''),
    ('P2', 'via 1', 'chiave tolta', '~0 V', ''),
    ('P1', 'via 16', 'chiave tolta', '~12 V', ''),
]
d.text(X, 146, 'RISULTATI DA COMPILARE (nero su via 4)', 3.5, bold=True)
d.parts_list(X, 149, rows, widths=(12, 20, 40, 28, 85),
             heads=('Prova', 'Rosso su', 'Condizione', 'Atteso', 'Valore letto / note'))

d.notes(X, 194, 'COME RIFERIRE', [
    'Scrivere nella chat i valori P1-P6 così come letti. Verranno registrati nel registro moduli',
    'e nel documento alimentazione-spegnimento.md (D-030) prima di qualsiasi collegamento.',
], h=3, step=4.6)

d.title_block(title=['Prova presa', 'diagnosi OBD'], subtitle='Cruscotto digitale',
              doc_type='Istruzione di prova', status='DA ESEGUIRE · NON VERIFICATO',
              code='C3AI-CR-PR-001', rev='A', date='20/10/2026', sheet='1/1',
              revisions=[('A', 'Prima emissione: vie 1/16, segnale chiave e calo all\'avviamento (D-030)', '20/10/2026')])
out = ROOT / 'cruscotto/docs/prova-presa-obd.svg'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(d.svg('Istruzione di prova sulla presa diagnosi C001: piedinatura da manuale, non misurata.'),
               encoding='utf-8')
print(out)
