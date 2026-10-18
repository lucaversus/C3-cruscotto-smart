# Data Logger — firmware a banco 0.2.0

Progetto **Cruscotto C3+AI**, sottoprogetto **Data Logger**.
Prima base di registrazione automatica per ESP32 HW-394. Separata dalla
[diagnostica 0.1.0](../diagnostic/README.md), conservata per il collaudo del solo ESP32.

## Comportamento implementato

- All'accensione tenta il montaggio MicroSD e apre una nuova sessione, senza pulsanti.
- Produce un campione di salute ESP32 ogni circa un secondo, non dati del veicolo.
- Crea `/bench_0001.csv`, poi il primo nome libero fino a `/bench_9999.csv`.
  Non cancella file né formatta automaticamente la scheda. Se i nomi sono esauriti,
  segnala `namespace_full`. I file già presenti vengono saltati con `SD.exists`.
- Scrive l'intestazione una volta. Ogni riga viene scritta, seguita da flush e chiusura.
- Se la MicroSD manca o la scrittura segnala errore, continua la diagnostica seriale
  e ritenta dopo 10 secondi. Al recupero crea una nuova sessione. Non conserva in RAM
  i campioni persi e non ricostruisce dati retroattivi.
- Legge solo il dispositivo I2C 0x68 e i registri DS3231 necessari. Non imposta
  l'orologio, non cancella OSF, non scrive AT24C32 e non esegue scansioni I2C.
- Accetta calendario BCD valido e formati 12/24 ore; il flag OSF rende l'ora non valida.
  Senza RTC valido registra comunque il campione con tempo monotono e data vuota.
- Seriale a 115200 baud: stato ogni 5 secondi, `s` stato, `h` aiuto.
- Nessun driver OBD/BSI, Wi-Fi, Bluetooth, display o pulsanti inizializzato.

La scelta confermata dall'utente è avvio automatico. I pulsanti restano inutilizzati;
non occorrono per questa fase. Il driver OLED aspetta l'identificazione del controller.

## Collegamenti proposti

| Funzione | GPIO ESP32 |
| --- | --- |
| I2C SDA / SCL | 21 / 22 |
| MicroSD SCK / MISO / MOSI | 18 / 19 / 23 |
| MicroSD CS | 27 |

Sono coerenti con lo [schema collegamenti](../../docs/schema-collegamenti.svg).
Impostazioni in `include/config.h`. I2C 100 kHz, timeout 50 ms, SPI iniziale 1 MHz.
Queste velocità sono valori di partenza, non prestazioni misurate sui moduli.
Non usare lo schema come layout fisico dei connettori.

**Moduli ordinati ma non ancora disponibili:** prima del caricamento e cablaggio
verificare serigrafie, livelli 3,3 V, pull-up, circuito batteria RTC e corrente disponibile
con picchi MicroSD. Usare solo alimentazione USB a banco, veicolo scollegato.
Questa versione inizializza SPI/I2C, a differenza della diagnostica 0.1.0.

## Formato CSV versione 1

```text
schema_version,source,sequence,uptime_us,rtc_state,rtc_calendar,heap_free_bytes,heap_min_bytes,missed_intervals
```

- `source=bench_esp32`: distingue questi file da acquisizioni automobilistiche future.
- `sequence`: numero delle righe scritte nell'avvio corrente, anche tra sessioni di recupero.
- `uptime_us`: tempo monotono a 64 bit dall'avvio, si azzera al reset.
- `rtc_state`: `unavailable`, `oscillator_stop`, `invalid_calendar` o `calendar_ok`.
- `rtc_calendar`: `YYYY-MM-DDTHH:MM:SS`, vuoto se non valido. Nessun suffisso Z:
  fuso orario, sincronizzazione e correttezza dell'ora non sono ancora certificati.
  `calendar_ok` significa soltanto calendario formalmente valido con OSF non impostato.
- `heap_*`: byte. `missed_intervals`: intervalli aggiuntivi da 1 secondo saltati per
  ritardi del ciclo; non misura le perdite del bus o tutti i campioni senza SD.

Le operazioni SD sono sincrone e possono ritardare il ciclo. La frequenza di 1 Hz è
nominale; nessuna garanzia di acquisizione real-time. Non si formano raffiche di campioni
per riempire intervalli mancanti. Nessuna misura automobilistica viene simulata.

## Compilazione e verifiche

Stesso stack della diagnostica: PlatformIO Core 6.1.18, Espressif32 6.12.0,
Arduino-ESP32 2.0.17. Usa soltanto FS/SD, SPI e Wire già inclusi nel framework;
nessuna nuova libreria esterna. C++14 per i controlli `static_assert`.

Dalla radice del repository:

```powershell
$env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE 'Documents\Codex\pio-c3'
& .\.tools\pio-venv\Scripts\python.exe -m platformio run --project-dir data-logger/firmware/logger
```

`src/calendar_checks.cpp` esercita a tempo di compilazione il decoder effettivamente
usato dal firmware: 18 controlli su date normali e non valide, BCD, anni bisestili,
secolo 2100, ore AM/PM, preservazione dell'output in errore e overflow del timer.
La compilazione fallisce se un controllo non passa. Non sono test hardware né
una simulazione dei guasti SD/I2C.

Stato: compilazione verificata il 18/10/2026; nessun caricamento di questa versione.
Esito SUCCESS, 22544 byte RAM statica e 352725 byte programma; tutti i 18
controlli a tempo di compilazione superati. Build finale senza avvisi applicativi.
Collaudo RTC/MicroSD e avvio automatico su scheda ancora da eseguire all'arrivo dei moduli.
Il backup originale e il firmware diagnostico restano disponibili.

## Limiti e collaudo successivo

Flush e close dell'API Arduino non espongono tutte le condizioni di errore del supporto:
il controllo del numero di byte e dello stream non certifica persistenza fisica.
Non è ancora implementata la verifica di rilettura, il recupero di file troncati,
la rotazione per dimensione o un'alimentazione che consenta arresto controllato.
Spegnimento improvviso, scheda piena o rimozione possono perdere righe e corrompere FAT.
Non rimuovere la scheda durante la registrazione e non considerare questi file un dataset
operativo. Politiche di arresto e alimentazione automotive saranno affrontate prima dell'auto.

Il collaudo dovrà coprire: SD assente, RTC assente/OSF/calendario valido, CSV reale
riletto su PC, due avvii con file distinti, errori di montaggio/scrittura e scheda piena.
La regolazione iniziale del RTC sarà un passaggio esplicito; non viene usata l'ora di build.

Riferimenti: [API SD Arduino-ESP32 2.0.17](https://github.com/espressif/arduino-esp32/blob/2.0.17/libraries/SD/src/SD.h),
[API Wire](https://github.com/espressif/arduino-esp32/blob/2.0.17/libraries/Wire/src/Wire.h),
[datasheet DS3231, registri calendario e OSF](https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf).
