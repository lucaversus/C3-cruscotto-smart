# Verifiche moduli — Data Logger

Registro iniziato il 19/10/2026. Prove finalizzate a SD, OLED e RTC su ESP32.
Nessun collegamento auto in questa fase.

## SD-M001 — lettore MicroSD

Richiesta: lettore scollegato, scheda rimossa, resistenza fra 3V3 e GND.
Risposta utente: **3 MOhm**; rimozione scheda e condizioni non confermate
separatamente. Dato riferito, non misurato direttamente dall agente. Non dimostra
compatibilita elettrica a 3,3 V o funzionalita SPI/scrittura. Prossimo passo:
identificazione lato opposto del lettore, poi prova funzionale quando cablato.

## RTC — preparazione verifica percorso batteria

19/10/2026: utente riferisce retro privo di scritte, con solo portabatteria.
Prossima misura richiesta: modulo completamente scollegato e pila rimossa,
modalita diodi, puntale rosso su VCC e nero sul contatto che tocca la faccia
positiva della pila. Lettura ancora non ricevuta; non prova corrente di ricarica
ne assenza di altri percorsi. Evitare conclusione di assenza ricarica dal solo OL.

## RTC-M001 — lettura riferita OL

19/10/2026: utente risponde OL alla misura diodi richiesta con rosso su VCC
e nero sul positivo portabatteria. Il precedente dubbio sul contatto centrale
non e risolto da una foto; identificazione del terminale e condizioni della
misura non confermate separatamente. Non equivale a prova di assenza ricarica.
Richiesta successiva: misura inversa, rosso positivo batteria e nero VCC, sempre
modulo scollegato e pila rimossa.

## RTC-M002 — verso inverso OL

19/10/2026: lettura utente OL anche nel verso inverso sugli stessi contatti.
Resta aperta l identificazione del contatto batteria: nessuna approvazione
all inserimento di CR2032 o conclusione sulla ricarica. Prossimo controllo
mirato: resistenza da GND del modulo al contatto centrale sul fondo del
portabatteria vuoto, modulo completamente scollegato.

## RTC-M003 — contatto centrale verso GND

19/10/2026: utente riferisce 0 alla misura richiesta in ohm fra GND modulo
e contatto centrale sul fondo del portabatteria vuoto. Coerente con negativo
a massa. Prossima misura: prova diodi da VCC (rosso) al contatto metallico
superiore/laterale che tocca la faccia positiva della pila (nero), senza
alimentazione e senza pila. Nessuna verifica di ricarica completata.

## RTC-M004 — percorso VCC verso positivo pila

19/10/2026: utente riferisce **1,35 V** in prova diodi, rosso VCC e nero
al contatto superiore/laterale positivo, dopo centrale identificato negativo
con RTC-M003. Percorso conduttivo rilevato in questa polarita; non e tensione
di carica e non quantifica la corrente a modulo alimentato. Non escludere
ricarica o inserire CR2032. Prossima richiesta: invertire puntali sugli stessi
contatti corretti, mantenendo modulo scollegato e pila rimossa.

## RTC-M005 — inverso sul positivo corretto: OL

19/10/2026: utente riferisce OL, rosso positivo portabatteria e nero VCC.
Con RTC-M004 (1,35 V diretto), rilevato percorso unidirezionale compatibile
con un ramo di ricarica; non e una misura della carica effettiva in esercizio.
Conclusione operativa: non dichiarare il modulo privo di ricarica e non
inserire CR2032 mentre il percorso resta presente. Chiedere sigla della pila
prima di scegliere un intervento; nessuna modifica hardware ancora effettuata.

## RTC — tipo pila confermato

19/10/2026: utente conferma prefisso CR dopo 2032: pila CR2032. Nessuna
modifica o inserimento autorizzati da una misura precedente. Serve identificare
e disabilitare il ramo di ricarica, poi verificarne l interruzione.

## D-019 — rimozione resistenza 201 scelta dall utente

19/10/2026: utente dichiara che eliminera la resistenza marcata 201 per
evitare ricarica della CR2032. Intervento programmato, non confermato eseguito.
Modulo scollegato e pila rimossa durante intervento; lasciare circuito aperto,
nessun ponticello al posto della resistenza. Dopo conferma esecuzione verificare
interruzione del percorso VCC verso pila prima di inserirla e mantenimento
dell ora in una successiva prova funzionale.


## Montaggio banco parziale — 20/10/2026

Utente: collegato tutto tranne il modulo SD, con pin da saldare e saldatore
non disponibile. Dichiarazione relativa al banco USB dello schema EL-003,
non collaudo dei moduli o conferma di collegamenti al veicolo.
La prima prova puo usare RTC/OLED/seriale senza lettore SD: firmware 0.3.0
resta in ATTESA SD, non crea sessioni e non avvia acquisizione.
STOP senza sessione segnala NESSUN FILE, non SALVATO.
Nessun nuovo firmware caricato in questo passaggio.

## Caricamento banco visibile — 20/10/2026, tentativo 1

COM3 CH340 rilevata da Windows e apertura seriale verificata. Tentato upload
profilo esp32-hw394-logger in PowerShell visibile. Esito: Failed to connect,
Wrong boot mode 0x13, download mode necessario. Fallimento prima della scrittura;
0.3.0 non dichiarata caricata. Nuovo tentativo predisposto in attesa BOOT manuale.
Log locale .tools/serial/upload-20261020-000728.log.

## Caricamento e avvio logger 0.3.0 — 20/10/2026

Secondo tentativo con BOOT manuale: esptool 4.9.0 su COM3 a 115200 baud,
segmenti verificati, SUCCESS. Log locale upload-20261020-000840.log.
Dopo riavvio EN tramite RTS, monitor visibile e file locale ricevono:

```text
c3_datalogger version=0.3.0 auto_start=1 kwp=0 van=0 no_radio=1 no_format=1
status state=ATTESA SD file= rows=0 dropped=0 rtc=oscillator_stop
storage=mount_failed retry_ms=10000
```

SD scollegata per pin da saldare: attesa e mancata registrazione previste.
RTC raggiungibile ma OSF attivo: ora non valida, nessuna impostazione effettuata.
Nessun collaudo SD, visualizzazione OLED, pulsante, batteria RTC o rete auto.
Il firmware sulla scheda ora e logger 0.3.0 banco, non piu il test SPI.
Terminale seriale lasciato aperto per l utente; salvataggi GitHub differiti.

## SD-M002 — lettore MicroSD sistemato (dichiarazione) — 20/10/2026

**Riferito:** utente "ho sistemato il modulo sd". Riferito al punto aperto
"saldare la strip pin prima del collegamento" (montaggio banco del 20/10/2026).
**Interpretazione:** intervento di montaggio dichiarato eseguito. Non dimostra
saldature prive di ponti, continuità dei sei contatti, alimentazione a 3,3 V o
funzionamento SPI/scrittura.
**Esito:** non conclusivo (intervento, non misura).
**Prossimo passo:** cablaggio W1–W6 secondo EL-003 rev B e prova di
registrazione a banco con firmware 0.3.0 già caricato.

## RTC-M006 — resistenza 201 rimossa (dichiarazione, D-019) — 20/10/2026

**Riferito:** utente "dissaldato la resistenza per evitare il caricamento della
pila". Riferito alla resistenza marcata 201 scelta in D-019.
**Interpretazione:** intervento D-019 dichiarato eseguito. Non dimostra ancora
l'interruzione del ramo VCC → positivo della pila rilevato in RTC-M004
(1,35 V in prova diodi), né l'assenza di ponti di stagno o di altri percorsi.
**Esito:** non conclusivo fino alla misura di verifica.
**Prossimo passo:** ripetere RTC-M004 nelle stesse condizioni (modulo scollegato,
pila fuori, prova diodi, rosso su VCC, nero sul contatto positivo del
portabatteria). Atteso OL al posto di 1,35 V. CR2032 ancora da non inserire.

## RTC-M007 — verifica interruzione ramo di ricarica: OL — 20/10/2026

**Misura riferita:** utente "ol". Condizioni richieste: modulo scollegato, pila
fuori, prova diodi, rosso su VCC, nero sul contatto positivo del portabatteria
(stessi punti di RTC-M004).
**Interpretazione:** il percorso VCC → positivo pila, che in RTC-M004 dava 1,35 V,
non conduce più dopo la rimozione della 201 (RTC-M006). Con RTC-M005 (OL nel
verso inverso, misurato prima dell'intervento) non risulta conduzione nella prova
diodi in nessuno dei due versi. Non misura la corrente reale a modulo alimentato,
la tensione della pila né il mantenimento dell'ora.
**Esito:** superata rispetto al criterio di RTC-M006 (OL atteso). D-019 eseguita.
**Prossimo passo:** misurare la tensione della CR2032 (attesi circa 3 V) e
inserirla nel portabatteria, con il modulo ancora scollegato.

## Pausa del progetto — 20/10/2026 (D-025)

Utente: CR2032 non disponibile ("la pila non ce l'ho") e progetto messo in pausa.
HW-RTC-BATTERY corretta da present_declared a candidate (da procurare).
Punto di ripresa: procurare la CR2032, misurarne la tensione e inserirla; poi
cablare la SD (W1–W6, EL-003 rev B) e fare la prima registrazione a banco con
impostazione UTC (`time ...Z`) e prova di mantenimento dell'ora dopo lo spegnimento.
