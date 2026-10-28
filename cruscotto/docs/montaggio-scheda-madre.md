# Montaggio a mano della scheda madre (D-046)

Revisione A — 28/10/2026. Procedura proposta, non ancora eseguita: nessuna scheda è stata montata o collaudata.

## Documenti da tenere sul banco

- `cruscotto/pcb/scheda-madre/montaggio/montaggio-lato-F.pdf` e `montaggio-lato-B.pdf`: contorni, sigle,
  numeri dei piedini e simbolo dei diodi di ogni componente (vettoriali: si ingrandiscono senza perdere dettaglio;
  il lato B è in vista speculare, come si vede girando la scheda).
- `cruscotto/pcb/scheda-madre/montaggio/elenco-montaggio.csv`: per ogni componente lato, tipo (SMD o a foro
  passante), sigla, valore, impronta, posizione in mm dal bordo sinistro e dal basso, segno di polarità.
- `cruscotto/docs/distinta-scheda-madre.md` per i codici esatti.

## Segni sulla serigrafia

| Componente | Segno | Come montarlo |
| --- | --- | --- |
| Diodi (D1-D4, D8, D9, D11-D13) e LED D7 | staffa a «[» attorno a una piazzola | la riga colorata del diodo (catodo) va dal lato della staffa |
| Elettrolitici C3, C29 | «+» | il lato con la striscia (negativo) va dalla parte opposta al «+» |
| Circuiti integrati, transistor, D5, D6, D10 (SOT-23) | pallino o triangolo | il segno sul chip (tacca, punto, smusso) va verso il pallino |
| Connettori, modulo ESP32, STEVAL (J6) | pallino o piazzola quadrata | piedino 1 dal lato segnato |
| Fili saldati (J4, J5, J10-J12) | nome di ogni filo accanto alla piazzola | vedi «Fili» sotto |

Sei componenti in zone fitte non hanno la sigla stampata (U1, R13, R17, R20, R37, R42): sono nel disegno di
montaggio e nell'elenco.

## Ordine di montaggio

1. **U2 e U3** (convertitori con piazzola termica, D-048): stagno sulle piazzole, chip in posizione, piedini;
   poi la piazzola centrale dal retro attraverso il foro metallizzato, finché lo stagno affiora sul lato F.
2. **Passo fine sul lato F**: USB-C J3 e CH340C U6 (trascinamento con flussante), modulo ESP32 U4 (piazzola di
   massa sotto il modulo dal retro, come U2/U3).
3. **Altri integrati e transistor** del lato F, poi i passivi del lato F, dal più piccolo al più grande.
4. **Componenti SMD del lato B** con lo stesso ordine.
5. **Foro passante**, per ultimi perché sporgono su entrambe le facce: pulsanti S1, S2, SW3, SW4, connettore J1,
   relè K1 e K2, C3 **coricato** sulla scheda (alto 17,5 mm in piedi), STEVAL J6.
6. **Modulo VAN** (D-060), dopo U4 perché ne copre i fori termici: togliere il connettore ad angolo, saldare
   4 pin diritti con il distanziale di plastica, appoggiare il modulo sul retro e saldare i pin in J8 (3V3, GND,
   RX, TX). CANH e CANL: due fili corti dal morsetto a vite alle piazzole J9. Resistenza 121 tolta e prove 1-4
   D-022 prima del montaggio, come per il primo modulo.
7. **Fili** (tabella sotto), con guaina termorestringente sui capi.

## Fili saldati (D-059)

| Piazzole | Filo | Note |
| --- | --- | --- |
| J4 | GND nero, 12V rosso, RPM blu, PWM giallo | ventola Delta AFB0412VA-00 (D-052) |
| J5 | NTC, GND | NTC Vishay NTCLE100E3104JB0 sul display, senza polarità |
| J10 | 5V, TXD, RXD, GND | verso P1 della S3; TXD e RXD per ora non collegati |
| J11 | IO19, IO11, IO12, IO13 | verso P2 della S3 |
| J12 | SPK, SPK | verso Speak (P6) della S3, senza polarità |
| J9 | CANH, CANL | dal morsetto a vite del modulo VAN (D-060) |

## Prima di alimentare

1. Controllo visivo con la lente: ponti di stagno sui piedini fini (J3, U6, U4), polarità di diodi ed elettrolitici.
2. Al tester, a scheda spenta: nessun cortocircuito tra +12V_F, +5V, +3V3_AON, +3V3_SW e massa (valori da
   annotare nel registro di collaudo).
3. Prima accensione dall'alimentatore da banco a 12-13 V con limite di corrente basso (circa 200 mA), senza S3
   e senza auto: misurare 5 V e 3,3 V. Le prove successive seguono la procedura del registro di collaudo.
