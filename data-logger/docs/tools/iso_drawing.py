"""Libreria comune per gli elaborati grafici del progetto Cruscotto C3+AI (D-024).

Riferimenti applicati:
- ISO 5457: formato A3 orizzontale 420 x 297 mm, cornice (margine sinistro 20 mm
  per l'archiviazione, 10 mm sugli altri lati), zone di riferimento 8 x 6 con
  numeri e lettere nel margine, segni di centraggio.
- ISO 7200: cartiglio di 180 mm nell'angolo in basso a destra, con campi
  obbligatori (proprietario, titolo, tipo e stato del documento, codice,
  revisione, data, lingua, foglio) e tabella delle revisioni sopra.
- IEC 61082-1: linee di collegamento continue di spessore unico, giunzioni a T
  con punto, nessuna giunzione a quattro vie, incrocio senza punto = nessun
  contatto, sigla e valore accanto al simbolo, recinzioni a tratto e punto.
- IEC 60617: simboli grafici (resistore, condensatore, NPN, amplificatore,
  terra, morsetto, contatto a pulsante); IEC 81346-1 per il prefisso "-" delle sigle.
- ISO 3098: scrittura diritta, altezze nominali 2,5 / 3,5 / 5 / 7 mm.
- ISO 128: spessori 0,25 (sottile), 0,35 (collegamenti e simboli), 0,7 mm (cornice).

Unità del disegno: millimetri. Coordinate su griglia di 2,5 mm.
"""
from html import escape
import math

W, H = 420.0, 297.0
FRAME = (20.0, 10.0, 410.0, 287.0)          # x0, y0, x1, y1 della cornice
FONT = "osifont, 'DejaVu Sans Condensed', 'Arial Narrow', Arial, sans-serif"
INK = '#000000'
THIN, NORMAL, THICK = 0.25, 0.35, 0.7
# Tratto e punto, ISO 128 tipo 04 (sottile): 12 / 3 / 0,5 / 3 mm.
DASH_DOT = '12 3 0.5 3'
DASHED = '3 1.5'


def num(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.')


class Sheet:
    def __init__(self, title):
        self.title = title
        self.items = []

    # --- primitive ---------------------------------------------------------
    def raw(self, svg):
        self.items.append(svg)

    def line(self, *points, width=NORMAL, dash=None):
        d = 'M' + ' L'.join(f'{num(x)} {num(y)}' for x, y in points)
        extra = f' stroke-dasharray="{dash}"' if dash else ''
        self.raw(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def wire(self, *points):
        """Linea di collegamento: solo tratti orizzontali e verticali."""
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            assert x0 == x1 or y0 == y1, f'collegamento obliquo {points}'
        self.line(*points)

    def rect(self, x, y, w, h, width=NORMAL, dash=None, fill='none'):
        extra = f' stroke-dasharray="{dash}"' if dash else ''
        self.raw(f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" '
                 f'fill="{fill}" stroke="{INK}" stroke-width="{width}"{extra}/>')

    def circle(self, x, y, r, fill='none', width=NORMAL):
        self.raw(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{fill}" '
                 f'stroke="{INK}" stroke-width="{width}"/>')

    def text(self, x, y, value, h=2.5, anchor='start', bold=False, rotate=0):
        weight = ' font-weight="bold"' if bold else ''
        rot = f' transform="rotate({rotate} {num(x)} {num(y)})"' if rotate else ''
        self.raw(f'<text x="{num(x)}" y="{num(y)}" font-family="{FONT}" font-size="{num(h)}" '
                 f'text-anchor="{anchor}" fill="{INK}"{weight}{rot}>{escape(str(value))}</text>')

    def dot(self, x, y):
        """Giunzione (IEC 60617-03-02-04)."""
        self.raw(f'<circle cx="{num(x)}" cy="{num(y)}" r="0.7" fill="{INK}"/>')

    # --- simboli IEC 60617 -------------------------------------------------
    def resistor(self, x0, y0, x1, y1, ref, value, label_side=None):
        """Resistore 04-01-01: rettangolo 7,5 x 2,5 mm al centro del tratto."""
        horizontal = y0 == y1
        assert horizontal or x0 == x1
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        L, B = 7.5, 2.5
        if horizontal:
            a, b = sorted((x0, x1))
            self.line((a, cy), (cx - L / 2, cy)); self.line((cx + L / 2, cy), (b, cy))
            self.rect(cx - L / 2, cy - B / 2, L, B)
            side = label_side or 'above'
            if side == 'above':
                self.text(cx, cy - 4.6, ref, 2.5, 'middle', True); self.text(cx, cy - 2, value, 2.5, 'middle')
            else:
                self.text(cx, cy + 4.6, ref, 2.5, 'middle', True); self.text(cx, cy + 7.2, value, 2.5, 'middle')
        else:
            a, b = sorted((y0, y1))
            self.line((cx, a), (cx, cy - L / 2)); self.line((cx, cy + L / 2), (cx, b))
            self.rect(cx - B / 2, cy - L / 2, B, L)
            if (label_side or 'right') == 'right':
                self.text(cx + 2.5, cy - 0.6, ref, 2.5, 'start', True); self.text(cx + 2.5, cy + 2.4, value, 2.5)
            else:
                self.text(cx - 2.5, cy - 0.6, ref, 2.5, 'end', True); self.text(cx - 2.5, cy + 2.4, value, 2.5, 'end')

    def capacitor(self, x, y0, y1, ref, value, polarized=False):
        """Condensatore 04-02-01, polarizzato 04-02-05 (segno + sull'armatura positiva, in alto)."""
        cy = (y0 + y1) / 2
        g = 0.75
        self.line((x, y0), (x, cy - g)); self.line((x, cy + g), (x, y1))
        self.line((x - 2.5, cy - g), (x + 2.5, cy - g), width=0.5)
        self.line((x - 2.5, cy + g), (x + 2.5, cy + g), width=0.5)
        if polarized:
            self.text(x - 3.4, cy - 1.6, '+', 2.5, 'middle', True)
        self.text(x + 3.5, cy - 0.6, ref, 2.5, 'start', True); self.text(x + 3.5, cy + 2.4, value, 2.5)

    def ground(self, x, y):
        """Terra / massa comune 02-15-01: tratto di 2,5 mm e tre linee decrescenti."""
        self.line((x, y), (x, y + 2.5))
        for i, half in enumerate((2.5, 1.6, 0.7)):
            self.line((x - half, y + 2.5 + i), (x + half, y + 2.5 + i))

    def supply(self, x, y, label):
        """Riferimento di alimentazione con nome del potenziale (IEC 61082-1)."""
        self.line((x, y), (x, y - 2.5)); self.line((x - 2, y - 2.5), (x + 2, y - 2.5))
        self.text(x, y - 3.6, label, 2.5, 'middle', True)

    def ground_side(self, x, y, direction=-1):
        """Simbolo di massa ruotato di 90°: direction -1 verso sinistra, +1 verso destra."""
        self.line((x, y), (x + direction * 2.5, y))
        for i, half in enumerate((2.5, 1.6, 0.7)):
            xx = x + direction * (2.5 + i)
            self.line((xx, y - half), (xx, y + half))

    def supply_side(self, x, y, label, direction=-1):
        """Riferimento di alimentazione ruotato di 90°, con nome del potenziale."""
        self.line((x, y), (x + direction * 2.5, y))
        bx = x + direction * 2.5
        self.line((bx, y - 2), (bx, y + 2))
        self.text(bx + direction * 1, y + 0.9, label, 2.5, 'end' if direction < 0 else 'start', True)

    def terminal(self, x, y, designation, signal=None, side='left'):
        """Morsetto 03-02-02 (cerchio vuoto) con sigla e nome del segnale."""
        self.circle(x, y, 0.9, fill='white')
        if side == 'left':
            self.text(x - 2, y - 1, designation, 2.5, 'end', True)
            if signal: self.text(x - 2, y + 2.4, signal, 2.5, 'end')
        else:
            self.text(x + 2, y - 1, designation, 2.5, 'start', True)
            if signal: self.text(x + 2, y + 2.4, signal, 2.5, 'start')

    def net_label(self, x, y, label, anchor='end'):
        dx = -1 if anchor == 'end' else 1
        self.text(x + dx, y - 0.9, label, 2.5, anchor, True)

    def not_connected(self, x, y):
        s = 1.2
        self.line((x - s, y - s), (x + s, y + s)); self.line((x - s, y + s), (x + s, y - s))

    def npn(self, x, y, ref, value):
        """Transistore NPN con involucro 05-05-01; (x, y) = terminale di base.
        Ritorna le coordinate dei terminali di collettore ed emettitore."""
        cx = x + 7.5
        self.circle(cx, y, 5)
        bar = x + 5
        self.line((x, y), (bar, y))
        self.line((bar, y - 2.8), (bar, y + 2.8), width=0.6)
        c = (x + 10, y - 7.5); e = (x + 10, y + 7.5)
        self.line((bar, y - 1.4), (x + 10, y - 4.2), (x + 10, y - 7.5))
        self.line((bar, y + 1.4), (x + 10, y + 4.2), (x + 10, y + 7.5))
        # Freccia sull'emettitore, uscente.
        ux, uy = (x + 10 - bar), (4.2 - 1.4)
        n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
        tip = (bar + ux * 4.2, y + 1.4 + uy * 4.2)
        px, py = -uy, ux
        a = (tip[0] - ux * 1.8 + px * 0.8, tip[1] - uy * 1.8 + py * 0.8)
        b = (tip[0] - ux * 1.8 - px * 0.8, tip[1] - uy * 1.8 - py * 0.8)
        self.raw(f'<path d="M{num(tip[0])} {num(tip[1])} L{num(a[0])} {num(a[1])} L{num(b[0])} {num(b[1])} Z" fill="{INK}"/>')
        self.text(cx + 6, y - 0.6, ref, 2.5, 'start', True); self.text(cx + 6, y + 2.4, value, 2.5)
        return c, e

    def amplifier(self, x, y, ref, pins, open_collector=True, power=False):
        """Amplificatore/comparatore 13-01 in forma rettangolare: 12,5 x 15 mm,
        simbolo distintivo ▷ in alto, ingressi a sinistra, uscita a destra.
        (x, y) = angolo superiore sinistro. pins: dict con chiavi 'in+', 'in-', 'out'.
        Ritorna i punti di collegamento (2,5 mm fuori dal contorno)."""
        w, h = 12.5, 15
        self.rect(x, y, w, h)
        self.text(x + w / 2, y + 4, '▷', 3.5, 'middle')
        self.text(x + w / 2, y - 1.5, ref, 2.5, 'middle', True)
        p_plus = (x - 2.5, y + 5); p_minus = (x - 2.5, y + 10); p_out = (x + w + 2.5, y + 7.5)
        self.line((x, y + 5), p_plus); self.line((x, y + 10), p_minus); self.line((x + w, y + 7.5), p_out)
        self.text(x + 1.2, y + 5.9, '+', 2.5); self.text(x + 1.2, y + 10.9, '−', 2.5)
        self.text(p_plus[0] + 1.2, y + 4.2, pins['in+'], 2, 'start')
        self.text(p_minus[0] + 1.2, y + 9.2, pins['in-'], 2, 'start')
        self.text(p_out[0] - 0.5, y + 6.7, pins['out'], 2, 'end')
        if open_collector:
            # Uscita a collettore aperto, tipo L (12-09-03): rombo con tratto inferiore.
            ox, oy, r = x + w - 3, y + 7.5, 1.2
            self.line((ox, oy - r), (ox + r, oy), (ox, oy + r), (ox - r, oy), (ox, oy - r), width=THIN)
            self.line((ox - r, oy + r + 0.5), (ox + r, oy + r + 0.5), width=THIN)
        return p_plus, p_minus, p_out

    def power_unit(self, x, y, ref, vcc_pin, gnd_pin):
        """Unità di alimentazione separata di un integrato (IEC 61082-1)."""
        w, h = 10, 12.5
        self.rect(x, y, w, h)
        self.text(x + w / 2, y + 5, 'VCC', 2, 'middle'); self.text(x + w / 2, y + h - 1.5, 'GND', 2, 'middle')
        self.text(x - 1, y + 4, ref, 2.5, 'end', True)
        top = (x + w / 2, y - 2.5 - 2.5); bottom = (x + w / 2, y + h + 2.5)
        self.line((x + w / 2, y), (x + w / 2, y - 5 + 2.5)); self.line((x + w / 2, y + h), bottom)
        self.text(x + w / 2 + 1, y - 0.6, vcc_pin, 2); self.text(x + w / 2 + 1, y + h + 2.2, gnd_pin, 2)
        return (x + w / 2, y - 2.5), bottom

    def push_button_no(self, x, y, ref, label=None):
        """Contatto di chiusura (NO) azionato a pulsante, 07-07-02, orizzontale.
        (x, y) = terminale sinistro; terminale destro a x + 10."""
        self.line((x, y), (x + 3, y)); self.line((x + 7, y), (x + 10, y))
        self.line((x + 3, y), (x + 7.6, y - 2.4))
        self.line((x + 5, y - 1.3), (x + 5, y - 5.5), width=THIN, dash='1 0.8')
        self.line((x + 3.5, y - 5.5), (x + 6.5, y - 5.5), (x + 6.5, y - 6.5))
        self.line((x + 3.5, y - 5.5), (x + 3.5, y - 6.5))
        self.text(x + 5, y - 8, ref, 2.5, 'middle', True)
        if label: self.text(x + 5, y + 4, label, 2.5, 'middle')
        return (x + 10, y)

    def enclosure(self, x, y, w, h, label, label_pos='top'):
        """Recinzione di un gruppo funzionale: tratto e punto sottile."""
        self.rect(x, y, w, h, width=THIN, dash=DASH_DOT)
        if label_pos == 'top':
            self.text(x + 2, y - 1.5, label, 2.5, 'start', True)
        else:
            self.text(x + 2, y + h + 3.5, label, 2.5, 'start', True)

    def element(self, x, y, w, h, ref, name, pins_left=(), pins_right=(), pitch=5, first=5,
                pins_top=(), pins_bottom=()):
        """Elemento (modulo) come rettangolo con morsetti 03-02-02 sul contorno.
        pins_*: sequenza di (designazione, nome). Ritorna dict nome -> punto di collegamento."""
        self.rect(x, y, w, h)
        self.text(x + w / 2, y - 4.5, ref, 3.5, 'middle', True)
        self.text(x + w / 2, y - 1.3, name, 2.5, 'middle')
        points = {}
        for i, (pin, label) in enumerate(pins_left):
            py = y + first + i * pitch
            if pin is None: continue
            self.line((x - 2.5, py), (x, py)); self.circle(x - 2.5, py, 0.6, fill='white')
            self.text(x + 1.2, py + 0.9, label, 2.5)
            self.text(x - 3.6, py - 1, pin, 2, 'end')
            points[label] = (x - 2.5, py)
        for i, (pin, label) in enumerate(pins_right):
            py = y + first + i * pitch
            if pin is None: continue
            self.line((x + w, py), (x + w + 2.5, py)); self.circle(x + w + 2.5, py, 0.6, fill='white')
            self.text(x + w - 1.2, py + 0.9, label, 2.5, 'end')
            self.text(x + w + 3.6, py - 1, pin, 2, 'start')
            points[label] = (x + w + 2.5, py)
        for i, (pin, label) in enumerate(pins_top):
            px = x + first + i * pitch
            self.line((px, y - 2.5), (px, y)); self.circle(px, y - 2.5, 0.6, fill='white')
            self.text(px, y + 3.4, label, 2.2, 'middle')
            points[label] = (px, y - 2.5)
        for i, (pin, label) in enumerate(pins_bottom):
            px = x + first + i * pitch
            self.line((px, y + h), (px, y + h + 2.5)); self.circle(px, y + h + 2.5, 0.6, fill='white')
            self.text(px, y + h - 1.6, label, 2.2, 'middle')
            points[label] = (px, y + h + 2.5)
        return points

    def block(self, x, y, w, h, title, lines=(), ref=None, dash=None):
        """Blocco funzionale per schemi a blocchi (IEC 61082-1)."""
        self.rect(x, y, w, h, dash=dash)
        yy = y + 5
        if ref:
            self.text(x + 2, yy, ref, 2.5, 'start', True); yy += 4
        self.text(x + 2, yy, title, 3.5, 'start', True); yy += 4.5
        for t in lines:
            self.text(x + 2, yy, t, 2.5); yy += 3.6

    def arrow(self, *points, both=False, dash=None, width=NORMAL):
        """Linea di flusso con freccia piena all'estremità (IEC 61082-1)."""
        self.line(*points, width=width, dash=dash)
        def head(p, q):
            dx, dy = p[0] - q[0], p[1] - q[1]; n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
            a = (p[0] - dx * 2.5 - dy * 0.9, p[1] - dy * 2.5 + dx * 0.9)
            b = (p[0] - dx * 2.5 + dy * 0.9, p[1] - dy * 2.5 - dx * 0.9)
            self.raw(f'<path d="M{num(p[0])} {num(p[1])} L{num(a[0])} {num(a[1])} L{num(b[0])} {num(b[1])} Z" fill="{INK}"/>')
        head(points[-1], points[-2])
        if both: head(points[0], points[1])

    # --- foglio ISO 5457 e cartiglio ISO 7200 ------------------------------
    def frame(self):
        x0, y0, x1, y1 = FRAME
        self.rect(x0, y0, x1 - x0, y1 - y0, width=THICK)
        cols, rows = 8, 6
        letters = 'ABCDEF'
        fw, fh = (x1 - x0) / cols, (y1 - y0) / rows
        for i in range(cols + 1):
            xx = x0 + i * fw
            if 0 < i < cols:
                self.line((xx, y0), (xx, y0 - 5), width=THIN); self.line((xx, y1), (xx, y1 + 5), width=THIN)
            if i < cols:
                self.text(xx + fw / 2, y0 - 1.6, str(i + 1), 3.5, 'middle')
                self.text(xx + fw / 2, y1 + 4.6, str(i + 1), 3.5, 'middle')
        for j in range(rows + 1):
            yy = y0 + j * fh
            if 0 < j < rows:
                self.line((x0, yy), (x0 - 5, yy), width=THIN); self.line((x1, yy), (x1 + 5, yy), width=THIN)
            if j < rows:
                self.text(x0 - 2.5, yy + fh / 2 + 1.2, letters[j], 3.5, 'middle')
                self.text(x1 + 5, yy + fh / 2 + 1.2, letters[j], 3.5, 'middle')
        # Segni di centraggio: dal bordo del foglio a 5 mm oltre la cornice.
        self.line((W / 2, 0), (W / 2, y0 + 5), width=THICK); self.line((W / 2, H), (W / 2, y1 - 5), width=THICK)
        self.line((0, H / 2), (x0 + 5, H / 2), width=THICK); self.line((W, H / 2), (x1 - 5, H / 2), width=THICK)

    def title_block(self, *, title, subtitle, doc_type, status, code, rev, date, sheet,
                    revisions=(), owner='Cruscotto C3+AI', created='C3+AI · agente Claude',
                    approved='— (non approvato)', language='it'):
        x1, y1 = FRAME[2], FRAME[3]
        w = 180.0
        x0 = x1 - w
        rh = 8.0
        y0 = y1 - 4 * rh
        self.raw(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(w)}" height="{num(4*rh)}" fill="white"/>')
        self.rect(x0, y0, w, 4 * rh, width=THICK)
        cells = [
            # x, y, w, h, etichetta, valore, altezza valore, grassetto
            (0, 0, 80, 1, 'Proprietario legale', owner, 3.5, True),
            (80, 0, 50, 1, 'Creato da', created, 2.5, False),
            (130, 0, 50, 1, 'Approvato da', approved, 2.5, False),
            (0, 1, 80, 1, 'Titolo supplementare', subtitle, 3.5, False),
            (80, 1, 50, 1, 'Tipo di documento', doc_type, 2.5, True),
            (130, 1, 50, 1, 'Stato del documento', status, 2.5, True),
            (0, 2, 80, 2, 'Titolo', title, 5, True),
            (80, 2, 50, 1, 'Numero di identificazione', code, 3.5, True),
            (130, 2, 15, 1, 'Rev.', rev, 3.5, True),
            (145, 2, 35, 1, 'Data di emissione', date, 3.5, False),
            (80, 3, 50, 1, 'Riferimento tecnico', 'D-024 · IEC 61082-1', 2.5, False),
            (130, 3, 15, 1, 'Lingua', language, 3.5, False),
            (145, 3, 35, 1, 'Foglio', sheet, 3.5, False),
        ]
        for cx, row, cw, span, label, value, vh, bold in cells:
            x, y, hh = x0 + cx, y0 + row * rh, span * rh
            self.rect(x, y, cw, hh, width=THIN)
            self.text(x + 1, y + 2.4, label, 1.8)
            lines = value if isinstance(value, (list, tuple)) else [value]
            base = y + hh - 1.6 - (len(lines) - 1) * (vh + 1)
            for k, t in enumerate(lines):
                self.text(x + 1.5, base + k * (vh + 1), t, vh, 'start', bold)
        if revisions:
            rows = list(revisions)[-4:]
            ty = y0 - (len(rows) + 1) * 5
            self.raw(f'<rect x="{num(x0)}" y="{num(ty)}" width="{num(w)}" height="{num((len(rows)+1)*5)}" fill="white"/>')
            self.rect(x0, ty, w, (len(rows) + 1) * 5, width=THIN)
            heads = [(0, 12, 'Rev.'), (12, 143, 'Descrizione della modifica'), (155, 25, 'Data')]
            for cx, cw, t in heads:
                self.rect(x0 + cx, ty, cw, 5, width=THIN); self.text(x0 + cx + 1, ty + 3.6, t, 2, 'start', True)
            for i, (r, desc, d) in enumerate(rows):
                yy = ty + (i + 1) * 5
                for cx, cw, t in zip((0, 12, 155), (12, 143, 25), (r, desc, d)):
                    self.rect(x0 + cx, yy, cw, 5, width=THIN); self.text(x0 + cx + 1, yy + 3.6, t, 2.2)
        return x0, y0

    def parts_list(self, x, y, rows, widths=(10, 18, 12, 60, 80), heads=('Pos.', 'Sigla', 'Q.tà', 'Descrizione', 'Note')):
        """Distinta componenti (ISO 7573) con intestazione in basso, posizioni crescenti verso l'alto."""
        rh = 5.0
        total = sum(widths)
        n = len(rows)
        yh = y + n * rh
        self.raw(f'<rect x="{num(x)}" y="{num(y)}" width="{num(total)}" height="{num((n+1)*rh)}" fill="white"/>')
        for i, row in enumerate(reversed(rows)):
            yy = y + i * rh
            cx = x
            for wdt, val in zip(widths, row):
                self.rect(cx, yy, wdt, rh, width=THIN); self.text(cx + 1, yy + 3.6, val, 2.2); cx += wdt
        cx = x
        for wdt, val in zip(widths, heads):
            self.rect(cx, yh, wdt, rh, width=NORMAL); self.text(cx + 1, yh + 3.6, val, 2.2, 'start', True); cx += wdt
        return total, (n + 1) * rh

    def notes(self, x, y, heading, lines, h=2.5, step=3.8):
        self.text(x, y, heading, 3.5, 'start', True)
        for i, t in enumerate(lines):
            self.text(x, y + 5 + i * step, t, h)

    def svg(self, description=''):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(W)}mm" height="{num(H)}mm" '
                f'viewBox="0 0 {num(W)} {num(H)}">'
                f'<title>{escape(self.title)}</title><desc>{escape(description)}</desc>'
                f'<rect width="{num(W)}" height="{num(H)}" fill="white"/>')
        return head + '\n'.join(self.items) + '</svg>\n'
