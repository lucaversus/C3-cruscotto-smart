# Inventario hardware — Cruscotto C3+AI / Data Logger

Aggiornato: **2026-10-20**. Vista generata da [hardware.json](hardware.json).
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

**Fonte:** Identificazione e collaudo a banco nella chat; data-logger/backups/esp32-hw394/README.md e firmware/diagnostic/README.md. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json. 20/10/2026: collegamento USB confermato dall utente; Windows rileva USB-SERIAL CH340 (COM3), apertura seriale riuscita. Primo upload logger 0.3.0 fallito prima della scrittura: esptool rileva boot mode 0x13 e richiede download mode; preparata ripetizione con BOOT manuale. Nessuna nuova versione dichiarata caricata.

**Foto archiviate:** [esp32-hw394-fronte.jpg](hardware-photos/esp32-hw394-fronte.jpg)

**Verifiche documentate:**

- esptool: ESP32-D0WD-V3 rev. 3.1, flash 4 MB, quarzo 40 MHz
- COM3 CH340; diagnostica 0.1.0 caricata, avvio e oltre 70 s osservati
- Backup flash completo con SHA-256 verificato; ripristino non provato
- Foto frontale archiviata: HW-394 / ESP-32D e basetta di espansione a morsetti visibili; nessuna verifica elettrica della basetta.
- 18/10/2026: firmware mcp2515-spi-test 0.1.0 caricato su COM3 con BOOT manuale; esptool conferma hash dei segmenti scritti. Sostituisce sulla scheda la diagnostica 0.1.0, i cui sorgenti sono conservati. Avvio verificato tramite stato seriale SPI_TEST=PASS (M-010).
- 20/10/2026: logger 0.3.0 profilo esp32-hw394-logger caricato su COM3 con BOOT manuale a 115200 baud; esptool conferma hash dei segmenti, SUCCESS. Dopo impulso EN tramite RTS, seriale conferma version=0.3.0, kwp=0 van=0 e ATTESA SD. Log locali .tools/serial/upload-20261020-000840.log e monitor successivo. Sostituisce il test MCP2515 sulla scheda; sorgenti storici conservati.

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
- VAN-M002 23/10/2026: prova 1 D-022 superata, resistenza 121 rimossa, H-L a modulo spento 73 kohm (non 120 ohm).
- VAN-M003 23/10/2026: prova 2 D-022 superata, continuità TX-3V3 a modulo spento.
- VAN-M004 23/10/2026: prova 3 D-022 superata, H-L 45 mV con modulo alimentato a 3,3 V dall'ESP32 (stato recessivo).

**Da verificare:**

- Alimentazione indicata 3,3 V: da verificare sul modulo
- Possibile uso col controller TWAI interno ESP32: scelta subordinata a verifica elettrica
- Candidato per ricezione fisica VAN con decoder software ESP32: applicazione documentata dal progetto VanBus, non collaudata su questo modulo o veicolo. Prima verificare alimentazione 3,3 V, assenza di terminazione aggiunta, livelli e inibizione hardware TX. Non usare il controller MCP2515 come decoder VAN.
- BLOCCANTE prima del collegamento VAN (D-022): modifiche dichiarate eseguite dall'utente il 23/10/2026 (resistenza 121 dissaldata, TX collegato a 3V3, VAN-M001); H-L 73 kohm misurato (VAN-M002, prova 1 superata); continuità TX-3V3 verificata (VAN-M003, prova 2 superata); H-L recessivo 45 mV (VAN-M004, prova 3 superata); da misurare: livello RX a 3,3 V. Procedura in docs/protocolli-veicolo.md.
- Disegnato nella tavola C3AI-DL-EL-004 rev A (D-042): RX→GPIO34 (W28), 3V3/GND dalla basetta 3 (W29/W30), ponticello TX–3V3, resistenza 121 da scollegare, CANH/CANL verso -X3 e quadro 0004 vie 1/3 solo dopo le verifiche D-022 1-5. Ordine DATA/DATAB non verificato.

### HW-SD-MODULE — Lettore MicroSD SPI 3,3 V — riferimento consigliato Create idea B0DRWPJ1T5

**Stato:** `present_declared` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link precedente; utente conferma “quelli che avevi consigliato tu”, poi “non sono arrivati” il 18/10/2026. Riferimento di acquisto non verificato fisicamente. Utente 19/10/2026: modulo arrivato. Consegna dichiarata; modello fisico, quantita e collaudi ancora da riscontrare. Foto utente PXL_20261019_210229701.jpg del 19/10/2026, archiviata e collegata con SHA-256; identificazione visiva, nessun collaudo. Utente 20/10/2026: modulo non collegato, pin ancora da saldare; saldatore non disponibile sul posto.

**Foto archiviate:** [sd-oled-rtc-arrivo.jpg](hardware-photos/sd-oled-rtc-arrivo.jpg)

**Verifiche documentate:**

- Foto del pezzo: contatti serigrafati 3V3, CS, MOSI, CLK, MISO, GND; presenza scheda MicroSD inserita. Alimentazione e SPI non misurate.
- SD-M001, 19/10/2026: utente riferisce 3 MOhm in risposta alla misura richiesta fra 3V3 e GND del lettore scollegato. Rimozione della scheda e condizioni effettive non confermate separatamente. Non prova tensione ammissibile, SPI o funzionamento SD.

**Da verificare:**

- Quantità, modello e serigrafie del materiale ricevuto
- Alimentazione, livelli SPI e picchi di corrente
- SD-M002, 20/10/2026: utente dichiara il modulo sistemato (strip pin); continuita, ponti di stagno, cablaggio EL-003 W1-W6 e prova di scrittura ancora da verificare.
- Prove a banco P-001 (interruzione senza STOP, 20-30 volte) e P-002 (calo tensione da avviamento) prima dell'auto, D-022; procedura in docs/alimentazione-spegnimento.md. Frequenza SPI oltre 1 MHz non collaudata.

### HW-RTC — RTC DS3231SN con AT24C32 e portabatteria sul retro da verificare

**Stato:** `present_declared` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link e conferma ordine in chat; “non sono arrivati” il 18/10/2026. Nessuna batteria confermata. Foto utente PXL_20261019_210229701.jpg del 19/10/2026, archiviata e collegata con SHA-256; identificazione visiva, nessun collaudo. Risolta la voce temporanea HW-BATTERY-MODULE-UNIDENTIFIED: coincide con HW-RTC. Utente 19/10/2026: sul retro nessuna scritta, visibile soltanto il portabatteria. Verifica ricarica ancora aperta; non richiedere altra foto del retro per cercare scritte assenti. Utente 19/10/2026 identifica la pila come CR2032, confermando prefisso CR dopo 2032. Utente 19/10/2026 sceglie rimozione della resistenza marcata 201 per evitare ricarica CR2032 (D-019). Dichiarazione al futuro: non ancora eseguita o collaudata. Utente 20/10/2026: riferisce collegato tutto il banco tranne SD. Dichiarazione di montaggio, nessuna prova funzionale o conferma della modifica RTC 201.

**Foto archiviate:** [sd-oled-rtc-arrivo.jpg](hardware-photos/sd-oled-rtc-arrivo.jpg)

**Verifiche documentate:**

- Foto: marcatura DS3231SN e serigrafie DS3231; connettori GND/VCC/SDA/SCL/SQW/32K. Il modulo chiamato batteria e questo RTC, non un UPS.
- RTC-M001, 19/10/2026: utente riferisce OL dopo richiesta prova diodi, rosso VCC e nero contatto positivo portabatteria, modulo scollegato e pila rimossa. Identificazione del contatto positivo e condizioni effettive non confermate separatamente; nessuna conclusione su assenza di ricarica.
- RTC-M002, 19/10/2026: utente riferisce OL anche invertendo i puntali sugli stessi due contatti. Non e ancora identificato con certezza il polo del portabatteria misurato: i due OL non dimostrano assenza di ricarica.
- RTC-M003, 19/10/2026: utente riferisce 0 alla misura richiesta in ohm fra GND modulo e contatto centrale sul fondo del portabatteria vuoto. Coerente con contatto centrale negativo collegato a massa; precedenti OL non utilizzabili per escludere ricarica.
- RTC-M004, 19/10/2026: dopo identificazione centrale negativo tramite RTC-M003, utente riferisce 1,35 V in prova diodi, rosso VCC e nero altro contatto superiore/laterale positivo, modulo scollegato e pila rimossa come richiesto. Esiste un percorso conduttivo in questa polarita; ricarica non esclusa. Non e una misura della tensione o corrente di carica in funzionamento.
- RTC-M005, 19/10/2026: utente riferisce OL nel verso inverso sul contatto positivo corretto (rosso positivo portabatteria, nero VCC). Insieme a RTC-M004 1,35 V diretto indica percorso unidirezionale compatibile con ramo di ricarica; nessuna misura di corrente o tensione di carica a modulo alimentato.
- 20/10/2026: logger 0.3.0 legge DS3231 via I2C e riferisce rtc=oscillator_stop. Raggiungibilita registri verificata, ora non valida; mantenimento, pila e interruzione ricarica ancora non collaudati.
- RTC-M007, 20/10/2026: dopo rimozione resistenza 201 (RTC-M006, D-019) utente riferisce OL in prova diodi rosso VCC, nero positivo portabatteria, modulo scollegato e pila fuori; prima 1,35 V (RTC-M004). Ramo di ricarica interrotto. Mantenimento ora non ancora provato.

**Da verificare:**

- Modello, quantità e pull-up I2C (circuito di ricarica risolto con D-019, RTC-M007)
- D-019 eseguita e ramo interrotto (RTC-M007). Da verificare: mantenimento dell ora con pila dopo impostazione UTC e spegnimento.

### HW-OLED — Display OLED monocromatico I2C consigliato — modello e controller non riscontrati

**Stato:** `present_declared` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Conferma ordine dei componenti consigliati; non è disponibile un riepilogo ordine che identifichi esattamente il display. Non richiedere di nuovo tutti i link già in chat. Utente 19/10/2026: modulo arrivato. Consegna dichiarata; modello fisico, quantita e collaudi ancora da riscontrare. Foto utente PXL_20261019_210229701.jpg del 19/10/2026, archiviata e collegata con SHA-256; identificazione visiva, nessun collaudo. Utente 20/10/2026: riferisce collegato tutto il banco tranne SD. Dichiarazione di montaggio, nessuna prova funzionale o conferma della modifica RTC 201.

**Foto archiviate:** [sd-oled-rtc-arrivo.jpg](hardware-photos/sd-oled-rtc-arrivo.jpg)

**Verifiche documentate:**

- Foto del pezzo: scheda nera, quattro contatti GND VCC SCL SDA; controller, risoluzione e tensioni non ancora verificati.

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

**Stato:** `present_declared` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Nessuna conferma esplicita nel contesto disponibile. Foto utente PXL_20261019_210229701.jpg del 19/10/2026, archiviata e collegata con SHA-256; identificazione visiva, nessun collaudo.

**Foto archiviate:** [sd-oled-rtc-arrivo.jpg](hardware-photos/sd-oled-rtc-arrivo.jpg)

**Verifiche documentate:**

- Scheda MicroSD presente e inserita nel lettore nella foto; marca Samsung visibile. Capacita nominale/effettiva, formato e contenuto ancora da riscontrare.

**Da verificare:**

- Capacita, formato e contenuti da riscontrare prima di scrivere; nessuna formattazione o cancellazione senza autorizzazione.

### HW-AUTO-POWER — Alimentazione temporanea proposta: Uadme 5 V, arresto manuale STOP

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Discussione alimentazione dal quadro: possibilità richiesta, non decisione approvata su circuito o pin. 18/10/2026: utente propone Uadme Amazon ASIN B0BFFDSNRC; pagina letta nel browser Work: modello dichiarato GYVRM-K240505, ingresso 8-40 V, uscita 5 +/-0,25 V, 5 A/25 W, non isolato. Specifiche commerciali non collaudate; nessun possesso/ordine confermato. 18/10/2026: proposta LAOMAO MP1584EN Amazon B0B92WYRR4; pagina letta nel browser: confezione 6 moduli, ingresso 4,5-28 V, uscita regolabile 0,8-20 V, 3 A massimi dichiarati. Valutato per banco, non selezionato per ingresso diretto auto; nessun ordine confermato. Utente 18/10/2026 esclude Pololu per costo/spedizione (D-014) e chiede di completare la proposta economica. Scelta tecnica proposta: +12 V permanente e segnale IGN, MOSFET mantenuto da ESP32 per chiusura SD; nessuna riserva autonoma su batteria scollegata. Nuova istruzione utente 18/10/2026 D-015: logger per pochi giorni, STOP manuale prima di spegnere auto; ritirata proposta MOSFET/mantenimento/IGN separato/riserva energetica. Nessun UPS richiesto.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Uadme B0BFFDSNRC: nessun ordine/possesso confermato; verificare uscita 5 V e funzionamento col carico.
- Prelievo alimentazione auto e fusibile di ramo da verificare; non collegare 12 V ai GPIO. Punto candidato da manuale: presa OBD via 16/1 (D-030), non ancora misurato.
- Arresto manuale STOP e conferma a display da implementare/collaudare con SD reale. Il pulsante non toglie fisicamente corrente.
- Nessuna garanzia su transitori oltre specifica, cadute in avviamento o spegnimento senza STOP; nessuna qualifica automotive dichiarata.

### HW-OBD-HARNESS — Derivazione dietro la presa OBD

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Preferenza utente: lasciare libera frontalmente la presa OBD; adattatore non identificato né ordinato.

**Verifiche documentate:**

- OBD-M001, 21/10/2026: via 16 = + batteria permanente (12,2 V chiave tolta, 12,2 V su marcia, 14,2 V motore acceso, minimo 9,0 V in avviamento letto dal tester); via 1 = + dopo contatto (0 V / 12,2 V); vie 4 e 5 a massa. Presa montata ruotata di 180° rispetto alla vista del foglio C3AI-CR-PR-001; numerazione stampata coerente.

**Da verificare:**

- Vie 16/1/4/5 confermate (OBD-M001); via 7 linea K non misurata. Derivazione posteriore da progettare tenendo conto della presa ruotata di 180°.
- Connettore posteriore C3, accesso fisico, lunghezza derivazione e massa di riferimento
- Identificare controconnettori posteriori della presa per derivazione a T con fronte libero, oppure punto equivalente documentato. Nessun ordine basato sulla sola foto frontale.

### HW-DASH-DISPLAY — Scheda RCmall ESP32-S3 con display 5 pollici — PCB serigrafato ESP32-8048S050

**Stato:** `present_verified` · **Quantità:** non confermata · **Ambito:** Cruscotto digitale

**Fonte:** Osservazioni preliminari nel README originale. Utente 20/10/2026: alla domanda sul possesso risponde "Ce l'ho" (D-026). Possesso dichiarato. Foto retro e fronte fornite in chat il 20/10/2026, archiviate senza metadati; nessun collaudo. Chip, flash e PSRAM letti con esptool il 20/10/2026.

**Foto archiviate:** [dash-display-retro.jpg](hardware-photos/dash-display-retro.jpg), [dash-display-fronte.jpg](hardware-photos/dash-display-fronte.jpg)

**Verifiche documentate:**

- Foto retro e fronte del 20/10/2026 archiviate con SHA-256: serigrafia PCB ESP32-8048S050 leggibile; modulo Espressif ESP32-S3-WROOM-1 probabile, sigla di memoria (es. N16R8) non leggibile alla risoluzione disponibile.
- Utente 20/10/2026: sul coperchio metallico del modulo è scritto "esp32-s3-wroom-1". Modulo identificato per lettura dichiarata; sigla di memoria (flash/PSRAM) non riferita.
- Visibili sul retro: slot MicroSD, USB-C, due pulsanti, cavo flat verso il pannello e connettori serigrafati SPI (IO10/IO11/IO12/IO13 da confermare), UART1 IO17/IO18, USB IO19/IO20, due connettori GND/3.3V/IO17/IO18 e uscita Speak. Identificazione visiva, nessuna misura.
- 20/10/2026: esptool 4.9.0 flash_id in sola lettura su COM4 (USB-SERIAL CH340, reset automatico DTR/RTS): ESP32-S3 (QFN56) rev v0.2, WiFi/BLE, Embedded PSRAM 8MB (AP_3v3), quarzo 40 MHz; flash produttore 0xc8 device 0x4018, 16 MB rilevati, quad da eFuse, 3,3 V. Coerente con WROOM-1 N16R8. Nessuna scrittura; log locale .tools/serial/dash-flash-id-20261020.log (MAC non pubblicato).
- 20/10/2026: backup completo flash 16 MB con esptool read_flash a 921600 baud su COM4 (216,3 s), SHA-256 90bdef73…c03b; nessuna scrittura. Dettagli in data-logger/backups/esp32-8048s050/README.md. Ripristino non provato.
- 20/10/2026: all'accensione il firmware di fabbrica mostra la LVGL Widgets Demo (stringhe nel backup: LVGL v8, Arduino-ESP32 / ESP-IDF v4.4.3, compilato 20/12/2022). Utente riferisce immagine visibile sul display: pannello e retroilluminazione funzionanti con il firmware di fabbrica.
- Utente 20/10/2026: variante ordinata senza touch, lo schermo non è touch (D-027). Probabile sigla commerciale ESP32-8048S050N, non riscontrata su etichetta.
- DSP-M001, 20/10/2026: firmware display-test 0.1.0 caricato (COM4, hash verificati); seriale psram_found=1, 8386215 byte, panel=ESP_OK, nessun dispositivo I2C su GPIO19/20; utente riferisce barre colore 'tutto conforme'. Pinout RGB, temporizzazioni 16 MHz, ordine colori, retroilluminazione GPIO2 e PSRAM octal verificati per questa scheda. Sostituisce sulla scheda il firmware di fabbrica (backup conservato).
- DSP-M002, 20/10/2026: ui-test LVGL 0.1.0 caricato; seriale fps=32 (limitato dai dati simulati a 33 ms), rendering medio 11 ms, 230 KB SRAM e 7,6 MB PSRAM liberi; utente: arco abbastanza fluido, cifre giri con lieve sfarfallio, indicatore LVGL 62 FPS / 34% CPU.
- DSP-M003, 20/10/2026: ui-test 0.1.1 con cifre in celle fisse; rendering medio 8 ms; utente riferisce numeri senza sfarfallio. Causa DSP-M002 risolta; tearing non visibile in questa prova, non escluso con schermate più pesanti.
- Utente 20/10/2026, connettori serigrafati (coerenti con foto retro): pulsanti BOOT/RST sotto il modulo, FPC1 accanto (probabile flat touch, non usato su variante senza touch), slot MicroSD; P2 'SPI' IO19(?)-11-12-13 (lettura IO19 da confermare, la fonte comunitaria indica IO10 come CS della MicroSD); P3 IO17-18 'UART1' + IO19-20 'USB'; P4 GND-3.3V-IO17-18; P5 come P4 con JST a passo minore; P6 'Speak'; P1 5V-TXD-RXD-GND sopra la USB-C. Dichiarazione e foto, nessuna misura.
- Utente 20/10/2026, ispezione visiva piste: i due contatti di P6 'Speak' entrano in U1, marcatura riferita 'AKK 7HG' (componente non identificato); da U1 piste verso IO17 e IO18. Utente: P2 serigrafato IO19-11-12-13. Nessuna misura.
- DSP-M004, 20/10/2026: continuità tra pin 'IO19' di P2 e IO19 di P3 a scheda scollegata (utente). P2 espone IO19, IO11, IO12, IO13; CS MicroSD non su P2.
- DSP-M007/M008, 21/10/2026: ESP-IDF 5.5, doppio framebuffer con scambio al vsync; frequenza del pannello misurata 39 Hz (PCLK 16 MHz); ui-idf 0.2.1 in direct mode: fluido, nessun artefatto riferito dall'utente, 26 FPS dati / 34-45 FPS indicatore LVGL.

**Da verificare:**

- Firmware attualmente caricato (23/10/2026): ui-idf 0.5.0 (ESP-IDF 5.5, OTA D-039, collegamento simulato, scatola nera DSP-M010, pagina 1 Dashboard DSP-M011; partizione storage LittleFS quasi piena di eventi di prova); altri firmware ricaricabili dai sorgenti.
- Revisione PCB ed etichetta sul fronte del pannello non leggibili nelle foto disponibili
- Luminosità PWM GPIO2, stabilità prolungata e comportamento termico da verificare; frequenza pannello stimata 39 Hz con PCLK 16 MHz (calcolo); tearing con schermate pesanti da valutare
- Quantità non dichiarata; backup eseguito, NVS vuota e nessun dato personale (README backup)
- Variante senza touch: nessun dispositivo I2C su GPIO19/20 (DSP-M001); assenza fisica del GT911 non ispezionata. GPIO19/20 riusabili solo dopo nuova decisione.
- U1 ('AKK 7HG') collegato a P6 e, da ispezione visiva, a IO17/IO18: conflitto con la K-line proposta su IO17/IO18. Confermare funzione di U1 con tono di prova. P1 TXD/RXD presumibilmente UART0 (GPIO43/44) condiviso con il CH340.
- Limiti termici dichiarati dal rivenditore Spotpear per ESP32-8048S050N/C (https://spotpear.com/index.php/index/product/detail/id/1426.html, letto 21/10/2026): funzionamento −20…+70 °C, magazzinaggio −30…+80 °C, assorbimento 320 mA a 5 V (non precisato se con retroilluminazione). Dato commerciale, nessun datasheet del pannello trovato; temperatura reale dietro la copertura del quadro da misurare (auto al sole, ferma e in marcia).

### HW-IMU-LSM6DSO — ST STEVAL-MKI196V1: adattatore DIL-24 con IMU LSM6DSO (accelerometro + giroscopio 6 assi)

**Stato:** `ordered_pending` · **Quantità:** 1 · **Ambito:** Data Logger e Cruscotto digitale (front-end, D-029, D-033)

**Fonte:** Utente 22/10/2026: "ST STEVAL-MKI196V1 ho preso questo" (Farnell Italia, codice 2987032, 15,36 € IVA esclusa, 4 disponibili al 22/10/2026). Ordine dichiarato, consegna non riscontrata. Sostituisce HW-IMU-LSM6DS3 (Seeed Grove LSM6DS3, candidato mai ordinato) e la prima scelta BMI270 (ordine annullato dal venditore). Storia: Utente 20/10/2026: richiesta sensore giroscopio e accelerazione. Prima scelta BMI270 (AliExpress 1005010561882473, voce HW-IMU-BMI270): ordine annullato perché il venditore non spedisce nella zona. Utente: "sostituiscilo con questo", link Reichelt LSM6DS3 Grove. Dati prodotto letti dalla pagina Reichelt il 20/10/2026.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- All'arrivo: riscontrare sigla STEVAL-MKI196V1 e marcatura del chip; foto da archiviare.
- Piedinatura DIL-24 ricavata da ST DB3714 rev 1 (schema STEVAL-MKI196V1, 22/10/2026): 1 VDD, 2 VDDIO, 3 OCS, 4 SCx, 5 SDx, 6 OSDO, 13 GND, 14 INT1, 15 INT2, 19 CS, 20 SCL, 21 SDA, 22 SDO/SA0; 7-12 e 23 liberi, 16-18 e 24 con resistenze non montate. Condensatori 100 nF su VDD e VDDIO presenti, nessuna pull-up I2C sulla scheda. Da riscontrare sulla serigrafia all'arrivo. Alimentazione 1,71-3,6 V: solo 3,3 V.
- Indirizzo I2C 0x6A con SDO/SA0 (piedino 22) a GND; CS (19) a 3,3 V per il modo I2C. SCx/SDx (4/5) a GND in modo 1 secondo ST (riscontrare sulla tabella dei piedini del datasheet LSM6DSO), OCS e OSDO liberi. Pull-up SDA/SCL: verificare quelle del modulo RTC, altrimenti 4,7 kohm verso 3,3 V. Nessun conflitto atteso con RTC 0x68, EEPROM 0x57, OLED 0x3C.
- Collegamento proposto: bus I2C HW-394 GPIO21/22 su ritaglio di millefori (basetta 4, tavola C3AI-DL-EL-004 rev A, D-042), non verificato. Fissaggio rigido e orientamento assi da definire; stesso sensore e montaggio tra raccolta dati e cruscotto (D-033).
- Temperatura di esercizio del chip -40...+85 °C: per la scheda madre definitiva valutare la famiglia industriale ISM330 (-40...+105 °C), con lo stesso chip anche nel logger (D-033).

### HW-AUDIO-SPK-TEST — Altoparlante miniatura di prova Multicomp Pro ABS-216-RC (8 Ω, 2 W, 200 Hz-20 kHz, 40×20 mm)

**Stato:** `ordered_pending` · **Quantità:** 1 · **Ambito:** Cruscotto digitale: prova a banco dell'uscita audio P6 dell'S3 (DSP-M005/M006, D-028)

**Fonte:** Utente 22/10/2026: "1504105 preso" (Farnell Italia, codice 1504105, 3,64 € IVA esclusa, scelto dalla ricerca del 22/10/2026). Ordine dichiarato, consegna non riscontrata.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- All'arrivo: riscontrare sigla e impedenza (circa 8 Ω misurati al tester, valore in continua leggermente inferiore).
- Senza cavetti: saldare due fili o usare coccodrilli; collegarlo solo a P6 Speak con firmware speak-test caricato.
- Prova da fare: tono 200 Hz di speak-test 0.1.1 per chiarire la funzione di U1 "AKK 7HG" (amplificatore o altro), prima di definire amplificatore e relè D-028.
- Solo banco: non è l'altoparlante del veicolo; relè e amplificatore D-028 ancora da definire.

### HW-FE-MODULE — Modulo ESP32-WROOM-32E-H4/H8 per il front-end, montato in fabbrica sulla scheda madre (D-029)

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Cruscotto digitale (scheda madre)

**Fonte:** Ricerca 20/10/2026: Reichelt offre ESP32WROOM32E (N4, 3,70 €), ESP32WROOM32E8 (8 MB, 4,18 €) ed ESP32WROOM32E16 (N16, 4,43 €), tutte −40…+85 °C; variante H non disponibile (utente: "non la trovo la h8 nel sito"). H4 presente nel catalogo componenti JLCPCB (C3013935) per montaggio in fabbrica. Utente 20/10/2026: "ok la faremo montare sulla mainboard": nessun acquisto separato del modulo.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Variante H4 o H8 (−40…+105 °C, senza PSRAM) da far montare dal produttore della scheda madre (utente 20/10/2026: "la faremo montare sulla mainboard"); varianti R2 escluse (PSRAM su GPIO16/17).
- Temperatura reale dietro il quadro da misurare prima della versione definitiva.
- Nessun acquisto deciso: prototipo con HW-ESP32 (HW-394).

### HW-MULTIMETER — UNI-T UT210E — multimetro / pinza amperometrica

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger — strumento di verifica

**Fonte:** Utente il 18/10/2026: “ho il tester per verificare il modulo con mcp2515”. Foto tester.jpg fornita il 18/10/2026: modello identificato visivamente; lettura M-001 successivamente riferita dall’utente, controllo puntali C-001 successivamente riferito 0, H-L ripetuta con lo stesso valore.

**Foto archiviate:** [tester-unit-ut210e.jpg](hardware-photos/tester-unit-ut210e.jpg)

**Verifiche documentate:**

- Identificazione visiva UNI-T UT210E nella foto tester.jpg, archiviata con SHA-256.
- Contatto diretto tra i puntali: utente riferisce 0 in risposta al controllo C-001 richiesto in modalità Ω.

**Da verificare:**

- Taratura assoluta e stato completo dello strumento non verificati.

### HW-BENCH-PSU — Alimentatore da banco (modello da riscontrare)

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger — strumento di verifica

**Fonte:** Utente 22/10/2026: "l'alimentatore da banco ce l'ho". Dichiarazione, nessuna foto o misura.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Modello, campo di tensione e limitazione di corrente da riscontrare: per KL-001 servono 9-16 V stabilizzati con limite di corrente (VBENCH).
- Utilizzabile anche per le prove P-001/P-002 del logger (alimentazione-spegnimento.md), se il campo lo consente.

### HW-ESP32-TERMINAL-BASE — Basetta di espansione a morsetti per ESP32 HW-394, visibile in foto

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Foto originale PXL_20261017_202948899.jpg già fornita, recuperata dai Download e archiviata il 18/10/2026.

**Foto archiviate:** [esp32-hw394-fronte.jpg](hardware-photos/esp32-hw394-fronte.jpg)

**Verifiche documentate:**

- Presenza visibile nella fotografia esp32-hw394-fronte.jpg

**Da verificare:**

- Continuità tra morsetti e socket, etichette e compatibilità meccanica da verificare

### HW-KLINE-INTERFACE — Interfaccia K-line autocostruita: prototipo banco NPN 2N5551 + LM2903B

**Stato:** `ordered_pending` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Utente 22/10/2026: carrello Farnell ShopCart.csv allegato e "ordine effettuato"; "per fare il circuito di prova faccio i collegamenti volanti", "la millefori la uso come base". Storia: Proposta 18/10/2026: https://www.mikroe.com/iso-9141-click e schema ufficiale v101 https://download.mikroe.com/documents/add-on-boards/click/iso_9141_click/iso-9141-click-schematic-v101.pdf. UART, selezione logica 3,3/5 V, VS separata 4,5-36 V. Nessun ordine confermato. Utente: MIKROE-4331 non trovato disponibile il 18/10/2026. Alternative esplorate: interfaccia da assemblare su E-L9637D, oppure Freematics OBD-II UART Adapter V2.1; nessuna alternativa acquistata o confermata. Utente propone circuito discreto con 2 NPN o PC817 e pull-up 510 Ohm/0,5 W: registrato come alternativa non approvata, senza schema completo ne conferma di possesso componenti. Scelta utente 18/10/2026: ok procediamo con il circuito autocostruito (D-013). Progetto locale schema-kline-banco.svg rev A, generatore e calcoli DC in tools/genera-kline-banco.py; nessun risultato sperimentale. Revisione B 18/10/2026: schema completo U1 e distinta sul foglio; pinout TI SLCS005AH sezione 4. Corretto contenitore LM2903B: SOIC-8 con adattatore DIP-8, non PDIP-8. Nessun acquisto o collaudo aggiuntivo. Revisione C, D-018: eliminato JP1; R3 510 ohm solo nel simulatore esterno da banco, non nel modulo. Nessun nuovo acquisto o collaudo. Revisione D: evidenziate porte TX ingresso, RX uscita e K-line bidirezionale; nessuna variazione elettrica. Revisione E 20/10/2026, D-022: R10 330 kohm 1% da OUT1 a IN1+ per isteresi 0,545-0,721 V sulla linea K (modello DC); possesso di R10 non confermato, nessun collaudo. Revisione F 20/10/2026, D-024: ridisegno IEC 60617 / IEC 61082-1 su foglio ISO, nessuna variazione elettrica. Utente 22/10/2026: "sto acquistando i pezzi per fare questo circuito"; saldatura disponibile in azienda ("il saldatore [...] quello in azienda al lavoro"). Acquisto in corso, componenti non ancora ricevuti.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Ordine Farnell 22/10/2026 (dichiarato, consegna non riscontrata): 2× LM2903BYDT (SOIC-8, versione B), 5× 2N5551BU onsemi, resistenze R1…R10 (330 Ω, 47 kΩ, 510 Ω 1 W 5 %, 68 kΩ, 10 kΩ 0,5 %, 150 kΩ, 4,7 kΩ, 1 kΩ, 330 kΩ), C1 100 nF e C2 10 µF, millefori MC01009 72×47 mm come base. All'arrivo riscontrare valori e sigle.
- Condensatori: nel carrello allegato erano SMD (KEMET 0603 100 nF, Panasonic EEEHB1C100R 10 µF); consigliata sostituzione con THT 1216438 e 8766754, versione effettivamente ordinata da riscontrare all'arrivo.
- Montaggio scelto dall'utente: collegamenti volanti sulla millefori, senza zoccolo, adattatore SOIC-8→DIP-8 né morsettiere (KL-003 resta riferimento per un montaggio successivo). Fili sottili saldati direttamente ai piedini SOIC (passo 1,27 mm): controllare al tester assenza di ponti prima di alimentare; fissare meccanicamente chip e fili.
- Verifica montaggio, pin E-B-C del 2N5551 onsemi sul datasheet, assenza corti e alimentazioni su banco limitato in corrente (HW-BENCH-PSU dichiarato).
- Misura statica e temporale RX/TX, eco, livelli 3,3 V, commutazione e margini UART a 10400; nessun firmware K-line caricato.
- Protezioni automotive, corti, transitori, alimentazioni parziali e compatibilita reale con auto da progettare/collaudare. Lo schema rev F e solo da banco.

### HW-J1-MICROFIT24 — Connettore verso l'auto -J1: Molex Micro-Fit 3.0 24 vie (femmina 43025-2400 sul cablaggio, spina 43020-2400 sul prototipo)

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger e Cruscotto digitale (D-044)

**Fonte:** Decisione D-044 dell'utente, 23/10/2026. Nessun ordine: componente candidato.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Da ordinare: femmina 43025-2400 (Farnell 629315, minimo 10 pezzi, 1,18 € cad. IVA esclusa), spina 43020-2400 (Farnell 634712, 1,78 €), contatti femmina 43030-0007 (Farnell 2101869, da 10 pezzi, 0,174 €), contatti maschio 43031-0007 (Farnell 2725169, 0,183 €); prezzi e disponibilità del 23/10/2026. Filo 20-24 AWG.
- Servono almeno due femmine: una per il cablaggio dell'auto, una per il cablaggio di prova a banco (R3 e alimentatore).
- Pinza a crimpare compatibile Micro-Fit da scegliere (quella originale Molex è costosa): verificare la tenuta di ogni crimpatura.
- Assegnazione delle vie: bozza in cruscotto/docs/scheda-madre.md (1 +BAT, 2 massa, 3 +APC, 4 K, 5/6 VAN, 7 massa VAN, 8-15 audio, 16-24 riserva).
- Scheda definitiva: connettore da circuito stampato 43045-2400 da prevedere nel disegno della scheda madre.

### HW-STOP-BUTTON — Pulsante STOP momentaneo normalmente aperto

**Stato:** `candidate` · **Quantità:** 1 · **Ambito:** Data Logger temporaneo

**Fonte:** Richiesta esplicita utente 18/10/2026, D-015: pulsante prima di spegnere l’auto.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso/ordine non confermato; firmware 0.3.0 propone GPIO32 verso GND con pull-up interna, cablaggio e funzionamento ancora da provare.
- Premuto: bloccare acquisizione, salvare/chiudere SD, confermare sul display; non usarlo per tagliare direttamente alimentazione.

### HW-LOGGER-SWITCH — Interruttore generale del logger sul + 12 V (dopo il fusibile, prima del convertitore)

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Utente 23/10/2026: "aggiungere un interruttore per spegnere il modulo k una volta nell'auto"; alla domanda su cosa debba spegnere: "Spegnere tutto il logger". Proposta in data-logger/docs/alimentazione-spegnimento.md.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Modello da scegliere: unipolare, 12 V cc, almeno 2 A, posizione OFF riconoscibile, montaggio sul contenitore.
- Uso solo dopo STOP e "SD CHIUSA": nessuna protezione del file se si toglie corrente durante la scrittura (P-001/P-002, D-022).
- Evoluzione da valutare: interruttore letto dal firmware con circuito di mantenimento (GPIO13, D-029).

### HW-DASH-HARNESS — Cablaggio temporaneo con fili volanti dietro al cruscotto

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Utente 18/10/2026, D-016: acquisizione OBD e dalla linea dietro al cruscotto, tutto quello che arriva. Punto di accesso richiesto, non cablaggio collaudato; nessun ordine dichiarato. Utente 18/10/2026 D-017: nessun connettore dedicato, fili volanti.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Identificare segnali, pin, protocollo e lunghezza cablaggio; fili fissati e isolati, nessun acquisto di connettore quadro richiesto.
- HW-CAN-VP230 presente candidato per ricezione VAN passiva; verificare interfaccia senza aggiungere terminazione.

### HW-FUSE-TAP — Gebildet B078T6NLTP, derivatore fusibile standard ATC proposto

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link utente 18/10/2026 https://www.amazon.it/dp/B078T6NLTP. Pagina Amazon non accessibile al lettore web; identificazione commerciale incrociata con schede distributori: https://www.manomano.fr/p/4pcs-12v-24v-20a-standard-atc-add-a-circuit-car-fuse-holder-atc-fuse-holder-blade-adapter-with-6pcs-blade-fuse-and-1pc-puller-236987415 e https://www.ebay.it/itm/287197489185. Indicano derivatore add-a-circuit standard ATC, non portafusibile in linea. Nessun ordine confermato.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Formato del fusibile, spazio e circuito di prelievo sulla specifica auto non verificati: non selezionato per acquisto.
- Non confondere con portafusibile in linea richiesto dalla distinta; valore fusibile di ramo da fissare secondo carico/cablaggio.

### HW-FUSE-HOLDER — Portafusibile acquistato, modello da riscontrare

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Utente 18/10/2026: ok portafusibile preso. Acquisto confermato; consegna, quantita e riferimento esatto non specificati. Non attribuire automaticamente l acquisto al derivatore Gebildet precedentemente proposto.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Riscontrare tipo e modello sul pezzo ricevuto; non proporre altro portafusibile prima del riscontro.
- Fusibile da 2 A previsto per ramo 12 V prima del convertitore; acquisto non confermato, valore da verificare con cavi e assorbimento reali.

### HW-RTC-BATTERY — Pila CR2032 non ricaricabile per RTC — da procurare

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Utente 19/10/2026 risponde 2032 e poi cr alla richiesta della sigla della pila. Quantita e tensione effettiva non misurate. Utente 20/10/2026: "la pila non ce l'ho". La risposta del 19/10/2026 indicava il tipo di pila richiesto dal portabatteria, non il possesso: stato corretto da present_declared a candidate (da procurare).

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Da procurare: una CR2032 (3 V, non ricaricabile). Inserimento consentito dal 20/10/2026: ramo di ricarica interrotto (RTC-M007).
- Prima dell inserimento misurare la tensione (attesi circa 3 V; sotto 2,7 V scarica).

## Proposta di collegamento — non validata fisicamente

GPIO firmware 0.3.0 proposti, non cablaggio fisico approvato: STOP normalmente aperto GPIO32-GND; UART2 RX16/TX17 attraverso interfaccia K-line; VAN RX34 attraverso HW-CAN-VP230. GPIO26 mantiene deselezionato MCP2515 eventualmente sullo stesso SPI. Nessun GPIO collegabile direttamente ai fili auto. Verifiche hardware a cura dell utente, non dichiarate superate.

| Funzione firmware | GPIO proposto |
| --- | --- |
| `kSda` | 21 |
| `kScl` | 22 |
| `kSck` | 18 |
| `kMiso` | 19 |
| `kMosi` | 23 |
| `kSdCs` | 27 |
| `kStopPin` | 32 |
| `kKwpRx` | 16 |
| `kKwpTx` | 17 |
| `kVanRx` | 34 |
| `kUnusedCanCs` | 26 |

L'illustrazione dei moduli non è la disposizione fisica dei pin.
