---
name: registro-collaudo
description: Registra nel progetto Cruscotto C3+AI una misura o una prova a banco riferita dall'utente (tensioni, resistenze, continuità, esiti seriali, prove P-xxx), aggiornando registro moduli e inventario nello stesso passaggio. Usare quando l'utente comunica il risultato di una verifica hardware.
---

# Registrare una misura o una prova

Fonti: `data-logger/docs/procedura-progetto.md` (aggiornamento e collaudi),
`data-logger/docs/verifiche-moduli.md` (formato delle voci esistenti).

## Prima di scrivere

- Identificare l'ID hardware (`HW-...`) in `hardware.json` e la verifica aperta
  a cui la misura risponde. Se la misura non corrisponde a nessuna verifica aperta,
  chiedere a cosa si riferisce invece di inventare un collegamento.
- Annotare esattamente cosa ha detto l'utente: valore, unità, strumento, punti
  di misura, condizioni (alimentato o no, componente scollegato, scala).
  Se manca un dato che cambia il significato (per esempio il punto di misura),
  chiedere solo quello.

## Voce nel registro moduli

In `verifiche-moduli.md`, nuova sezione con codice progressivo del modulo
(es. `SD-M002`, `VAN-M001`, `P-001 esito 1`) e data:

- **Misura riferita:** valori e condizioni come dichiarati dall'utente.
- **Interpretazione:** cosa dimostra e, separatamente, cosa NON dimostra.
- **Esito:** superata / non superata / non conclusiva, rispetto al criterio scritto
  nella procedura relativa (es. prerequisiti VAN in `protocolli-veicolo.md`,
  P-001/P-002 in `alimentazione-spegnimento.md`).
- **Prossimo passo:** la verifica successiva, una sola.

## Inventario

- Aggiungere la riga all'array `verified` dell'elemento solo se l'esito è superato,
  con codice della voce e data; altrimenti aggiornare la voce in `open_checks`.
- Non promuovere lo `status` (presente → verificato) senza tutte le verifiche richieste.
- `python tools/project_preflight.py --render-inventory`, poi `python tools/dev.py check`.

## Regole

- Mai trasformare una misura parziale in collaudo completo, né presumere pin o
  protocolli del veicolo da una misura a banco (D-008, D-020).
- Più misure sullo stesso modulo: registrare subito ciascuna in locale e pubblicare
  a fine sequenza (skill `chiusura-blocco`), non a ogni valore.
