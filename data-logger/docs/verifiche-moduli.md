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

Utente: CR2032 non disponibile ("la pila non ce l'ho"); Data Logger in pausa
finché il modulo K-line non sarà pronto ("finché non avrò pronto il modulo K").
HW-RTC-BATTERY corretta da present_declared a candidate (da procurare).
Punto di ripresa: modulo K-line pronto; inoltre procurare la CR2032, misurarne la tensione e inserirla; poi
cablare la SD (W1–W6, EL-003 rev B) e fare la prima registrazione a banco con
impostazione UTC (`time ...Z`) e prova di mantenimento dell'ora dopo lo spegnimento.

## DSP-M001 — scheda display ESP32-8048S050, prova display 0.1.0 — 20/10/2026

Cruscotto digitale (D-026), HW-DASH-DISPLAY. Registrata qui come unico registro
moduli del repository.
**Prova eseguita:** firmware [display-test 0.1.0](../../cruscotto/firmware/display-test/README.md)
caricato su COM4 (CH340) a 921600 baud, hash verificati da esptool, dopo backup
della flash di fabbrica. Seriale letta dall'agente: `psram_found=1
psram_bytes=8386215 psram_free=7617827 panel=ESP_OK i2c_sda=19 i2c_scl=20 i2c_devices=0`.
**Osservazione riferita:** utente "tutto conforme" alla richiesta di otto barre
bianco, giallo, ciano, verde, magenta, rosso, blu, nero, senza sfarfallio o righe spostate.
**Interpretazione:** PSRAM in modo octal (qio_opi) funzionante con framebuffer
800×480 RGB565; pinout RGB (DE 40, VSYNC 41, HSYNC 39, PCLK 42, dati
8/3/46/9/1, 5/6/7/15/16/4, 45/48/47/21/14), ordine dei colori, temporizzazioni
a 16 MHz e retroilluminazione GPIO2 confermati per questa scheda. Nessun dispositivo
I2C su GPIO19/20, coerente con la variante senza touch (D-027). Non dimostra
stabilità prolungata, fluidità (FPS), comportamento termico, MicroSD o
alimentazione in auto; la luminosità non è regolata (solo acceso).
**Esito:** superata rispetto al criterio del README della prova.
**Prossimo passo:** prima interfaccia LVGL di prova con misura di FPS e memoria.

## DSP-M002 — prova UI LVGL 0.1.0 su ESP32-8048S050 — 20/10/2026

**Prova eseguita:** firmware [ui-test 0.1.0](../../cruscotto/firmware/ui-test/README.md)
(LVGL 8.3.11, dati simulati) caricato su COM4, hash verificati. Seriale letta
dall'agente: `panel=ESP_OK fps=32 refr_avg_ms=11 heap_int_free=230836 psram_free=7617827`,
stabile per oltre 10 s.
**Osservazione riferita:** "l'arco scorre abbastanza fluidamente, i numeri dei giri
hanno un po' di sfarfallio"; indicatore LVGL 62 FPS e 34% CPU.
**Interpretazione:** il rendering non è il limite (11 ms per aggiornamento). Il
contatore seriale (32) segue l'aggiornamento dei dati ogni 33 ms; il valore LVGL
(62) conta i cicli di refresh, non i quadri effettivamente mostrati dal pannello,
stimati in circa 39 Hz da PCLK 16 MHz e porch (calcolo, non misura). Lo sfarfallio
delle cifre è compatibile con copia nel framebuffer singolo non sincronizzata con
la scansione (tearing) e con lo spostamento dell'etichetta a larghezza variabile:
causa non ancora isolata.
**Esito:** non conclusiva per la fluidità; funzionamento LVGL su pannello superato.
**Prossimo passo:** etichetta a posizione e larghezza fisse, poi eventuale
sincronizzazione della copia con il vsync, confrontando l'osservazione.

## DSP-M003 — prova UI LVGL 0.1.1, cifre a posizione fissa — 20/10/2026

**Modifica:** ui-test 0.1.1, giri in quattro celle fisse da 34 px, una per cifra,
ridisegnate solo se cambiano. Caricato su COM4, hash verificati. Seriale:
`fps=32 refr_avg_ms=8 heap_int_free=230092 psram_free=7617827`.
**Osservazione riferita:** "no i numeri vanno bene" alla domanda se le cifre
sfarfallano ancora.
**Interpretazione:** lo sfarfallio di DSP-M002 era dovuto allo spostamento
dell'etichetta a larghezza variabile; il tearing del framebuffer singolo non è
risultato visibile in questa prova, ma non è escluso con schermate più pesanti.
Non verifica stabilità prolungata né comportamento termico.
**Esito:** superata (sfarfallio cifre risolto).
**Prossimo passo:** definire con l'utente contenuti e disposizione della prima
schermata reale del cruscotto.

## DSP-M004 — continuità P2 "IO19" ↔ P3 IO19 — 20/10/2026

**Misura riferita:** utente "c'è continuità" alla prova richiesta: scheda
ESP32-8048S050 scollegata da USB e alimentazione, UT210E in continuità/Ω, puntali
sul pin serigrafato IO19 di P2 e sul pin IO19 di P3.
**Interpretazione:** il primo pin di P2 è sullo stesso nodo di IO19 di P3: P2
espone IO19, IO11, IO12, IO13; la selezione della MicroSD (IO10 secondo la fonte
comunitaria) non è portata su P2. Non prova che il nodo sia proprio GPIO19 del
modulo né l'assenza di altri componenti sullo stesso nodo.
**Esito:** superata (serigrafia confermata come stesso collegamento).
**Prossimo passo:** tono di prova su IO17/IO18 con altoparlante su P6 per
identificare la funzione di U1.

## DSP-M005 — speak-test 0.1.0, tono 1 kHz, P6 in V~ — 20/10/2026

**Prova:** speak-test 0.1.0 caricato (hash verificati); ciclo 10 s tono 1 kHz su
IO17, 10 s su IO18, 10 s pausa, confermato dalla seriale. UT210E in V~ sui due
contatti di P6, nient'altro collegato.
**Misura riferita:** "rimane sempre praticamente a 0" in tutte le fasi.
**Interpretazione:** non conclusiva. Possibili cause: U1 non pilotato da IO17/IO18;
amplificatore con abilitazione su un altro pin; banda V~ del tester insufficiente
a 1 kHz (tipicamente decine-centinaia di Hz). Non dimostra l'assenza di
collegamento fra U1 e IO17/IO18.
**Esito:** non conclusiva.
**Prossimo passo:** ripetere con tono a 200 Hz (speak-test 0.1.1).

## DSP-M006 — speak-test 0.1.1, tono 200 Hz, funzione Hz — 20/10/2026

**Prova:** speak-test 0.1.1 caricato (hash verificati), ciclo confermato dalla
seriale. UT210E in Hz: prima sui due contatti di P6 ("niente"), poi come
riferimento con nero su GND di P4 e rosso su IO17/IO18 di P4 ("niente").
**Interpretazione:** il tester non si aggancia nemmeno al segnale diretto da
3,3 V sul pin che lo genera: con questo strumento la prova non distingue la
presenza del tono. Non dimostra né esclude il collegamento U1 ↔ IO17/IO18.
**Esito:** non conclusiva (limite dello strumento).
**Prossimo passo:** prova d'ascolto con un piccolo altoparlante su P6 quando
disponibile; nel frattempo l'assegnazione proposta evita comunque IO17/IO18
per la K-line.

## DSP-M007 — ui-idf 0.2.0 su ESP-IDF 5.5, doppio framebuffer — 21/10/2026

**Prova:** ui-idf 0.2.0 caricato su COM4 (hash verificati), avvio da `ota_0` con
la nuova tabella partizioni (D-039). Seriale: `panel=ESP_OK fps=13 refr_avg_ms=75
panel_hz=39 heap_int_free=333039 psram_free=6316724`, stabile per oltre 15 s;
`ota_state=2` (valido, caricamento via cavo).
**Osservazione riferita:** "l'immagine è molto stabile"; arco "un po' a scattini"
per i 13 FPS, "i numeri specialmente sono buoni".
**Interpretazione:** frequenza del pannello **misurata 39 Hz** (prima stimata).
Doppio framebuffer con scambio al vsync: nessun tearing riferito. Il ridisegno
completo in PSRAM (`full_refresh`) costa 75 ms e limita a 13 FPS.
**Esito:** superata per stabilità e assenza di tearing; fluidità non sufficiente.
**Prossimo passo:** `direct_mode` con sincronizzazione delle sole zone cambiate
tra i due framebuffer (ui-idf 0.2.1).

## DSP-M008 — ui-idf 0.2.1, direct mode con zone sincronizzate — 21/10/2026

**Prova:** ui-idf 0.2.1 caricato su COM4 (hash verificati), avvio da `ota_0`.
Seriale: `fps=26 refr_avg_ms=27 panel_hz=39 heap_int_free=333035 psram_free=6316724`.
**Osservazione riferita:** "l'arco è più fluido, non ci sono artefatti"; indicatore
LVGL tra 34 e 45 FPS, CPU tra 70 e 80%.
**Interpretazione:** il ridisegno delle sole zone cambiate con copia nell'altro
framebuffer porta i quadri utili a circa il limite dei dati simulati (aggiornamento
ogni 33 ms) mantenendo l'assenza di tearing. La CPU riferita dall'indicatore LVGL
include l'attesa del vsync e la copia delle zone: da ottimizzare (compito dedicato,
attesa non attiva) quando si separeranno i compiti sui due core.
**Esito:** superata (fluidità e assenza di tearing).
**Prossimo passo:** pubblicazione del blocco; poi protocollo front-end ↔ S3.
