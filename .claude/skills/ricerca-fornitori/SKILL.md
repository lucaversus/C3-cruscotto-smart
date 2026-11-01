---
name: ricerca-fornitori
description: Controlla codici, giacenze e prezzi dei componenti sui fornitori (Farnell, Mouser, DigiKey, TME) con le API ufficiali e gli script tools/controlla-distinta-*.py, preparando la distinta CSV nel formato giusto. Usare prima di proporre o confermare un acquisto o quando l'utente chiede disponibilità e prezzi.
---

# Cercare componenti sui fornitori

Script: `tools/controlla-distinta-farnell.py`, `tools/controlla-distinta-mouser-digikey.py`,
`tools/controlla-distinta-tme.py`. Esempi validi: `cruscotto/docs/distinta-scheda-madre-codici.csv`.

## Prima di cercare

- Controllare il magazzino (`C:\Progetti\DB-componenti-elettronici\giacenze.csv`, se presente)
  e `data-logger/docs/hardware.json`: un pezzo già posseduto o ordinato non si ricompra.
- Fornitori in quest'ordine: Farnell, Future, RS Pro, Mouser, DigiKey, TME; LCSC solo per
  pezzi cinesi, a mano (niente API). Mai scraping dei siti: solo API ufficiali.
- Quantità: almeno 2 esemplari per componente (preferenza dell'utente).

## Formato della distinta CSV (obbligatorio)

Intestazione esatta, UTF-8: `rif,qta,codice,ricerca,note`

| Colonna | Contenuto | Esempio |
|---|---|---|
| `rif` | riferimenti nello schema | `D1 D2` |
| `qta` | numero intero per una copia | `4` |
| `codice` | **codice del produttore** (o parole da cercare); **mai vuoto** | `P6KE33A` |
| `ricerca` | solo `mpn` (codice esatto) oppure `parole` (ricerca libera) | `mpn` |
| `note` | testo libero | `TVS` |

Errore già successo (31/10/2026): codice scritto nella colonna `ricerca` e `codice` vuoto. Tutte
le righe davano «non trovato» (Mouser) ed «errore 400» (DigiKey). Dal 01/11/2026 gli script si
fermano con l'elenco delle righe sbagliate: correggere il file, non aggirare il controllo.

Il file temporaneo va nella cartella scratchpad, non nel repository, salvo una distinta da conservare.

## Esecuzione

```bash
PYTHONIOENCODING=utf-8 python tools/controlla-distinta-mouser-digikey.py <distinta.csv> [--copie=N]
```

Stesso uso per gli altri due script. Il risultato è `<distinta>-<fornitore>.csv` accanto al file.

## Lettura del risultato

- «non trovato» o «errore» su **tutte** le righe = problema del file o delle credenziali, non dei
  fornitori: prima ricontrollare il formato, poi provare la singola API.
- «codice diverso: da controllare» = il fornitore ha restituito un altro prodotto (per esempio un
  portapila al posto della pila): non darlo per confermato.
- Un codice esatto non trovato può esistere con un suffisso (MF-R005 → MF-R005-2): riprovare con
  `parole` e leggere il produttore.
- Giacenza e prezzo sono una fotografia del giorno, non un ordine. TME: catalogo esterno con
  giacenza 0 e minimi a bobina intera, da scartare.
- Dati elettrici: verificarli sul datasheet del produttore; la presenza a catalogo non li conferma.

## Credenziali

Solo in file fuori dal repository (`~/.farnell_api_key`, `~/.mouser_api_key`,
`~/.digikey_client_id`, `~/.digikey_client_secret`, `~/.tme_api_token`, `~/.tme_api_secret`)
o variabili d'ambiente. Mai leggerle a schermo, stamparle o metterle in un commit.
