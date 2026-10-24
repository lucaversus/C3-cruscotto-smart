# Scheda madre — circuito stampato (KiCad 10)

Progetto KiCad della scheda madre del cruscotto (D-029, D-044, D-045, D-046). Stato:
circuito stampato con la **sola meccanica**; schema elettrico iniziato con il foglio
**alimentazione** (C3AI-CR-EL-001 rev C) e **front-end** (C3AI-CR-EL-002 rev A, `front-end.kicad_sch`),
proposte non verificate.

- `scheda-madre.kicad_pcb`: generato da `tools/genera-pcb-scheda-madre.py` con il Python di
  KiCad. Contiene il bordo letto dal DXF dell'utente (`cruscotto/meccanica/scheda-madre-contorno.dxf`),
  il foro Ø38 della ventola, 6 fori di fissaggio Ø3 senza rame, 4 fori Ø3,2 della ventola
  40 × 40, gli interruttori S1/S2 (tattili 6 × 6 alti 7,3 mm) sotto i pulsanti originali e il
  connettore J1 Micro-Fit 2×12 orizzontale sul retro, con il fronte al bordo inferiore.
  S1/S2 centrati sotto i pulsanti e ruotati di ±111° (piedini paralleli al bordo): i piedini
  rispettano 0,5 mm dal bordo, gli angoli dell'ingombro del corpo sporgono di circa 0,5 mm. Su
  User.Drawings il contorno della S3, su User.Comments le zone dello studio C3AI-CR-PL-001.
- `scheda-madre.kicad_sch`: generato da `tools/genera-schema-scheda-madre.py` (Python normale)
  con i simboli delle librerie di KiCad 10. Collegamenti disegnati con fili dentro ogni blocco,
  etichette solo per le reti verso altri blocchi o fogli. Il generatore confronta il netlist
  esportato da KiCad con le reti volute e si ferma a ogni differenza. Etichette globali: valgono in tutti i fogli. ERC: 1 errore atteso
  (IO34 `VAN_RX` senza sorgente fino al foglio VAN) e 21 avvisi per i segnali dei fogli non
  ancora disegnati (K-line, VAN, audio, MicroSD, collegamento con l'S3). Anteprima in `disegni/CR-EL-001_scheda-madre-alimentazione.png`.
- Faccia **F** = faccia interna verso la S3 (componenti caldi, interruttori); **B** = retro
  (ventola, J1).
- Regole: 2 strati, 1,6 mm, piste e distanze minime 0,2 mm, via 0,6/0,3, 0,5 mm dal bordo;
  montaggio a mano, si produce solo il circuito stampato (D-046).

Rigenerare:

```text
python tools/genera-schema-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/genera-pcb-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb
```

Le modifiche fatte a mano in KiCad sugli elementi generati si perdono rigenerando: quando
inizierà lo sbroglio il generatore servirà solo per il bordo.

Controllo DRC del 24/10/2026: 0 violazioni.
