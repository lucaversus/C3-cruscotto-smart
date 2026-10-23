# Data Logger — firmware 0.4.0

Progetto **Cruscotto C3+AI**, sottoprogetto **Data Logger**. Revisione software
20/10/2026 (0.3.1, D-022). Implementazione per HW-ESP32; compilazione distinta dal caricamento
e dal collaudo. Dal 20/10/2026 sulla scheda e caricata la 0.3.0 banco, con avvio seriale verificato;
la 0.3.1 non e caricata.

Novita 0.3.1 rispetto alla 0.3.0: pianificazione OBD con PID prioritari e pausa
ridotta fra richieste; frequenza SPI della MicroSD impostabile in compilazione e
registrata nel file. Profilo banco invariato nel comportamento, salvo la riga `sd_spi_hz`.

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
`hardware.json`. I2C 100 kHz, SPI MicroSD 1 MHz predefinita (vedi sotto). Sono assegnazioni firmware proposte,
non una verifica di cablaggio né pin del connettore auto. Lo schema generale
storico rimane illustrativo: per questa release vale la tabella, GPIO33 inutilizzato.
Le verifiche fisiche sono a cura dell'utente (D-020); nessun loro esito è presunto.
RTC: resistenza 201 rimossa (D-019), ramo di ricarica interrotto verificato il 20/10/2026 (RTC-M007).

## Acquisizione OBD e VAN

**K-line**: UART2 10400 8N1, TX invertito/RX normale per l'interfaccia discreta
D-013 (2N5551 + LM2903B), non per collegamento diretto. Fast init 25/25 ms,
StartCommunication funzionale indirizzo 0x33; apprende l'indirizzo ECU dalla
risposta valida. Intervalli temporali da verificare sull'interfaccia assemblata.
Richiede eco TX coerente. Scopre le bitmap dei PID mode 01. A ogni giro interroga
i PID prioritari dichiarati supportati (0x0C giri, 0x0D velocita, 0x04 carico,
0x0B MAP, 0x10 portata aria, 0x23 pressione rail) e poi uno solo degli altri
PID supportati, a rotazione; i PID bitmap sono esclusi. Pausa fra richieste:
attesa di 60 ms dopo l'ultimo byte di risposta piu 40 ms (`kKwpRequestGapMs`),
quindi sopra il P3min ISO 14230 di 55 ms; nella 0.3.0 erano 250 ms. Con N PID
prioritari supportati, ciascuno viene letto circa ogni N+1 richieste invece che
ogni giro completo. Tempi reali della centralina ancora da misurare.
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

## Frequenza SPI MicroSD

Predefinita 1 MHz, valore prudente da banco. Si cambia solo in compilazione,
entro 0,4-25 MHz (controllo `static_assert`), per esempio:

```text
PLATFORMIO_BUILD_FLAGS=-DLOGGER_SD_SPI_HZ=10000000 python tools/dev.py build
```

All'avvio la seriale riporta `sd_spi_hz=` e il CSV registra l'evento di sistema
`sd_spi_hz` con il valore nel campo `id`. Procedura di innalzamento: prima
completare a banco la prova di scrittura a 1 MHz, poi 4, 10 e 20 MHz con cavi
corti, controllando `queue_dropped`, errori `write_failed` e chiusura SALVATO.
Adottare il valore piu alto stabile con margine, registrandolo nel registro moduli.
Nessuna frequenza superiore a 1 MHz e collaudata.

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

Su un clone nuovo eseguire prima `python tools/dev.py setup` dalla radice;
poi `python tools/dev.py check` e `python tools/dev.py build`.
I comandi funzionano su Windows/Linux/macOS senza attivazione manuale della venv.
Dettagli e prerequisiti in [CONTRIBUTING.md](../../../CONTRIBUTING.md).
Usare lo stesso ingresso portabile anche sull'ambiente locale esistente:

```text
python tools/dev.py check
python tools/dev.py build
```

`calendar_checks.cpp` e `logic_checks.cpp` esercitano il codice realmente usato:
calendario/UTC, debounce e overflow timer, STOP e condizioni di salvataggio,
checksum/header KWP, bitmap PID, limiti decoder VAN. Sono controlli a compilazione,
non un emulatore di ESP32, UART, RMT o guasti del supporto SD.

`host-tests/test_logic.cpp` (D-023) esegue sul PC, con gli stessi header, test
su dati generati: andata e ritorno VAN con encoder enhanced Manchester di
riferimento a 125 e 62,5 kbit/s, CRC-15 confrontato con un'implementazione
indipendente dai coefficienti del polinomio, rilevamento di ogni errore su un
singolo bit, tolleranza temporale RMT, parsing KWP incrementale, bitmap PID,
equità della pianificazione 0.3.1, rimbalzi casuali dello STOP e calendario UTC
confrontato con la libreria C. Verificata la sensibilità con difetti introdotti
di proposito (decoder, polinomio, XOR finale, rotazione PID, debounce).
`python tools/dev.py lint` esegue cppcheck su sorgenti e test.
Collaudi completi di registrazione SD, sorgenti veicolo e spegnimento fisico ancora
da eseguire; avvio a banco e raggiungibilita RTC verificati il 20/10/2026.
Il 20/10/2026 e stata caricata la 0.3.0 banco su COM3 con hash verificati,
avvio ATTESA SD e RTC oscillator_stop; modulo SD ancora scollegato.
La 0.3.1 e verificata soltanto in compilazione (vedi VERIFICA.md).

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

## Aggiornamento dalla MicroSD — versione 0.4.0 (richiesta utente 23/10/2026)

Per cambiare firmware senza smontare il logger dall'auto.

1. Sul PC: `python tools/prepara-aggiornamento-sd.py` (profilo predefinito
   `esp32-hw394-vehicle`, oppure il nome del profilo come argomento). Compila e crea
   `.tools/aggiornamento-sd/update/` con `c3_logger.bin` e `c3_logger.sha256`.
2. Copiare la cartella `update` nella radice della MicroSD del logger.
3. Accendere il logger: all'avvio, prima della registrazione, il firmware trova il file,
   ne calcola l'impronta SHA-256 e la confronta con `c3_logger.sha256`; se coincide lo
   scrive nell'altra partizione dell'ESP32 (OLED "AGGIORNAMENTO - NON SPEGNERE") e riavvia.
   Il file diventa `c3_logger.bin.done`; se l'impronta manca o non coincide, o la
   scrittura fallisce, diventa `c3_logger.bin.bad` e il logger parte con la versione attuale.
4. **Ritorno automatico**: la versione nuova si conferma da sola dopo 20 s di
   funzionamento. Se si blocca o si riavvia prima, al riavvio successivo il bootloader
   torna alla precedente. Spegnere il logger entro 20 s dal primo avvio annulla
   l'aggiornamento (va ripetuto).
5. **Ritorno manuale**: tenere premuto **STOP all'accensione per 3 s** fa ripartire la
   versione presente nell'altra partizione (OLED "VERSIONE PRECEDENTE").

Partizioni: tabella Arduino predefinita (`app0`/`app1` da 1,25 MB, firmware attuale
circa 0,36 MB). Seriale: righe `sd_update ...`. Sorgenti: `src/sd_update.cpp`,
`parseSha256Hex()` in `logger_logic.h` con test sul PC.
