# Collaudo SPI MCP2515 — banco, versione 0.1.0

HW-ESP32 e HW-CAN-MCP2515, nel perimetro D-006 e D-010.
Sorgente separato: preserva diagnostica 0.1.0 e logger 0.2.0.
Caricarlo sostituisce il programma sulla scheda; è stato caricato il 18/10/2026, con BOOT manuale e hash dei segmenti verificati da esptool.

## Cablaggio della sola prova

Scollegare USB durante i collegamenti. Nessun altro modulo collegato.
Usare le etichette GPIO sulla scheda, non il numero di posizione del contatto.
Le serigrafie D18/D19/D23/D26 sono visibili nella foto HW-ESP32 archiviata;
la corrispondenza dei morsetti della basetta non è ancora verificata.

| ESP32 | Modulo MCP2515 |
| --- | --- |
| 3V3 | VCC |
| GND | GND |
| GPIO18 / D18 | SCK |
| GPIO19 / D19 | SO (uscita modulo, ingresso ESP32) |
| GPIO23 / D23 | SI (ingresso modulo, uscita ESP32) |
| GPIO26 / D26 | CS |

INT non collegato; H e L fisicamente scollegati. Non applicare 5 V.
Pin scelti per questo test a banco, non assegnazione definitiva del logger.

## Comportamento e criterio di accettazione

SPI mode 0, 100 kHz, UART 115200. Un solo test all'avvio:
RESET SPI, attesa 20 ms, verifica modalità configurazione in CANSTAT/CANCTRL,
scrittura e rilettura CNF1 con 0x55, 0xAA e 0x00, ripristino del valore iniziale.
Le scritture sono subordinate alla verifica della modalità configurazione.
Non imposta modalità normale, non richiede trasmissioni e non accede ai buffer TX.
Il bitrate CAN non viene determinato o configurato per il funzionamento sul bus.

`SPI_TEST=PASS` richiede tutte le letture corrette e il ripristino del registro;
non prova transceiver, bitrate CAN, terminazione o compatibilità con l'auto.
Assenza modulo o MISO bloccato a 0/1 devono produrre FAIL.
Lo stato viene ripetuto ogni 5 s, senza ripetere automaticamente la prova.

Riferimento: [Microchip DS20001801J](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf),
registri CANSTAT/CANCTRL/CNF1 e istruzioni RESET, READ, WRITE.

## Compilazione

```powershell
$env:PLATFORMIO_CORE_DIR='C:\Users\Luca\Documents\Codex\pio-c3'
& .\.tools\pio-venv\Scripts\python.exe -m platformio run --project-dir data-logger/firmware/mcp2515-spi-test
```

Compilazione verificata il 18/10/2026: SUCCESS, RAM 21.560 byte, flash 274.757 byte.
Preflight e git diff --check superati. Stato hardware: caricato su COM3 il 18/10/2026; avvio e prova SPI verificati con lettura diretta `status SPI_TEST=PASS uptime_ms=15545`. CAN non collaudato. Misure preliminari in
[collaudo-mcp2515.md](../../docs/collaudo-mcp2515.md).
