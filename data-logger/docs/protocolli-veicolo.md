# Protocolli veicolo — Cruscotto C3+AI / Data Logger

Revisione 2, 18/10/2026. Evidenze, non schema di collegamento al veicolo.
Ambito D-006, D-008, D-011 e D-012; HW-CAN-MCP2515, HW-CAN-VP230 e HW-SCANNER.

## Cosa mostrano le nuove foto

- `ecu obd.png`: protocollo UCE 5, ISO 14230-4 KWP, fast init,
  10,4 kbaud; campo generico ECU address/CAN Id: 10; calibrazione 9656710099.
  Il nome del campo non rende l'indirizzo un identificativo CAN; formato
  numerico non precisato dall'app, non convertito arbitrariamente in esadecimale.
- `targhetta.jpg`: etichetta pressioni pneumatici con codice di produzione;
  la sequenza iniziale sembra 10375, lettura visiva non certificata.
  Non è l'etichetta identificativa BSI e non codifica da sola la topologia rete.
  Originale con identificativo veicolo conservato solo localmente, escluso da Git.
- `obd presa.jpg`: presa diagnostica e parte della scatola fusibili/BSI.
  Non consente di identificare con sicurezza ogni contatto cablato, l'assegnazione
  dei fili posteriori o il codice completo della BSI: etichetta inferiore tagliata.

Gli originali di tutte e tre le foto sono conservati localmente nella cartella
ignorata `.tools/hardware-photo-originals/`. Nessuna delle tre nuove immagini
è pubblicata: il controllo automatico ha richiesto autorizzazione specifica
per il possibile identificativo veicolo. Le trascrizioni tecniche non includono VIN.

## Conclusione tecnica e livelli di certezza

**Diagnosi motore: nuova evidenza diretta a favore di KWP2000 su K-line,
fast init, 10,4 kbaud.** La tabella ufficiale ELM associa questo alla selezione 5.
Lo screenshot è evidenza del protocollo riportato dall'app, non una cattura
fisica della linea o un log della negoziazione. Non dedurre da esso il protocollo
usato per diagnosticare la BSI o la rete che collega BSI e quadro.

**Conflitto conservato:** la vecchia foto Creader indicava CAN, con la stessa
calibrazione 9656710099. Non si elimina quella foto né si dichiara dimostrato
che entrambi i protocolli siano disponibili. Per il progetto la precedente
assunzione di OBD su CAN viene ritirata; K-line è il riferimento provvisorio
per la diagnosi motore, da confermare con una connessione corrente riuscita
e lettura del protocollo negoziato (ATDP/ATDPN se l'adattatore è compatibile ELM).
Non è ancora nota l'identità o la disponibilità dell'adattatore usato nell'app.

**Rete BSI: non identificata definitivamente su questo esemplare.**
La documentazione formativa Citroen C3 del dicembre 2001 descrive una BSI
che collega CAN del gruppo motore e più reti VAN; VAN comfort a 125 kbit/s
per quadro/display/radio e altri servizi. È un'ipotesi coerente per una prima C3,
non una prova applicabile a tutte le revisioni 2005. La BSI è un gateway:
parlare di un unico suo protocollo confonde rete abitacolo e diagnostica.
Non estendere il bitrate della documentazione alla specifica auto senza verifica.

Per chiudere la variante serve codice ricambio/famiglia BSI leggibile e riscontro
con schema specifico della variante di produzione, oppure identificazione
non invasiva del segnale su un punto già identificato da documentazione.
Le tre foto attuali non permettono di assegnare pin, bitrate o decoder BSI definitivi.

## Conseguenze per il Data Logger

- Nessun collegamento al veicolo viene autorizzato da questa analisi.
- MCP2515 e VP230 sono interfacce CAN: la prova SPI M-010 non dimostra accesso
  alla diagnosi K-line, alla rete VAN o alla rete CAN interna dell'auto.
- Se si usa K-line occorre un'interfaccia elettrica K-line adatta e un gestore
  KWP/inizializzazione; non collegare K-line direttamente a ESP32 o ai terminali H/L.
- Se il quadro usa VAN, un MCP2515 non decodifica i frame VAN cambiando bitrate.
- Nessun nuovo modulo è stato scelto, ordinato o dichiarato mancante.
  Gli schemi esistenti restano proposte di banco, senza pin auto esecutivi.

## Fonti consultate

- [Elm Electronics ELM327DSL, p. 27 e descrizione ISO/K-line](https://elmelectronics.com/wp-content/uploads/2020/05/ELM327DSL.pdf).
- Citroen, *C3 Technical Introduction*, rif. i.1.352, dicembre 2001,
  sezione 1 pp. 1-7, [riproduzione del documento del costruttore](https://www.scribd.com/document/759219550/C3-TECHNICAL).
  Documento storico generale: non certifica la variante della vettura.
- Foto fornite dall'utente il 18/10/2026: copie locali, non incluse nel repository.

## Aggiornamento: etichetta BSI identificata — 18/10/2026

Nuova foto `BSI ID.jpg`, originale archiviato soltanto localmente:
- riferimento 9653667330;
- variante BSI F02-00;
- livello MG.

La tabella del costruttore Peugeot D6AN012EP0, sezione 3.6, identifica F02-00
come Siemens Light 2001 VAN, livello medio. Questa corrispondenza di famiglia
rende l'architettura CAN/VAN una conclusione documentale, più forte della
precedente ipotesi fondata sul solo anno. La tabella consultata elenca applicazioni
Peugeot: non equivale a uno schema dei connettori della C3 specifica.

La documentazione C3 già citata descrive VAN comfort 125 kbit/s verso
quadro/display/radio e CAN del gruppo motore: la BSI collega reti diverse.
La diagnosi motore KWP dello screenshot rimane separata da queste reti.
Non si conclude che la diagnosi BSI usi necessariamente il medesimo protocollo.

Superata la precedente necessità di ottenere il codice etichetta. Restano
piedinatura dello specifico connettore, conferma dei livelli e del bitrate sul
veicolo e decodifica dei dati; nessuna misura sul bus effettuata.
MCP2515 non può decodificare VAN; nessun acquisto o collegamento viene deciso.

Fonte aggiuntiva: [riproduzione del documento Peugeot D6AN012EP0, identificazione BSI](https://www.scribd.com/document/485332590/peugeot-BSI).

## Precisazione interfaccia VAN — 18/10/2026

L'affermazione precedente sulle interfacce CAN va distinta per funzione:
MCP2515 è un controller CAN e non può decodificare frame VAN. Il transceiver
SN65HVD230 separato (HW-CAN-VP230) può invece essere valutato come ricevitore
fisico VAN con decoder software ESP32; questa applicazione è documentata
dall'autore di [VanBus](https://github.com/0xCAFEDECAF/VanBus#-schematics).
Non è una certificazione TI di compatibilità VAN né un collaudo sul nostro modulo.
Controllare resistenza di terminazione, livelli, protezioni e inibizione del
trasmettitore prima dell'uso. Non ordinare un secondo modulo VAN ora.

## Prerequisiti bloccanti per l'ascolto VAN — 20/10/2026 (D-022)

Prima di collegare HW-CAN-VP230 alla linea dietro al quadro (D-016, D-017), tutti
i punti seguenti devono risultare superati e registrati in `verifiche-moduli.md`.
Se uno manca, il collegamento non si esegue. Motivo: il bus VAN comfort serve
quadro, display e radio; un carico o un trasmettitore attivo possono disturbarli.

1. **Terminazione rimossa.** La resistenza marcata 121 (120 ohm) del modulo, se
   collegata tra H e L, va scollegata. A modulo non alimentato, misurare H-L:
   valore atteso nell'ordine dei kohm o superiore, non circa 120 ohm.
2. **Trasmettitore inibito in hardware.** Il pin TX del modulo (ingresso D del
   transceiver) collegato direttamente a 3V3 del modulo, mai flottante e mai a un
   GPIO ESP32. Verificare continuità TX-3V3 a modulo non alimentato.
3. **Stato recessivo a banco.** Modulo alimentato a 3,3 V, H e L scollegati da
   qualsiasi bus: tensione differenziale H-L prossima a 0 V (recessivo). Un valore
   dell'ordine di 2 V indica driver attivo: non collegare.
4. **Uscita RX.** Livello a 3,3 V sul pin RX verso GPIO34; nessuna tensione oltre 3,3 V.
5. **Punto di collegamento identificato** su fonte documentale della variante
   (biblioteca tecnica) e conferma elettrica, come richiesto da D-008.

Il firmware non trasmette su VAN, ma non può garantire queste condizioni:
sono verifiche fisiche a cura dell'utente (D-020). Stato al 23/10/2026: prove 1-4 superate
a banco (`verifiche-moduli.md`, VAN-M002…M005); prova 5 (punto sul veicolo) da eseguire.

## Decodifiche VAN pubblicate dalla comunità — 20/10/2026

Ricerca richiesta dall'utente (D-026). Fonti comunitarie, non del costruttore:
descrivono vetture PSA simili, **non verificate sulla nostra C3**. Servono a
interpretare i frame grezzi già previsti dal logger (D-016), non a collegarsi.

- [pinterpeti.hu, PSA VAN bus](http://pinterpeti.hu/psavanbus/PSA-VAN.html):
  tabelle per Peugeot 206, 307, 406 S2 e **Citroën C3 2004**, con stato di
  decodifica per ogni IDEN. Esempi rilevanti per il cruscotto:

  | IDEN | Da → a | Contenuto dichiarato | Decodifica |
  | --- | --- | --- | --- |
  | 824 | BSI → quadro | giri motore e velocità | parziale |
  | 8A4 | BSI → vari | luminosità quadro, chilometraggio, temperatura acqua ed esterna, motore avviato | ~90% |
  | 4FC | BSI | stato luci e spie | (file separati) |
  | 564 / 524 | BSI → display | stato vettura e messaggi/avvisi | parziale |
  | 664 | quadro → BSI | pulsanti (emergenza, chiusura, luminosità) | parziale |
  | 8FC | — | contachilometri, letto all'avviamento | 100% |
  | 9C4 | COM 2000 → broadcast | **comandi radio al volante** (volume, ricerca, sorgente, rotella) | quasi completa |
  | E24 | BSI → radio | **VIN in chiaro**, trasmesso periodicamente | 100% |

- [0xCAFEDECAF/VanBus](https://github.com/0xCAFEDECAF/VanBus) (MIT): libreria
  ESP32/ESP8266 per VAN a 125 kbit/s; con SN65HVD230 a 3,3 V. Il solo partitore
  resistivo su ESP32 dà molti errori CRC secondo l'autore.
- [0xCAFEDECAF/VanLiveConnect](https://github.com/0xCAFEDECAF/VanLiveConnect):
  decodificatore completo (`VanIden.h`, `PacketToJson.ino`) collaudato su una
  Peugeot 406 del 2003: velocità, giri, carburante, temperatura motore, spie,
  contachilometri, avvisi. Collegamento documentato su DATA/DATA B dei pin 2-3
  del blocco ISO "A" della radio: possibile punto di ascolto alternativo al quadro,
  da verificare sulla nostra radio.

Conseguenze:

1. I comandi al volante (9C4) risultano trasmessi sul VAN dal COM 2000: ipotesi
   favorevole per usarli come tasti del cruscotto in solo ascolto, da confermare.
2. **Privacy:** E24 contiene il VIN. Nei log grezzi D-016 il VIN comparirà:
   escluderlo o mascherarlo prima di pubblicare o condividere dati (AGENTS.md).
3. Nessuna di queste fonti autorizza trasmissioni sul bus o collegamenti prima dei
   prerequisiti D-022. La lunghezza di alcuni frame varia con l'anno di produzione.

Lato motore (K-line): per il DV4TD 8HZ un catalogo commerciale indica centraline
Siemens SID802/SID804/SID806 o Bosch EDC16C34; il tipo montato sulla nostra auto
non è identificato. Nessuna lista PID pubblica trovata per questa centralina: si
parte dai PID standard OBD (modo 01, PID 00 per quelli supportati) e si verifica.

## Dotazioni dichiarate della vettura — 20/10/2026

Utente: radio originale con comandi al volante; climatizzatore **automatico** con
sonda temperatura abitacolo sulla plancia ai lati della radio; **sensore pioggia
e luminosità** per tergicristalli e luci automatiche. Dichiarazioni, non verificate
sull'auto. MAN-017 PDF 3 indica che la BSI comanda luci e tergicristalli anche
in base al sensore pioggia. Per il cruscotto: stato luci e luminosità quadro
(IDEN 4FC e 8A4 nelle decodifiche comunitarie) candidati per la regolazione
giorno/notte del display; temperatura abitacolo da cercare sul VAN (non trovata
nelle decodifiche pubblicate); nessuna derivazione sui fili delle sonde.

## Connettore del quadro 0004 dagli schemi — 20/10/2026

Lettura **visiva** degli schemi renderizzati in locale (MAN-017 PDF 5, pag. 94
"Fendinebbia"; MAN-006 PDF 14 "Motorino avviamento", PDF 78 "Informazioni freni
DV4TD", PDF 111 "Ventilazione - riscaldamento"). Coerente in tutti e quattro:

| 0004, connettore 18 vie nero (18V NR) | Filo | Altro capo |
| --- | --- | --- |
| via 1 | 9004A (multiplex, tratto marcato) | BSI1 connettore 10V NR via 8 (filo 9004) |
| via 3 | 9005A (multiplex) | BSI1 10V NR via 10 (filo 9005) |
| via 7 | XE1 (multiplex) | BSI1 10V NR via 6 (filo XE) |
| via 9 | M0004, massa | punto di massa MC35 |

- 9004/9005 sono la coppia DATA/DATAB della rete VAN tra BSI e quadro (MAN-017
  PDF 3); quale dei due sia DATA non è indicato. XE è il terzo filo multiplex,
  probabilmente risveglio/alimentazione rete (il testo parla di 4 fili, due di
  alimentazione): funzione da confermare, **non collegarlo**.
- La stessa terna 9004/9005/XE raggiunge anche il blocco radio "84--" (linee
  tratteggiate = secondo equipaggiamento, MAN-006 PDF 14) e il comando
  climatizzazione 8025 (PDF 111): conferma documentale che quadro, radio e clima
  sono sulla stessa rete VAN della BSI. Il COM 2000 (CV00) è invece su un'altra
  coppia multiplex (9012/9013, BSI connettore 40V BA).
- Alimentazioni +12 V del quadro: non presenti in queste pagine, da cercare.
- Schemi di manuale generale RTA: variante e numerazione da riscontrare a vista
  sul connettore reale prima di qualsiasi derivazione; nessuna misura con
  multimetro sui fili multiplex (MAN-017 PDF 3).

Aggiornamento 21/10/2026, D-032: il VIN (IDEN E24) non viene filtrato dal logger;
va mascherato in post-elaborazione prima di qualsiasi pubblicazione o condivisione.
