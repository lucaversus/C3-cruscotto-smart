# Cruscotto C3+AI

> **Data Logger in pausa dal 20/10/2026 (D-025), fino a quando il modulo K-line
> ([KL-001 rev F](data-logger/docs/kline-autocostruita.md)) sarà pronto.**
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

## Disegni del progetto

Tutte le tavole e le infografiche, con anteprime, sono nella cartella [`disegni/`](disegni/README.md).

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
| D-028 | approvata | Messaggi audio dell'IA dall'S3 sugli altoparlanti dell'auto tramite **relè di commutazione**: a riposo altoparlanti collegati alla radio originale; durante il messaggio il relè li collega all'uscita audio dell'S3 (radio di fatto in muto). Funziona anche a radio spenta; nessun comando trasmesso sul VAN. | Utente 20/10/2026: messaggi "anche con radio spenta e in caso di radio accesa quest'ultima messa in muto"; "io avevo pensato alla proposta A, l'auto è quella originale". Amplificatore, relè, canali e altoparlanti da definire; uscite radio a ponte da non collegare a massa. |
| D-029 | approvata | Architettura del cruscotto a **due microcontrollori**: un ESP32 **front-end** legge VAN (solo ricezione) e K-line e inoltra all'S3 dati compatti su UART a 2 fili; l'ESP32-S3 8048S050 gestisce display, IA, audio e relè, senza collegamenti diretti al veicolo. Prototipo con HW-ESP32 (HW-394) e moduli presenti; obiettivo finale una **scheda madre** dietro l'S3 con modulo ESP32-WROOM-32E senza PSRAM (N8 o N16: la PSRAM occupa GPIO16/17), protezioni 12 V, convertitore 5 V, interfacce VAN/K-line, relè audio e **connettore multipolare** verso l'auto. | Utente 20/10/2026: "allora passiamo a questa nuova architettura"; obiettivo scheda madre con "connettore multipolo per rendere il collegamento con l'auto più solido e di veloce e pulita installazione". Stesso hardware e codice tra raccolta dati e uso (dataset IA coerente). Nessun acquisto ordinato; GPIO S3 e protocollo UART da definire. |
| D-030 | approvata | Alimentazione del cruscotto da **+12 V permanente con ingresso chiave**: accensione con la chiave (in futuro anche ad altri eventi), mantenimento di qualche secondo dopo lo spegnimento per salvare lo stato, poi autospegnimento; consumo a riposo da contenere (obiettivo indicativo < 1 mA). Avviamento superato con **condensatore di riserva sulla scheda madre**. Protezioni: fusibile, inversione polarità, TVS, filtro, massa comune con il quadro. | Utente 20/10/2026: "1.B e 2. condensatore lo vedo come più facile installare nella mainboard". Non sostituisce D-015 per il logger temporaneo. Calo reale all'avviamento, durata e capacità del condensatore da misurare/calcolare; punto di prelievo +12 V e segnale chiave da identificare. |
| D-031 | approvata | **Raffreddamento attivo** del cruscotto: dissipatore in alluminio dietro l'S3 e **ventola 12 V** predisposta nelle staffe stampate, pilotata in PWM dal front-end. Funziona anche a **motore spento** finché la batteria a riposo resta sopra una **soglia di guardia (partenza 12,3 V)**, con isteresi e tempo massimo; scheda madre con **dominio sempre acceso** a basso consumo (front-end in sonno, NTC, misura batteria, ventola) separato dal dominio principale 5 V/S3. Sensori NTC vicino al display. | Utente 21/10/2026: "predisporrei immediatamente una ventola e applicherò un dissipatore in alluminio dietro il modulo S3", "se la ventola sarebbe possibile farla funzionare da macchina spenta fino ad un livello della batteria di guardia studiamolo"; conferma "procedi". Limiti pannello dichiarati dal rivenditore −20…+70 °C (magazzinaggio +80 °C). Soglie da tarare; efficacia da misurare la prossima estate. |
| D-032 | approvata | **VIN nei dati grezzi VAN** (IDEN E24 secondo le decodifiche comunitarie): il logger continua a registrare tutto senza filtri (D-016); il VIN va **mascherato solo prima di pubblicare o condividere** i dati, in post-elaborazione. Gli originali con VIN restano solo in locale, esclusi da Git. | Utente 21/10/2026, alla questione A della revisione generale: "mascheriamolo solo prima della pubblicazione". Strumento di mascheramento da realizzare prima della prima pubblicazione di dati; nessuna modifica al firmware. |
| D-033 | approvata | **Stessi canali nel Data Logger e nel front-end**: oltre a VAN e K-line il logger registra IMU (HW-IMU-LSM6DSO; fino al 22/10/2026 indicato HW-IMU-LSM6DS3), tensione batteria, segnale chiave e temperature NTC, con gli stessi sensori, montaggi e frequenze previsti per il cruscotto, così che il dataset di addestramento corrisponda ai dati disponibili in uso. Fonti di dati aggiuntive per l'IA da valutare (questioni aperte). | Utente 21/10/2026, questione B della revisione: "assolutamente sì, anzi pensa possiamo dare in pasto altri dati all'AI". Firmware logger, schema EL-003 e GPIO del logger da aggiornare; nessun collegamento eseguito. |
| D-034 | approvata | Licenza del repository **MIT** per codice, documenti e disegni del progetto; file `LICENSE` nella radice. Codice di terzi con la propria licenza (THIRD_PARTY.md); manuali e dati personali esclusi. Evitare librerie GPL nel firmware distribuito. | Utente 21/10/2026: "il progetto per me è totalmente open, chiunque vuole può utilizzarlo"; "ok mit". |
| D-035 | approvata | Diagnosi OBD in **sola lettura** estesa ai servizi **0x03** (codici guasto memorizzati) e **0x02** (dati al momento del guasto), oltre a 0x01 e all'avvio KWP 0x81. Restano **vietati** 0x04 (cancellazione codici), comandi agli attuatori e qualsiasi scrittura. | Utente 21/10/2026, alla domanda della revisione: "si". Integra D-008 e la checklist revisione-firmware; nessuna implementazione o prova ancora eseguita. |
| D-036 | approvata | **Wi-Fi dell'S3 spento di norma**, acceso solo su **attivazione specifica** dell'utente (modalità servizio) per scarico dati e aggiornamenti; mai durante la normale visualizzazione, per evitare disturbi al display e calore. Modalità di attivazione (es. comandi al volante a veicolo fermo) da definire; scarico solo verso la rete di casa (D-032). | Utente 21/10/2026: "il wifi lo implementerei soltanto su attivazione specifica, così risparmiamo un po' di problemi con il display e di temperature". Nessuna implementazione. |
| D-037 | approvata | Requisiti del firmware dell'S3 da implementare: **IA multi-modello** con riferimento di "normalità" della vettura e analisi in frequenza delle vibrazioni; **scatola nera** (ultimo minuto di tutti i dati in PSRAM, salvato in flash su anomalia o codice guasto); **etichette** dell'utente con i comandi al volante; **grafica senza tearing** (doppio framebuffer sincronizzato); **pagina diagnostica** sul telefono (Wi-Fi o BLE solo su attivazione, D-036); **audio con coda di priorità** e volume legato alla velocità. | Utente 21/10/2026: "tutti gli altri punti implementiamoli nel FW". Ordine di implementazione e piattaforma (Arduino-ESP32 2.x / ESP-IDF 4.4 o versione 5.x) da definire; nessuna implementazione ancora. |
| D-038 | approvata | **App per smartphone** di diagnostica, impostazioni e visualizzazione in tempo reale. **Impostazioni modificabili solo a veicolo fermo** (velocità nulla dal VAN, verifica nel firmware dell'S3); **vista in tempo reale e diagnostica anche in marcia** tramite **Bluetooth LE**. Precisa D-036: il Wi-Fi resta solo in modalità servizio, il BLE può restare attivo durante la guida. Abbinamento con codice; l'app non comanda mai il veicolo (D-035). | Utente 21/10/2026: "i settaggi solo a veicolo fermo per sicurezza, il resto anche a veicolo in movimento". Telefono dell'utente Android; scelta dell'utente: **app nativa Flutter** ("proverei lei", 21/10/2026), Android per primo, licenza MIT del progetto. Libreria BLE **flutter_reactive_ble** (BSD-3); esclusa flutter_blue_plus (licenza non open source per uso commerciale, in contrasto con D-034). Flutter SDK e Android SDK da installare sul PC; nessuna implementazione. |
| D-039 | approvata | **Aggiornamenti e recupero del firmware S3** senza smontare: aggiornamento via **BLE** dall'app (veicolo fermo) o **Wi-Fi** in modalità servizio; livello 1 **doppia partizione OTA**; livello 2 **ritorno automatico** alla versione precedente se il nuovo firmware non supera l'autotest; livello 3 **firmware di emergenza** in partizione dedicata, avviato tenendo premuto un pulsante su **IO19** durante il reset (secondo pulsante su EN). Il front-end viene aggiornato dall'S3 tramite UART. | Utente 21/10/2026: "prevediamo i livelli 1 2 e 3". Livello 4 (prolunga USB-C) non scelto. Pulsanti originali del quadro o pulsanti nascosti da definire; EN dell'S3 da prelevare dalle piazzole del pulsante RST; firmware di emergenza da scrivere. |
| D-040 | approvata | **Ruoli nella catena dell'IA**: (1) il **Data Logger** raccoglie il dataset completo per giorni, comprese le **etichette dal volante** (da aggiungere al logger alla ripresa, D-025); (2) l'**addestramento avviene sul PC**; (3) l'**S3 esegue** il modello addestrato e conserva la **scatola nera** degli eventi per spiegare gli allarmi e raccogliere casi (anche falsi allarmi) per **riaddestramenti periodici** sul PC, distribuiti con aggiornamento OTA (D-039). | Utente 21/10/2026, dopo la spiegazione dei ruoli: "sì, tutto chiaro". Logica di scatola nera ed etichette provata sull'S3 perché il logger è in pausa; formato riutilizzabile. |
| D-041 | approvata | **Priorità di sviluppo del cruscotto**: prima la struttura grafica e funzionale della dashboard, provata a banco con l'S3 collegato via USB; app Flutter (D-038) e aggiornamenti via Bluetooth (D-039) rinviati alla fase precedente l'installazione sull'auto. Le protezioni già presenti nel firmware (doppia partizione, ritorno automatico) restano. | Utente 21/10/2026: "prima da capire tutta la struttura grafica e funzionale della dashboard [...] prima di installarlo sulla macchina andremo a sviluppare il discorso dell'app Flutter anche per gli aggiornamenti tramite Bluetooth". |
| D-042 | approvata | **Data Logger completo costruito su millefori e provato a banco prima dell'installazione sull'auto**; collegamenti tra le basette con **fili saldati, senza morsetti** né zoccoli/adattatori non indispensabili. Disposizione proposta (non ancora approvata): millefori MC01009 (K-line, ESP32, RTC + MicroSD) più un ritaglio per l'IMU HW-IMU-LSM6DSO, OLED, modulo VAN HW-CAN-VP230 (solo ricezione, GPIO34) e STOP con fili, tavola C3AI-DL-EL-004 rev A. | Utente 22/10/2026: "creare il data logger completo sulla millefori ... e fare la prova a banco con quella prima di installarla sull'auto"; "niente morsetti salderò i fili da una basetta all'altra". D-025 invariata (ripresa all'arrivo del modulo K); VAN disegnato perché sarà usato (utente 22/10/2026: "una volta fatte le prove e modifiche andrà utilizzato"), ma collegato al quadro solo dopo le verifiche D-022; alimentazione in auto (HW-AUTO-POWER) non ancora posseduta. Nulla montato o collaudato. |
| D-043 | approvata | **Pubblicazione su GitHub a fine sessione**: durante la sessione commit e controlli locali; push, PR, attesa della CI e unione in main una sola volta quando l'utente scrive «fine sessione». Eccezioni: esito CI necessario prima (es. prima di caricare un firmware) o richiesta espressa dell'utente. D-021 resta valida al momento della pubblicazione. | Utente 22/10/2026: "visto che l'operazione CI necessita di molto tempo e interrompe troppo la sessione eseguiamola, salvo casi in cui è necessario prima, al momento che a fine della sessione io ti scriverò 'fine sessione'". |
| D-044 | approvata | **Connettore verso l'auto -J1 = Molex Micro-Fit 3.0 a 24 vie** (2x12, passo 3 mm, aggancio a scatto e inserimento in un solo verso, 5 A per contatto, -40...+105 °C). Il cablaggio dell'auto termina con la femmina 43025-2400 (contatti 43030-0007); il prototipo a banco usa da subito la spina volante 43020-2400 (contatti 43031-0007), la scheda madre definitiva il connettore da circuito stampato 43045-2400 che si innesta nella stessa femmina. Vie 1-16 come la bozza di -J1, 17-24 di riserva. | Utente 23/10/2026: "prevedere immediatamente un connettore da usare per l'interfaccia k uguale a quello definitivo [...] così fatto il lavoro la prima volta sull'auto ce lo ritroveremo poi"; scelta "Molex Micro-Fit 3.0, 20/24 vie": adottate 24 vie (più riserva). Disponibilità Farnell 23/10/2026; nulla ordinato. Pinza a crimpare da scegliere. |
| D-045 | approvata | **Contorno della scheda madre** dal modello 3D del cruscotto dell'utente (`cruscotto/meccanica/scheda-madre-contorno.dxf`, 178,7 × 74 mm, 6 fori Ø3), al posto del contorno della S3 (137 × 84 mm). La scheda madre è **installata direttamente dietro la S3**; **foro centrale con ventolina** che soffia verso la S3 (D-031); **ai due estremi gli interruttori** azionati dai due pulsanti del quadro originale. | Utente 24/10/2026: "questo è il contorno della motherboard, [...] al centro si potrebbe creare un foro e mettere una ventolina che soffia verso l's3, [...] sarà installata direttamente dietro. agli estremi ci saranno i due switch comandati dai pulsanti del cruscotto originale". Ventola 40 × 40 e posizione degli interruttori proposte nello studio C3AI-CR-PL-001 rev C, da verificare sul modello 3D. |
| D-046 | approvata | **Scheda madre assemblata a mano dall'utente**: si fa produrre **solo il circuito stampato** (nudo), i componenti si saldano a mano. Regole di progetto: componenti a foro passante o SMD saldabili a mano (passivi da 0805 in su, SOIC/SOT/TSSOP, moduli con piazzole sul bordo come il WROOM); niente QFN, BGA né LGA sulla scheda: i sensori in LGA (IMU) restano su modulo o adattatore con connettore. **Componenti che scaldano di più sulla faccia interna**, attorno al foro della ventola, nel flusso d'aria (ventola al centro confermata, D-045). Distanza tra scheda madre e S3 da fissare a progetto completato, simulando lo spessore della scheda. | Utente 24/10/2026: "la ventola andrà bene al centro"; "metterei i componenti che scaldano di più all'interno così verrebbero investiti dal flusso d'aria della ventola"; "progetterei per essere assemblata da me, farei produrre soltanto il pcb". Interpretazione di "all'interno": faccia rivolta verso la S3, vicino alla ventola. |
| D-047 | approvata | **3,3 V del dominio sempre acceso con convertitore a commutazione** (proposto LMR36510, 65 V, 1 A, 26 µA a vuoto) invece del regolatore lineare dal 12 V. Motivi: con il front-end acceso per tutto il viaggio il lineare dissiperebbe 0,65-0,9 W dietro al display (D-031) contro circa 0,1 W; corrente fino a 1 A per MicroSD, VAN, IMU e RTC; dalla batteria circa un terzo della corrente a motore spento. Rischi gestiti a progetto: disturbi in onde medie (induttanza schermata, anello di commutazione corto, piano di massa, ferrite d'ingresso) e sulle misure analogiche (filtri RC, media nel firmware). | Utente 24/10/2026, dopo il confronto lineare/commutazione: "ok con il convertitore a commutazione". Schema C3AI-CR-EL-001 rev B; componenti non ancora ordinati né collaudati. |
| D-048 | approvata | **Piazzola termica dei regolatori saldata a mano dal retro** (U2 TPS54360B e U3 LMR36510, contenitore HSOIC con piazzola sotto il corpo, ammesso da D-046): si saldano prima i piedini laterali, poi si riempie di stagno dal lato opposto il foro sotto la piazzola. Il circuito stampato prevede sotto ogni piazzola i fori termici dell'impronta più un foro metallizzato centrale da circa 1-1,5 mm per far passare lo stagno; nessuna stazione ad aria calda richiesta. | Utente 24/10/2026, dopo la spiegazione del metodo: "ok per la saldatura piazzola". Diametro del foro da fissare nello sbroglio; metodo da provare sul primo esemplare. |
| D-049 | approvata | **GPIO2 del front-end per accendere la ventola**: comanda il P-MOSFET lato alto che stacca il 12 V della ventola a riposo (una ventola a 4 fili con il solo PWM non si ferma e consumerebbe a motore spento). GPIO2 è un pin di avvio: una resistenza da 100k lo tiene basso al reset, come richiesto dall'avvio dell'ESP32. Velocità su GPIO26 (ingresso PWM della ventola), giri su GPIO14. | Utente 24/10/2026, alla proposta dello schema C3AI-CR-EL-002: "1. ok". Non collaudato. |
| D-050 | approvata | **Modulo ESP32-WROOM-32E-H4/H8 del front-end montato a mano** come il resto della scheda (D-046), al posto del montaggio in fabbrica scelto il 20/10/2026: il modulo va comprato a parte e la sua piazzola di massa si salda dal retro come in D-048. Anche la presa USB-C a passo 0,5 mm della programmazione a banco si salda a mano. | Utente 24/10/2026: "2. montaggio a mano, per saldare l'usb-c non c'è problema". Fornitore della variante H4/H8 da trovare (non disponibile su Reichelt il 20/10/2026). |
| D-051 | approvata | **Soluzione mista moduli/chip sulla scheda madre**: il **ricevitore VAN** è il modulo blu SN65HVD230 (tipo HW-CAN-VP230, resistenza 121 rimossa, TX al 3,3 V tramite la scheda) su file di pin a passo 2,54 mm (4 vie 3.3V/GND/RX/TX e 2 vie CANH/CANL); la **MicroSD** è il modulo lettore (tipo HW-SD-MODULE) su fila di pin a 6 vie (3V3/CS/MOSI/CLK/MISO/GND); l'**RTC** resta il chip DS3231SN saldato sulla scheda (nessun LED da togliere, meno ingombro); l'IMU resta su modulo DIL-24. Moduli saldati, non solo infilati, per le vibrazioni. | Utente 24/10/2026, dopo il confronto moduli/chip: "soluzione mista". I moduli del Data Logger restano al logger (D-042); l'utente acquista sempre almeno 2 esemplari. Interasse delle file di pin e altezza dai file STEP dei moduli dell'utente (pin a 90° sostituibili con pin dritti). |

Nessuna nuova proposta tecnica è resa definitiva solo perché compare in una
risposta, nella distinta proposta o in un disegno. Per cambiare una decisione
approvata serve una nuova indicazione utente o la risoluzione esplicita di un conflitto.

## Questioni ancora aperte — non sono decisioni definitive

- **Richieste dell'utente del 23/10/2026**:
  1. **Interruttore generale del logger** ("spegnere il modulo k una volta nell'auto";
     precisato: spegnere tutto il logger). Proposta in
     [alimentazione-spegnimento.md](data-logger/docs/alimentazione-spegnimento.md): sul + 12 V
     dopo il fusibile, da usare dopo STOP; componente da scegliere (HW-LOGGER-SWITCH).
  2. **Aggiornamento del firmware dalla MicroSD**: firmware logger 0.4.0, compilato, non
     caricato né collaudato; procedura nel
     [README del firmware](data-logger/firmware/logger/README.md).
- Fonti di dati per l'IA (D-033): base prioritaria confermata dall'utente il 21/10/2026 ("sono i dati più importanti per valutare anomalie") = tutti i messaggi VAN, i PID OBD supportati, codici guasto e dati derivati. Sensori aggiuntivi rinviati dall'utente a dopo le prime acquisizioni ("li valuteremo dopo", 21/10/2026) (ricevitore GNSS anche per l'ora, microfono MEMS con sole caratteristiche del suono, sensore pressione/umidità). Posizione GNSS = dato personale, da trattare come il VIN (D-032).
- Sensore inerziale (accelerometro + giroscopio) richiesto dall'utente il 20/10/2026 per il cruscotto: modello, scheda di collegamento (front-end o S3), fissaggio e orientamento da definire; da valutare anche nel Data Logger perché il dataset contenga gli stessi dati. Modello scelto: **LSM6DSO su adattatore ST STEVAL-MKI196V1** (HW-IMU-LSM6DSO), ordinato dall'utente il 22/10/2026 su Farnell; scartati il BMI270 (ordine annullato dal venditore) e il Grove LSM6DS3 (mai ordinato).
- Mappa collegamenti del cruscotto (in definizione, 20/10/2026): ipotesi utente "molto probabilmente" scheda del quadro originale collegata e nascosta dietro il display, per evitare errori BSI (MAN-017 PDF 3: DATA/DATAB tra BSI e quadro, avvisi integrati nel quadro). Comandi al volante della radio originale da valutare come ingresso del cruscotto: percorso (VAN tramite COM 2000 o filo diretto alla radio) non verificato.
- Alimentazione: per il cruscotto D-030 (presa OBD via 16 permanente, via 1 chiave,
  da manuale e da verificare con la prova C3AI-CR-PR-001). Lo stesso punto è candidato
  anche per il logger (D-015); protezioni automotive e convertitore da scegliere.
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
potenziometri e generatori di segnali. Fluidità misurata a banco (DSP-M002/M003):
rendering LVGL 8-11 ms, 32 aggiornamenti dati/s; con PCLK 16 MHz il pannello si
ridisegna circa 39 volte al secondo (stima): l'obiettivo iniziale di 60 FPS va
rivisto o richiede temporizzazioni diverse, da provare.

## Hardware del cruscotto — stato al 21/10/2026

Scheda **ESP32-8048S050** (HW-DASH-DISPLAY), variante **senza touch** (D-027):
ESP32-S3-WROOM-1, 16 MB flash, 8 MB PSRAM octal (esptool), pannello RGB 800×480
con controller ST7262 secondo la fonte comunitaria. Pinout RGB, temporizzazioni a
16 MHz, retroilluminazione GPIO2 e PSRAM verificati a banco (DSP-M001); connettori
P1-P6 rilevati (DSP-M004). Backup della flash di fabbrica in
[data-logger/backups/esp32-8048s050](data-logger/backups/esp32-8048s050/README.md).
Limiti termici dichiarati dal rivenditore: −20…+70 °C, magazzinaggio +80 °C (D-031).
Dettagli e verifiche aperte nell'[inventario](data-logger/docs/hardware-inventory.md);
la precedente sezione "Diagnosi all'arrivo" è completata e sostituita da questa.
Architettura e collegamenti: D-028…D-031, [scheda madre](cruscotto/docs/scheda-madre.md).

## Stato del repository

Il data logger dispone di un primo [firmware diagnostico per il solo ESP32](data-logger/firmware/diagnostic/README.md),
con configurazione PlatformIO. Non acquisisce ancora dati dal veicolo.
Sorgenti logger aggiornati alla 0.3.1 (D-022), solo compilata; sulla scheda HW-394 resta la 0.3.0.
Sulla scheda del cruscotto è caricato ora **ui-idf 0.4.0** (ESP-IDF 5.5, doppio framebuffer, compiti separati, collegamento simulato, scatola nera ed etichette, DSP-M010); gli altri firmware di prova si ricaricano dai sorgenti. [Protocollo front-end ↔ S3](cruscotto/docs/protocollo-fe-s3.md) v1 con libreria comune `fe_link.h` e test host.
Il [logger 0.3.0](data-logger/firmware/logger/README.md) implementa registrazione
MicroSD, RTC, OLED, STOP, OBD KWP e ricezione VAN. Profili banco/veicolo separati;
sorgenti e GPIO proposti, non collaudati sul veicolo. Profilo banco 0.3.0 caricato e avviato il 20/10/2026: ATTESA SD
(modulo scollegato), RTC oscillator_stop; nessun collaudo veicolo.
Cruscotto digitale (D-026): scheda ESP32-8048S050 identificata (ESP32-S3, 16 MB
flash, 8 MB PSRAM, esptool), variante senza touch (D-027), backup di fabbrica in
[data-logger/backups/esp32-8048s050](data-logger/backups/esp32-8048s050/README.md).
[Prova display 0.1.0](cruscotto/firmware/display-test/README.md): compilata,
caricata e conforme a banco (DSP-M001): pinout RGB e PSRAM verificati. [Prova UI LVGL](cruscotto/firmware/ui-test/README.md) 0.1.1 (DSP-M003). Mappa dei collegamenti in definizione (D-028…D-030); [istruzione di prova presa OBD](disegni/CR-PR-001_prova-presa-obd.png) C3AI-CR-PR-001; [scheda madre preliminare](cruscotto/docs/scheda-madre.md) C3AI-CR-BL-001 rev D e studio d'ingombro C3AI-CR-PL-001 rev E (contorno D-045, montaggio a mano D-046, assieme 3D in cruscotto/meccanica); schema elettrico iniziato, fogli alimentazione C3AI-CR-EL-001 rev C, front-end C3AI-CR-EL-002 rev A e interfacce veicolo C3AI-CR-EL-003 rev B e sensori e memoria C3AI-CR-EL-004 rev B (proposte, D-051); [requisiti dell'interfaccia](cruscotto/docs/interfaccia-requisiti.md) in raccolta (D-041).

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
rev F (isteresi R10 D-022, disegno IEC D-024). NPN e comparatore, calcoli DC verificati; non montato o collaudato.
Installazione auto e protezioni ancora da progettare.

### Logger temporaneo: arresto manuale

D-015 sostituisce la proposta di mantenimento con batteria permanente, MOSFET
e rilevamento IGN. STOP chiude i file, conferma SALVATO e arresta acquisizione;
poi si toglie alimentazione. Il pulsante non interrompe direttamente la corrente.
Punto di prelievo auto ancora da verificare, nessun pin presunto.
