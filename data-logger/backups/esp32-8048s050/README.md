# Backup iniziale scheda display ESP32-8048S050

Copia completa della flash prima di caricare firmware del progetto (D-026).
Contenuto di fabbrica non identificato: origine e funzionalità non certificate.

## Identificazione

- Scheda RCmall con display 5″, PCB serigrafato ESP32-8048S050 (foto archiviate).
- Modulo ESP32-S3-WROOM-1 (lettura del coperchio riferita dall'utente).
- Chip ESP32-S3 (QFN56), revisione v0.2; Embedded PSRAM 8 MB (esptool).
- Flash: 16 MB, produttore 0xc8 device 0x4018, quad da eFuse, 3,3 V.
- Quarzo 40 MHz. Collegamento CH340 su COM4, Windows 11, esptool v4.9.0.
- Acquisizione: 20 ottobre 2026, 20:29:39, ora locale del PC dal nome file.

## Archivio

`esp32s3-8048s050-original-20261020-202939.bin`: lettura da `0x00000000` per
`0x1000000` byte, pari a **16.777.216 byte**, a 921600 baud. Esptool ha
riportato lettura completata in 216,3 secondi, senza scrittura o cancellazione.

```text
90bdef73475e88624c327f668a7c957fdbc76231999ee0ed75e4f3abdb65c03b
```

Da questa cartella, verificare con `sha256sum -c SHA256SUMS` oppure in PowerShell:

```powershell
Get-FileHash .\esp32s3-8048s050-original-20261020-202939.bin -Algorithm SHA256
```

La verifica conferma l'integrità del file, non la validità del firmware.
Non sono state eseguite una seconda lettura indipendente o una prova di ripristino.
L'archivio copre la flash SPI, non eFuse o altre memorie.

## Tabella partizioni (0x8000), lettura del file

`nvs` 0x9000 (20 KiB), `otadata` 0xE000, `app0` 0x10000 e `app1` 0x150000
(1,25 MiB ciascuna), `spiffs` 0x290000 (1,375 MiB), `coredump` 0x3F0000.
Compatibile con lo schema predefinito Arduino-ESP32 da 4 MB: i restanti 12 MB
della flash non sono partizionati.

## Controllo contenuti — 20/10/2026

Analisi in sola lettura del file, senza modificarlo:

- `nvs` (0x9000, 5 pagine): tutte le pagine vuote, nessuna chiave scritta.
  Nessuna credenziale Wi-Fi o altro dato memorizzato.
- `app1`, `spiffs`, `coredump` e i 12 MB oltre 0x400000: interamente 0xFF.
- `otadata`: 12 byte diversi da 0xFF, dati di avvio OTA, nessun testo.
- `app0`: firmware LVGL Widgets Demo (stringhe LVGL v8, Arduino-ESP32 /
  ESP-IDF v4.4.3, compilato 20/12/2022); testi dimostrativi, nessun dato personale.

Conclusione: pubblicabile come il backup HW-394. Il file è quasi tutto 0xFF e
si comprime molto nel repository. SHA-256 invariato.
