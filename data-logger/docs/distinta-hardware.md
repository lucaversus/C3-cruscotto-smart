# Distinta hardware — Cruscotto C3+AI / Data Logger

Revisione A — 18/10/2026. Proposta tecnica consolidata, non ordine di acquisto
né schema esecutivo auto. Fonte per disponibilità e collaudi: hardware.json.
Vincoli D-002, D-003, D-004, D-005, D-006, D-007, D-008, D-010 e D-011.
La richiesta di definire l'hardware non equivale ad approvazione di moduli
commerciali non identificati. Nessun componente candidato è segnato come ordinato.

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
