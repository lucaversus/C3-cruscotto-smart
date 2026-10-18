# Inventario hardware — Cruscotto C3+AI / Data Logger

Aggiornato: **2026-10-18**. Vista generata da [hardware.json](hardware.json).
Non modificare manualmente: usare `python tools/project_preflight.py --render-inventory`.

Il materiale presente ma non collaudato va valutato prima di proporre acquisti sostitutivi.
Le decisioni definitive restano nel [README principale](../../README.md#decisioni-definitive).

## Stati

- `present_verified`: Presente; verifiche effettivamente eseguite indicate nella voce.
- `present_declared`: Presente secondo il contesto utente; non equivale a verifica elettrica.
- `ordered_pending`: Ordinato dall’utente, non ancora arrivato.
- `not_confirmed`: Disponibilità o ordine non confermati: non presumere possesso né assenza.
- `candidate`: Solo ipotesi di progetto; non confondere con materiale acquistato.

## Materiale e fonti

### HW-ESP32 — ESP32 HW-394 a 30 pin, modulo marcato ESP-32D

**Stato:** `present_verified` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Identificazione e collaudo a banco nella chat; data-logger/backups/esp32-hw394/README.md e firmware/diagnostic/README.md. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json.

**Foto archiviate:** [esp32-hw394-fronte.jpg](hardware-photos/esp32-hw394-fronte.jpg)

**Verifiche documentate:**

- esptool: ESP32-D0WD-V3 rev. 3.1, flash 4 MB, quarzo 40 MHz
- COM3 CH340; diagnostica 0.1.0 caricata, avvio e oltre 70 s osservati
- Backup flash completo con SHA-256 verificato; ripristino non provato
- Foto frontale archiviata: HW-394 / ESP-32D e basetta di espansione a morsetti visibili; nessuna verifica elettrica della basetta.
- 18/10/2026: firmware mcp2515-spi-test 0.1.0 caricato su COM3 con BOOT manuale; esptool conferma hash dei segmenti scritti. Sostituisce sulla scheda la diagnostica 0.1.0, i cui sorgenti sono conservati. Avvio verificato tramite stato seriale SPI_TEST=PASS (M-010).

**Da verificare:**

- Piedinatura fisica HW-394 e corrente disponibile per i moduli esterni
- Basetta a morsetti visibile in foto: continuità e corrispondenza delle etichette non ancora provate.

### HW-CAN-MCP2515 — Modulo MCP2515, quarzo 8 MHz, transceiver marcato VP230

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Inventario iniziale fornito dall’utente; successiva correzione “ma non abbiamo già il modulo can?” il 18/10/2026. Il precedente “non possiedo altro” non annulla più questa voce. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json. Utente: retro verniciato di nero, piste non visibili; non è stato richiesto di rimuovere il rivestimento.

**Foto archiviate:** [mcp2515-fronte.jpg](hardware-photos/mcp2515-fronte.jpg), [mcp2515-dettaglio.jpg](hardware-photos/mcp2515-dettaglio.jpg)

**Verifiche documentate:**

- Foto fronte e dettaglio archiviate: MCP2515, quarzo 8.000 e marcatura VP230 leggibili; connettori J1/J3 non ancora identificati elettricamente.
- M-001 / M-002: resistenza H-L riferita 51,8 kOhm e ripetuta dopo controllo C-001 dei puntali (0 riferito). Nessuna conclusione su compatibilità o funzionamento CAN.
- M-003: utente riferisce 119 Ohm direttamente su R2 (marcata 121).
- M-004a/b: utente riferisce circa 52 kOhm da L a ciascuna delle due estremità di R2; non indica un collegamento diretto a bassa resistenza verso L nelle condizioni della prova.
- M-005a/b: H verso R2 lato POW riferito 0 (Ω richiesto), lato J1 120 Ohm; compatibile con collegamento diretto del lato POW a H. A modulo spento H-L resta circa 52 kOhm; circuito e alimentazione non ancora validati.
- M-006: resistenza VCC-GND riferita circa 9 kOhm a modulo spento. Non prova tensione ammissibile o funzionamento.
- M-007: utente riferisce 0 in modalità Ω tra VCC connettore e pin 3 U1 VP230; coerente con alimentazione diretta del transceiver, che da datasheet TI richiede 3,3 V.
- M-008: utente risponde “arriva” alla verifica VCC verso VDD del MCP2515; annotazione qualitativa di continuità, senza resistenza numerica. La compatibilità SPI non è ancora collaudata.
- M-009: utente riferisce 3,3 V tra VCC e GND del modulo alimentato a banco da ESP32; comunicazione SPI e funzionamento CAN non verificati.
- M-010: letto direttamente su COM3 status SPI_TEST=PASS uptime_ms=15545; prova registri SPI a 100 kHz mode 0 con alimentazione 3,3 V M-009. Non è un collaudo CAN o di stabilità prolungata.

**Da verificare:**

- Funzionamento del transceiver, terminazione e comunicazione CAN ancora da collaudare; nessun collegamento auto autorizzato da questo test.
- M-007 indica VCC diretto al VP230: non applicare 5 V. SPI a 3,3 V verificato soltanto a banco, 100 kHz mode 0.
- Funzione dei connettori J1/J3 e circuito di terminazione da ricostruire; nessun nuovo modulo da acquistare prima della valutazione degli esistenti.

### HW-CAN-VP230 — Modulo CAN blu VP230 / SN65HVD230

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Inventario iniziale utente e correzione sul CAN del 18/10/2026. Nessun collaudo del modulo documentato. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json. Valutazione 18/10/2026: https://github.com/0xCAFEDECAF/VanBus sezione Schematics documenta SN65HVD230 come ricevitore fisico VAN; datasheet TI SN65HVD230 descrive RS e driver disabilitabile. Non prova funzionamento del modulo posseduto.

**Foto archiviate:** [can-vp230-fronte.jpg](hardware-photos/can-vp230-fronte.jpg), [can-vp230-dettaglio.jpg](hardware-photos/can-vp230-dettaglio.jpg)

**Verifiche documentate:**

- Foto fronte e dettaglio archiviate: marcatura VP230 e serigrafie 3.3V/GND/RX/TX; resistenza con codice 121 e serigrafia 120R visibili, valore non misurato.

**Da verificare:**

- Alimentazione indicata 3,3 V: da verificare sul modulo
- Resistenza 120 ohm apparentemente fissa: da misurare; non aggiungere terminazione al bus auto senza verifica
- Possibile uso col controller TWAI interno ESP32: scelta subordinata a verifica elettrica
- Candidato per ricezione fisica VAN con decoder software ESP32: applicazione documentata dal progetto VanBus, non collaudata su questo modulo o veicolo. Prima verificare alimentazione 3,3 V, assenza di terminazione aggiunta, livelli e inibizione hardware TX. Non usare il controller MCP2515 come decoder VAN.

### HW-SD-MODULE — Lettore MicroSD SPI 3,3 V — riferimento consigliato Create idea B0DRWPJ1T5

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link precedente; utente conferma “quelli che avevi consigliato tu”, poi “non sono arrivati” il 18/10/2026. Riferimento di acquisto non verificato fisicamente.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Quantità, modello e serigrafie del materiale ricevuto
- Alimentazione, livelli SPI e picchi di corrente

### HW-RTC — RTC DS3231 / AT24C32 — riferimento consigliato TECNOIOT B07LH592FM

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link e conferma ordine in chat; “non sono arrivati” il 18/10/2026. Nessuna batteria confermata.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Modello, quantità, pull-up I2C e circuito di ricarica batteria
- Non inserire una CR2032 non ricaricabile prima di verificare il circuito

### HW-OLED — Display OLED monocromatico I2C consigliato — modello e controller non riscontrati

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Conferma ordine dei componenti consigliati; non è disponibile un riepilogo ordine che identifichi esattamente il display. Non richiedere di nuovo tutti i link già in chat.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Distinguere raccomandazione 1,3 pollici e link 0,96/0,91; non inventare modello definitivo
- Controller, risoluzione, ordine dei pin e compatibilità 3,3 V sul pezzo ricevuto

### HW-SCANNER — Launch Creader 3001

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger — strumento di verifica

**Fonte:** Foto fornite e conferma utente che si tratta della stessa C3 e che dispone ancora del lettore.

**Verifiche documentate:**

- Foto del lettore sulla stessa C3: “Protocol Type CAN”
- 18/10/2026: nuova schermata ECU di altro strumento/app non identificato riporta ISO 14230-4 KWP fast init 10,4 kbaud, calibrazione 9656710099 coincidente con la precedente foto. Indicazione CAN Creader in conflitto e non più base per cablaggio OBD.

**Da verificare:**

- Risolvere differenza tra vecchia indicazione CAN e nuova schermata KWP mediante protocollo effettivamente negoziato e letture correnti; non assumere accesso BSI dalla diagnosi motore.

### HW-SD-CARD — Scheda MicroSD (supporto di memoria, distinta dal lettore)

**Stato:** `not_confirmed` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Nessuna conferma esplicita nel contesto disponibile.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso, capacità e formattazione da confermare prima di ordinare un duplicato

### HW-AUTO-POWER — Alimentazione temporanea proposta: Uadme 5 V, arresto manuale STOP

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Discussione alimentazione dal quadro: possibilità richiesta, non decisione approvata su circuito o pin. 18/10/2026: utente propone Uadme Amazon ASIN B0BFFDSNRC; pagina letta nel browser Work: modello dichiarato GYVRM-K240505, ingresso 8-40 V, uscita 5 +/-0,25 V, 5 A/25 W, non isolato. Specifiche commerciali non collaudate; nessun possesso/ordine confermato. 18/10/2026: proposta LAOMAO MP1584EN Amazon B0B92WYRR4; pagina letta nel browser: confezione 6 moduli, ingresso 4,5-28 V, uscita regolabile 0,8-20 V, 3 A massimi dichiarati. Valutato per banco, non selezionato per ingresso diretto auto; nessun ordine confermato. Utente 18/10/2026 esclude Pololu per costo/spedizione (D-014) e chiede di completare la proposta economica. Scelta tecnica proposta: +12 V permanente e segnale IGN, MOSFET mantenuto da ESP32 per chiusura SD; nessuna riserva autonoma su batteria scollegata. Nuova istruzione utente 18/10/2026 D-015: logger per pochi giorni, STOP manuale prima di spegnere auto; ritirata proposta MOSFET/mantenimento/IGN separato/riserva energetica. Nessun UPS richiesto.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Uadme B0BFFDSNRC: nessun ordine/possesso confermato; verificare uscita 5 V e funzionamento col carico.
- Prelievo alimentazione auto e fusibile di ramo da verificare; non collegare 12 V ai GPIO. Nessun pin auto assegnato.
- Arresto manuale STOP e conferma a display da implementare/collaudare con SD reale. Il pulsante non toglie fisicamente corrente.
- Nessuna garanzia su transitori oltre specifica, cadute in avviamento o spegnimento senza STOP; nessuna qualifica automotive dichiarata.

### HW-OBD-HARNESS — Derivazione dietro la presa OBD

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Preferenza utente: lasciare libera frontalmente la presa OBD; adattatore non identificato né ordinato.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Connettore posteriore C3, accesso fisico, lunghezza derivazione e massa di riferimento
- Identificare controconnettori posteriori della presa per derivazione a T con fronte libero, oppure punto equivalente documentato. Nessun ordine basato sulla sola foto frontale.

### HW-DASH-DISPLAY — Scheda RCmall ESP32-S3 con display 5 pollici — variante da identificare

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Cruscotto futuro

**Fonte:** Osservazioni preliminari nel README originale; non attestano un ordine o un collaudo.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso e modello non confermati per questa fase; non trasferire i dati della variante 1,9 pollici
- PCB, flash, PSRAM, interfaccia display e pinout da verificare

### HW-MULTIMETER — UNI-T UT210E — multimetro / pinza amperometrica

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger — strumento di verifica

**Fonte:** Utente il 18/10/2026: “ho il tester per verificare il modulo con mcp2515”. Foto tester.jpg fornita il 18/10/2026: modello identificato visivamente; lettura M-001 successivamente riferita dall’utente, controllo puntali C-001 successivamente riferito 0, H-L ripetuta con lo stesso valore.

**Foto archiviate:** [tester-unit-ut210e.jpg](hardware-photos/tester-unit-ut210e.jpg)

**Verifiche documentate:**

- Identificazione visiva UNI-T UT210E nella foto tester.jpg, archiviata con SHA-256.
- Contatto diretto tra i puntali: utente riferisce 0 in risposta al controllo C-001 richiesto in modalità Ω.

**Da verificare:**

- Taratura assoluta e stato completo dello strumento non verificati.

### HW-ESP32-TERMINAL-BASE — Basetta di espansione a morsetti per ESP32 HW-394, visibile in foto

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Foto originale PXL_20261017_202948899.jpg già fornita, recuperata dai Download e archiviata il 18/10/2026.

**Foto archiviate:** [esp32-hw394-fronte.jpg](hardware-photos/esp32-hw394-fronte.jpg)

**Verifiche documentate:**

- Presenza visibile nella fotografia esp32-hw394-fronte.jpg

**Da verificare:**

- Continuità tra morsetti e socket, etichette e compatibilità meccanica da verificare

### HW-KLINE-INTERFACE — Interfaccia K-line autocostruita: prototipo banco NPN 2N5551 + LM2903B

**Stato:** `candidate` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Proposta 18/10/2026: https://www.mikroe.com/iso-9141-click e schema ufficiale v101 https://download.mikroe.com/documents/add-on-boards/click/iso_9141_click/iso-9141-click-schematic-v101.pdf. UART, selezione logica 3,3/5 V, VS separata 4,5-36 V. Nessun ordine confermato. Utente: MIKROE-4331 non trovato disponibile il 18/10/2026. Alternative esplorate: interfaccia da assemblare su E-L9637D, oppure Freematics OBD-II UART Adapter V2.1; nessuna alternativa acquistata o confermata. Utente propone circuito discreto con 2 NPN o PC817 e pull-up 510 Ohm/0,5 W: registrato come alternativa non approvata, senza schema completo ne conferma di possesso componenti. Scelta utente 18/10/2026: ok procediamo con il circuito autocostruito (D-013). Progetto locale schema-kline-banco.svg rev A, generatore e calcoli DC in tools/genera-kline-banco.py; nessun risultato sperimentale.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso e ordine dei singoli componenti non confermati; distinta di costruzione in docs/kline-autocostruita.md.
- Verifica montaggio, pin transistor secondo produttore, assenza corti e alimentazioni su banco limitato in corrente; alimentatore banco non confermato.
- Misura statica e temporale RX/TX, eco, livelli 3,3 V, commutazione e margini UART a 10400; nessun firmware K-line caricato.
- Protezioni automotive, corti, transitori, alimentazioni parziali e compatibilita reale con auto da progettare/collaudare. Lo schema rev A e solo da banco.

### HW-STOP-BUTTON — Pulsante STOP momentaneo normalmente aperto

**Stato:** `candidate` · **Quantità:** 1 · **Ambito:** Data Logger temporaneo

**Fonte:** Richiesta esplicita utente 18/10/2026, D-015: pulsante prima di spegnere l’auto.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso/ordine non confermato; GPIO e cablaggio da fissare nel firmware.
- Premuto: bloccare acquisizione, salvare/chiudere SD, confermare sul display; non usarlo per tagliare direttamente alimentazione.

### HW-DASH-HARNESS — Derivazione linea dietro al cruscotto originale

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Utente 18/10/2026, D-016: acquisizione OBD e dalla linea dietro al cruscotto, tutto quello che arriva. Punto di accesso richiesto, non cablaggio collaudato; nessun ordine dichiarato.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Identificare connettore, terminali, pin, protocollo e lunghezza cablaggio della specifica vettura.
- HW-CAN-VP230 presente candidato per ricezione VAN passiva; verificare interfaccia senza aggiungere terminazione.

## Proposta di collegamento — non validata fisicamente

GPIO proposti nel firmware 0.2.0, non cablaggio fisico approvato. GPIO32/33 illustrati per pulsanti eventuali, non inizializzati.

| Funzione firmware | GPIO proposto |
| --- | --- |
| `kSda` | 21 |
| `kScl` | 22 |
| `kSck` | 18 |
| `kMiso` | 19 |
| `kMosi` | 23 |
| `kSdCs` | 27 |

L'illustrazione dei moduli non è la disposizione fisica dei pin.
