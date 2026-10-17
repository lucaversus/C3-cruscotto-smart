# Diagnostica ESP32 a banco

Firmware minimo per HW-394 con ESP32 classico e flash da 4 MB. Il profilo
`esp32dev` è una configurazione generica compatibile con il chip identificato,
non una verifica della piedinatura della scheda HW-394.

Usare la sola alimentazione USB con tutti i moduli esterni e il veicolo
scollegati. Non inizializza SPI, I2C, MicroSD, RTC, bus automobilistici,
Wi-Fi o Bluetooth. Non esegue scansioni GPIO né scritture persistenti
applicative. Non presume che BSI o diagnostica OBD2 usino CAN.

All'avvio stampa versione, chip, revisione, core, frequenza CPU, flash,
SDK, causa di reset e memoria. Ogni cinque secondi stampa il tempo
monotono in microsecondi e lo stato della heap. Il tempo non è una data RTC.
`s` richiede uno stato; `h` mostra l'aiuto. Nessun comando modifica la flash.
La causa di reset è il valore numerico `esp_reset_reason_t` di ESP-IDF.
Non registra un contatore persistente di avvii. La PSRAM riportata dipende
anche dalla configurazione di compilazione e non certifica l'hardware presente.

## Compilazione

PlatformIO Core 6.1.18, piattaforma Espressif32 fissata a 6.12.0
(Arduino-ESP32 2.0.17). Non sono necessarie librerie applicative aggiuntive.

Dalla radice del repository, con PlatformIO disponibile:

```powershell
pio run --project-dir data-logger/firmware/diagnostic
```

Se si usa l'ambiente locale isolato preparato in questo progetto:

```powershell
$env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE 'Documents\Codex\pio-c3'
& .\.tools\pio-venv\Scripts\python.exe -m platformio run --project-dir data-logger/firmware/diagnostic
```

La compilazione non carica il firmware. Gli output sono in `.pio/build/`
all'interno della cartella diagnostica e sono esclusi da Git.
La cache usa un percorso corto fuori dal checkout per evitare errori di
estrazione dovuti alla lunghezza dei percorsi su Windows; non va aggiunta a Git.

## Prova hardware da effettuare separatamente

Compilazione verificata il 18 ottobre 2026 con PlatformIO Core 6.1.18:
esito SUCCESS, RAM statica 21472 byte, programma 269909 byte su partizione
applicativa da 1310720 byte. Queste misure non includono l'uso dinamico
durante l'esecuzione. Firmware non ancora caricato né provato sulla scheda.

Il caricamento sostituisce il firmware attuale e scrive anche componenti
di avvio e partizioni: va eseguito soltanto nel passaggio concordato,
dopo verifica del backup. Il ripristino del backup non è ancora stato provato.

Dopo il caricamento, verificare seriale a 115200, banner coerente con
ESP32 e flash da 4194304 byte, stato periodico per almeno un minuto,
comandi `s` e `h`, riavvio con EN e assenza di reset imprevisti.
Questa prova non certifica MicroSD, RTC, protocolli del veicolo o alimentazione.
