# Cruscotto C3+AI

## Fonti del progetto — consultazione obbligatoria

Prima di acquisti, firmware, schemi o collegamenti leggere questa sezione,
[l'inventario hardware](data-logger/docs/hardware-inventory.md),
[lo stato del Data Logger](data-logger/README.md) e la
[procedura di aggiornamento](data-logger/docs/procedura-progetto.md).
Le istruzioni per gli agenti sono in [AGENTS.md](AGENTS.md).

L'inventario sorgente è [hardware.json](data-logger/docs/hardware.json);
la vista Markdown è generata per evitare due elenchi divergenti.
Comando prima di decidere e prima di pubblicare:

```powershell
python tools/project_preflight.py
```

## Decisioni definitive

Registro iniziale consolidato il **18/10/2026** dalle conferme dell'utente.
Le date indicano la registrazione, non necessariamente la prima discussione.

| ID | Stato | Decisione | Fondamento / vincolo |
| --- | --- | --- | --- |
| D-001 | approvata | Progetto principale **Cruscotto C3+AI**, sottoprogetto **Data Logger**. | Nomi richiesti dall'utente per tutti i cartigli. |
| D-002 | approvata | Sviluppare prima il Data Logger; solo repository **lucaversus/C3-cruscotto-smart**. | Ordine di lavoro e perimetro richiesti. |
| D-003 | approvata | Strumenti software gratuiti, preferibilmente open source; riutilizzare l'hardware disponibile prima di nuovi acquisti. | Vincoli utente; controllare anche moduli non collaudati e in consegna. |
| D-004 | approvata | Registrazione ad **avvio automatico**, senza conferma tramite pulsante. | Utente: “non sono arrivati e facciamola partire in automatico”. |
| D-005 | approvata | Pulsanti soltanto se necessari in futuro; nessun pulsante richiesto dalla prima versione. | Indicazione esplicita utente. Gli elementi disegnati sono opzionali. |
| D-006 | approvata | **Non acquistare CAN Pal o un altro modulo CAN ora**: verificare prima HW-CAN-MCP2515 e HW-CAN-VP230 già disponibili. | Correzione utente: “ma non abbiamo già il modulo can?”. La raccomandazione CAN Pal è ritirata. |
| D-007 | approvata | Lasciare **libera frontalmente la presa OBD**. | Preferenza esplicita utente; soluzione posteriore da identificare, non adattatore già approvato. |
| D-008 | approvata | Non presumere CAN sulla BSI; identificare rete e punto di accesso. Primo ascolto BSI passivo; diagnostica OBD di sola lettura. | Progetto iniziale. Foto Creader indica CAN per la diagnostica, non per l'intera rete BSI. |
| D-009 | approvata | Tutti i documenti visivi di progetto con cornice e cartiglio: progetto, sottoprogetto, titolo, codice, revisione, data, foglio e stato di validazione. | Richiesta esplicita utente; componenti illustrati e fili continui nello schema collegamenti. |
| D-010 | approvata | Prima fase firmware a banco USB: preservare diagnostica 0.1.0; base 0.2.0 separata, nessuna acquisizione auto finché le interfacce non sono verificate. | 0.1.0 caricata e collaudata; 0.2.0 compilata, non caricata né collaudata sui moduli. |
| D-011 | approvata | Inventario e decisioni versionati, consultati prima di ogni scelta pertinente e aggiornati nello stesso cambiamento. | Richiesta utente del 18/10/2026: non delegare il controllo della memoria all'utente. |
| D-012 | approvata | Archiviare nel repository le foto hardware già disponibili e collegarle all'inventario; consultarle prima di richiederle nuovamente. | Richiesta utente del 18/10/2026. Conservare evidenze e SHA-256, senza metadati personali nelle copie pubblicate. |

Nessuna nuova proposta tecnica è resa definitiva solo perché compare in una
risposta, nella distinta proposta o in un disegno. Per cambiare una decisione
approvata serve una nuova indicazione utente o la risoluzione esplicita di un conflitto.

## Questioni ancora aperte — non sono decisioni definitive

- Alimentazione dal quadro: possibilità proposta dall'utente, non pin, circuito,
  corrente aggiuntiva o convertitore già approvati. Protezioni automotive e arresto
  controllato MicroSD da progettare; nessun modulo alimentatore da ordinare alla cieca.
- Adattatore dietro OBD, connettore posteriore C3 e massa di riferimento da identificare.
- Moduli CAN: livelli, alimentazione e terminazione da verificare prima del riuso.
  TWAI interno + HW-CAN-VP230 è una possibilità; MCP2515 resta disponibile.
- OBD: indicazione CAN osservata sul Creader della stessa auto; bitrate, ID e PID
  non ancora identificati. Protocollo BSI e architettura delle reti non confermati.
- MicroSD, RTC e OLED ordinati e ancora in consegna. I riferimenti commerciali
  sono indicazioni dal contesto; modello OLED, quantità e pezzi consegnati da riscontrare.
- GPIO21/22 I2C e GPIO18/19/23 + CS27 sono una **proposta firmware**, registrata
  in hardware.json e verificata contro config.h, non il pinout fisico HW-394 approvato.
- Regolazione iniziale RTC, alimentazione di mantenimento, driver OLED, capacità
  della scheda MicroSD e formato finale dei dati auto restano da completare.

Cruscotto digitale custom per Citroën C3 Phase 1, 1.4 HDi, motore DV4TD / 8HZ.

## Sottoprogetti e ordine di lavoro

Il repository ospita due attività collegate:

1. **[Data logger](data-logger/README.md)**: primo progetto da sviluppare,
   basato su ESP32, MicroSD e RTC DS3231 per raccogliere dati BSI e OBD2
   e costruire un dataset di guida per TinyML e rilevamento di anomalie.
2. **Cruscotto digitale**: progetto successivo, descritto nelle sezioni seguenti.

Il data logger è un sottoprogetto nello stesso repository e condivide la sua
cronologia Git; non è un repository separato né un submodule.

## Obiettivo e sviluppo previsto

Dashboard ad alto contrasto, leggibile di giorno e di notte, su display da 5″
800×480 con ESP32-S3 e interfaccia LVGL. Lo sviluppo previsto usa PlatformIO e
C++, con un simulatore PC basato su SDL per provare la UI prima del flash.

La logica della dashboard dovrà ricevere gli stessi parametri da sorgenti
intercambiabili: dati simulati, modalità demo e ingressi reali. Sono previsti
filtri software (media mobile/EMA), soglie di allarme e test a banco con
potenziometri e generatori di segnali. I 60 FPS sono un obiettivo da misurare
sull'hardware, non una prestazione già verificata.

## Hardware: osservazioni preliminari

La scheda scelta è un modulo integrato RCmall ESP32 + display da 5″, ancora in
attesa di diagnosi diretta. La foto del venditore mostra un modulo indicato come
ESP32-S3-WROOM, USB-C, slot microSD, pulsanti BOOT/RESET, connettori di espansione
e un connettore di alimentazione. La sigla del PCB sembra ESP32-8048S050:
identificazione e revisione restano da confermare.

Il display da 5″ è previsto come RGB 800×480; pin, temporizzazioni, memoria e
controller touch non sono ancora verificati. La foto annotata descrive la
disposizione dei componenti, ma non sostituisce uno schema elettrico.

La documentazione della variante da 1,9″ riporta:

| Caratteristica | Dato dichiarato per la sola variante 1,9″ |
| --- | --- |
| Scheda | ESP32-1732S019 |
| Display | ST7789, 170×320 pixel |
| Collegamento | SPI, con segnali CS/SCK/DC |
| Memoria | Sigla ESP32-S3-R8N16: 8 MB PSRAM e 16 MB flash dichiarati |

Questi dati non sono trasferibili automaticamente alla variante da 5″.
L'affermazione del venditore secondo cui cambia soltanto la dimensione non è
sufficiente per scegliere driver o assegnare GPIO: SPI e RGB richiedono
configurazioni diverse.

La descrizione commerciale generale contiene incongruenze: cita Bluetooth
Classic BR/EDR e 520 KB di SRAM, mentre ESP32-S3 supporta Bluetooth LE e dispone
di 512 KB di SRAM interna. Non viene quindi usata come riferimento definitivo
per la configurazione.

Un framebuffer 800×480 RGB565 occupa 750 KiB; due occupano circa 1,46 MiB,
oltre alla memoria dell'applicazione. Quantità, tipo e funzionamento della
PSRAM della scheda da 5″ dovranno essere verificati.

## Diagnosi all'arrivo della scheda

1. Fotografare e leggere le sigle di PCB e modulo ESP32, inclusa la revisione.
2. Recuperare lo schema, la tabella dei pin e l'esempio Arduino/LVGL specifico
   per la variante da 5″ dal venditore.
3. Identificare il chip e verificare flash e PSRAM con strumenti diagnostici
   e un firmware minimo, senza sovrascrivere alla cieca il firmware di fabbrica.
4. Confermare i GPIO del display RGB, le temporizzazioni, il controllo della
   retroilluminazione e il controller touch con i relativi collegamenti.
5. Verificare alimentazione e ingressi utilizzabili; i segnali automobilistici
   e i 12 V richiedono circuiti di alimentazione/protezione e adattamento,
   prima di raggiungere la scheda o i suoi GPIO.
6. Provare prima il display con l'esempio del produttore, poi configurare
   PlatformIO/LVGL e misurare fluidità, memoria e stabilità in modalità demo.

## Stato del repository

Il data logger dispone di un primo [firmware diagnostico per il solo ESP32](data-logger/firmware/diagnostic/README.md),
con configurazione PlatformIO. Non acquisisce ancora dati dal veicolo.
Una [base logger 0.2.0](data-logger/firmware/logger/README.md) separata prepara
registrazione automatica MicroSD e RTC: compilata, non ancora collaudata su hardware.
Per il cruscotto digitale non sono ancora presenti firmware, simulatore o test
eseguibili: le dipendenze e la configurazione hardware saranno fissate dopo
l'identificazione della scheda display. Il layout della UI e il simulatore PC
possono essere sviluppati prima dell'arrivo dell'hardware.

### Collaudo SPI a banco — 18/10/2026

HW-CAN-MCP2515 alimentato a 3,3 V (M-009); firmware separato
[data-logger/firmware/mcp2515-spi-test](data-logger/firmware/mcp2515-spi-test/README.md)
compilato e caricato su HW-ESP32 con hash dei segmenti verificati da esptool.
Esito letto direttamente su COM3: `SPI_TEST=PASS` (M-010), SPI a 100 kHz mode 0.
Questo programma è ora sulla scheda, in sostituzione della diagnostica 0.1.0
i cui sorgenti sono conservati. CAN non collaudato; nessuna connessione al veicolo.
