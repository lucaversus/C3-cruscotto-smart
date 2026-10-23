# Protocollo front-end ↔ ESP32-S3 — versione 1

Revisione A, 21/10/2026. Cruscotto C3+AI, D-029 (architettura), D-033 (stessi canali
nel logger), D-035 (diagnosi in sola lettura), D-037/D-039 (firmware S3, aggiornamenti).
Implementazione comune: [`cruscotto/firmware/common/include/fe_link.h`](../firmware/common/include/fe_link.h);
test host: `cruscotto/firmware/common/host-tests/test_fe_link.cpp` (eseguiti da `dev.py check`).

**Stato: proposta implementata come libreria e testata sul PC; nessuna prova tra
schede ancora eseguita.**

## Livello fisico

| Front-end (ESP32) | Segnale | ESP32-S3 |
| --- | --- | --- |
| GPIO25 (UART1 TX) | → | IO11 (RX, connettore P2) |
| GPIO33 (UART1 RX) | ← | IO12 (TX, connettore P2) |
| GND | — | GND (P1) |

Logica 3,3 V, 921 600 baud, 8N1, nessun controllo di flusso. Cavo corto sulla
scheda madre (-J2). A 921 600 baud la capacità utile è circa 90 KB/s.

## Trama

Ogni trama è codificata **COBS** e terminata da un byte **0x00**: il ricevitore si
risincronizza sempre al delimitatore successivo, anche dopo rumore o byte persi.

| Campo | Byte | Note |
| --- | --- | --- |
| tipo | 1 | vedi tabella dei tipi |
| sequenza | 1 | contatore per direzione, rileva trame perse |
| tempo | 4 | microsecondi dall'avvio del mittente (little endian) |
| corpo | 0-242 | dipende dal tipo |
| CRC | 2 | CRC-16/CCITT-FALSE su tipo, sequenza, tempo e corpo |

Payload massimo 250 byte; trame con CRC errato o COBS non valida vengono scartate
e contate (contatore errori nel messaggio di stato).

## Tipi di messaggio

| Tipo | Direzione | Corpo | Uso |
| --- | --- | --- | --- |
| 0x01 HELLO | FE → S3 | versione protocollo, capacità, versione firmware | all'avvio e su richiesta |
| 0x02 HEARTBEAT | entrambe | stato, contatori errori | 1 al secondo; assenza > 3 s = collegamento perso |
| 0x10 SIGNALS | FE → S3 | n × {id u16, qualità u8, valore float32} | fino a 34 segnali per trama |
| 0x11 RAW_VAN | FE → S3 | {IDEN u16, flag u8, dati} | frame VAN grezzo, solo se abilitato |
| 0x12 RAW_KWP | FE → S3 | {servizio u8, dati} | risposta K-line grezza, solo se abilitata |
| 0x13 EVENT | FE → S3 | {codice u16, argomento i32} | chiave, avviamento, errori bus, soglie |
| 0x14 DTC_LIST | FE → S3 | {n, codici u16} | risposta al servizio 0x03 (D-035) |
| 0x30 COMMAND | S3 → FE | {comando u8, argomento i32} | vedi comandi |
| 0x31 ACK | entrambe | {tipo, sequenza, esito} | conferma dei comandi |

**Comandi S3 → front-end:** richiesta codici guasto (0x03), richiesta dati al momento
del guasto (0x02), inoltro dei frame grezzi sì/no, sincronizzazione dell'ora, ingresso
in aggiornamento firmware. Nessun comando può produrre scritture verso il veicolo:
il front-end usa solo i servizi OBD ammessi (D-035) e il VAN in sola ricezione.

## Qualità del valore

Ogni segnale porta la propria qualità, così che nessun dato venga scambiato per un altro:

| Qualità | Significato |
| --- | --- |
| 0 valido | letto e decodificato con regola verificata sul veicolo |
| 1 non aggiornato | ultimo valore noto oltre il proprio periodo atteso |
| 2 da verificare | decodifica da fonte comunitaria non ancora riscontrata sulla C3 |
| 3 simulato | prove a banco: sul display compare la scritta DEMO |
| 4 errore | sensore o bus in errore |

## Registro dei segnali (estendibile)

| Id | Segnale | Unità | Fonte prevista |
| --- | --- | --- | --- |
| 0x0001 | giri motore | giri/min | VAN 824 / OBD 0x0C |
| 0x0002 | velocità | km/h | VAN 824 / OBD 0x0D |
| 0x0003 | temperatura acqua | °C | VAN 8A4 / OBD 0x05 |
| 0x0004 | temperatura esterna | °C | VAN 8A4 |
| 0x0005 | carburante | % | VAN |
| 0x0006 | contachilometri | km | VAN 8FC |
| 0x0007 / 0x0008 | luci / spie e avvisi | campo di bit | VAN 4FC, 524, 564 |
| 0x0009 | comandi al volante | campo di bit | VAN 9C4 |
| 0x0010 | tensione batteria | V | partitore GPIO35 |
| 0x0011 | chiave | 0/1 | GPIO39 (presa OBD via 1) |
| 0x0013 | temperatura abitacolo | °C | climatizzatore automatico via VAN (messaggio da identificare) |
| 0x0012 | consumo istantaneo (econometro) | l/100 km | da definire: calcolo nel front-end da dati motore K-line e velocità |
| 0x0020-0x0026 | IMU: accelerazioni, rotazioni, temperatura | g, °/s, °C | LSM6DSO (HW-IMU-LSM6DSO) |
| 0x0030 / 0x0031 | NTC display / scheda | °C | GPIO36 / GPIO32 |
| 0x0040 / 0x0041 | ventola | %, giri/min | GPIO26 / GPIO14 |
| 0x0100 + PID | PID OBD servizio 0x01 | unità del PID | K-line |

Campi di bit (definiti in `common/include/dash_logic.h`, firmware S3 0.5.0; la
corrispondenza con i bit dei messaggi VAN è compito del front-end, da verificare):

- **0x0007 luci**: bit 0 freccia sinistra, 1 freccia destra, 2 anabbaglianti,
  3 abbaglianti, 4 fendinebbia, 5 retronebbia, 6 luci di posizione.
- **0x0008 spie**: bit 0 freni, 1 pressione olio, 2 temperatura acqua, 3 carica
  batteria, 4 candelette, 5 avaria motore, 6 ABS, 7 airbag, 8 cinture, 9 riserva,
  10 porte aperte, 11 freno a mano. Bit 0-3 = spie di sicurezza, sempre visibili.

Le fonti VAN derivano da decodifiche comunitarie: finché non sono riscontrate sulla
vettura i valori viaggiano con qualità 2.

## Frequenze indicative

Segnali motore e velocità 10-20 al secondo; IMU 50-100 campioni al secondo, raggruppati
in trame; temperature e batteria 1-2 al secondo (batteria più rapida durante
l'avviamento); frame grezzi VAN quando abilitati, centinaia al secondo. Il traffico
stimato resta sotto il 30% della capacità della linea.

## Aggiornamento del front-end (D-039)

L'S3 riceve il firmware (BLE o Wi-Fi in modalità servizio), invia il comando di
ingresso in aggiornamento, poi porta il front-end nel bootloader tramite le linee
EN e GPIO0 previste sulla scheda madre e lo riprogramma sulla stessa UART con il
protocollo del bootloader Espressif. Dettagli da definire con la scheda madre.

## Compatibilità

Il campo versione di HELLO cambia solo per modifiche incompatibili; tipi o segnali
sconosciuti vengono ignorati dal ricevitore, così che front-end e S3 possano essere
aggiornati in momenti diversi.
