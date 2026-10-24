# Scheda madre — circuito stampato (KiCad 10)

Progetto KiCad della scheda madre del cruscotto (D-029, D-044, D-045, D-046). Stato:
**solo meccanica**, nessuno schema elettrico ancora.

- `scheda-madre.kicad_pcb`: generato da `tools/genera-pcb-scheda-madre.py` con il Python di
  KiCad. Contiene il bordo letto dal DXF dell'utente (`cruscotto/meccanica/scheda-madre-contorno.dxf`),
  il foro Ø38 della ventola, 6 fori di fissaggio Ø3 senza rame, 4 fori Ø3,2 della ventola
  40 × 40, gli interruttori S1/S2 (tattili 6 × 6 alti 7,3 mm) sotto i pulsanti originali e il
  connettore J1 Micro-Fit 2×12 orizzontale sul retro, con il fronte al bordo inferiore. Su
  User.Drawings il contorno della S3, su User.Comments le zone dello studio C3AI-CR-PL-001.
- Faccia **F** = faccia interna verso la S3 (componenti caldi, interruttori); **B** = retro
  (ventola, J1).
- Regole: 2 strati, 1,6 mm, piste e distanze minime 0,2 mm, via 0,6/0,3, 0,5 mm dal bordo;
  montaggio a mano, si produce solo il circuito stampato (D-046).

Rigenerare:

```text
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/genera-pcb-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb
```

Le modifiche fatte a mano in KiCad sugli elementi generati si perdono rigenerando: quando
inizierà lo sbroglio il generatore servirà solo per il bordo.

Controllo DRC del 24/10/2026: 0 violazioni.
