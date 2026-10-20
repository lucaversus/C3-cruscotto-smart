# Scheda madre del cruscotto — progetto preliminare

Revisione A, 20/10/2026. Cruscotto C3+AI, decisioni D-028, D-029, D-030.
Schema a blocchi: [C3AI-CR-BL-001 rev A](scheda-madre-blocchi.png) ([SVG](scheda-madre-blocchi.svg),
generatore `tools/genera-scheda-madre.py`).

**Stato: proposta.** Nessun componente scelto in via definitiva, nessuno schema
elettrico esecutivo, nessun circuito stampato. I pin del veicolo vengono da manuali
generici RTA e da fonti comunitarie e vanno verificati (D-008, D-022).

## Scopo

Una scheda fissata dietro l'ESP32-S3 8048S050 che raccoglie tutti i collegamenti
verso l'auto in un **connettore multipolare unico** (-J1) e contiene il **front-end**
ESP32 (D-029): l'S3 non ha fili diretti verso il veicolo. Prima della scheda madre
si costruisce un prototipo con i moduli già presenti (HW-ESP32, HW-CAN-VP230,
KL-001 su millefori, HW-IMU-LSM6DS3).

## Blocchi

| Sigla | Blocco | Contenuto proposto | Vincoli |
| --- | --- | --- | --- |
| -U1…U3 | Ingresso 12 V | protezione inversione polarità, TVS, filtro LC, interruttore di mantenimento lato alto (MOSFET P o driver dedicato) | D-030; fusibile di ramo nel cablaggio vicino al prelievo (HW-FUSE-HOLDER) |
| -C1 | Riserva avviamento | diodo + supercondensatore con carica limitata | capacità da calcolare dopo la misura C3AI-CR-PR-001 (P5) |
| -U4/U5 | Alimentazione | buck 12 → 5 V (ingresso ≥ 40 V, 2-3 A) + LDO 3,3 V a basso consumo | 5 V anche per l'S3 tramite -J2 / P1 |
| -U6 | Front-end | ESP32-WROOM-32E-**H4/H8** montato in fabbrica (HW-FE-MODULE) | senza PSRAM; stessi GPIO del logger 0.3.x |
| -U7 | VAN | SN65HVD230 solo ricezione: D a 3V3, nessuna resistenza da 120 Ω | prerequisiti D-022 bloccanti |
| -U8 | K-line | circuito KL-001 rev F (2N5551 + LM2903B, isteresi R10) | progetto da banco: protezioni auto da aggiungere |
| -U9 | IMU | LSM6DS3 a 0x6A (o connettore Grove per il modulo) | fissaggio rigido, assi indicati in serigrafia |
| -U10 | RTC (opzionale) | DS3231 a 0x68 | utile per i timestamp del dataset |
| -U11 | Programmazione | USB-seriale con reset automatico, oppure connettore a 6 poli | aggiornamenti senza smontare |
| -K1/K2 | Audio (D-028) | un relè a doppio scambio per canale, pilotato a transistor con diodo di ricircolo | a riposo radio → altoparlanti; uscite radio a ponte mai a massa |
| -J1 | Verso l'auto | connettore multipolare unico (tipo da scegliere, es. Molex Micro-Fit 3.0) | ritenuta meccanica e codifica contro l'inserimento errato |
| -J2 | Verso l'S3 | P1, P2, P6 della scheda 8048S050 | cavo corto |

## GPIO del front-end (proposta)

Ripresi dal logger 0.3.x (`data-logger/firmware/logger/include/config.h`), così che
raccolta dati e uso in auto leggano il veicolo con lo stesso codice.

| GPIO | Funzione | Note |
| --- | --- | --- |
| 16 / 17 | UART2 K-line RX / TX | come il logger |
| 34 | VAN RX | solo ingresso, come il logger |
| 21 / 22 | I2C SDA / SCL | IMU 0x6A, RTC 0x68 opz. |
| 25 / 33 | UART1 TX / RX verso l'S3 | |
| 35 | tensione batteria (partitore) | ADC1, solo ingresso |
| 39 | segnale chiave (+ dopo contatto) | ingresso protetto, solo ingresso |
| 13 | comando di mantenimento alimentazione | a riposo spento |
| 4 | LED di stato | |
| 18 / 19 / 23 / 27 | MicroSD opzionale | stessi pin del logger: la scheda madre può fare anche da registratore |

Evitati i pin di avvio (0, 2, 5, 12, 15) e quelli della flash (6-11).

## Collegamenti verso l'S3 (-J2)

| Connettore S3 | Segnale | Note |
| --- | --- | --- |
| P1 | 5 V, GND | alimentazione dell'S3 dalla scheda madre |
| P2 IO11 / IO12 | UART RX / TX dal front-end | MicroSD dell'S3 non usata, slot vuoto, IO10 alto |
| P2 IO13 | comando relè audio | spento al reset |
| P2 IO19 | riserva | stesso nodo di P3 IO19 (DSP-M004) |
| P6 Speak | uscita audio verso i relè | funzione di U1 su IO17/IO18 da confermare (DSP-M005/M006) |

Rispetto alla proposta precedente la UART passa su IO11/IO12: IO17/IO18 restano
all'amplificatore U1 se la prova d'ascolto lo conferma.

## Connettore verso l'auto (-J1, bozza)

| Via | Segnale | Origine nel veicolo |
| --- | --- | --- |
| 1 | + batteria (fusibile nel cablaggio) | presa OBD via 16 |
| 2 | massa di potenza | presa OBD via 4/5 |
| 3 | + dopo contatto (segnale chiave) | presa OBD via 1 |
| 4 | linea K | presa OBD via 7 |
| 5 / 6 | VAN DATA / DATA B | quadro 0004 vie 1 / 3 (ordine da verificare) |
| 7 | massa di riferimento VAN | quadro 0004 via 9 |
| 8-11 | canale Sx: radio + / −, altoparlante + / − | da identificare sul cablaggio radio |
| 12-15 | canale Dx: radio + / −, altoparlante + / − | da identificare |
| 16 | riserva | |

## Bilancio di potenza (stima, da misurare)

Totale 1-2 A a 5 V (5-10 W) con audio attivo: S3 e display 0,3-0,6 A, front-end e
interfacce 0,1-0,25 A, relè 0,07 A, amplificatore a picchi 0,5-1 A. A riposo
(spento con mantenimento aperto) obiettivo < 1 mA dalla batteria.

## Prima di disegnare lo schema elettrico

1. Esiti della prova C3AI-CR-PR-001: vie 16/1 della presa OBD e calo all'avviamento.
2. Prova d'ascolto su P6 per la funzione di U1.
3. Prototipo a banco: front-end HW-394 + S3 su UART, VP230 e KL-001 montati.
4. Prerequisiti VAN D-022 e prima cattura passiva dal quadro.
5. Identificazione dei fili altoparlanti della radio e del tipo di uscita.
6. Misura della temperatura dietro il quadro; scelta di connettori e componenti
   con temperatura e vibrazioni adatte.
7. Strumento di progetto del circuito stampato: KiCad (gratuito, open source, D-003).
