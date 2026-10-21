# Data Logger — Cruscotto C3+AI

## Consultazione prima di modificare il progetto

Le [decisioni definitive](../README.md#decisioni-definitive) nel README principale
sono vincolanti. Consultare sempre anche [l'inventario](docs/hardware-inventory.md)
e la [procedura](docs/procedura-progetto.md); eseguire `python tools/project_preflight.py`
dalla radice. In particolare i due moduli CAN esistono già nell'inventario:
non suggerire un altro acquisto prima della loro verifica.

Sottoprogetto per lo sviluppo di un data logger basato su ESP32 per
Citroën C3 Phase 1, 1.4 HDi (DV4TD / 8HZ), da realizzare prima del
cruscotto digitale.

## Obiettivo

Raccogliere un dataset pulito di guida per addestrare modelli di intelligenza
artificiale destinati all'esecuzione locale (TinyML / Anomaly Detection).
Il dataset servirà allo sviluppo successivo di un cruscotto digitale custom
con display IPS e avvisi vocali.

## Funzioni previste

- D-016: ascolto passivo della linea dietro al cruscotto originale, conservando
  tutti i messaggi ricevuti in forma grezza, anche quelli non ancora decodificati.
  Pin, protocollo e capacità di acquisizione senza perdite restano da verificare.
- D-016: interrogazioni diagnostiche di sola lettura dalla presa OBD durante
  il funzionamento del veicolo, conservando richieste e risposte disponibili.
  La raccolta OBD dipende dai parametri esposti e dalla frequenza sostenibile;
  non equivale alla cattura di tutte le reti interne dell’auto.
- Identificazione della sorgente e timestamp per correlare le due acquisizioni;
  registrazione degli errori e delle perdite rilevabili. Fronte OBD libero (D-007).
- Raccolta di RPM, temperature, pressioni, MAF (portata massica dell'aria)
  e MAP (pressione assoluta nel collettore), nei limiti dei parametri
  effettivamente esposti dalla centralina.
- Registrazione su MicroSD con riferimento temporale fornito da RTC DS3231.
- Esportazione delle registrazioni per controllo della qualità, preparazione
  del dataset e addestramento dei modelli.

## Architettura prevista e verifiche aperte

Le due sorgenti, bus BSI e diagnostica OBD2, dovranno convergere nel sistema
ESP32 di acquisizione e registrazione. Il DS3231 fornirà data e ora;
per ordinare eventi ravvicinati servirà anche un contatore monotono
con risoluzione adeguata alle frequenze di acquisizione.

Il protocollo fisico e logico del bus BSI va identificato sulla specifica auto:
non si assume che sia CAN. La nuova schermata del 18/10/2026 indica
ISO 14230-4 KWP fast init a 10,4 kbaud per la diagnosi motore; contraddice
la vecchia indicazione CAN Creader. La successiva foto BSI identifica F02-00 / MG (9653667330), famiglia
Siemens Light 2001 VAN secondo tabella del costruttore; pin e segnali
della specifica C3 restano da verificare.
Vedere [evidenze e conclusioni](docs/protocolli-veicolo.md). Interfaccia K-line,
PID supportati e frequenze sostenibili restano da verificare; MCP2515/VP230 non sostituiscono un transceiver K-line. Il controller MCP2515
non decodifica VAN; il modulo VP230 separato può essere valutato come
ricevitore fisico VAN con decoder software ESP32, senza equivalere a un
collaudo del modulo o della vettura.
L'acquisizione BSI è prevista inizialmente in ascolto passivo; le richieste
OBD2 saranno limitate alla lettura dei parametri diagnostici.

Per rendere utilizzabile il dataset si dovranno definire unità, identificativi
delle sorgenti, timestamp, stato di validità, gestione dei dati mancanti,
errori e perdite di acquisizione. I dati grezzi dovranno essere conservabili
insieme ai dati decodificati per consentire verifiche successive.

## Decisioni da definire

- ESP32 identificato e flash verificata: vedere inventario. Restano da verificare
  piedinatura fisica e alimentazione dei moduli esterni.
- Veicolo dichiarato C3 2005, 1.4 HDi DV4TD/8HZ; variante rete e punti
  di collegamento ancora da verificare.
- Transceiver o adattatori adatti alle interfacce effettive.
- Alimentazione automotive, protezioni e gestione di accensione/spegnimento.
- Elenco dei segnali, frequenze e strategia delle interrogazioni OBD2.
- Formato dei file, sincronizzazione RTC, gestione delle sessioni e recupero
  dopo interruzione dell'alimentazione.
- Modalità di estrazione e analisi dei dati, annotazioni delle sessioni
  e criteri di qualità per l'addestramento.
- Prove a banco e criteri di verifica prima dell'installazione.

## Stato e organizzazione

È presente un primo [firmware diagnostico a banco](firmware/diagnostic/README.md)
per il solo ESP32, con configurazione PlatformIO e uscita seriale.
Non implementa ancora acquisizione BSI/OBD2, MicroSD o RTC. Le funzioni del logger 0.3.0 sono implementate nei sorgenti separati,
non ancora caricate o validate sui moduli. Le prove sulla scheda sono separate dalla compilazione.

Il [logger 0.3.0](firmware/logger/README.md) implementa avvio automatico,
MicroSD con rotazione e verifica di chiusura, DS3231, OLED e pulsante STOP.
Il profilo veicolo aggiunge OBD KWP fast init e ricezione VAN con salvataggio
anche dei byte non interpretati. Profili/GPIO proposti descritti nel README firmware.
Sorgenti aggiornati alla [0.3.1](firmware/logger/README.md) (D-022): PID OBD
prioritari, pausa KWP ridotta e SPI MicroSD configurabile; solo compilata, non caricata.
Profilo banco 0.3.0 caricato e avviato il 20/10/2026 su COM3: ATTESA SD
(modulo scollegato) e RTC oscillator_stop; ora non ancora impostata.
Lettore SD, OLED e RTC ricevuti il 19/10/2026; verifiche hardware a cura dell'utente
(D-020), nessun esito positivo presunto. Resistenza RTC 201 rimossa il 20/10/2026 (RTC-M006), ramo di ricarica
interrotto verificato (RTC-M007). Il programma sulla scheda ora e logger 0.3.0 banco.

La cartella `docs/` ospiterà la documentazione tecnica di dettaglio.
Il modello ESP32-S3 e il display previsti per il cruscotto non vincolano
la scelta della scheda per il data logger.

La documentazione generale del cruscotto rimane nel [README principale](../README.md).

## Collaudo MCP2515 a banco

Preparato il [test SPI separato](firmware/mcp2515-spi-test/README.md) per
HW-CAN-MCP2515 con HW-ESP32, secondo D-006 e D-010: reset, verifica modalità
configurazione e scrittura/rilettura registri a 100 kHz, senza traffico CAN.
Caricato il 18/10/2026 con hash verificati da esptool; letto su COM3
`status SPI_TEST=PASS uptime_ms=15545`. CAN non collaudato.
Ha sostituito la diagnostica; dal 20/10/2026 e a sua volta sostituito dal logger
0.3.0 banco. Sorgenti dei test conservati.
GPIO del solo test: SCK18, MISO19, MOSI23, CS26; H/L e INT scollegati.

## Distinta hardware

[Distinta hardware](docs/distinta-hardware.md): riuso del materiale presente e
ordinato, interfaccia K-line e valutazione VP230 per VAN passivo.
Architettura proposta; alimentazione automotive, interfaccia K-line completa
e cablaggio posteriore OBD non ancora rilasciati per acquisto/installazione.

## K-line autocostruita

Scelta D-013 registrata: [circuito a banco rev G](docs/kline-autocostruita.md), isteresi R10 (D-022), R3 al 5% (D-028),
NPN 2N5551 e comparatore LM2903B. UART 10400 con solo TX invertito.
Schema e modello DC prodotti; componenti non confermati, nessun montaggio,
collaudo. Driver K-line implementato nella 0.3.0, non ancora caricato.
Nessun collegamento alla vettura.

## Alimentazione e arresto manuale

D-015: logger temporaneo per pochi giorni. Avvio automatico; pulsante STOP
chiude la SD e mostra SALVATO - PUOI SPEGNERE, poi acquisizione arrestata fino
al prossimo avvio. Niente UPS, mantenimento MOSFET o arresto automatico IGN.
[Alimentazione e STOP rev B](docs/alimentazione-spegnimento.md).
Funzione implementata nella 0.3.0, non collaudata sul modulo; stato ARRESTATO
non significa disconnessione elettrica dell'ESP32. Uadme candidato, non collaudato.

## Collegamenti per la prima prova USB

[Schema di collegamento banco](docs/collegamenti-banco-030.md), rev. B (IEC 61082-1, D-024):
SD, RTC, OLED e STOP. Nessun collegamento al veicolo e nessun caricamento
eseguito durante la preparazione del disegno.
