"""Disponibilità e prezzi di una distinta su TME (API ufficiale v2), in euro, per l'Italia.

Uso:
  python tools/controlla-distinta-tme.py [distinta.csv] [--copie=1]
Distinta predefinita: cruscotto/docs/distinta-scheda-madre-da-cercare.csv (stesse colonne delle distinte per
Farnell, Mouser e DigiKey: rif, qta, codice, ricerca = mpn o parole, note). Credenziali fuori dal repository,
mai stampate (https://developers.tme.eu/, applicazione API v2):
  TME_TOKEN e TME_APP_SECRET, oppure i file ~/.tme_api_token e ~/.tme_api_secret
  (valore da solo, oppure righe TME_TOKEN=... e TME_APP_SECRET=...).
Accesso OAuth 2.0 client_credentials (Basic token:secret su /auth/token, token Bearer valido 5 minuti), poi
/products/search per trovare il simbolo TME dal codice del produttore e /products/data per prezzi e giacenza.
Il risultato va in <distinta>-tme.csv. Fotografia del giorno, non un ordine.
"""
from pathlib import Path
import base64
import csv
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.tme.eu'


def secret(env, name, key):
    value = os.environ.get(env)
    path = Path.home() / name
    if not value and path.is_file():
        lines = [ln.strip() for ln in path.read_text(encoding='utf-8', errors='replace').splitlines() if ln.strip()]
        for ln in lines:
            m = re.match(key + r'\s*=\s*(\S+)', ln)
            if m:
                return m.group(1)
        value = lines[0] if lines and ' ' not in lines[0] and '=' not in lines[0] else None
    return value or None


def norm(code):
    return ''.join(ch for ch in (code or '').upper() if ch.isalnum())


class TME:
    name = 'TME'

    def __init__(self):
        self.tok = secret('TME_TOKEN', '.tme_api_token', 'TME_TOKEN')
        self.sec = secret('TME_APP_SECRET', '.tme_api_secret', 'TME_APP_SECRET')
        self.key = self.tok and self.sec
        self.access, self.scade = None, 0

    def headers(self):
        if not self.access or time.time() > self.scade:
            req = urllib.request.Request(
                API + '/auth/token', data=b'grant_type=client_credentials',
                headers={'Content-Type': 'application/x-www-form-urlencoded',
                         'Authorization': 'Basic ' + base64.b64encode(f'{self.tok}:{self.sec}'.encode()).decode()})
            with urllib.request.urlopen(req, timeout=30) as r:
                a = json.load(r)
            self.access, self.scade = a['access_token'], time.time() + float(a.get('expires_in', 300)) - 30
        return {'Authorization': 'Bearer ' + self.access, 'Accept': 'application/json'}

    def get(self, path, params):
        url = API + path + '?' + urllib.parse.urlencode(params, doseq=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers=self.headers()), timeout=30) as r:
            return json.load(r)

    def search(self, term, how):
        """Prodotti TME per un codice del produttore o parole, il più vicino per primo."""
        phrase = term[:40]
        data = self.get('/products/search', {'phrase': phrase, 'scope[]': ['products'], 'country': 'IT',
                                             'language': 'IT', 'limit': 20})
        elems = ((data.get('data') or {}).get('products') or {}).get('elements') or []
        if how == 'mpn':
            def rank(p):
                syms = [norm(s) for s in p.get('manufacturer_symbols') or []]
                return (norm(term) in syms, any(s.startswith(norm(term)) or norm(term).startswith(s) for s in syms))
            elems = sorted(elems, key=rank, reverse=True)
        return [dict(code=p['symbol'], mpn=(p.get('manufacturer_symbols') or [''])[0],
                     maker=(p.get('manufacturer') or {}).get('name', ''), desc=p.get('description', ''),
                     minimo=p.get('minimal_amount') or 1, multipli=p.get('multiples') or 1,
                     exact=norm(term) in [norm(s) for s in p.get('manufacturer_symbols') or []]) for p in elems]

    def prices(self, symbols):
        """{simbolo: (giacenza, [(quantità, prezzo)])}, al massimo 50 simboli per chiamata."""
        out = {}
        for i in range(0, len(symbols), 50):
            data = self.get('/products/data', {'scope[]': ['prices', 'stock'], 'symbols[]': symbols[i:i + 50],
                                               'country': 'IT', 'currency': 'EUR'})
            for e in (data.get('data') or {}).get('elements') or []:
                out[e['symbol']] = (int(e.get('stock_quantity') or 0),
                                    [(int(p['amount']), float(p['price'])) for p in (e.get('prices') or {}).get('elements') or []])
        return out


def break_price(breaks, qty):
    best = None
    for q, p in sorted(breaks):
        if q <= qty or best is None:
            best = p
    return best


def main():
    src = ROOT / 'cruscotto/docs/distinta-scheda-madre-da-cercare.csv'
    copies = 1
    for a in sys.argv[1:]:
        if a.startswith('--copie='):
            copies = int(a.split('=', 1)[1])
        else:
            src = Path(a)
    shop = TME()
    if not shop.key:
        raise SystemExit('Credenziali TME non trovate (vedi la descrizione dello script).')
    rows = list(csv.DictReader(src.open(encoding='utf-8-sig')))
    found = {}
    for row in rows:
        try:
            res = shop.search(row['codice'], row['ricerca'])
            found[row['codice']] = (res[0] if res else None, '')
        except Exception as e:  # rete o limite: la riga resta da ricontrollare
            found[row['codice']] = (None, f'errore: {type(e).__name__} {getattr(e, "code", "")}'.strip())
        time.sleep(0.3)
    price = shop.prices(sorted({p['code'] for p, _ in found.values() if p}))
    out = src.with_name(src.stem + '-tme.csv')
    with out.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rif', 'qta', 'codice', 'fornitore', 'codice fornitore', 'produttore e codice trovato',
                    'giacenza', 'qta da ordinare', 'prezzo unitario €', 'totale €', 'stato', 'note'])
        for row in rows:
            qty = int(row['qta']) * copies
            p, err = found[row['codice']]
            if not p:
                w.writerow([row['rif'], qty, row['codice'], 'TME', '', '', '', '', '', '', err or 'non trovato',
                            row['note']])
                print(f"{row['rif']:<12} {row['codice']:<26} TME: {err or 'non trovato'}")
                continue
            stock, breaks = price.get(p['code'], (0, []))
            q = max(qty, p['minimo'])
            q = -(-q // p['multipli']) * p['multipli']
            unit = break_price(breaks, q) if breaks else None
            stato = 'ok' if p['exact'] else 'codice diverso: da controllare'
            w.writerow([row['rif'], qty, row['codice'], 'TME', p['code'], f"{p['maker']} {p['mpn']}", stock, q,
                        unit, round(unit * q, 2) if unit is not None else '', stato, row['note']])
            print(f"{row['rif']:<12} {row['codice']:<26} TME: {p['code']} giacenza {stock} "
                  f"{'' if p['exact'] else '(codice diverso)'}")
    print(f'\n{out}  ({datetime.date.today():%d/%m/%Y})')


if __name__ == '__main__':
    main()
