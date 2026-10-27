"""Confronto prezzi della distinta tra Farnell, Mouser e DigiKey e scelta della combinazione più economica.

Uso:
  python tools/confronta-fornitori.py [distinta.csv] [--copie=2]
Distinta predefinita: cruscotto/docs/distinta-scheda-madre-acquisto.csv (codici esatti, colonne come le altre
distinte). Credenziali come in controlla-distinta-farnell.py e controlla-distinta-mouser-digikey.py, mai
stampate. Per ogni voce e fornitore: quantità da ordinare (minimo d'ordine e multipli compresi), prezzo e costo;
poi, per ogni combinazione di fornitori, ogni voce va al più economico con giacenza sufficiente e si somma la
spedizione. Le regole di spedizione in SPEDIZIONE sono indicative e vanno verificate al momento dell'ordine.
Risultato in <distinta>-confronto.csv; fotografia del giorno, non un ordine.
"""
from itertools import combinations
from pathlib import Path
import csv
import datetime
import importlib.util
import math
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
# Spedizione in Italia (€ IVA esclusa): (soglia per la gratuità, costo sotto soglia). Valori indicativi da
# verificare sul sito di ogni fornitore prima dell'ordine.
SPEDIZIONE = {'Farnell': (0.0, 0.0), 'Mouser': (50.0, 20.0), 'DigiKey': (50.0, 18.0)}


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'tools' / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


far = load('controlla-distinta-farnell')
md = load('controlla-distinta-mouser-digikey')


class Farnell:
    name = 'Farnell'

    def __init__(self):
        self.key = md.secret('FARNELL_API_KEY', '.farnell_api_key')

    def offers(self, mpn):
        out = []
        for p in far.search(self.key, 'it.farnell.com', mpn, 'mpn'):
            breaks = [(int(b.get('from', 1)), b.get('cost')) for b in p.get('prices') or [] if b.get('cost') is not None]
            out.append(dict(code=p.get('sku', ''), mpn=p.get('translatedManufacturerPartNumber', ''),
                            stock=(p.get('stock') or {}).get('level') or 0, breaks=breaks,
                            min=int(p.get('translatedMinimumOrderQuality') or 1), mult=1))
        return out


class Mouser(md.Mouser):
    def offers(self, mpn):
        data = md.http('https://api.mouser.com/api/v1/search/partnumber?apiKey=' + self.key,
                       {'SearchByPartRequest': {'mouserPartNumber': mpn, 'partSearchOptions': 'Exact'}})
        out = []
        for p in ((data.get('SearchResults') or {}).get('Parts') or []):
            breaks = [(int(b.get('Quantity', 1)), md.number(b.get('Price'))) for b in p.get('PriceBreaks') or []]
            out.append(dict(code=p.get('MouserPartNumber', ''), mpn=p.get('ManufacturerPartNumber', ''),
                            stock=int(md.number(p.get('AvailabilityInStock')) or 0),
                            breaks=[b for b in breaks if b[1] is not None],
                            min=int(md.number(p.get('Min')) or 1), mult=int(md.number(p.get('Mult')) or 1)))
        return out


class DigiKey(md.DigiKey):
    def offers(self, mpn):
        data = md.http('https://api.digikey.com/products/v4/search/keyword',
                       {'Keywords': mpn, 'Limit': 10, 'Offset': 0}, self.headers())
        out = []
        for p in list(data.get('ExactMatches') or []) + list(data.get('Products') or []):
            for v in p.get('ProductVariations') or []:
                breaks = [(int(b.get('BreakQuantity', 1)), b.get('UnitPrice')) for b in v.get('StandardPricing') or []]
                out.append(dict(code=v.get('DigiKeyProductNumber', ''), mpn=p.get('ManufacturerProductNumber', ''),
                                stock=int(v.get('QuantityAvailableforPackageType') or 0), breaks=breaks,
                                min=int(v.get('MinimumOrderQuantity') or 1), mult=1))
        return out


def cost(offer, qty):
    """Quantità da ordinare e costo totale per avere almeno qty pezzi."""
    n = max(qty, offer['min'])
    n = int(math.ceil(n / offer['mult']) * offer['mult'])
    price = md.break_price(offer['breaks'], n)
    return n, price, (price * n if price is not None else None)


def cheapest(offers, mpn, qty):
    """Offerta più economica con lo stesso codice del produttore e giacenza sufficiente."""
    best = None
    for o in offers:
        if not md.norm(o['mpn']).startswith(md.norm(mpn)) or not o['breaks']:
            continue
        n, price, total = cost(o, qty)
        if total is None or o['stock'] < n:
            continue
        if best is None or total < best[3]:
            best = (o, n, price, total)
    return best


def shipping(name, subtotal):
    threshold, fee = SPEDIZIONE[name]
    return 0.0 if subtotal >= threshold else fee


def main():
    src = ROOT / 'cruscotto/docs/distinta-scheda-madre-acquisto.csv'
    copies = 2
    for a in sys.argv[1:]:
        if a.startswith('--copie='):
            copies = int(a.split('=', 1)[1])
        else:
            src = Path(a)
    shops = [s for s in (Farnell(), Mouser(), DigiKey()) if s.key]
    rows = list(csv.DictReader(src.open(encoding='utf-8')))
    table = []  # (riga, qty, {fornitore: (offerta, n, prezzo, totale)})
    for row in rows:
        qty = int(row['qta']) * copies
        found = {}
        for shop in shops:
            try:
                best = cheapest(shop.offers(row['codice']), row['codice'], qty)
            except Exception as e:  # rete o limite: la voce risulta non disponibile da quel fornitore
                print(f"  {shop.name} {row['codice']}: errore {type(e).__name__}", flush=True)
                best = None
            if best:
                found[shop.name] = best
            time.sleep(1.1)
        table.append((row, qty, found))
        line = ', '.join(f'{k} {v[3]:.2f} €' for k, v in sorted(found.items(), key=lambda kv: kv[1][3]))
        print(f"{row['rif'][:14]:<14} {row['codice'][:24]:<24} {line or 'non disponibile'}", flush=True)

    names = [s.name for s in shops]
    plans = []
    for k in range(1, len(names) + 1):
        for subset in combinations(names, k):
            assign, missing = {}, []
            for i, (row, qty, found) in enumerate(table):
                options = [(found[n][3], n) for n in subset if n in found]
                if options:
                    assign[i] = min(options)[1]
                elif found:
                    missing.append(row['rif'])
            if missing:
                continue
            sub = {n: sum(table[i][2][n][3] for i, s in assign.items() if s == n) for n in subset}
            ship = {n: shipping(n, sub[n]) for n in subset}
            plans.append((sum(sub.values()) + sum(ship.values()), subset, assign, sub, ship))
    plans.sort(key=lambda p: p[0])
    total, subset, assign, sub, ship = plans[0]

    out = src.with_name(src.stem + '-confronto.csv')
    with out.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rif', 'qta', 'codice'] + [f'{n} €' for n in names] + ['scelto', 'codice fornitore',
                                                                           'quantità da ordinare', 'costo €', 'note'])
        for i, (row, qty, found) in enumerate(table):
            pick = assign.get(i)
            o = found[pick] if pick else None
            w.writerow([row['rif'], qty, row['codice']] +
                       [round(found[n][3], 2) if n in found else '' for n in names] +
                       [pick or 'non disponibile', o[0]['code'] if o else '', o[1] if o else '',
                        round(o[3], 2) if o else '', row['note']])
    print(f'\n{out}  ({datetime.date.today():%d/%m/%Y}, copie {copies}, prezzi IVA esclusa)')
    print('combinazioni (merce + spedizione indicativa):')
    for p in plans[:5]:
        print(f"  {' + '.join(p[1]):<26} {p[0]:8.2f} €  " +
              ', '.join(f'{n} {p[3][n]:.2f} + sped. {p[4][n]:.0f}' for n in p[1]))
    missing = [row['rif'] for row, qty, found in table if not found]
    if missing:
        print('non disponibili presso nessuno:', ', '.join(missing))


if __name__ == '__main__':
    main()
