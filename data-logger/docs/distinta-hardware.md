# Distinta hardware — Cruscotto C3+AI / Data Logger

Revisione F — 18/10/2026. Proposta tecnica consolidata, non ordine di acquisto
né schema esecutivo auto. Fonte per disponibilità e collaudi: hardware.json.
Vincoli D-002, D-003, D-004, D-005, D-006, D-007, D-008, D-010 e D-011.
La richiesta di definire l'hardware non equivale ad approvazione di moduli
commerciali non identificati. Nessun componente candidato è segnato come ordinato.

## Lista corrente da usare per gli acquisti

Questa sezione sostituisce le precedenti proposte: D-013, D-014, D-015, D-016.
Le sezioni successive restano come storico tecnico, non come carrello corrente.

Gia presenti: ESP32 HW-394, basetta a morsetti, MCP2515 e modulo blu VP230.
Gia ordinati: lettore MicroSD, RTC DS3231 e OLED. Non ricomprarli.

| Quantita | Da procurare se non gia disponibile | Destinazione / limite |
| --- | --- | --- |
| 1 | Convertitore Uadme GYVRM-K240505, ASIN B0BFFDSNRC, uscita 5 V | Candidato gia esaminato; misurare uscita prima dell'ESP32. Non collaudato in auto |
| 1 | Portafusibile in linea e fusibile di ramo | Valore definitivo secondo cavo e carico; 2 A resta una proposta |
| 1 | Pulsante momentaneo normalmente aperto, a 2 contatti | STOP logico, non interruttore di potenza |
| 1 | 2N5551 NPN TO-92 | K-line, pinout secondo produttore |
| 1 + 1 | LM2903B in PDIP-8 e zoccolo DIP-8 | Ricevitore K-line del prototipo documentato |
| 1 ciascuna | Resistenze 330 ohm e 47 kohm, 0,25 W, 5% | K-line |
| 1 | Resistenza 510 ohm, 1 W, 1% | Pull-up per prova a banco, non da inserire automaticamente sulla linea auto |
| 1 ciascuna | Resistenze 68 kohm, 150 kohm e 4,7 kohm, 0,25 W, 1% | K-line |
| 2 | Resistenze 10 kohm, 0,25 W, 1% | K-line |
| 1 | Resistenza 1 kohm, 0,25 W | K-line |
| 1 ciascuno | Condensatore ceramico 100 nF ed elettrolitico 10 microfarad, 16 V | Alimentazione a 5 V del ricevitore |
| 1 | Jumper a 2 contatti con ponticello | Prova K-line a banco |
| 1 | Basetta millefori | Montaggio interfaccia K-line |
| 1 insieme | Morsetti, filo flessibile per segnali e alimentazione, guaina termorestringente e fascette | Lunghezze dipendenti dalla collocazione; niente acquisto di controconnettori presunti |
| 1 | Contenitore isolante con fissaggi per le schede | Dimensioni da scegliere sul montaggio reale |
| 1 se manca | MicroSD 16-32 GB | Possesso non confermato; verificare prima di duplicare l'acquisto |

Restano da identificare soltanto per completare il cablaggio specifico auto:
controconnettori/terminali per derivazione posteriore OBD e linea dietro al
cruscotto, lunghezze dei cavi e punto alimentazione. Non li dichiariamo scelti
senza identificazione. Il fronte OBD resta libero (D-007).
La distinta K-line e acquistabile per costruire il prototipo a banco descritto
in [kline-autocostruita.md](kline-autocostruita.md), non e una validazione del
collegamento all'auto. Nessun nuovo ordine e dichiarato.

Niente secondo modulo CAN, Pololu, UPS o circuito di mantenimento MOSFET.
Avvio automatico, STOP, chiusura SD e conferma SALVATO prima di togliere corrente.
Due sorgenti: OBD di sola lettura e tutti i messaggi ricevuti dalla linea dietro
al cruscotto, conservati anche senza decodifica e distinti per sorgente/tempo.

## Storico delle proposte precedenti

Le sezioni sotto documentano l'evoluzione: per gli acquisti prevale la lista corrente.

## Composizione della prima versione

| Funzione | Scelta di progetto proposta | ID / disponibilità | Accettazione ancora necessaria |
| --- | --- | --- | --- |
| CPU | Riutilizzare ESP32 HW-394 30 pin già identificato | HW-ESP32, presente | Prova contemporanea di acquisizione, buffer e scrittura SD |
| Cablaggio banco | Basetta a morsetti esistente | HW-ESP32-TERMINAL-BASE, presente | Corrispondenza morsetti/socket; fissaggio definitivo diverso dai fili volanti |
| Archivio | Lettore MicroSD SPI già ordinato | HW-SD-MODULE, in consegna | Modello ricevuto, livelli 3,3 V, picchi e prova di scrittura |
| Supporto dati | MicroSD 16-32 GB FAT32, preferenza high endurance | HW-SD-CARD, possesso non confermato | Prima verificare se già disponibile; capacità utile dipende dal volume reale dei log |
| Ora | DS3231/AT24C32 già ordinato | HW-RTC, in consegna | Pull-up, alimentazione, circuito batteria; tipo batteria scelto solo dopo controllo ricarica |
| Stato locale | OLED monocromatico I2C già ordinato | HW-OLED, in consegna | Controller, pinout e modello sul pezzo; nessun secondo display |
| OBD motore | Interfaccia K-line basata su L9637D, UART ESP32 e adattamento TX/RX adeguato | HW-KLINE-INTERFACE, candidato | Selezionare modulo con schema, verificare livelli, protezioni e supporto fast init; identificare anche adattatore già usato nell'app |
| BSI / VAN comfort | Valutare il modulo blu SN65HVD230 esistente come ricevitore e decodifica software ESP32 | HW-CAN-VP230, presente non collaudato | Ricezione valida sul bus identificato, nessuna terminazione aggiunta, trasmissione inibita in hardware, livelli/protezioni verificati |
| CAN eventuale | Conservare MCP2515 8 MHz + VP230 già presente | HW-CAN-MCP2515, SPI collaudato | Non richiesto per leggere K-line o VAN; traffico CAN ancora non collaudato |
| Alimentazione | Ingresso auto protetto, conversione a 5 V e distribuzione 3,3 V dimensionata | HW-AUTO-POWER, candidato | Modello/valori e punto di prelievo da definire: vedi requisiti sotto |
| Connessione auto | Derivazione posteriore a T, oppure punto equivalente documentato, mantenendo OBD frontale libera | HW-OBD-HARNESS, candidato | Controconnettori reali, punto VAN, pin K-line e masse da identificare su schema specifico |
| Montaggio | Scatola isolante, fissaggi, PCB/adattatori saldati e connettori bloccabili; cavi adeguati | Accessori non ancora inventariati come posseduti | Distinta meccanica dipendente da dimensioni moduli e posizione scelta |
| Comandi | Avvio automatico; nessun pulsante nella prima versione | D-004 / D-005 | Nessun acquisto pulsanti ora |

## Requisiti delle interfacce

### K-line

Il L9637 è un candidato di interfaccia elettrica ISO 9141, non un interprete
KWP completo: fast init, messaggi, timeout e gestione degli errori restano nel
firmware ESP32. La tensione sulla linea auto non deve raggiungere i GPIO.
La scheda da comprare deve avere schema disponibile e livelli TX/RX compatibili
tramite adattamento documentato. Non basta un'inserzione che dica ESP32/Arduino.
Non fissare valori di pull-up/adattamento prima di vedere lo schema della scheda.

### VAN passivo

La documentazione VanBus riporta SN65HVD230 con ricezione VAN e decoder nel
microcontrollore. Questo consente una verifica del materiale già presente prima
di comprare altra interfaccia. Il chip non decodifica il protocollo da solo;
il controller MCP2515 non svolge questa funzione. Non copiare collegamenti
radio generici sul connettore della specifica C3 senza schema.
Non collegare il modulo blu con la resistenza 120 ohm ancora inserita alla rete
VAN: prima identificarla e predisporre assenza di carico di terminazione aggiuntivo.
Verificare inibizione fisica del trasmettitore e prestazioni del ricevitore nella
modalità scelta. Nessun cablaggio RS/TXD viene approvato da questa distinta.

## Alimentazione per installazione definitiva

Una scheda ESP32 alimentata da USB a banco non è un alimentatore automotive.
L'insieme da dimensionare comprende:

- fusibile vicino al punto di prelievo, sezione fili e portafusibile coerenti;
- protezione da inversione e sovratensioni/transitori, inclusi quelli non
  sopportabili dal convertitore scelto; coordinamento delle protezioni;
- conversione 12 V nominali verso 5 V regolati, con margine sui picchi misurati;
- alimentazione 3,3 V dei moduli con budget di corrente verificato, senza
  presumere sufficiente il regolatore della basetta o dell'ESP32;
- rilevazione perdita alimentazione e riserva energetica sufficiente alla
  chiusura dei file, dimensionata da corrente e tempo effettivo misurati;
- gestione spegnimento e assorbimento a vettura ferma.

Un generico modulo step-down 12/5 V non soddisfa automaticamente questi requisiti.
Punto quadro suggerito dall'utente ancora non convalidato: nessun pin o valore
fusibile/TVS/condensatore è scelto senza dati del circuito e carichi.

## Cosa possiamo fissare e cosa manca per ordinare

Base di riuso proposta: ESP32 esistente, SD/RTC/OLED già ordinati, VAN passivo
con verifica del VP230 presente; K-line come interfaccia aggiuntiva da selezionare.
MCP2515 conservato, nessun nuovo CAN o controller TSS463 da ordinare ora.

Non è ancora possibile rilasciare una distinta completa pronta per l'acquisto:
1. verificare modello/schema di un modulo K-line e adattamento logico;
2. dimensionare e scegliere alimentazione/protezioni/chiusura SD;
3. identificare controconnettori e punti di accesso auto;
4. riscontrare modelli dei pezzi in consegna e disponibilità MicroSD.

Queste voci non sono dettagli che si possono presumere dal codice BSI.
Non bloccano lo sviluppo a banco di archivio, RTC e acquisizione simulata.
Nessun firmware o schema grafico viene modificato da questa distinta:
i disegni precedenti restano proposte non esecutive per il collegamento auto.

## Fonti primarie e limiti

- [ST L9637, pagina prodotto e datasheet](https://www.st.com/en/automotive-analog-and-power/l9637.html): interfaccia K-line ISO 9141; non selezione di un modulo commerciale specifico.
- [VanBus, sezione Schematics](https://github.com/0xCAFEDECAF/VanBus#-schematics): esperienza dell'autore con SN65HVD230 e VAN, non certificazione del nostro modulo.
- [TI SN65HVD230](https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf): caratteristiche del chip, ingressi e modalità; non schema del modulo blu.
- [ESP32 RMT VAN RX](https://github.com/morcibacsi/esp32_rmt_van_rx): possibile decoder open source; integrazione con SD/RTC ancora da verificare.

## Proposta concreta K-line — 18/10/2026

Candidato raccomandato: **MikroE ISO 9141 Click, MIKROE-4331**, basato su L9637D.
UART con logica selezionabile 3,3/5 V; JP1 da impostare su 3V3. VS bus separata
4,5-36 V secondo documentazione; non confondere VS con alimentazione logica.
È un transceiver, non un interprete ELM: KWP e fast init saranno nel firmware.
Si può collegare tramite contatti/cablaggio adeguato senza acquistare una
scheda madre mikroBUS né software MikroE a pagamento. Non ancora ordinato.
Schema ufficiale v101 consultato; verifica fisica dei livelli e circuito bus
completo richiesta prima dell'auto. Non richiede di scegliere alla cieca un
convertitore UART esterno, poiché la scheda prevede logica 3V3 selezionabile.

- [Produttore](https://www.mikroe.com/iso-9141-click)
- [Schema v101](https://download.mikroe.com/documents/add-on-boards/click/iso_9141_click/iso-9141-click-schematic-v101.pdf)
- [Farnell Italia, codice 4696642](https://it.farnell.com/mikroelektronika/mikroe-4331/development-boardseval-kits/dp/4696642)

Prezzo e stock sono dati variabili: verifica al momento dell'ordine.

## Alternative per indisponibilita MIKROE-4331 — 18/10/2026

Utente non trova MIKROE-4331 disponibile. Nessun ordine o cambio definitivo.

- **E-L9637D da assemblare:** il chip e venduto separatamente, formato SOIC-8;
  occorrono adattatore/PCB, componenti del circuito e saldatura, non e un modulo
  pronto. Schema, alimentazione e livelli restano da progettare e verificare.
  [DigiKey](https://www.digikey.it/it/products/detail/stmicroelectronics/E-L9637D/1852145).
- **Freematics OBD-II UART Adapter V2.1:** adattatore completo con UART compatibile
  3,3/5 V dichiarata, libreria open source e interprete AT. Prezzo sul negozio
  consultato 87 USD, prima di costi di acquisto/spedizione. Non e solo un
  transceiver e non sostituisce l'acquisizione VAN. Richiede derivazione
  posteriore per lasciare libera la presa frontale (D-007). Verificare supporto
  e prova KWP fast init sulla C3 prima di promuoverlo a interfaccia collaudata.
  [Produttore](https://shop.freematics.com/products/freematics-obd-ii-uart-adapter-v2-1-for-arduino).

Prezzi, stock e consegna sono variabili; nessuna promessa di disponibilita
alla destinazione italiana senza verifica al momento dell'ordine.

## Proposta utente: interfaccia discreta — valutazione preliminare

Due NPN (2N2222/BC547) oppure PC817, pull-up 510 ohm/0,5 W e resistenze
4,7/10 kohm sono una proposta, non una distinta approvata. Nessun possesso
di questi componenti confermato. Serve lo schema per verificare livelli RX,
inversione logica TX/RX, correnti, polarizzazione e comportamento al reset.
Non aggiungere pull-up alla linea auto senza valutare il circuito complessivo.
Su 510 ohm, con linea tenuta bassa e 14,4 V, la dissipazione ideale e
14,4^2/510 = 0,407 W; a 16 V e 0,502 W. La resistenza da 0,5 W proposta
non ha margine sufficiente per essere fissata come scelta automotive definitiva.
PC817 richiede verifica di CTR e tempi di commutazione nel circuito effettivo;
non e una sostituzione automatica del circuito a transistor e non prova
isolamento galvanico completo se alimentazioni/masse restano comuni.

Software: UART ESP32 a 10400 baud, normalmente 8N1, con KWP2000/ISO14230,
checksum, timeout ed eco. ISO-TP per CAN/ISO15765 non e il protocollo da usare.
Fast init richiede impulsi temporizzati sulla linea prima del messaggio UART:
non consiste solo nell'inviare byte a 10400 baud. Nessun codice caricato.
Riferimenti: [progetto dell'autore con schemi alternativi](https://github.com/muki01/OBD2_K-line_Reader),
[libreria K-line](https://github.com/muki01/OBD2_KLine_Library),
[ELM327, inizializzazione e parametri temporali](https://elmelectronics.com/wp-content/uploads/2020/05/ELM327DSL.pdf).

## Scelta D-013: costruzione in proprio

Il 18/10/2026 l’utente sceglie circuito autocostruito. Le precedenti proposte
MIKROE/Freematics restano tracciate, non sono acquisti o materiale posseduto.
La soluzione tecnica corrente è [prototipo NPN + comparatore, rev A](kline-autocostruita.md).
Distinta componenti per banco e schema con cartiglio allegati; progetto auto
protetto e collaudi ancora aperti. Due soli NPN e PC817 non sono la soluzione
implementata nel disegno.

## Candidato alimentazione proposto dall'utente — 18/10/2026

[Uadme, ASIN B0BFFDSNRC](https://www.amazon.it/dp/B0BFFDSNRC), modello dichiarato
GYVRM-K240505. Scheda letta direttamente tramite browser Work:
8-40 V ingresso; 5 +/-0,25 V uscita; 5 A, 25 W massimi dichiarati; non isolato;
60 x 24,5 x 20 mm. Protezioni commercialmente dichiarate: sovra/sottotensione,
sovraccarico, surriscaldamento e corto. Soglie e condizioni non specificate.
Non confondere la dichiarazione generica di protezione con prova ISO 7637/16750
o tolleranza al load dump. Inversione di polarita non dimostrata dalla pagina.

Potenza nominale plausibilmente sufficiente al logger, ma picchi e regolazione
vanno misurati. Ingresso minimo 8 V: continuita durante avviamento non garantita.
Non comprende chiusura SD o riserva energetica documentate. E un candidato di
conversione da valutare con protezioni esterne, non un alimentatore completo
approvato per l'auto. Nessun ordine confermato. Pololu D36V28F5 citato qui come storico; successivamente escluso dall'utente (D-014).

## Secondo candidato Amazon: MP1584EN — 18/10/2026

[LAOMAO B0B92WYRR4](https://www.amazon.it/dp/B0B92WYRR4), 6 moduli regolabili:
ingresso 4,5-28 V, uscita 0,8-20 V, corrente 3 A massimi dichiarati nella
pagina letta direttamente tramite browser Work. Adatto da valutare per prove
su alimentazione pulita, regolando e misurando prima l'uscita a carico scollegato.
Non scelto per collegamento diretto auto: minore margine di ingresso rispetto
ai candidati 40/50 V, nessuna protezione automotive completa documentata,
uscita affidata a regolazione con trimmer. Il valore massimo di corrente non
certifica la corrente continua ottenibile sulla specifica schedina.
Nessun ordine o possesso confermato; nessun acquisto di un kit di sei moduli
necessario al solo Data Logger sulla base della presente valutazione.

## Alimentazione: proposta completa del circuito normale

Pololu escluso da acquisto (D-014). Base economica Uadme e circuito di
mantenimento/spegnimento: [distinta e netlist](alimentazione-spegnimento.md).
La batteria dell’auto resta disponibile fino alla chiusura dei file; nessun UPS
autonomo aggiunto. Richiede +12 permanente, massa e IGN identificati.
Nessun pin auto assegnato, nessun collaudo hardware o ordine dichiarato.

## Versione corrente semplificata — D-015

Prevale sulle proposte precedenti: logger temporaneo per pochi giorni,
avvio automatico e pulsante STOP prima di spegnere l'auto. Circuito di
mantenimento MOSFET, IGN separato per arresto, UPS e riserva energetica ritirati.
Non ordinare i componenti di quel circuito. La K-line resta autocostruita.

Materiale corrente: ESP32 e moduli gia censiti; SD/RTC/OLED ordinati;
componenti K-line in kline-autocostruita.md; Uadme candidato; portafusibile di
ramo con fusibile adeguato (proposta 2 A da riscontrare), un pulsante NO,
fili/morsetti/contenitore. Consultare alimentazione-spegnimento.md rev B.
Il segnale SALVATO compare solo dopo chiusura SD riuscita; fino a quel momento
l'alimentazione resta presente. Il pulsante non taglia corrente.

## Precisazione acquisizione — D-016, 18/10/2026

Due ingressi: OBD con HW-KLINE-INTERFACE per diagnosi di sola lettura, e
linea dietro al cruscotto con ricevitore da verificare (HW-CAN-VP230 candidato
per VAN). Conservare tutti i messaggi ricevuti dalla linea, anche non decodificati;
correlare con richieste/risposte OBD tramite timestamp e sorgente. Nessun
pin del connettore cruscotto è assegnato; non confondere il punto richiesto
con un protocollo già misurato. Nessuna garanzia di acquisizione senza perdite
prima del collaudo. D-007 lascia libero il fronte OBD.
