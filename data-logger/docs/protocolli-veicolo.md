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
