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
