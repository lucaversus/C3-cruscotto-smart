# K-line autocostruita — Cruscotto C3+AI / Data Logger

Revisione E, 20/10/2026. Disegno C3AI-DL-KL-001, rev E (D-022: isteresi R10).
**Prototipo da banco non collaudato: nessun collegamento al veicolo.**
Scelta utente: realizzare l'interfaccia in proprio; la scelta non certifica
il circuito o autorizza pin auto presunti. Ambito D-008, D-010, D-011, D-013.

## Soluzione

NPN 2N5551 per portare K a massa (trasmissione); comparatore LM2903B
per ricevere con soglia riferita alla tensione della linea, invece della
soglia base-emettitore di un secondo transistor. R10 in retroazione positiva
introduce isteresi, per evitare commutazioni multiple sui fronti lenti della K-line. Ricevitore a 5 V con
uscita open collector e pull-up a 3,3 V. Masse comuni, nessun optoisolamento.
Non usare PC817 come sostituto diretto. Non usa MCP2515 o CAN.

Schema modificabile: [SVG](schema-kline-banco.svg). Anteprima: [PNG](schema-kline-banco.png).
Non e una piedinatura del veicolo o una scheda automotive certificata.

## Distinta per un prototipo da banco

Tutte le resistenze dei partitori a tolleranza 1%; valori da acquistare solo
se non gia disponibili. Possesso/ordine di questi componenti non confermato.

| Rif. | Quantita | Valore / componente | Nota |
| --- | --- | --- | --- |
| Q1 | 1 | 2N5551, NPN TO-92 | Scegliere produttore e verificare E/B/C sul relativo datasheet |
| U1 | 1 | LM2903B, versione SOIC-8 | Adattatore SOIC-8 → DIP-8; non scambiare con LM2903 senza B |
| R1 | 1 | 330 ohm, 0,25 W, 5% | Base TX |
| R2 | 1 | 47 kohm, 0,25 W, 5% | Base-emettitore, Q1 spento a GPIO flottante |
| R3 | 1 | 510 ohm, 1 W, 1% | Solo simulatore esterno da banco; non montare nel modulo |
| R4 | 1 | 68 kohm, 0,25 W, 1% | Partitore K |
| R5, R7 | 2 | 10 kohm, 0,25 W, 1% | Partitori verso massa |
| R6 | 1 | 150 kohm, 0,25 W, 1% | Riferimento VBENCH |
| R8 | 1 | 4,7 kohm, 0,25 W, 1% | Pull-up RX a 3V3 |
| R9 | 1 | 1 kohm, 0,25 W | Serie RX ESP32 |
| R10 | 1 | 330 kohm, 0,25 W, 1% | Retroazione OUT1 → IN1+, isteresi (rev E) |
| C1 | 1 | 100 nF ceramico | Bypass U1, vicino ai pin 8/4 |
| C2 | 1 | 10 microfarad, 16 V | Positivo su +5 V, negativo a GND |
| Montaggio | 1 insieme | Adattatore SOIC-8 → DIP-8, zoccolo DIP-8, millefori, morsetti e fili | Saldature e piedinatura da controllare |

Non ordinare in questa fase un altro modulo CAN o un'interfaccia Freematics.
Il tester esistente consente i controlli statici, non dimostra i tempi UART.

## Connessioni elettriche complete (netlist di riferimento)

I nomi di rete uguali indicano un collegamento. Non usare numeri di posizione
fisica dei transistor come se fossero universali fra produttori.

| Elemento | Collegamento |
| --- | --- |
| R1 | TX_INV — base Q1 |
| R2 | Base Q1 — GND |
| Q1 | Collettore K_BENCH; emettitore GND |
| R3, esterna al modulo | VBENCH — R3 — K_BENCH, soltanto nel simulatore da banco |
| R4 | K_BENCH — VSENSE |
| R5 | VSENSE — GND |
| R6 | VBENCH — VREF |
| R7 | VREF — GND |
| U1A pin 3 (+) | VSENSE |
| U1A pin 2 (-) | VREF |
| U1A pin 1 (out) | RX_RAW |
| R8 | 3V3 — RX_RAW |
| R9 | RX_RAW — RX_3V3 |
| R10 | RX_RAW — VSENSE (U1A pin 1 — pin 3) |
| U1 pin 8, pin 4 | +5V, GND rispettivamente |
| U1B pin 5, pin 6, pin 7 | GND, VREF, non collegato rispettivamente |
| C1, C2 | Fra +5V e GND (polarita C2 come distinta) |
| ESP32 | GND comune; 3V3 e +5V da alimentazioni regolate concordate, non da K |

Proposta logica firmware: GPIO17 TX_INV e GPIO16 RX_3V3 (non ancora assegnazione
finale dell'intero logger). Il GPIO TX deve restare basso a riposo: NPN inverte.
Usare inversione UART del solo TX; RX non invertito. Applicare la configurazione
in modo da non produrre impulsi dominanti indesiderati durante inizializzazione.
Non collegare questi segnali al firmware SPI attualmente caricato presumendo
che esegua il test K-line: non lo esegue.

## Alimentazione e ambito del primo collaudo

VBENCH = 9-16 V stabilizzati con limitazione di corrente; +5V = 4,75-5,25 V;
3V3 = logica ESP32. Alimentazioni e GND corretti prima di applicare VBENCH,
rimuovere VBENCH prima di spegnere la logica. Alimentatore banco non ancora
censito come disponibile: non usare l'auto come sostituto per la prova.
R3 esterna simula il pull-up della vettura sul banco; nessun jumper nel modulo. Il pull-up della vettura non e
stato verificato e non va raddoppiato automaticamente. Non collegare 12 V
ad alcun ingresso ESP32 o al pin 3V3. Montare e controllare tutto spento.

La protezione automotive contro inversione, cortocircuiti, ESD/transitori,
load dump, disturbi e alimentazioni parziali NON e compresa o validata in
questa revisione. Q1 non ha limitazione attiva di corrente su corto a batteria.
La tensione nominale del transistor non dimostra robustezza del sistema.
La revisione per l'auto richiede uno studio dedicato del circuito protetto.

## Verifiche svolte e limiti

`python data-logger/docs/tools/genera-kline-banco.py` rigenera lo schema e
verifica un modello DC a estremi delle resistenze, non una simulazione SPICE.
Con resistori all'1% (partitori, R8 e R10), offset assunto +/-3 mV, 3V3 a
3,135-3,465 V, uscita bassa 0-0,4 V e VBENCH 9-16 V (rev E):

- soglia in discesa della linea (uscita alta) 0,4018-0,4801 VBENCH;
- soglia in salita (uscita bassa) 0,4710-0,5216 VBENCH; tutte entro 0,3-0,7 VBENCH;
- isteresi riferita alla linea K 0,545-0,721 V, indipendente da VBENCH
  (circa 3,3 V × R4 / (R10 + R8)); in rev D era assente;
- massimo ingresso comparatore 2,123 V, sotto 4,75-2 V;
- beta forzato massimo calcolato circa 8,51 con TX minimo assunto 2,5 V,
  VBE massimo assunto 1,2 V e tolleranze resistenze base;
- R3 massimo calcolato 0,507 W a 16 V: selezionata 1 W per il banco.

Sono calcoli con ipotesi esplicite: non provano VCEsat al punto reale,
commutazione del transistor, isteresi, margini ai disturbi, propagazione,
capacita del cablaggio o risposta della centralina. Nessun risultato
sperimentale acquisito. Nessun componente segnato come posseduto.

Primo controllo futuro: continuita e assenza corti a circuito spento; poi
stati statici K alta/bassa su banco limitato e tensione RX. Solo dopo,
verifica temporale a 10400 baud e fast init, gestione eco e timeout.
Nessun firmware K-line compilato o caricato in questo passaggio.

## Fonti / originalita

Schema e generatore prodotti per questo repository, senza copia di immagini
esterne. Riferimenti funzionali e limiti dei componenti:

- [TI LM2903B datasheet](https://www.ti.com/lit/ds/symlink/lm2903b.pdf): pinout, uscita open collector, alimentazione e campo ingressi; verificare codice ordinato.
- [onsemi 2N5551 datasheet](https://www.onsemi.com/pdf/datasheet/2n5551t-d.pdf): NPN TO-92 e caratteristiche; il collaudo resta necessario.
- [ELM327 DSL](https://elmelectronics.com/wp-content/uploads/2020/05/ELM327DSL.pdf): distinzione KWP fast init da solo invio UART.

## Revisione B — riordino schema e correzione contenitore

U1 rappresentato intero, vista superiore con tutti gli otto piedini; condensatori
disegnati, distinta base sullo stesso foglio e cartiglio aggiornato. Collegamenti
e valori elettrici invariati. Il datasheet TI SLCS005AH distingue LM2903B da
LM2903: per la versione B usare SOIC-8 con adattatore a DIP-8, non il PDIP-8
precedentemente indicato per errore. Pinout verificato nella sezione 4 del
datasheet; nessuna verifica hardware aggiuntiva.

## Revisione C — simulatore esterno

Conferma utente 18/10/2026: eliminare JP1. La resistenza R3 da 510 ohm / 1 W
resta solo nel simulatore esterno al modulo. Sul banco si collega il modulo
alla linea simulata come alla linea della vettura, con alimentazioni e masse
corrette. Il solo richiamo resistivo simula il carico statico, non risposte ECU,
disturbi o transitori della vettura; non costituisce collaudo KWP completo.
In auto non montare R3 aggiuntiva senza riscontro del richiamo gia presente.

## Revisione E — isteresi del comparatore, 20/10/2026

D-022. Aggiunta R10 330 kohm 1% tra uscita OUT1 (pin 1, nodo RX_RAW) e
ingresso IN1+ (pin 3, VSENSE). Senza retroazione, rumore e fronti lenti della
linea (richiamo resistivo e capacita del cablaggio) potevano far oscillare
l'uscita durante la transizione e produrre byte spuri o errori di framing.
Il generatore verifica soglie e isteresi agli estremi delle tolleranze; resta un
modello DC, senza tempi di propagazione, rumore reale o carico dell'ingresso ESP32.
Primo controllo aggiuntivo al montaggio: con il simulatore da banco, rampa lenta
della linea K e verifica che RX_3V3 cambi stato una sola volta per ciascun fronte.
Nessun altro collegamento o valore modificato; componenti non confermati.

## Revisione D — porte esterne evidenziate

RX_3V3 e uscita dal modulo verso RX ESP32; TX_INV e ingresso dal TX ESP32.
K-line e bidirezionale verso linea esterna, simulata da K_BENCH nella prova.
Porte colorate e direzioni visibili sul disegno; collegamenti elettrici invariati.
Alimentazioni: +5 V, 3V3, riferimento VBENCH 9–16 V e GND comune.
