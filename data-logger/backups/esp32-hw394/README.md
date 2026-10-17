# Backup iniziale ESP32 HW-394

Copia completa della flash prima di caricare firmware del progetto.
Secondo il proprietario la scheda è nuova, mai programmata da lui.
Il contenuto preinstallato non è stato identificato: non ne sono certificate
origine o funzionalità.

## Identificazione

- Scheda HW-394 a 30 pin, modulo marcato ESP-32D (identificazione visiva).
- Chip ESP32-D0WD-V3, revisione v3.1 (esptool).
- Flash: 4 MB; tensione riportata dai pin di strapping: 3,3 V.
- Quarzo: 40 MHz.
- Collegamento CH340 su COM3, Windows 11, esptool v5.6.0.
- Acquisizione: 17 ottobre 2026, 23:36:59, ora locale del PC dal nome file.

## Archivio

`esp32-original-20261017-233659.bin`: lettura da `0x00000000` per
`0x400000` byte, pari a **4.194.304 byte**. Esptool ha riportato lettura
completata in 372,8 secondi, senza scrittura o cancellazione della flash.

Dimensione del file ricevuto verificata. SHA-256 coincidente con il risultato
PowerShell del proprietario:

```text
702a591483514093a9dd3c6255b492895cedf7dba1ea95d0d5e1ca3bad8cb4b2
```

Da questa cartella, verificare su Linux con `sha256sum -c SHA256SUMS`.
Su PowerShell usare:

```powershell
Get-FileHash .\esp32-original-20261017-233659.bin -Algorithm SHA256
```

La verifica conferma l'integrità del trasferimento, non la validità del firmware.
Non sono state eseguite una seconda lettura indipendente o una prova di ripristino.
L'archivio copre la flash SPI, non eFuse o altre memorie, e non è un'immagine
universale per schede diverse.
