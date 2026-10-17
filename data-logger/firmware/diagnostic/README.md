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

## Compilazione e primo collaudo hardware

Compilazione verificata il 18 ottobre 2026 con PlatformIO Core 6.1.18:
esito SUCCESS, RAM statica 21472 byte, programma 269909 byte su partizione
applicativa da 1310720 byte. Queste misure non includono l'uso dinamico
durante l'esecuzione.

### Esito del 18 ottobre 2026

- Firmware del commit `735fbda` caricato su COM3 a 115200 baud con
  PlatformIO/esptool 4.9.0. Caricamento SUCCESS e hash dei dati scritti verificati.
- Prima della scrittura, SHA-256 del backup completo ricontrollato:
  `702a591483514093a9dd3c6255b492895cedf7dba1ea95d0d5e1ca3bad8cb4b2`.
- L'ingresso automatico in download mode non è riuscito (boot mode 0x13).
  Il caricamento è riuscito tenendo BOOT premuto. Dopo il rilascio è stato
  necessario premere EN/RESET per avviare l'applicazione.
- Lettura diretta della seriale per 20 secondi: comandi `h` e `s` funzionanti,
  stato periodico ogni 5 secondi, heap libera stabile a 351476 byte e nessun
  riavvio osservato nella finestra acquisita.
- Screenshot del monitor: 12 righe, da uptime 100550191 a 155550191 microsecondi
  (55 secondi consecutivi), con incrementi di 5000000 microsecondi e heap libera
  stabile a 351476 byte. Heap minima da 345888 a 345884 byte: variazione di
  4 byte del minimo storico, senza calo della memoria libera corrente visibile.
- L'utente ha successivamente confermato di aver atteso l'intervallo richiesto
  di almeno un minuto. Non è stato acquisito un log completo di quell'intervallo:
  la continuità dell'intero minuto non è verificata automaticamente.

Esito: caricamento e prima prova funzionale positivi; nessun reset imprevisto
nelle finestre direttamente osservate. Non sono ancora verificati banner di
avvio completo, stabilità prolungata, RTC, MicroSD o comunicazioni veicolo.
La misura della heap è un dato runtime e non è confrontabile direttamente
con il budget RAM statico indicato dalla compilazione.

Il caricamento sostituisce il firmware attuale e scrive anche componenti
di avvio e partizioni: va eseguito soltanto nel passaggio concordato,
dopo verifica del backup. Il ripristino del backup non è ancora stato provato.

Per completare il collaudo, acquisire il banner di avvio (ESP32 e flash da
4194304 byte), un log continuo di almeno un minuto e una prova documentata
di riavvio con EN. Serialità prevista: 115200 baud; comandi `s` e `h`.
Questa prova non certifica MicroSD, RTC, protocolli del veicolo o alimentazione.
