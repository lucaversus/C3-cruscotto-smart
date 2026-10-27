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
- Regole: 4 strati (D-057: F e B componenti e piste, In1 piano di massa continuo, In2 piste e massa),
  1,6 mm, distanza minima 0,2 mm, pista minima 0,15 mm, via 0,6/0,3, 0,3 mm dal bordo; regola di progetto
  `scheda-madre.kicad_dru` (un raggio di raccordo termico basta sui fori passanti, massa garantita da In1);
  montaggio a mano, si produce solo il circuito stampato (D-046).

Rigenerare:

```text
python tools/genera-schema-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/genera-pcb-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb
```

Le modifiche fatte a mano in KiCad sugli elementi generati si perdono rigenerando: la rigenerazione
rifà piazzamento e sbroglio da capo (sezione «Sbroglio completo» qui sotto).

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
6,2 mm residui). Dal 27/10/2026 (D-059) J4, J5 e J10-J12 sono piazzole per fili saldati: il filo verso la
S3 va piegato parallelo alla scheda (spazio di circa 9,9 mm). Sul retro i più alti sono i relè K1/K2 (15,7 mm), C3
(10,1 mm), le file di pin del modulo VAN (8,7 mm) e J1 con la spina: profondità disponibile
dietro la scheda madre da misurare (verifica aperta 1 in `cruscotto/docs/scheda-madre.md`). Senza modello 3D in KiCad: U2, J1, J3, J10-J12, K1/K2
(altezze dalle schede tecniche).

DRC del 25/10/2026: nessun errore oltre ai 325 collegamenti non ancora tracciati (sbroglio da
fare). Da rivedere prima dello sbroglio: interasse delle file di pin del modulo VAN, profondità
dietro la scheda, posizione fine dei gruppi (piazzamento automatico, non ottimizzato per le piste).

## Sbroglio automatico, prima stesura (25/10/2026)

`tools/sbroglia-scheda-madre.py` (Python di KiCad): classi di rete (Potenza 1,0 mm, Medio 0,5 mm,
segnali 0,25 mm), piani di massa sulle due facce, esportazione Specctra, Freerouting 2.5.0 su Java 25
portatile (la versione CLI nativa per Windows si blocca), importazione e riempimento dei piani.
Esito con 25 passate (circa 30 minuti): 1617 piste e 210 via, **71 connessioni non tracciate**
secondo Freerouting; DRC: 108 elementi non connessi (comprese isole del piano di massa), 187 tratti
sotto 0,2 mm vicino alle piazzole, 36 piste troppo vicine al foro della ventola (Freerouting non
vede il foro come bordo), 34 raccordi termici incompleti. Anteprime `sbroglio-rame-F.png` e
`sbroglio-rame-B.png` (superate). **Non utilizzabile così**: serve un piazzamento più raccolto per gruppo e
una zona vietata attorno al foro della ventola, poi un nuovo sbroglio.

## Sbroglio completo a 4 strati (26/10/2026)

Con due strati Freerouting si fermava a 28-32 connessioni aperte; la scheda passa a 4 strati (D-057).
Lo spostamento della ventola verso il centro della S3 (D-058) è stato provato e scartato: peggiorava lo
sbroglio (46 connessioni aperte).

Procedura (Python di KiCad; Freerouting e Java come sopra):

```text
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/genera-pcb-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/sbroglia-scheda-madre.py <java.exe> <freerouting.jar> 40
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/completa-sbroglio-scheda-madre.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/serigrafia-scheda-madre.py
```

1. `sbroglia-scheda-madre.py`: classi di rete (Potenza 0,8 mm, 5V 0,6 mm, Medio 0,3 mm, segnali 0,2 mm),
   riempimenti di massa su F, In1 e B, In1 dichiarato strato di alimentazione nel file Specctra (niente piste,
   piano continuo), Freerouting con 40 passate (si ferma da solo dopo 10 passate senza miglioramenti),
   massa anche su In2, via di cucitura ogni 4 mm. Esito: 27-31 connessioni aperte. Freerouting usa limiti di
   tempo interni: due esecuzioni sullo stesso piazzamento danno risultati leggermente diversi.
2. `completa-sbroglio-scheda-madre.py`: uscita fissa dei piedini della USB-C (D+ e D- alternati su A6/B6 e
   A7/B7, impossibili da unire sullo stesso strato: ogni piedino scende a una via sfalsata), poi ricerca A*
   su griglia di 0,05 mm negli strati F, In2 e B per ogni collegamento mancante, con rimozione e nuovo
   tracciamento delle reti che si bloccano a vicenda, una via verso In1 nelle isole di massa e controllo
   finale con il DRC di KiCad (errori e avvisi su distanze, fori e tratti morti), ripetuto fino a esito pulito.

Esito della scheda in questo repository (rifatta il 27/10/2026 con le piazzole per fili di D-059): 3987 piste
(F 1602, In2 1678, B 707, 4,2 m in tutto) e 514 via. **DRC: 0 errori, 0 collegamenti mancanti**, nessun avviso
su fori o tratti morti. Serigrafia (28/10/2026, `tools/serigrafia-scheda-madre.py`): sigle alte 1,0 mm (0,8 mm
dove serve) lontane da piazzole e bordo, pallino sul piedino 1 di integrati, transistor e connettori, nomi dei fili
accanto alle piazzole, titolo e lato su F e B; DRC con **0 violazioni anche tra gli avvisi**. Nove sigle senza posto
restano solo nel disegno di montaggio (`montaggio/`), con la guida in `cruscotto/docs/montaggio-scheda-madre.md`. Il confronto con lo schema segnala differenze di
forma: le impronte sono assegnate dal generatore (varianti HandSolder) e non collegate ai simboli; le reti sono
verificate dal generatore dello schema. Anteprime: `sbroglio-rame-F.png`, `sbroglio-rame-In2.png`,
`sbroglio-rame-B.png` (B in vista speculare).

Limiti: sbroglio generato e controllato solo dal DRC; nessuna revisione di integrità del segnale (USB senza
impedenza controllata, piste lunghe di potenza da verificare con le correnti), serigrafia da riordinare,
nessun Gerber prodotto, nessuna scheda costruita o collaudata. Verifiche aperte in
`cruscotto/docs/scheda-madre.md` ancora valide (profondità dietro la scheda, interasse del modulo VAN, ecc.).

## Distinta materiali

Elenco generato dallo schema in `distinta-materiali.csv`; distinta ragionata (moduli già presenti, valori da
confermare, cablaggi) in `cruscotto/docs/distinta-scheda-madre.md`. Rigenerare l'elenco:

```text
kicad-cli sch export bom --fields "Reference,Value,Footprint,Description,QUANTITY,DNP" --labels "Rif,Valore,Impronta,Descrizione,Qta,DNP" --group-by "Value,Footprint" --ref-range-delimiter "" -o cruscotto/pcb/scheda-madre/distinta-materiali.csv cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch
```
