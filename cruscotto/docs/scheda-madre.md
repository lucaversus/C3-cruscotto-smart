# Scheda madre del cruscotto — progetto preliminare

Revisione B, 21/10/2026 (rev A 20/10/2026). Cruscotto C3+AI, decisioni D-028…D-031.
Schema a blocchi: [C3AI-CR-BL-001 rev D](../../disegni/CR-BL-001_scheda-madre-blocchi.png) ([SVG](../../disegni/sorgenti/CR-BL-001_scheda-madre-blocchi.svg),
generatore `tools/genera-scheda-madre.py`). Studio d'ingombro: [C3AI-CR-PL-001 rev E](../../disegni/CR-PL-001_scheda-madre-ingombro.png)
([SVG](../../disegni/sorgenti/CR-PL-001_scheda-madre-ingombro.svg), generatore `tools/genera-ingombro-scheda-madre.py`).

**Stato: proposta.** Nessun componente scelto in via definitiva. Schema elettrico
iniziato in KiCad (fogli alimentazione C3AI-CR-EL-001 rev C, front-end C3AI-CR-EL-002 rev A,
interfacce veicolo C3AI-CR-EL-003 rev B, sensori e memoria C3AI-CR-EL-004 rev B e collegamento S3 e audio
C3AI-CR-EL-005 rev A, proposta non verificata);
circuito stampato con la sola meccanica. I pin del veicolo vengono da manuali
generici RTA e da fonti comunitarie e vanno verificati (D-008, D-022).

## Scopo

Una scheda fissata dietro l'ESP32-S3 8048S050 che raccoglie tutti i collegamenti
verso l'auto in un **connettore multipolare unico** (-J1) e contiene il **front-end**
ESP32 (D-029): l'S3 non ha fili diretti verso il veicolo. Prima della scheda madre
si costruisce un prototipo con i moduli già presenti (HW-ESP32, HW-CAN-VP230,
KL-001 su millefori, HW-IMU-LSM6DSO).

## Blocchi

| Sigla | Blocco | Contenuto proposto | Vincoli |
| --- | --- | --- | --- |
| -U1…U3 | Ingresso 12 V | TVS bidirezionale, diodo ideale contro l'inversione (LM74700-Q1 + MOSFET N), ferrite; accensione del 5 V con chiave O mantenimento sull'EN del buck | D-030; fusibile di ramo nel cablaggio vicino al prelievo (HW-FUSE-HOLDER); schema CR-EL-001 |
| -C1 | Riserva avviamento | diodo + supercondensatore con carica limitata | capacità da calcolare dopo la misura C3AI-CR-PR-001 (P5) |
| -U4/U5 | Alimentazione | buck 12 → 5 V 3,5 A (TPS54360B, 60 V) acceso a comando + buck 12 → 3,3 V 1 A sempre acceso a basso consumo (LMR36510, 65 V, 26 µA) | 5 V anche per l'S3 tramite -J2 / P1; schema CR-EL-001 |
| -U6 | Front-end | ESP32-WROOM-32E-**H4/H8** montato a mano (HW-FE-MODULE, D-050) | senza PSRAM; stessi GPIO del logger 0.3.x |
| -U7 | VAN | SN65HVD230 solo ricezione: D a 3V3, nessuna resistenza da 120 Ω | prerequisiti D-022 bloccanti |
| -U8 | K-line | circuito KL-001 rev F (2N5551 + LM2903B, isteresi R10) | progetto da banco: protezioni auto da aggiungere |
| -U9 | IMU | LSM6DSO a 0x6A (prototipo: STEVAL-MKI196V1 DIL-24); in definitiva valutare ISM330 −40…+105 °C | fissaggio rigido, assi indicati in serigrafia; stesso chip del logger (D-033) |
| -U10 | RTC (opzionale) | DS3231 a 0x68 | utile per i timestamp del dataset |
| -U11 | Programmazione | USB-seriale con reset automatico, oppure connettore a 6 poli | aggiornamenti senza smontare |
| -K1/K2 | Audio (D-028) | un relè a doppio scambio per canale (Omron G2RL-2, bobina 5 V), pilotato da MOSFET con diodo di ricircolo; eccitati: S3 sui due altoparlanti in serie | a riposo radio → altoparlanti; uscite radio a ponte mai a massa; schema CR-EL-005 |
| -J1 | Verso l'auto | **Molex Micro-Fit 3.0, 24 vie** (D-044): sulla scheda 43045-2400, sul cablaggio 43025-2400 | ritenuta meccanica e codifica contro l'inserimento errato |
| -J2 | Verso l'S3 | P1, P2, P6 della scheda 8048S050 | cavo corto |

## GPIO del front-end (proposta)

Ripresi dal logger 0.3.x (`data-logger/firmware/logger/include/config.h`), così che
raccolta dati e uso in auto leggano il veicolo con lo stesso codice.

| GPIO | Funzione | Note |
| --- | --- | --- |
| 16 / 17 | UART2 K-line RX / TX | come il logger |
| 34 | VAN RX | solo ingresso, come il logger |
| 21 / 22 | I2C SDA / SCL | IMU 0x6A, RTC 0x68 opz. |
| 25 / 33 | UART1 TX / RX verso l'S3 | |
| 35 | tensione batteria (partitore) | ADC1, solo ingresso |
| 39 | segnale chiave (+ dopo contatto) | ingresso protetto, solo ingresso |
| 13 | comando di mantenimento alimentazione | a riposo spento |
| 4 | LED di stato | |
| 5 | pulsante destro del quadro (S2) | pull-up 10k; pin di avvio, alto a riposo (D-054) |
| 26 | ventola 12 V, PWM (D-031) | ingresso PWM della ventola a 4 fili, a collettore aperto (CR-EL-002) |
| 2 | accensione della ventola | P-MOSFET lato alto; pin di avvio: basso al reset (resistenza da 100k), D-049 |
| 14 | giri ventola (tachimetrica) | ingresso con pull-up |
| 36 / 32 | NTC vicino al display / NTC sulla scheda | ADC1 |
| 18 / 19 / 23 / 27 | MicroSD opzionale | stessi pin del logger: la scheda madre può fare anche da registratore |

Evitati i pin di avvio 0, 12, 15 e quelli della flash (6-11). GPIO2, anch'esso pin di avvio, è
usato per l'accensione della ventola perché a riposo deve restare basso come richiede l'avvio (D-049);
GPIO5, anch'esso pin di avvio, per il pulsante destro perché a riposo resta alto (D-054).

## Schema elettrico: alimentazione (C3AI-CR-EL-001 rev C, proposta)

Foglio KiCad `cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch`, generato da
`tools/genera-schema-scheda-madre.py`; tavola [CR-EL-001](../../disegni/CR-EL-001_scheda-madre-alimentazione.png).
Valori ripresi dagli esempi dei datasheet TI e dalla prova OBD-M001 (12,2 V a riposo,
14,2 V a motore acceso, minimo 9,0 V in avviamento letto dal tester).

- **Ingresso**: J1 via 1 → D1 SMCJ26CA (bidirezionale, blocca circa 42 V) → U1 LM74700-Q1
  con Q1 MOSFET N 60 V in DPAK (diodo ideale: inversione di polarità e niente ritorno di
  corrente verso l'auto durante l'avviamento) → C3 220 µF 50 V di riserva → ferrite FB1 → `+12V_F`.
- **5 V principale**: U2 TPS54360B 60 V / 3,5 A, 600 kHz, L1 8,2 µH, diodo B560C. Acceso se
  la chiave è inserita (`KEY_IN` tramite D3 e partitore R5/R6: avvio a circa 8 V, arresto a
  circa 6,3 V) **oppure** se il front-end tiene alto GPIO13 (`PWR_HOLD` tramite D4/R7). R8
  tiene spento a riposo: al reset del front-end il 5 V dipende solo dalla chiave (D-030).
- **3,3 V sempre acceso** (convertitore a commutazione, D-047): U3 LMR36510 65 V / 1 A, 26 µA a vuoto, EN collegato all'ingresso.
  Alimenta front-end e sensori anche a motore spento (D-031). Al posto del regolatore
  lineare della proposta precedente: con il front-end attivo un lineare dal 12 V
  dissiperebbe 0,5-0,8 W vicino al display.
- **Misure verso il front-end**: `KEY_SENSE` (GPIO39, 100k/22k) e `VBAT_SENSE` (GPIO35,
  470k/100k, circa 21 µA a 12 V), filtrate da 100 nF e limitate da BAT54S verso massa e 3,3 V.
- Consumo a riposo stimato: U1 80 µA + U3 26 µA + partitori circa 25 µA + front-end in sonno,
  sotto 1 mA (D-030). Da misurare sul prototipo.

Da verificare prima dell'ordine: modello del MOSFET (proposto IPD50N06S4L-12), induttori L1/L2
(corrente di saturazione), ferrite, capacità di riserva dopo la misura del calo
all'avviamento con un oscilloscopio o un registratore (il tester non vede i picchi brevi).
U2 e U3 hanno la piazzola termica sotto il corpo (HSOIC, ammessi da D-046): si saldano a mano
riempiendo di stagno dal retro un foro metallizzato centrale da circa 1-1,5 mm più i fori termici
dell'impronta (D-048); diametro da fissare nello sbroglio.

## Schema elettrico: front-end (C3AI-CR-EL-002 rev A, proposta)

Foglio `cruscotto/pcb/scheda-madre/front-end.kicad_sch`, sottofoglio della radice, stesso
generatore; tavola [CR-EL-002](../../disegni/CR-EL-002_scheda-madre-front-end.png).

- **U4 ESP32-WROOM-32E-H4** (HW-FE-MODULE) con i GPIO della tabella sopra; 22 µF + 100 nF,
  EN con 10k/1 µF, pulsanti RESET e BOOT.
- **Programmazione a banco**: USB-C (passo 0,5 mm, saldatura a trascinamento) con CH340C
  alimentato dalla sola USB tramite AP2112K-3.3, reset automatico con due MMBT3904,
  4,7k in serie sulla UART0. In auto la presa non serve: aggiornamenti attraverso l'S3 (D-039).
- **Collegamento con l'S3**: 1k in serie su GPIO25/GPIO33, verso il connettore -J2 del foglio
  successivo; limitano la corrente verso l'S3 spenta.
- **I2C**: 4,7k verso il 3,3 V sempre acceso.
- **NTC 100k** (B3950) sulla scheda (GPIO32) e vicino al display su JST-XH (GPIO36): 16 µA ciascuna.
- **Ventola a 4 fili** Delta AFB0412VA-00 (D-052; fili nero GND, rosso +12 V, blu giri, giallo PWM) su connettore standard: alimentazione staccata a riposo da un P-MOSFET
  60 V (ZXMP6A13F proposto) comandato da GPIO2, velocità con PWM a collettore aperto
  (GPIO26, logica invertita), giri con pull-up a 3,3 V e 1k verso GPIO14.

Il generatore confronta le reti di tutti i fogli con il netlist di KiCad. Modulo ESP32 e presa USB-C montati a mano (D-050); GPIO2 per la ventola approvato (D-049).

## Schema elettrico: interfacce veicolo (C3AI-CR-EL-003 rev B, proposta)

Foglio `cruscotto/pcb/scheda-madre/interfacce-veicolo.kicad_sch`; tavola
[CR-EL-003](../../disegni/CR-EL-003_scheda-madre-interfacce-veicolo.png).

- **K-line** (-U8 del blocco): reti della KL-001 rev F (Q8 MMBT5551, versione SMD del 2N5551;
  U7 LM2903B; isteresi R44 = R10 della rev F), con tre cambiamenti per l'auto:
  TVS bidirezionale D8 (SMBJ26CA) sulla linea, diodo D9 in serie al collettore (linea negativa),
  soglia R42 presa dalla **linea chiave** invece che dalla batteria (nessun consumo a riposo;
  con la chiave la linea vale circa la tensione di batteria). Comparatore alimentato dal 5 V
  principale; pull-up dell'uscita al 3,3 V sempre acceso. Protezione dal corto della linea K
  verso la batteria durante la trasmissione: da studiare.
- **VAN** (-U7 del blocco, D-051): modulo blu SN65HVD230 (tipo HW-CAN-VP230, resistenza 121
  rimossa) su file di pin J8 (3.3V/GND/RX/TX) e J9 (CANH/CANL); TX collegato al 3,3 V sulla scheda,
  quindi sola ricezione; NUP2105L sulle due linee, 100k verso massa su GPIO34 (nessuna resistenza
  interna). Alimentato da un 3,3 V separato (U9 AP2112K dal 5 V principale): il VAN si ascolta solo a quadro acceso, nessun consumo a riposo. Ordine DATA /
  DATA B da verificare (D-022); la massa di riferimento VAN di J1 (via 7) resta da collegare.

Nessun collegamento all'auto prima dei prerequisiti D-022 e D-008.

## Schema elettrico: sensori e memoria (C3AI-CR-EL-004 rev B, proposta)

Foglio `cruscotto/pcb/scheda-madre/sensori-memoria.kicad_sch`; tavola
[CR-EL-004](../../disegni/CR-EL-004_scheda-madre-sensori-memoria.png).

- **IMU** (-U9 del blocco): zoccolo per il modulo STEVAL-MKI196V1 (HW-IMU-LSM6DSO, D-046):
  scheda 18,0 × 30,5 mm, due file da 12 pin a passo 2,54 con **interasse 15,0 mm** (Gerber ST,
  non 15,24 come uno zoccolo DIP), quindi due strip femmina 1x12 sull'impronta del progetto
  `scheda-madre:ST_DIL24_Adapter_W15.0mm`; piedinatura da ST DB3714 rev 1: VDD/VDDIO e CS al 3,3 V sempre acceso (CS alto =
  I2C), SDO/SA0 a massa (indirizzo 0x6A), SCL/SDA sul bus I2C; INT1/INT2 non collegati (GPIO
  libero eventuale: 5). Da riscontrare sulla serigrafia all'arrivo.
- **RTC** (-U10, facoltativo): DS3231SN in SOIC-16W come il modulo del logger, piedini 5-12 a
  massa come da datasheet, pila CR2032 su portapila (HW-RTC-BATTERY, da procurare) senza
  ricarica (D-019).
- **MicroSD** (facoltativa, D-051): modulo lettore (tipo HW-SD-MODULE) su fila di pin J7
  (3V3/CS/MOSI/CLK/MISO/GND), SPI su GPIO18/19/23/27 come il logger, 10k di pull-up su CS,
  alimentato dal 3,3 V acceso a quadro: a riposo il firmware deve tenere basse le linee SPI.

ERC con i quattro fogli: 0 errori, 11 avvisi per i segnali del foglio ancora da disegnare
(collegamento con l'S3, audio) e per la massa di riferimento VAN. Il generatore confronta 88
reti con il netlist di KiCad. Interasse delle file di pin e altezza dei moduli VAN e MicroSD da
misurare sui pezzi prima dello sbroglio (D-051).

## Schema elettrico: collegamento S3 e audio (C3AI-CR-EL-005 rev A, proposta)

Foglio `cruscotto/pcb/scheda-madre/s3-audio.kicad_sch`; tavola
[CR-EL-005](../../disegni/CR-EL-005_scheda-madre-s3-audio.png).

- **Cavetti verso la S3**: J10 (P1), J11 (P2), J12 (P6) su connettori PicoBlade/MX1.25 a 1,25 mm
  (cavetti con i connettori MX1.25 dell'utente, HW-MX125-PLUGS). Il 5 V passa dal Schottky D13
  (B340A): se la S3 è collegata anche alla USB, il suo 5 V non risale nella scheda madre.
- **Relè audio** (D-028): K1 (sinistro) e K2 (destro), Omron G2RL-2 DPDT con bobina 5 V,
  pilotati da AO3400A sul comando IO13 della S3, 100k verso massa sul gate: a riposo, a quadro
  spento o con la S3 spenta la radio resta sugli altoparlanti. Eccitati, l'uscita della S3 va
  sui due altoparlanti **in serie** (D-053; circa 8 Ω visti dall'amplificatore mono U1): le uscite
  della radio restano scollegate, mai a massa.
- **Pulsanti del quadro** (D-054): S1 (sinistro) a IO19 della S3, S2 (destro) a GPIO5 del
  front-end con pull-up 10k. Accesso di servizio dalla USB-C della S3 (D-055): UART0 e USB nativa
  della S3 non collegate alla scheda madre.

ERC con i cinque fogli: 0 errori, 1 avviso per la massa di riferimento VAN (J1 via 7) ancora da
collegare. Il generatore confronta 95 reti con il netlist di KiCad.

## Verifiche aperte prima dello sbroglio (25/10/2026)

1. **Profondità dietro la scheda madre** (verso il fondo del quadro): sul retro i pezzi più alti
   sono i relè K1/K2 (15,7 mm), C3 e J4 (circa 10 mm), la ventola (10 mm) e J1 con la spina del
   cablaggio inserita. Da misurare sull'auto o sul modello del quadro.
2. **Modulo VAN blu**: interasse tra le file di pin J8 (4 vie) e J9 (CANH/CANL) e altezza, dal
   pezzo o da un modello 3D (D-051).
3. **STEVAL-MKI196V1**: confermare sul pezzo interasse 15,0 mm e piedino 1 (misure dai Gerber ST).
4. **Telaio stampato**: nessun contatto con i componenti della faccia F (controllo fatto solo
   verso i componenti della S3, margine minimo 5,5 mm).
5. **Audio (D-053)**: potenza di U1 (prova d'ascolto su P6), impedenza degli altoparlanti, fase.
6. **Ventola (D-052)**: limite +70 °C rispetto alla temperatura misurata dietro il quadro.
7. **Massa di riferimento VAN** (J1 via 7): collegamento da decidere con la verifica sul quadro.

## Raffreddamento e dominio sempre acceso (D-031)

- **Due domini di alimentazione.** Sempre acceso: buck 3,3 V a bassissimo consumo
  (LMR36510, CR-EL-001) dal +12 V protetto, front-end in sonno con risveglio periodico, NTC,
  misura della batteria, comando ventola. Principale: buck 5 V e S3, accesi con
  chiave e mantenimento (D-030).
- **Ventola 12 V** alimentata direttamente dal +12 V protetto (nessun bisogno del
  buck a motore spento), MOSFET in PWM su GPIO26, giri su GPIO14 per rilevare il blocco.
  Cuscinetti a sfera, temperatura nominale ≥ 70 °C, preferibilmente 4 fili.
- **Logica di partenza** (soglie da tarare): motore acceso e display > 60 °C →
  ventola proporzionale; motore spento, display > 55 °C e batteria a riposo
  > 12,3 V → ventola accesa; sotto 12,3 V spenta e bloccata fino al successivo
  avviamento; isteresi 5 °C; tempo massimo a motore spento 6 h.
- Limiti del pannello dichiarati dal rivenditore: funzionamento −20…+70 °C,
  magazzinaggio −30…+80 °C. Al sole d'estate la protezione principale resta
  passiva (schermatura, distanza dalla copertura, dissipatore); efficacia da
  misurare la prossima estate.

## Ingombro (C3AI-CR-PL-001)

**Contorno definitivo (D-045, 24/10/2026)** dal modello 3D del cruscotto dell'utente:
[`cruscotto/meccanica/scheda-madre-contorno.dxf`](../meccanica/scheda-madre-contorno.dxf),
**178,7 × 74 mm**, 6 fori di fissaggio Ø3 in (±80, 13), (±75, 48), (±30, 79) mm, due
rientranze laterali. La scheda madre sta **direttamente dietro la S3**. Il generatore dello
studio legge il DXF e controlla che ogni zona stia nel contorno, lontana dai fori, dalla
ventola e dagli interruttori.

- **Ventola** (D-031): foro Ø38 al centro con ventola 40 × 40 × 10 a 12 V sul lato
  opposto, che soffia verso la S3; in alternativa 30 × 30 con foro Ø28.
- **Interruttori -S1/-S2** ai due estremi, sotto i pulsanti del quadro originale: dall'assieme
  3D ([assieme-cruscotto.step](../meccanica/assieme-cruscotto.step)) in (±84,3, 32,2) mm nelle
  coordinate del contorno; l'estremità del pulsante è a circa 6,3 mm dalla scheda, quindi
  interruttore tattile 6 × 6 con pulsante alto circa 7 mm (o una prolunga); corsa da verificare.
- **Distanza tra retro della S3 e scheda madre** nell'assieme attuale: circa **9,9 mm**; i
  componenti della faccia interna devono restare più bassi, con margine per l'aria (D-046).
- **-J1** Micro-Fit 2×12 (D-044) al bordo inferiore, al centro; **-J2** verso la S3 al
  bordo superiore, al centro.

| Voce | Area |
| --- | --- |
| Blocchi di base, netto | ≈ 3 680 mm² |
| Base con piste e distanze (× 1,5) | ≈ 5 520 mm² |
| Facoltativi (RTC + CR2032, MicroSD) | ≈ 705 mm² netti |
| Contorno meno foro della ventola | ≈ 9 510 mm² |

Conclusione preliminare: tutti i blocchi di base e i facoltativi RTC/MicroSD stanno su una
sola faccia attorno alla ventola. Il supercondensatore di riserva (36 × 24 mm, misura P5
della prova sulla presa OBD) non trova posto su questa faccia: retro o fuori scheda, da
decidere. Da rilevare sul pezzo: posizione relativa delle due schede, connettori P1/P2/P6
e altezze dei componenti sul retro della S3.

## Montaggio a mano e raffreddamento dei componenti (D-046)

- Si fa produrre **solo il circuito stampato**; i componenti li salda l'utente.
- Componenti ammessi: foro passante; SMD con passivi **0805 o più grandi**, integrati in
  **SOIC, SOT, TSSOP**; moduli con piazzole sul bordo (WROOM). **Esclusi QFN, BGA, LGA**:
  l'IMU (LGA) resta su modulo o adattatore con connettore (es. STEVAL-MKI196V1 o il suo
  equivalente definitivo, D-033). Ogni scelta di componente va controllata con questa regola.
- **Componenti che scaldano di più sulla faccia interna**, rivolta verso la S3, attorno al
  foro della ventola (D-045): convertitore 12 → 5 V, regolatore 3,3 V, protezioni d'ingresso,
  front-end. Il flusso della ventola li investe prima di uscire tra le due schede.
- Distanza tra scheda madre e S3: da fissare a progetto completato, simulando nel modello 3D
  lo spessore della scheda con i componenti.

## Collegamenti verso l'S3 (-J2)

Connettori della S3 a passo 1,25 mm (MX1.25; P5 a 1,0 mm), ordine dei piedini riferito
dall'utente il 25/10/2026, vista dal retro con la USB-C a destra (HW-DASH-DISPLAY).

| Connettore S3 | Piedini | Uso sulla scheda madre (CR-EL-005) |
| --- | --- | --- |
| P1 (dal basso in alto) | 5V, TXD, RXD, GND | J10: 5 V dalla scheda madre tramite il Schottky D13 e massa comune; UART0 non collegata (riserva) |
| P2 (da destra a sinistra) | IO19, IO11, IO12, IO13 | J11: IO19 pulsante sinistro S1 (D-054), IO11 ricezione dal front-end, IO12 trasmissione, IO13 comando relè |
| P3 | IO17, IO18, IO19, IO20 | non usato; IO19/IO20 = USB nativa (possibile porta nascosta) |
| P4, P5 | GND, 3.3V, IO17, IO18 | non usati (IO17/IO18 verso U1) |
| P6 Speak | 2 piedini senza polarità | J12: uscita differenziale verso i relè |

P2 e P3 non portano massa: il riferimento del collegamento seriale arriva da P1.

Rispetto alla proposta precedente la UART passa su IO11/IO12: IO17/IO18 restano
all'amplificatore U1 se la prova d'ascolto lo conferma.

## Connettore verso l'auto (-J1, Micro-Fit 3.0 24 vie, D-044)

Tipo deciso il 23/10/2026 (D-044); assegnazione delle vie ancora bozza. Lo stesso cablaggio
dell'auto (femmina 43025-2400) si innesta prima nella spina volante del prototipo a banco
(43020-2400, tavola C3AI-DL-EL-004) e poi nel connettore della scheda definitiva (43045-2400).

| Via | Segnale | Origine nel veicolo |
| --- | --- | --- |
| 1 | + batteria (fusibile nel cablaggio) | presa OBD via 16 |
| 2 | massa di potenza | presa OBD via 4/5 |
| 3 | + dopo contatto (segnale chiave) | presa OBD via 1 |
| 4 | linea K | presa OBD via 7 |
| 5 / 6 | VAN DATA / DATA B | quadro 0004 vie 1 / 3 (ordine da verificare) |
| 7 | massa di riferimento VAN | quadro 0004 via 9 |
| 8-11 | canale Sx: radio + / −, altoparlante + / − | da identificare sul cablaggio radio |
| 12-15 | canale Dx: radio + / −, altoparlante + / − | da identificare |
| 16 | riserva | |
| 17-24 | riserva (es. luci, comandi, segnali futuri) | |

## Bilancio di potenza (stima, da misurare)

Totale 1-2 A a 5 V (5-10 W) con audio attivo: S3 e display 0,3-0,6 A, front-end e
interfacce 0,1-0,25 A, relè 0,07 A, amplificatore a picchi 0,5-1 A. A riposo
(spento con mantenimento aperto) obiettivo < 1 mA dalla batteria.

## Prima di disegnare lo schema elettrico

1. Esiti della prova C3AI-CR-PR-001: vie 16/1 della presa OBD e calo all'avviamento (eseguita,
   OBD-M001; picchi brevi da rimisurare con strumento più veloce).
2. Prova d'ascolto su P6 per la funzione di U1.
3. Prototipo a banco: front-end HW-394 + S3 su UART, VP230 e KL-001 montati.
4. Prerequisiti VAN D-022 e prima cattura passiva dal quadro.
5. Identificazione dei fili altoparlanti della radio e del tipo di uscita.
6. Rilievo sul pezzo S3: connettori P1/P2/P6, USB-C, MicroSD, altezze dei
   componenti sul retro, zona antenna Wi-Fi; scelta dei distanziali con dissipatore.
7. Misura della temperatura dietro il quadro; scelta di connettori e componenti
   con temperatura e vibrazioni adatte.
8. Strumento di progetto del circuito stampato: KiCad (gratuito, open source, D-003); produzione del solo
   circuito stampato e montaggio a mano (D-046).
