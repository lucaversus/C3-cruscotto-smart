"""Disponibilità e prezzi della distinta della scheda madre su Farnell (API element14 Product Search).

Uso:
  python tools/controlla-distinta-farnell.py [distinta.csv] [--negozio=it.farnell.com] [--copie=1]
La chiave API si legge dalla variabile d'ambiente FARNELL_API_KEY o, in mancanza, dal file
~/.farnell_api_key fuori dal repository (registrazione gratuita su https://partner.element14.com);
lo script non la stampa e non la scrive altrove. Distinta predefinita:
cruscotto/docs/distinta-scheda-madre-codici.csv (colonne rif, qta, codice, ricerca, note; ricerca = mpn per
il codice del produttore, parole per una ricerca libera). Il risultato va in un CSV accanto alla distinta
con codice Farnell, giacenza e prezzo unitario per la quantità richiesta; è una fotografia del giorno, non
un ordine. Una sola richiesta al secondo, entro i limiti dell'API.
"""
from pathlib import Path
import csv
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.element14.com/catalog/products'


def args():
    src = ROOT / 'cruscotto/docs/distinta-scheda-madre-codici.csv'
    store, copies = 'it.farnell.com', 1
    for a in sys.argv[1:]:
        if a.startswith('--negozio='):
            store = a.split('=', 1)[1]
        elif a.startswith('--copie='):
            copies = int(a.split('=', 1)[1])
        else:
            src = Path(a)
    return src, store, copies


def search(key, store, term, how):
    query = {
        'term': ('manuPartNum:' if how == 'mpn' else 'any:') + term,
        'storeInfo.id': store,
        'resultsSettings.offset': 0,
        'resultsSettings.numberOfResults': 10,
        'resultsSettings.responseGroup': 'large',
        'callInfo.responseDataFormat': 'json',
        'callInfo.apiKey': key,
    }
    with urllib.request.urlopen(API + '?' + urllib.parse.urlencode(query), timeout=30) as r:
        data = json.load(r)
    ret = data.get('manufacturerPartNumberSearchReturn') or data.get('keywordSearchReturn') or {}
    return ret.get('products') or []


def norm(code):
    return ''.join(ch for ch in (code or '').upper() if ch.isalnum())


def best(products, mpn):
    """Tra i risultati: prima lo stesso codice del produttore, poi la giacenza più alta."""
    def key(p):
        same = mpn is not None and norm(p.get('translatedManufacturerPartNumber')).startswith(norm(mpn))
        return (same, (p.get('stock') or {}).get('level') or 0)
    return max(products, key=key)


def unit_price(prices, qty):
    best = None
    for p in prices or []:
        if p.get('from', 1) <= qty:
            best = p.get('cost')
    return best if best is not None else (prices[0].get('cost') if prices else None)


def main():
    src, store, copies = args()
    key = os.environ.get('FARNELL_API_KEY')
    keyfile = Path.home() / '.farnell_api_key'
    if not key and keyfile.is_file():
        key = keyfile.read_text(encoding='utf-8').strip()
    if not key:
        raise SystemExit(f'Manca la chiave API element14: variabile FARNELL_API_KEY o file {keyfile}.')
    rows = list(csv.DictReader(src.open(encoding='utf-8')))
    out = src.with_name(src.stem + '-farnell.csv')
    total, missing = 0.0, []
    with out.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rif', 'qta', 'codice', 'codice Farnell', 'produttore e codice trovato', 'giacenza',
                    'prezzo unitario €', 'totale €', 'stato', 'note'])
        for row in rows:
            qty = int(row['qta']) * copies
            try:
                found = search(key, store, row['codice'], row['ricerca'])
            except Exception as e:  # rete o limite dell'API: la riga resta da ricontrollare
                found, err = [], f'errore: {type(e).__name__}'
            else:
                err = ''
            if not found:
                missing.append(row['rif'])
                w.writerow([row['rif'], qty, row['codice'], '', '', '', '', '', err or 'non trovato', row['note']])
            if found:
                p = best(found, row['codice'] if row['ricerca'] == 'mpn' else None)
                price = unit_price(p.get('prices'), qty)
                stock = (p.get('stock') or {}).get('level')
                cost = price * qty if price is not None else None
                total += cost or 0.0
                exact = row['ricerca'] == 'mpn' and norm(p.get('translatedManufacturerPartNumber')) == norm(row['codice'])
                w.writerow([row['rif'], qty, row['codice'], p.get('sku', ''),
                            f"{p.get('brandName', '')} {p.get('translatedManufacturerPartNumber', '')}".strip(),
                            stock, price, round(cost, 2) if cost is not None else '',
                            p.get('productStatus', '') + ('' if exact else ' (codice diverso: da controllare)'),
                            row['note']])
            print(f"{row['rif']:<14} {row['codice']:<28} {'trovato' if found else 'NON TROVATO'}", flush=True)
            time.sleep(1.1)
    print(f'\n{out}  ({datetime.date.today():%d/%m/%Y}, negozio {store}, copie {copies})')
    print(f'totale indicativo (IVA esclusa, voci trovate): {total:.2f} €')
    if missing:
        print('non trovati:', ', '.join(missing))


if __name__ == '__main__':
    main()
