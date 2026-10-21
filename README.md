# Cruscotto C3+AI

> **Data Logger in pausa dal 20/10/2026 (D-025), fino a quando il modulo K-line
> ([KL-001 rev G](data-logger/docs/kline-autocostruita.md)) sarà pronto.**
> Alla ripresa: procurare anche una CR2032 per l'RTC (ramo di ricarica già
> interrotto, RTC-M007), cablare la SD secondo [EL-003 rev B](data-logger/docs/collegamenti-banco-030.md)
> e fare la prima registrazione a banco. Dettagli nel [registro moduli](data-logger/docs/verifiche-moduli.md).

## Fonti del progetto — consultazione obbligatoria

Prima di acquisti, firmware, schemi o collegamenti leggere questa sezione,
[l'inventario hardware](data-logger/docs/hardware-inventory.md),
[lo stato del Data Logger](data-logger/README.md) e la
[procedura di aggiornamento](data-logger/docs/procedura-progetto.md).
Le istruzioni per gli agenti sono in [AGENTS.md](AGENTS.md).
Per iniziare da un clone nuovo, su un altro PC o con un altro agente, seguire
[CONTRIBUTING.md](CONTRIBUTING.md): setup, check e build riproducibili.

L'inventario sorgente è [hardware.json](data-logger/docs/hardware.json);
la vista Markdown è generata per evitare due elenchi divergenti.
Comando prima di decidere e prima di pubblicare:

```powershell
python tools/project_preflight.py
```

## Biblioteca tecnica della vettura

[Indice dei manuali e ricerca per argomento](docs/manuali/indice.md), rev. 1,
19/10/2026: consultare prima di cercare nuovamente documentazione su diagnosi,
BSI/VAN, quadro, alimentazioni e motore DV4TD. Distingue fonte documentale,
pagina e variante da una misura sul veicolo. Originali e dati personali esclusi da Git.

## Decisioni definitive

Registro iniziale consolidato il **18/10/2026** dalle conferme dell'utente.
Le date indicano la registrazione, non necessariamente la prima discussione.

| ID | Stato | Decisione | Fondamento / vincolo |
| --- | --- | --- | --- |
| D-001 | approvata | Progetto principale **Cruscotto C3+AI**, sottoprogetto **Data Logger**. | Nomi richiesti dall'utente per tutti i cartigli. |
| D-002 | approvata | Sviluppare prima il Data Logger; solo repository **lucaversus/C3-cruscotto-smart**. | Ordine di lavoro e perimetro richiesti. Dal 20/10/2026 l'ordine è aggiornato da D-026 (cruscotto avviato durante la pausa D-025); perimetro invariato. |
| D-003 | approvata | Strumenti software gratuiti, preferibilmente open source; riutilizzare l'hardware disponibile prima di nuovi acquisti. | Vincoli utente; controllare anche moduli non collaudati e in consegna. |
| D-004 | approvata | Registrazione ad **avvio automatico**, senza conferma tramite pulsante. | Utente: “non sono arrivati e facciamola partire in automatico”. |
| D-005 | superata | Inizialmente nessun pulsante richiesto nella prima versione; sostituita da D-015. | Scelta iniziale conservata; il 18/10/2026 l’utente richiede STOP manuale per il logger temporaneo. |
| D-006 | approvata | **Non acquistare CAN Pal o un altro modulo CAN ora**: verificare prima HW-CAN-MCP2515 e HW-CAN-VP230 già disponibili. | Correzione utente: “ma non abbiamo già il modulo can?”. La raccomandazione CAN Pal è ritirata. |
| D-007 | approvata | Lasciare **libera frontalmente la presa OBD**. | Preferenza esplicita utente; soluzione posteriore da identificare, non adattatore già approvato. |
| D-008 | approvata | Non presumere CAN sulla BSI; identificare rete e punto di accesso. Primo ascolto BSI passivo; diagnostica OBD di sola lettura. | Progetto iniziale; aggiornamento 18/10/2026: nuova schermata OBD indica KWP, in conflitto con CAN del Creader. Nessuna delle due identifica la rete BSI. |
| D-009 | approvata | Tutti i documenti visivi di progetto con cornice e cartiglio: progetto, sottoprogetto, titolo, codice, revisione, data, foglio e stato di validazione. | Richiesta esplicita utente; componenti illustrati e fili continui nello schema collegamenti. Dal 20/10/2026 la parte "componenti illustrati" è superata da D-024 (simboli IEC); cornice, cartiglio e fili continui restano validi. |
| D-010 | approvata | Prima fase firmware a banco USB: preservare diagnostica 0.1.0; base 0.2.0 separata, nessuna acquisizione auto finché le interfacce non sono verificate. | 0.1.0 caricata e collaudata; 0.2.0 compilata, non caricata né collaudata sui moduli. |
| D-011 | approvata | Inventario e decisioni versionati, consultati prima di ogni scelta pertinente e aggiornati nello stesso cambiamento. | Richiesta utente del 18/10/2026: non delegare il controllo della memoria all'utente. |
| D-012 | approvata | Archiviare nel repository le foto hardware già disponibili e collegarle all'inventario; consultarle prima di richiederle nuovamente. | Richiesta utente del 18/10/2026. Conservare evidenze e SHA-256, senza metadati personali nelle copie pubblicate. |
| D-013 | approvata | Realizzare in proprio l’interfaccia K-line; prima prototipo e collaudo a banco, poi progetto protetto per auto. | Utente 18/10/2026: “ok procediamo con il circuito autocostruito”. La scelta non certifica lo schema né conferma possesso dei componenti. |
| D-014 | approvata | Escludere il convertitore Pololu dalla distinta acquisti. | Utente 18/10/2026: costo e tempi di invio eccessivi. Eventuali citazioni precedenti restano storiche, non proposte correnti. |
| D-015 | approvata | Data Logger temporaneo per pochi giorni: avvio automatico, pulsante STOP per salvataggio e arresto prima di spegnere l’auto. Nessun UPS o mantenimento automatico richiesto. | Utente 18/10/2026: semplificare lo spin-off; premere il pulsante prima di togliere alimentazione. Conservare limiti elettrici reali e protezione di base. |
| D-016 | approvata | Due sorgenti di acquisizione: diagnostica dalla presa OBD e ascolto passivo della linea dietro al cruscotto originale. Conservare tutti i messaggi ricevuti dalla linea, anche non decodificati, e le risposte OBD di sola lettura, distinguendo le sorgenti. | Utente 18/10/2026: acquisizione tramite OBD e linea dietro al cruscotto, “tutto quello che arriva”. D-007 resta valida; pin e protocollo della linea da verificare. |

| D-017 | approvata | Collegamento temporaneo alla linea dietro al cruscotto con fili volanti fissati e isolati; nessun connettore dedicato da acquistare per questo punto. | Utente 18/10/2026: non interessa il connettore del quadro; identificazione elettrica dei segnali resta necessaria prima del collegamento. |

| D-018 | approvata | Modulo K-line senza jumper JP1 e senza richiamo R3 integrato; resistenza 510 ohm soltanto nel simulatore esterno da banco. | Conferma utente 18/10/2026: collaudare il modulo collegandolo alla linea simulata come alla vettura; nessuna risposta ECU simulata dalla sola resistenza. |

| D-019 | approvata | Usare CR2032 nel RTC e rimuovere la resistenza marcata 201 per interrompere il ramo di ricarica. | Utente 19/10/2026: intervento scelto; eseguito il 20/10/2026 (RTC-M006), ramo interrotto verificato con OL (RTC-M007); confermare interruzione del percorso prima di inserire la pila. Nessuna qualifica hardware dal solo intento. |
| D-020 | approvata | Proseguire con il firmware completo; verifiche tecniche dei moduli a cura dell'utente. Implementare SD/RTC/OLED, STOP D-015, OBD KWP D-013 e ricezione VAN D-008/D-016. | Utente 19/10/2026: "ci penso io alle verifiche". Non equivale a collaudo superato o ad autorizzazione a presumere pin auto. GPIO firmware 0.3.0 documentati come proposti. |
| D-021 | approvata | Controllo di compatibilita a fine blocco, prima di ogni pubblicazione; riscontro decisioni/inventario/configurazioni, check e build quando pertinente. Dopo pubblicazione verificare ref e pipeline sul commit esatto. | Utente 20/10/2026: rendere il controllo una regola. Esecuzione prima di GitHub e conferma CI dopo; non sostituisce collaudi hardware. Build invariata riutilizzabile per sole modifiche documentali, dichiarandolo. |
| D-022 | approvata | Applicare le proposte della revisione del 20/10/2026: firmware 0.3.1 (PID OBD prioritari, pausa KWP ridotta sopra P3min, SPI MicroSD configurabile, predefinita 1 MHz); K-line rev E con isteresi R10; verifiche VAN bloccanti prima del collegamento; prove a banco P-001/P-002 su interruzione e calo di tensione; controllo NVS del backup. | Utente 20/10/2026: "procedere con tutto quello che hai scritto, aggiornando il Git". Non è collaudo: 0.3.1 non caricata, rev E non montata, verifiche VAN e P-001/P-002 non eseguite. D-013, D-015, D-016 restano valide. |
| D-023 | approvata | Qualità del progetto: test C++ host della logica firmware in `dev.py check`, analisi statica cppcheck nella CI (`dev.py lint`), procedure guidate nel repository (`.claude/skills/`: chiusura-blocco, registro-collaudo, revisione-firmware). | Utente 20/10/2026: "Sono d'accordo con quello che hai scritto". Strumenti gratuiti e open source (D-003); procedure nel repository, non sul PC di Luca (AGENTS.md). Non sostituiscono collaudi hardware. |
| D-024 | approvata | Elaborati grafici secondo le norme: simboli IEC 60617, schemi IEC 61082-1, foglio A3 ISO 5457 con zone di riferimento, cartiglio ISO 7200 con tabella revisioni, scrittura ISO 3098, spessori ISO 128. Rifatti KL-001 rev F, EL-003 rev B, EL-001 rev E (storico, sostituito da EL-003) e BL-001 rev D, da una libreria comune `iso_drawing.py`. | Utente 20/10/2026: schemi "non costruiti seguendo le regole ISO", chiede di correggerli tutti. Supera la parte "componenti illustrati" di D-009. Nessuna variazione elettrica: reti, valori e GPIO invariati. |
| D-025 | approvata | Data Logger in pausa dal 20/10/2026 fino a quando il modulo K-line (KL-001) sarà pronto. Alla ripresa: CR2032 da procurare, cablaggio SD (EL-003 rev B) e prima registrazione a banco con prova di mantenimento dell'ora. | Utente 20/10/2026: "al momento metterei in pausa questo progetto secondario", precisato: "finché non avrò pronto il modulo K". Nessuna decisione tecnica modificata; verifiche aperte invariate. |
| D-026 | approvata | Avviare il **Cruscotto digitale** durante la pausa del Data Logger (D-025). Aggiorna l'ordine di lavoro di D-002; perimetro invariato (unico repository). Primo passo: diagnosi della scheda RCmall ESP32-S3 5″ (HW-DASH-DISPLAY) secondo la sezione "Diagnosi all'arrivo della scheda". | Utente 20/10/2026: "voglio iniziare con il progetto del cruscotto"; dichiara di possedere la scheda ("Ce l'ho"). Possesso dichiarato, modello e variante non riscontrati; nessun driver o GPIO fissato. |
| D-027 | approvata | Cruscotto **senza interazione touch**: display dietro la copertura trasparente del quadro; variante ordinata senza touch. Nessun input tattile nella UI. | Utente 20/10/2026: "l'ho ordinato non touch perché tanto andrà dietro la copertura trasparente del cruscotto e non ci sarà modo di interagire con il tocco". Comandi eventuali (es. cambio pagina) da definire separatamente. |
| D-036 | approvata | R3 del simulatore da banco K-line: 510 ohm, **1 W, 5%** invece di 1 W, 1%. KL-001 rev G, distinta rev K. Soglie e isteresi invariate (dipendono da R4-R8 e R10 all'1%). | Utente 21/10/2026: all'1% trova solo una 600 mW, che a 16 V lavorerebbe all'85% della nominale (0,51 W); su proposta di usare la 1 W al 5%, risponde "aggiorna". Candidato individuato TE Neohm EP1WSS510RJ, non ordinato. |
| D-037 | approvata | Resistenze **a foro passante (THT, reofori assiali)**: tutte, nel prototipo K-line e nella futura scheda principale del front end, da progettare con impronte THT per le resistenze. Non riguarda gli integrati (LM2903B resta in SOIC-8 su adattatore DIP-8). | Utente 21/10/2026: "le resistenze sono tutte a filo passante", precisato come affermazione; "così quando progetterai la mainboard del front end saprai il tipo di montaggio". Nessuna scheda del front end ancora progettata. |

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
- OBD: nuova evidenza indica ISO 14230-4 KWP fast init 10,4 kbaud, in conflitto
  con precedente indicazione CAN Creader. BSI F02-00 / MG, riferimento 9653667330: famiglia Siemens Light 2001 VAN
  identificata documentalmente; pin e segnali della variante da verificare. Vedere [registro protocolli](data-logger/docs/protocolli-veicolo.md).
  Il MCP2515 non decodifica VAN e nessun modulo CAN gestisce K-line; il
  VP230 separato è candidato come ricevitore fisico VAN con decoder ESP32,
  da collaudare. Vedere [distinta hardware](data-logger/docs/distinta-hardware.md).
- Lettore MicroSD, OLED e RTC DS3231 ricevuti il 19/10/2026 e fotografati,
  non collaudati. Il modulo chiamato batteria e HW-RTC, non un UPS.
  Presente anche una MicroSD inserita; capacita e contenuti ancora da riscontrare.
- GPIO21/22 I2C e GPIO18/19/23 + CS27 sono una **proposta firmware**, registrata
  in hardware.json e verificata contro config.h, non il pinout fisico HW-394 approvato.
- Regolazione iniziale RTC su hardware, alimentazione di mantenimento, identificazione OLED, capacità
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
Sorgenti logger aggiornati alla 0.3.1 (D-022), solo compilata; sulla scheda resta la 0.3.0.
Il [logger 0.3.0](data-logger/firmware/logger/README.md) implementa registrazione
MicroSD, RTC, OLED, STOP, OBD KWP e ricezione VAN. Profili banco/veicolo separati;
sorgenti e GPIO proposti, non collaudati sul veicolo. Profilo banco 0.3.0 caricato e avviato il 20/10/2026: ATTESA SD
(modulo scollegato), RTC oscillator_stop; nessun collaudo veicolo.
Cruscotto digitale (D-026): scheda ESP32-8048S050 identificata (ESP32-S3, 16 MB
flash, 8 MB PSRAM, esptool), variante senza touch (D-027), backup di fabbrica in
[data-logger/backups/esp32-8048s050](data-logger/backups/esp32-8048s050/README.md).
[Prova display 0.1.0](cruscotto/firmware/display-test/README.md): compilata,
caricata e conforme a banco (DSP-M001): pinout RGB e PSRAM verificati. UI e simulatore PC non ancora presenti.

### Collaudo SPI a banco — 18/10/2026

HW-CAN-MCP2515 alimentato a 3,3 V (M-009); firmware separato
[data-logger/firmware/mcp2515-spi-test](data-logger/firmware/mcp2515-spi-test/README.md)
compilato e caricato su HW-ESP32 con hash dei segmenti verificati da esptool.
Esito letto direttamente su COM3: `SPI_TEST=PASS` (M-010), SPI a 100 kHz mode 0.
Questo programma era sulla scheda fino al caricamento logger 0.3.0 del 20/10/2026;
aveva sostituito la diagnostica 0.1.0
i cui sorgenti sono conservati. CAN non collaudato; nessuna connessione al veicolo.

### Interfaccia K-line autocostruita

Scelta D-013: [schema e distinta del prototipo a banco](data-logger/docs/kline-autocostruita.md),
rev G (isteresi R10 D-022, disegno IEC D-024, R3 al 5% D-036). NPN e comparatore, calcoli DC verificati; non montato o collaudato.
Installazione auto e protezioni ancora da progettare.

### Logger temporaneo: arresto manuale

D-015 sostituisce la proposta di mantenimento con batteria permanente, MOSFET
e rilevamento IGN. STOP chiude i file, conferma SALVATO e arresta acquisizione;
poi si toglie alimentazione. Il pulsante non interrompe direttamente la corrente.
Punto di prelievo auto ancora da verificare, nessun pin presunto.
