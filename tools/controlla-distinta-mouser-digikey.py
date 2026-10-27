"""Disponibilità e prezzi di una distinta su Mouser e DigiKey (API ufficiali), in euro, per l'Italia.

Uso:
  python tools/controlla-distinta-mouser-digikey.py [distinta.csv] [--copie=1]
Distinta predefinita: cruscotto/docs/distinta-scheda-madre-da-cercare.csv (stesse colonne della distinta per
Farnell: rif, qta, codice, ricerca = mpn o parole, note). Credenziali fuori dal repository, mai stampate:
  Mouser  (https://www.mouser.com/api-hub/, Search API): MOUSER_API_KEY o ~/.mouser_api_key
  DigiKey (https://developer.digikey.com/, Product Information V4): DIGIKEY_CLIENT_ID / DIGIKEY_CLIENT_SECRET
          o ~/.digikey_client_id e ~/.digikey_client_secret
Un fornitore senza credenziali viene saltato. Il risultato va in <distinta>-mouser-digikey.csv: per ogni voce e
fornitore codice, produttore e codice trovato, giacenza, prezzo unitario per la quantità richiesta. Fotografia
del giorno, non un ordine; una richiesta al secondo.
"""
from pathlib import Path
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


def secret(env, name):
    value = os.environ.get(env)
    path = Path.home() / name
    if not value and path.is_file():
        value = path.read_text(encoding='utf-8').strip()
    return value or None


def http(url, data=None, headers=None, form=False):
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers or {})
    if data is not None and not form:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def norm(code):
    return ''.join(ch for ch in (code or '').upper() if ch.isalnum())


def number(text):
    """'1.234 In magazzino' o '€ 1,23' -> numero."""
    m = re.search(r'[0-9][0-9.,]*', str(text or ''))
    if not m:
        return None
    s = m.group(0)
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    else:
        s = s.replace('.', '') if s.count('.') > 1 or re.fullmatch(r'\d{1,3}\.\d{3}', s) else s
    try:
        return float(s)
    except ValueError:
        return None


def break_price(breaks, qty):
    """breaks: [(quantità minima, prezzo)] -> prezzo unitario per qty."""
    best = None
    for q, p in sorted(breaks):
        if q <= qty or best is None:
            best = p
    return best


class Mouser:
    name = 'Mouser'

    def __init__(self):
        self.key = secret('MOUSER_API_KEY', '.mouser_api_key')

    def search(self, term, how):
        base = 'https://api.mouser.com/api/v1/search/'
        if how == 'mpn':
            data = http(base + 'partnumber?apiKey=' + self.key,
                        {'SearchByPartRequest': {'mouserPartNumber': term, 'partSearchOptions': 'Exact'}})
        else:
            data = http(base + 'keyword?apiKey=' + self.key,
                        {'SearchByKeywordRequest': {'keyword': term, 'records': 10, 'startingRecord': 0}})
        out = []
        for p in ((data.get('SearchResults') or {}).get('Parts') or []):
            breaks = [(int(b.get('Quantity', 1)), number(b.get('Price'))) for b in p.get('PriceBreaks') or []]
            out.append(dict(code=p.get('MouserPartNumber', ''), mpn=p.get('ManufacturerPartNumber', ''),
                            maker=p.get('Manufacturer', ''), stock=int(number(p.get('AvailabilityInStock')) or 0),
                            breaks=[b for b in breaks if b[1] is not None], status=p.get('LifecycleStatus') or ''))
        return out


class DigiKey:
    name = 'DigiKey'

    def __init__(self):
        self.cid = secret('DIGIKEY_CLIENT_ID', '.digikey_client_id')
        self.csec = secret('DIGIKEY_CLIENT_SECRET', '.digikey_client_secret')
        self.key = self.cid and self.csec
        self.token = None

    def headers(self):
        if not self.token:
            tok = http('https://api.digikey.com/v1/oauth2/token',
                       {'client_id': self.cid, 'client_secret': self.csec, 'grant_type': 'client_credentials'},
                       form=True)
            self.token = tok['access_token']
        return {'Authorization': 'Bearer ' + self.token, 'X-DIGIKEY-Client-Id': self.cid,
                'X-DIGIKEY-Locale-Site': 'IT', 'X-DIGIKEY-Locale-Language': 'it',
                'X-DIGIKEY-Locale-Currency': 'EUR', 'Accept': 'application/json'}

    def search(self, term, how):
        data = http('https://api.digikey.com/products/v4/search/keyword',
                    {'Keywords': term, 'Limit': 10, 'Offset': 0}, self.headers())
        products = list(data.get('ExactMatches') or []) + list(data.get('Products') or [])
        out = []
        for p in products:
            var = p.get('ProductVariations') or [{}]
            v = max(var, key=lambda x: x.get('QuantityAvailableforPackageType') or 0)
            breaks = [(int(b.get('BreakQuantity', 1)), b.get('UnitPrice')) for b in v.get('StandardPricing') or []]
            out.append(dict(code=v.get('DigiKeyProductNumber', ''), mpn=p.get('ManufacturerProductNumber', ''),
                            maker=(p.get('Manufacturer') or {}).get('Name', ''),
                            stock=int(p.get('QuantityAvailable') or 0), breaks=breaks,
                            status=(p.get('ProductStatus') or {}).get('Status', '')))
        return out


def best(found, mpn):
    def key(p):
        return (mpn is not None and norm(p['mpn']).startswith(norm(mpn)), p['stock'])
    return max(found, key=key)


def main():
    src = ROOT / 'cruscotto/docs/distinta-scheda-madre-da-cercare.csv'
    copies = 1
    for a in sys.argv[1:]:
        if a.startswith('--copie='):
            copies = int(a.split('=', 1)[1])
        else:
            src = Path(a)
    shops = [s for s in (Mouser(), DigiKey()) if s.key]
    if not shops:
        raise SystemExit('Nessuna credenziale Mouser o DigiKey trovata (vedi la descrizione dello script).')
    rows = list(csv.DictReader(src.open(encoding='utf-8')))
    out = src.with_name(src.stem + '-mouser-digikey.csv')
    with out.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rif', 'qta', 'codice', 'fornitore', 'codice fornitore', 'produttore e codice trovato',
                    'giacenza', 'prezzo unitario €', 'totale €', 'stato', 'note'])
        for row in rows:
            qty = int(row['qta']) * copies
            line = []
            for shop in shops:
                try:
                    found = shop.search(row['codice'], row['ricerca'])
                    err = ''
                except Exception as e:  # rete, limite o credenziali: la riga resta da ricontrollare
                    found, err = [], f'errore: {type(e).__name__} {getattr(e, "code", "")}'.strip()
                if not found:
                    w.writerow([row['rif'], qty, row['codice'], shop.name, '', '', '', '', '', err or 'non trovato',
                                row['note']])
                    line.append(f'{shop.name}: {err or "non trovato"}')
                else:
                    p = best(found, row['codice'] if row['ricerca'] == 'mpn' else None)
                    price = break_price(p['breaks'], qty) if p['breaks'] else None
                    exact = row['ricerca'] == 'mpn' and norm(p['mpn']).startswith(norm(row['codice']))
                    w.writerow([row['rif'], qty, row['codice'], shop.name, p['code'], f"{p['maker']} {p['mpn']}",
                                p['stock'], price, round(price * qty, 2) if price is not None else '',
                                p['status'] + ('' if exact else ' (codice diverso: da controllare)'), row['note']])
                    line.append(f"{shop.name}: {p['mpn']} giacenza {p['stock']}")
                time.sleep(1.1)
            print(f"{row['rif']:<12} {row['codice']:<26} " + ' | '.join(line), flush=True)
    print(f'\n{out}  ({datetime.date.today():%d/%m/%Y}, fornitori {", ".join(s.name for s in shops)})')


if __name__ == '__main__':
    main()
