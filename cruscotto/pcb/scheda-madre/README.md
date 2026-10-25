# Scheda madre — circuito stampato (KiCad 10)

Progetto KiCad della scheda madre del cruscotto (D-029, D-044, D-045, D-046). Stato:
circuito stampato con la **sola meccanica**; schema elettrico iniziato con il foglio
**alimentazione** (C3AI-CR-EL-001 rev C), **front-end** (C3AI-CR-EL-002 rev A, `front-end.kicad_sch`) e
**interfacce veicolo** (C3AI-CR-EL-003 rev B, `interfacce-veicolo.kicad_sch`) e **sensori e memoria**
(C3AI-CR-EL-004 rev B, `sensori-memoria.kicad_sch`) e **collegamento S3 e audio** (C3AI-CR-EL-005
rev A, `s3-audio.kicad_sch`), proposte non verificate.

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
  esportato da KiCad con le reti volute e si ferma a ogni differenza. Etichette globali: valgono in tutti i fogli. ERC: 0 errori,
  1 avviso per la massa di riferimento VAN (J1 via 7) ancora da collegare. Anteprima in `disegni/CR-EL-001_scheda-madre-alimentazione.png`.
- `scheda-madre.pretty/` con `fp-lib-table`: impronte del progetto non presenti nelle librerie
  standard, per ora `ST_DIL24_Adapter_W15.0mm` (adattatore ST DIL24, interasse 15,0 mm).
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

## Piazzamento preliminare (25/10/2026)

Il generatore legge il netlist dello schema con `kicad-cli`, assegna le reti ai piedini e
dispone tutti i 139 componenti per blocchi, controllando contorno, fori (zona libera di
3,2 mm oltre il foro), foro e corpo della ventola, sovrapposizioni e, per i componenti a foro
passante, entrambe le facce. Anteprime: `piazzamento-lato-F.png` (faccia interna verso la
S3) e `piazzamento-lato-B.png` (retro, vista speculare).

- Faccia F (altezza massima circa 8 mm, distanza dalla S3 ~9,9 mm): alimentazione con le
  parti calde accanto alla ventola a sinistra (D-046), front-end ESP32 a destra, USB-C e
  CH340C al bordo superiore libero dalla S3, K-line e VAN, cavetti J10-J12 verso la S3.
- Faccia B: relè K1/K2, zoccolo dell'IMU J6, modulo VAN (J8/J9), RTC con portapila (pila
  sostituibile dal retro), condensatore C3, connettore della ventola J4, J1 verso l'auto.
- Modulo ESP32: radio non usata (D-029, D-036), quindi courtyard sul solo corpo e nessuna
  zona vietata d'antenna; fori termici da 0,2 mm sotto la piazzola di massa.
- Regole nel file di progetto `scheda-madre.kicad_pro` (foro minimo 0,2 mm per i fori termici).

**Orientamento:** il DXF dell'utente descrive la scheda vista dal retro, KiCad la disegna vista
dalla faccia F (verso la S3): le x sono speculari. Per i pezzi legati alla S3 vale x(KiCad) =
−x(assieme): J10 (P1), J12 (Speak) e J11 (P2) stanno quindi a x negative. Per inserire il modello 3D
esportato (`kicad-cli pcb export step --subst-models --user-origin 148.5x151mm`) nell'assieme:
rotazione di 180° attorno all'asse y, poi traslazione (0, 12, 23,6) mm.

**Altezze (25/10/2026, modello 3D di KiCad e tft-5inch.step):** sulla faccia F il componente più
critico è C29 (5,4 mm) con 5,5 mm di spazio residuo verso i componenti della S3; poi L1 (6,0 mm,
6,2 mm residui) e J5 (7,0 mm, 7,4 mm residui). Cavetti verso la S3 su PicoBlade ad angolo retto
(53048), spina parallela alla scheda. Sul retro i più alti sono i relè K1/K2 (15,7 mm), C3 e J4
(10,1 mm), le file di pin del modulo VAN (8,7 mm) e J1 con la spina: profondità disponibile
dietro la scheda madre da conoscere. Senza modello 3D in KiCad: U2, J1, J3, J10-J12, K1/K2
(altezze dalle schede tecniche).

DRC del 25/10/2026: nessun errore oltre ai 325 collegamenti non ancora tracciati (sbroglio da
fare). Da rivedere prima dello sbroglio: interasse delle file di pin del modulo VAN, profondità
dietro la scheda, posizione fine dei gruppi (piazzamento automatico, non ottimizzato per le piste).
