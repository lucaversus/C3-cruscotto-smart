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

- Acquisizione dei dati del bus di bordo associato alla BSI.
- Interrogazioni diagnostiche OBD2 durante il funzionamento del veicolo.
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
Non implementa ancora acquisizione BSI/OBD2, MicroSD o RTC. Le funzioni
di registrazione descritte sono obiettivi da implementare e validare,
non capacità già disponibili. Le prove sulla scheda sono separate dalla compilazione.

È inoltre presente la prima [base logger 0.2.0](firmware/logger/README.md),
separata dalla diagnostica: avvio automatico, CSV di salute ESP32 su MicroSD
e lettura DS3231 con stato di validità. Compilazione e 18 controlli sul decoder
verificati; non ancora caricata né collaudata con i moduli, ancora in consegna.
Pulsanti, OLED e acquisizione automobilistica restano disabilitati.

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
Sulla scheda sostituisce la diagnostica, i cui sorgenti sono conservati.
GPIO del solo test: SCK18, MISO19, MOSI23, CS26; H/L e INT scollegati.

## Distinta hardware

[Distinta rev A](docs/distinta-hardware.md): riuso del materiale presente e
ordinato, interfaccia K-line e valutazione VP230 per VAN passivo.
Architettura proposta; alimentazione automotive, interfaccia K-line completa
e cablaggio posteriore OBD non ancora rilasciati per acquisto/installazione.

## K-line autocostruita

Scelta D-013 registrata: [circuito a banco rev A](docs/kline-autocostruita.md),
NPN 2N5551 e comparatore LM2903B. UART 10400 con solo TX invertito.
Schema e modello DC prodotti; componenti non confermati, nessun montaggio,
firmware K-line o collaudo. Nessun collegamento alla vettura.
