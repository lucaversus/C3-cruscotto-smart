# Firmware S3 su ESP-IDF 5.5 — versione 0.3.0

Cruscotto C3+AI, HW-DASH-DISPLAY (D-026, D-037, D-039). Base del futuro firmware
dell'S3 su **ESP-IDF 5.5** (piattaforma PlatformIO ufficiale espressif32@6.12.0),
al posto di Arduino-ESP32 2.x. Stato: **0.3.0 caricata il 21/10/2026** (DSP-M009: compiti separati, collegamento fe_link simulato in loopback). Precedenti: DSP-M007 (0.2.0, stabile ma 13 FPS) e DSP-M008 (0.2.1 direct mode, superata: fluido, nessun artefatto, pannello 39 Hz misurati).

## Cosa cambia rispetto a ui-test 0.1.1

- **Doppio framebuffer** in PSRAM (`num_fbs = 2`): LVGL disegna l'intera schermata
  nel buffer non visibile (`full_refresh`); lo scambio avviene al **vsync**, per
  eliminare il tearing. Bounce buffer da 10 righe e ripartenza al vsync
  (`CONFIG_LCD_RGB_RESTART_IN_VSYNC`), utili anche con il Wi-Fi (D-036).
- Seriale: `panel_hz` = vsync contati al secondo, cioè la frequenza **misurata** del
  pannello (prima stimata ~39 Hz).
- **Tabella partizioni OTA** (`partitions.csv`, D-039): `ota_0`/`ota_1` da 3 MB,
  `recovery` (tipo test) da 1,5 MB, `coredump`, `storage` LittleFS da 8,3 MB per
  messaggi audio e scatola nera.
- **Ritorno automatico** (`CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE`): una versione
  nuova si conferma da sola dopo 10 s con il display funzionante; altrimenti al
  riavvio il bootloader torna alla precedente.
- **Firmware di emergenza** (`CONFIG_BOOTLOADER_APP_TEST`, GPIO19 basso all'avvio):
  partizione `recovery` riservata; il firmware di emergenza non è ancora scritto.

Stessa schermata simulata di ui-test 0.1.1 (scritta "DEMO - dati simulati - IDF 5.5").
`sdkconfig.defaults` è la sorgente della configurazione; il file `sdkconfig.*`
generato è escluso da Git.

## Versione 0.4.0 — scatola nera ed etichette (D-037, D-040)

- `blackbox.cpp`: memoria circolare in PSRAM (65 536 campioni × 12 byte) con ogni
  valore ricevuto; su evento salva in `/data/ev/evt_NNNN.bin` (LittleFS sulla
  partizione `storage`, componente joltwallet/littlefs 1.22.3, MIT) la finestra da
  50 s prima a 10 s dopo. File: intestazione di 48 byte (`C3BB`, formato 1, motivo,
  dimensione campione, istante, numero campioni, versione firmware) seguita dai campioni
  `{ms u32, id u16, qualità u8, riservato u8, valore float32}`.
- `labels.cpp`: pressione lunga (≥ 2 s) di un comando al volante (segnale VAN 9C4)
  o, a banco, del pulsante BOOT → etichetta e salvataggio dell'evento; scritta
  "SEGNALAZIONE REGISTRATA" per 3 s. Il simulatore preme ogni 90 s.
- Da fare: cancellazione degli eventi più vecchi, lettura dei file dal telefono o via Wi-Fi.

Collaudo: DSP-M010.

## Versione 0.5.0 — pagina 1 "Dashboard" (D-041)

Prima pagina secondo [interfaccia-requisiti.md](../../docs/interfaccia-requisiti.md) rev B,
affinata con l'utente il 23/10/2026: **schermata da viaggio senza scritte, solo icone e
numeri**, con dati simulati (unica scritta: "DEMO - dati simulati", obbligatoria finché i
dati non sono reali).

- **Giri**: barra a tutta larghezza con i numeri 1…5 (x1000) grandi all'interno, sopra il
  colore; inizio smussato in diagonale fino a 1000 giri. Colore dell'intera barra (scelta
  dell'utente 23/10/2026): verde fino a 2500 giri/min, sfumatura fino ad arancione pieno a
  3000, arancione fino a 3500, poi rosso acceso senza sfumatura (potenza massima 50 kW a
  4000 giri/min secondo le schede tecniche; limitatore non trovato).
- **Velocità** al centro, cifre in grassetto con angoli arrotondati (`font_speed.c`,
  Montserrat ingrossato e arrotondato da `tools/genera-font-velocita.py`; licenza OFL),
  aggiornata al massimo 4 volte al secondo.
- **Acqua** in verticale a sinistra con l'icona del termometro **dentro la barra**, in
  basso (42 px): del colore della barra sulla parte vuota e nera su quella riempita,
  tagliata al livello: bianca fino a 50 °C, sfumatura
  verso l'azzurro 0x00C0FF (75-100 °C), poi verso il rosso fino a 110 °C, riquadro di
  avviso da 110 °C. **Gasolio** in verticale a destra, icona del distributore dentro la
  barra con la stessa inversione: bianco, ambra in riserva (≤ 10 %).
- **Spie a icona** (`icons.c`, disegni originali in stile ISO 2575 da `tools/genera-icone.py`,
  colorate dal firmware): nascoste se spente, compaiono sopra la fascia dei dati secondari
  (icona batteria e tensione, icona termometro e temperatura esterna); frecce ai lati più grandi (84 px) con angoli appena arrotondati;
  **prova lampade** di 3 s all'avvio.
- **Riquadro degli avvisi** con icona grande: collegamento assente (ambra), pressione
  olio, freni, acqua alta, carica batteria (rosso), in quest'ordine di priorità.
- Logica pura in `common/include/dash_logic.h` (soglie, colori, priorità), con
  `static_assert` e test sul PC `common/host-tests/test_dash_logic.cpp`.
- Simulatore: giri 800-4700, acqua 30-115 °C in 2 minuti, gasolio dal 60 al 5 % in
  5 minuti, freccia sinistra 10 s ogni 40 s, candelette nei primi 8 s, pressione olio
  5 s ogni 120 s (dopo 60 s).

**Soglie dell'acqua e della riserva solo proposte**, da fissare con i dati del logger;
fondo scala giri 5000 da verificare. Stato: caricata su COM4 il 23/10/2026 (hash
verificati); seriale 22-23 FPS, 36-39 ms per ridisegno, collegamento simulato senza errori.
Collaudo visivo superato (DSP-M011, 23/10/2026).

## Versione 0.6.0 — sequenza d'avvio con controllo di sistema e GO

Secondo [interfaccia-requisiti.md](../../docs/interfaccia-requisiti.md), "Sequenza di avvio":

- **Apertura in stile "Matrix"**: codice verde che scende ai lati (carattere unscii 16),
  pannello centrale "C3+AI CONTROLLO SISTEMA" con i controlli che compaiono uno ogni
  350 ms con l'esito: OK verde, ERRORE rosso, attesa ambra, N/D grigio.
- **Controlli**: display, PSRAM libera > 1 MB, file system della scatola nera, collegamento
  con il front-end, tensione batteria (11-15,5 V), temperatura acqua, IMU, NTC del display,
  candelette. **N/D** (moduli non ancora installati, esclusi dal GO): ricezione VAN,
  K-line, audio, modello IA. Un dato che non arriva entro 5 s è un errore.
- **GO** (carattere grande della velocità) solo quando tutti i controlli sono finiti senza
  errori, la spia candelette è spenta (preriscaldo finito) e sono passati almeno 4 s;
  preriscaldo oltre 30 s = errore. Dopo 1,5 s dissolvenza verso la dashboard, che parte
  con la prova lampade.
- In caso di errore: niente GO, bordo rosso e elenco con gli errori per 6 s, poi la
  dashboard comunque (serve per guidare).
- Logica pura in `common/include/startup_logic.h`, con `static_assert` e test sul PC.
- Seriale: `ui_idf avvio: GO dopo N ms`. Con il simulatore (candelette nei primi 8 s) il GO
  arriva dopo circa 7,7 s. Fluidità durante l'apertura circa 13 FPS (pioggia solo ai lati
  del pannello opaco), poi 21-22 FPS sulla dashboard.
- Messaggio vocale di conferma non ancora presente: dipende dalla verifica dell'uscita audio.

Affinamenti del 23/10/2026 (richieste dell'utente dopo la prima prova):

- **Effetto tridimensionale**: barre con canale incavato (sfumatura scura, bordo sottile) e
  riempimento a rilievo (tinta chiara da un lato, scura dall'altro); alone attorno al
  riquadro degli avvisi e al pannello d'avvio; ombra del GO. Velocità senza effetto 3D.
- Valori di acqua e gasolio **dentro** le rispettive barre (larghe 64 px), in alto, senza
  unità: stessa inversione di colore dell'icona (colore della barra sulla parte vuota, nero
  su quella riempita).
- **Barra dei giri lampeggiante** da 3500 giri (rosso acceso / rosso spento, periodo 0,4 s).
- **Debug a banco** (solo in questa fase): **RST** riavvia la scheda e ripete il controllo
  iniziale; **BOOT** premuto brevemente ripete la prova lampade; BOOT tenuto 2 s registra
  ancora un'etichetta (D-040).
- **Econometro** al limite inferiore dello schermo (240 x 24 px): consumo istantaneo
  l/100 km (segnale 0x0012, fonte da definire), verde fino a 5, ambra verso 8, rosso da 12
  (soglie proposte). Il simulatore lo lega ai giri.
- **Carico delle due CPU** sullo schermo (riga piccola sotto la velocità, provvisoria fino
  alla pagina Diagnostica) e nel report seriale (`cpu0`, `cpu1`), misurato ogni secondo dal
  tempo dei compiti di inattività (statistiche FreeRTOS in `sdkconfig.defaults`).
- Controlli d'avvio con l'esito allineato a destra (non esce più dal pannello).
- Seriale: avvio 19 FPS, dashboard 15-18 FPS (prima 22: costo delle sfumature);
  cpu0 3-11 %, cpu1 61-69 %.

Stato: compilata e caricata su COM4 il 23/10/2026 (hash verificati). Collaudo visivo in corso.

Affinamenti successivi del 23/10/2026:

- **Sagoma della C3 prima serie** (icona 176x88 da `tools/genera-icone.py`) al centro sopra
  la velocità: dentro la **temperatura dell'abitacolo** (segnale 0x0013, climatizzatore via
  VAN, messaggio da identificare), accanto la **temperatura esterna**; a sinistra la
  tensione della batteria. Sono dati secondari: le spie accese vi si sovrappongono.
- Valori di acqua e gasolio dentro le barre (76 px) **con unità** (° e %), stessa
  inversione di colore dell'icona anche a barra piena.
- **Avvio**: finestra più piccola (400x270) con più pioggia di codice ai lati; i controlli
  superati scorrono verso l'alto e spariscono, **gli errori restano fissi** in cima; **GO**
  scritto in grande dentro la finestra con lo stesso carattere (Share Tech Mono 120 px,
  `font_go.c` da `tools/genera-font-avvio.py`).
- Riga di servizio **FPS / CPU0 / CPU1** del firmware al posto dell'indicatore di LVGL
  (che misurava solo il compito grafico, attesa del vsync compresa, e non era la somma
  delle due CPU).
- Seriale: avvio 13-14 FPS, dashboard 15-17 FPS; cpu0 3-5 %, cpu1 62-92 %.

## Luminosità automatica (richiesta utente 23/10/2026)

- Retroilluminazione in **PWM** su GPIO2 (LEDC, **400 Hz**, 10 bit) al posto dell'acceso/spento.
  A 5 kHz sotto il 100 % lo schermo si spegneva; 400 Hz come la libreria esp32-smartdisplay
  per queste schede (DSP-M012).
- **Anabbaglianti accesi** (segnale 0x0007 bit 2): luminosità al **40 %**.
- **Protezione termica** dall'NTC del display (segnale 0x0030; limite dichiarato del
  pannello +70 °C): da 55 °C riduzione lineare fino al 30 % a 65 °C, 20 % da 68 °C (al 10 %
  si legge poco, DSP-M012). Vale il
  valore più basso tra le due regole; senza dato termico nessuna riduzione.
- Variazione graduale (1 % ogni 10 ms); valore nel report seriale (`bl=`). Simulatore:
  anabbaglianti accesi 20 s ogni 60 s.
- Soglie **proposte** in `dash_logic.h` (`backlightTarget`), con test sul PC; da tarare in
  auto (e in seguito dall'app, D-038).

Prima prova a banco (23/10/2026): con PWM a 5 kHz al 40 % lo schermo risulta **spento**
(utente: "quando scende la luminosita non si vede più niente"). Aggiunti la percentuale e
la frequenza sulla riga di servizio ("LUM xx% a N Hz") e i comandi seriali di debug
`bl 0..100`, `bl auto`, `pwm <Hz>` per trovare livello minimo e frequenza adatti.

## Versione 0.7.0

Luminosità automatica e comandi seriali di debug (sopra); numero di versione accanto alla
scritta DEMO ("DEMO - dati simulati - FW 0.7.0"), definito in `src/version.h`.

## Scatola nera: rotazione degli eventi (0.7.0, 23/10/2026)

Prima di salvare un evento si cancellano i più vecchi finché restano libero almeno 1 MB e
meno di 30 eventi; all'avvio si cancellano i file evento vuoti (salvataggi falliti a
memoria piena). Report seriale: `bb_del` = eventi cancellati. Prova: con la memoria piena
(79 file, 8456 KB su 8512) l'evento successivo è stato salvato dopo la cancellazione di 50
file vecchi (`bb_events=1 bb_fail=0 bb_del=50`).
