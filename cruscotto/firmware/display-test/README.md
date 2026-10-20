# Prova display ESP32-8048S050 — versione 0.1.0

Cruscotto C3+AI, primo firmware della scheda HW-DASH-DISPLAY (D-026, D-027).
Stato: **caricato il 20/10/2026 e collaudato a banco (DSP-M001): conforme**. Il firmware di fabbrica
(LVGL Widgets Demo) è salvato in `data-logger/backups/esp32-8048s050/`.

## Cosa fa

1. Stampa sulla seriale presenza e dimensione della PSRAM. Con
   `memory_type = qio_opi` l'avvio riuscito con PSRAM trovata conferma il modo octal.
2. Inizializza il pannello RGB 800×480 (esp_lcd, framebuffer in PSRAM),
   disegna otto barre verticali e accende la retroilluminazione su GPIO2.
3. Scansiona il bus I2C su GPIO19 (SDA) / GPIO20 (SCL), dove la variante con
   touch ha il GT911 (0x5D o 0x14). Atteso nessun dispositivo (D-027).

Riga ripetuta ogni 5 s a 115200 baud:
`display_test version=0.1.0 psram_found=1 psram_bytes=... panel=ESP_OK i2c_devices=0 [] ...`

## Criterio di accettazione

Barre da sinistra a destra: **bianco, giallo, ciano, verde, magenta, rosso,
blu, nero**, senza sfarfallio né righe spostate. Rosso e blu invertiti indicano
ordine dei dati da correggere; colori mancanti indicano un GPIO dati errato.
`panel=ESP_OK` e `psram_found=1` sono necessari ma non sufficienti: decide
l'osservazione del display riferita dall'utente.

## Pinout e temporizzazioni — verificati su questa scheda (DSP-M001)

Fonte comunitaria, non del produttore: definizione
[esp32-8048S050C.json](https://github.com/rzeldent/platformio-espressif32-sunton/blob/main/esp32-8048S050C.json).
Valori in `../common/include/board_8048s050.h`: DE 40, VSYNC 41, HSYNC 39, PCLK 42 a 16 MHz,
porch 8/8 e impulsi 4; dati D0..D15 = 8, 3, 46, 9, 1, 5, 6, 7, 15, 16, 4,
45, 48, 47, 21, 14. MicroSD su 10–13 coerente con la serigrafia "SPI".

## Compilazione e caricamento

`python tools/dev.py build` compila anche questo progetto (nessun caricamento).
Caricamento solo su richiesta esplicita dell'utente, su COM4 (CH340) a 921600 baud;
sostituisce il firmware di fabbrica, ripristinabile dal backup con esptool `write_flash 0`.
