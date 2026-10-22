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
  colore; inizio smussato in diagonale fino a 1000 giri. Colore dell'intera barra verde
  fino a 3500 giri/min, poi sfumatura fino a tutta rossa a 4500 (potenza massima 50 kW
  a 4000 giri/min secondo le schede tecniche; limitatore non trovato).
- **Velocità** al centro, cifre in grassetto con angoli arrotondati (`font_speed.c`,
  Montserrat ingrossato e arrotondato da `tools/genera-font-velocita.py`; licenza OFL),
  aggiornata al massimo 4 volte al secondo.
- **Acqua** in verticale a sinistra (icona termometro): bianca fino a 50 °C, sfumatura
  verso l'azzurro 0x00C0FF (75-100 °C), poi verso il rosso fino a 110 °C, riquadro di
  avviso da 110 °C. **Gasolio** in verticale a destra (icona distributore): bianco, ambra
  in riserva (≤ 10 %).
- **Spie a icona** (`icons.c`, disegni originali in stile ISO 2575 da `tools/genera-icone.py`,
  colorate dal firmware): nascoste se spente, compaiono sopra la fascia dei dati secondari
  (icona batteria e tensione, icona termometro e temperatura esterna); frecce ai lati;
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
Collaudo visivo in corso.
