# Data Logger — firmware 0.3.0

Progetto **Cruscotto C3+AI**, sottoprogetto **Data Logger**. Revisione software
19/10/2026. Implementazione per HW-ESP32; compilazione distinta dal caricamento
e dal collaudo. Dal 20/10/2026 sulla scheda e caricata la 0.3.0 banco, con avvio seriale verificato.

## Funzionamento

Avvio automatico: monta la MicroSD, crea il primo `/c3_000001.csv` libero
(fino a 999999), quindi avvia le sorgenti abilitate. Non formatta e non sovrascrive
file. Senza SD ritenta ogni 10 s; non acquisisce dati prima dell'apertura riuscita.
Registra stato ESP32, calendario DS3231, pacchetti originali e PID decodificati.
Buffer di scrittura 8 KiB, coda 256 record, sincronizzazione nominale ogni secondo,
rotazione a circa 64 MiB. SdFat espone gli errori di scrittura/sync/chiusura.

Premendo STOP (o inviando `stop`), interrompe nuove richieste OBD, completa la
risposta già in corso entro il timeout, ferma VAN, svuota la coda, aggiunge il footer,
sincronizza e chiude. Riapre in lettura e verifica dimensione e ultima riga.
Solo se tutti i controlli riescono mostra **SALVATO / PUOI SPEGNERE**.
Lo STOP è definitivo fino al riavvio; non interrompe elettricamente l'alimentazione.
STOP tenuto all'avvio impedisce la registrazione. In errore non dichiara SALVATO,
non riparte automaticamente e non nasconde la sessione incompleta.

L'OLED 128×64 mostra stato, righe, perdite della coda, ora e stato delle sorgenti.
Profili SH1106 (iniziale) e SSD1306 selezionabili: non identificano il controller
fisico. OLED assente non blocca il logger: stato disponibile su seriale 115200.
RTC assente, calendario invalido o flag OSF non bloccano la registrazione monotona.
Nessun Wi-Fi/Bluetooth, nessuna scrittura AT24C32, nessuna simulazione dati auto.

## Profili e GPIO proposti

[Schema dei collegamenti per la prova USB](../../docs/collegamenti-banco-030.md),
rev. A: SD, RTC, OLED e STOP, senza connessioni al veicolo.

| Profilo PlatformIO | Funzioni |
| --- | --- |
| `esp32-hw394-logger` (predefinito) | Banco: SD, RTC, OLED, STOP; sorgenti auto disabilitate |
| `esp32-hw394-vehicle` | Stesse funzioni, più OBD KWP e ricezione VAN |

| Collegamento logico HW-ESP32 | GPIO |
| --- | --- |
| HW-RTC e HW-OLED: SDA / SCL | 21 / 22 |
| HW-SD-MODULE: CLK / MISO / MOSI / CS | 18 / 19 / 23 / 27 |
| Pulsante STOP normalmente aperto verso GND, pull-up interna | 32 |
| Interfaccia K-line: RX / TX ESP32 | 16 / 17 |
| HW-CAN-VP230: uscita RX verso ESP32 (solo ingresso) | 34 |
| CS MCP2515 eventuale sullo stesso SPI, mantenuto HIGH | 26 |

Configurazione unica in `include/config.h`, riscontrata dal preflight con
`hardware.json`. I2C 100 kHz, SPI 1 MHz. Sono assegnazioni firmware proposte,
non una verifica di cablaggio né pin del connettore auto. Lo schema generale
storico rimane illustrativo: per questa release vale la tabella, GPIO33 inutilizzato.
Le verifiche fisiche sono a cura dell'utente (D-020); nessun loro esito è presunto.
RTC: rimozione resistenza 201 scelta in D-019, esecuzione ancora non confermata.

## Acquisizione OBD e VAN

**K-line**: UART2 10400 8N1, TX invertito/RX normale per l'interfaccia discreta
D-013 (2N5551 + LM2903B), non per collegamento diretto. Fast init 25/25 ms,
StartCommunication funzionale indirizzo 0x33; apprende l'indirizzo ECU dalla
risposta valida. Intervalli temporali da verificare sull'interfaccia assemblata.
Richiede eco TX coerente. Scopre le bitmap dei PID mode 01 e interroga tutti
quelli dichiarati, esclusi i PID bitmap, con pausa 250 ms fra richieste.
Dopo tre errori consecutivi riconnette. Registra anche risposte negative,
sconosciute, frammenti e checksum errati. Decodifica carico, farfalla, livello
carburante, temperature, pressioni, giri, velocità, portata aria e tensione
soltanto per i PID implementati; gli altri restano nei byte originali.
Non cancella DTC, non comanda attuatori, non richiede VIN. Non implementa slow init
né rilevamento automatico del protocollo; il profilo KWP resta da provare sull'auto.

**VAN**: ricezione passiva via RMT e HW-CAN-VP230, nessun MCP2515 e nessuna
trasmissione VAN. Profilo iniziale comfort 125 kbit/s; `LOGGER_VAN_BODY=1`
seleziona 62,5 kbit/s, `LOGGER_VAN_INVERT=1` cambia polarità logica: scegliere
solo sulla base del segnale identificato. Conserva fino a 64 byte per frame,
ID e stato CRC/timing/overflow, inclusi gli ID non interpretati.
Il transceiver deve essere predisposto fisicamente in sola ricezione e senza
terminazione aggiunta alla rete: il software non può garantire questa condizione.
Non promette di registrare ogni segnale o ogni pacchetto: RMT, buffer e SD hanno
limiti; overflow della coda è contato, perdite prima della coda non sono quantificate.
Timestamp VAN alla consegna RMT, non al SOF. Non conserva le forme d'onda originali.

## Comandi seriali (Invio)

- `status` oppure `s`: stato, file, contatori, RTC e memoria.
- `stop`: stesso arresto del pulsante.
- `time YYYY-MM-DDTHH:MM:SSZ`: imposta esplicitamente UTC nel DS3231,
  rilegge i registri, quindi cancella OSF. Non usa la data di compilazione.
- `oled sh1106` oppure `oled ssd1306`: selezione persistente in NVS.
- `help`: elenco comandi.

## CSV versione 2

```text
schema_version,session_id,sequence,source,mono_us,rtc_calendar,rtc_state,rtc_read_mono_us,event,frame_id,id,chunk_offset,raw_hex,value,unit,queue_dropped,van_bad,kwp_errors
```

`session_id` casuale all'avvio della sessione, `sequence` crescente anche tra
segmenti; `source`: system, van_rx, kwp_tx, kwp_rx, obd_pid. ID numerici decimali;
per obd_pid: `(indirizzo ECU << 8) | PID`. `raw_hex` conserva byte esadecimali;
frame KWP lunghi sono divisi in blocchi da 64 byte con frame_id e chunk_offset.
Il checksum finale e gli header fanno parte dei byte grezzi KWP.

`mono_us` è il tempo monotono ESP32 al rilevamento software, non UTC.
`rtc_calendar` è l'ultima lettura RTC, associata a `rtc_read_mono_us`, non l'ora
esatta della cattura. I task possono produrre dati in ordine diverso dai timestamp:
per l'analisi usare mono_us e l'ancora RTC, non l'ordine delle righe come orologio.
Senza impostazione UTC esplicita: `calendar_timezone_unknown`; dopo comando
verificato: `utc_set_by_user`; altrimenti calendario vuoto e causa di invalidità.
Questo stato non certifica la precisione o sincronizzazione dell'orologio.
I contatori sono quelli osservati al momento della scrittura.
`stop_footer` conclude una sessione arrestata; `segment_end` chiude un segmento.
`health` riporta heap libero nel campo id. I valori fisici hanno unità esplicita.

Sync, chiusura e rilettura riducono il rischio ma non certificano la persistenza
fisica dopo un'interruzione improvvisa. Non esiste UPS; STOP prima di togliere
alimentazione rimane necessario. File senza footer vanno considerati incompleti.

## Compilazione riproducibile e controlli

PlatformIO 6.1.18, Espressif32 6.12.0, Arduino-ESP32 2.0.17, C++14.
SdFat 2.3.1 e U8g2 Arduino 2.37.1 fissate a commit in platformio.ini;
licenze e provenienza in [THIRD_PARTY.md](THIRD_PARTY.md).

```powershell
$env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE 'Documents/Codex/pio-c3'
& .tools/pio-venv/Scripts/python.exe -m platformio run --project-dir data-logger/firmware/logger -e esp32-hw394-logger -e esp32-hw394-vehicle
```

`calendar_checks.cpp` e `logic_checks.cpp` esercitano il codice realmente usato:
calendario/UTC, debounce e overflow timer, STOP e condizioni di salvataggio,
checksum/header KWP, bitmap PID, limiti decoder VAN. Sono controlli a compilazione,
non un emulatore di ESP32, UART, RMT o guasti del supporto SD.
Collaudi completi di registrazione SD, sorgenti veicolo e spegnimento fisico ancora
da eseguire; avvio a banco e raggiungibilita RTC verificati il 20/10/2026.
Il 20/10/2026 e stata caricata la 0.3.0 banco su COM3 con hash verificati,
avvio ATTESA SD e RTC oscillator_stop; modulo SD ancora scollegato.

## Caricamento con terminale visibile

Dalla radice del repository, in PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File .\tools\carica-logger-visibile.ps1 -Porta COM3
```

Il criterio Bypass vale soltanto per questo processo, non modifica le impostazioni
Windows. Lo script mostra build e upload, poi apre automaticamente il monitor
seriale 115200 baud, DTR/RTS inattivi dopo impulso EN di avvio,
con copia dei dati in .tools/serial/monitor-*.log.
Ctrl+C chiude il monitor. Il profilo predefinito e esp32-hw394-logger (banco).
Chiudere un precedente monitor prima di un nuovo caricamento.

Se HW-394 segnala Wrong boot mode, aggiungere `-AttendiBoot`: il terminale
attende Invio mentre si mantiene BOOT premuto; rilasciarlo alla prima scrittura.

Per riaprire soltanto il monitor aggiungere `-SoloMonitor` (nessun reset).
`-Riavvia` richiede esplicitamente un impulso EN: non usarlo su una registrazione
aperta. Dopo upload il riavvio normale e automatico.
