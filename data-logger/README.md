# Data logger ibrido per Citroën C3

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
non si assume che sia CAN. Anche trasporto diagnostico OBD2, interfacce
necessarie, PID supportati e frequenze sostenibili restano da verificare.
L'acquisizione BSI è prevista inizialmente in ascolto passivo; le richieste
OBD2 saranno limitate alla lettura dei parametri diagnostici.

Per rendere utilizzabile il dataset si dovranno definire unità, identificativi
delle sorgenti, timestamp, stato di validità, gestione dei dati mancanti,
errori e perdite di acquisizione. I dati grezzi dovranno essere conservabili
insieme ai dati decodificati per consentire verifiche successive.

## Decisioni da definire

- Modello ESP32, memoria e interfacce disponibili.
- Anno/versione del veicolo, protocolli e punti di collegamento verificati.
- Transceiver o adattatori adatti alle interfacce effettive.
- Alimentazione automotive, protezioni e gestione di accensione/spegnimento.
- Elenco dei segnali, frequenze e strategia delle interrogazioni OBD2.
- Formato dei file, sincronizzazione RTC, gestione delle sessioni e recupero
  dopo interruzione dell'alimentazione.
- Modalità di estrazione e analisi dei dati, annotazioni delle sessioni
  e criteri di qualità per l'addestramento.
- Prove a banco e criteri di verifica prima dell'installazione.

## Stato e organizzazione

Requisiti iniziali documentati; firmware, configurazione PlatformIO e test
non sono ancora presenti. Le funzioni descritte sono obiettivi da implementare
e validare, non capacità già disponibili.

La cartella `docs/` ospiterà la documentazione tecnica di dettaglio.
Il modello ESP32-S3 e il display previsti per il cruscotto non vincolano
la scelta della scheda per il data logger.

La documentazione generale del cruscotto rimane nel [README principale](../README.md).
