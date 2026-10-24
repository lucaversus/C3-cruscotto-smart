# Scheda madre del cruscotto — progetto preliminare

Revisione B, 21/10/2026 (rev A 20/10/2026). Cruscotto C3+AI, decisioni D-028…D-031.
Schema a blocchi: [C3AI-CR-BL-001 rev D](../../disegni/CR-BL-001_scheda-madre-blocchi.png) ([SVG](../../disegni/sorgenti/CR-BL-001_scheda-madre-blocchi.svg),
generatore `tools/genera-scheda-madre.py`). Studio d'ingombro: [C3AI-CR-PL-001 rev D](../../disegni/CR-PL-001_scheda-madre-ingombro.png)
([SVG](../../disegni/sorgenti/CR-PL-001_scheda-madre-ingombro.svg), generatore `tools/genera-ingombro-scheda-madre.py`).

**Stato: proposta.** Nessun componente scelto in via definitiva, nessuno schema
elettrico esecutivo, nessun circuito stampato. I pin del veicolo vengono da manuali
generici RTA e da fonti comunitarie e vanno verificati (D-008, D-022).

## Scopo

Una scheda fissata dietro l'ESP32-S3 8048S050 che raccoglie tutti i collegamenti
verso l'auto in un **connettore multipolare unico** (-J1) e contiene il **front-end**
ESP32 (D-029): l'S3 non ha fili diretti verso il veicolo. Prima della scheda madre
si costruisce un prototipo con i moduli già presenti (HW-ESP32, HW-CAN-VP230,
KL-001 su millefori, HW-IMU-LSM6DSO).

## Blocchi

| Sigla | Blocco | Contenuto proposto | Vincoli |
| --- | --- | --- | --- |
| -U1…U3 | Ingresso 12 V | protezione inversione polarità, TVS, filtro LC, interruttore di mantenimento lato alto (MOSFET P o driver dedicato) | D-030; fusibile di ramo nel cablaggio vicino al prelievo (HW-FUSE-HOLDER) |
| -C1 | Riserva avviamento | diodo + supercondensatore con carica limitata | capacità da calcolare dopo la misura C3AI-CR-PR-001 (P5) |
| -U4/U5 | Alimentazione | buck 12 → 5 V (ingresso ≥ 40 V, 2-3 A) + LDO 3,3 V a basso consumo | 5 V anche per l'S3 tramite -J2 / P1 |
| -U6 | Front-end | ESP32-WROOM-32E-**H4/H8** montato in fabbrica (HW-FE-MODULE) | senza PSRAM; stessi GPIO del logger 0.3.x |
| -U7 | VAN | SN65HVD230 solo ricezione: D a 3V3, nessuna resistenza da 120 Ω | prerequisiti D-022 bloccanti |
| -U8 | K-line | circuito KL-001 rev F (2N5551 + LM2903B, isteresi R10) | progetto da banco: protezioni auto da aggiungere |
| -U9 | IMU | LSM6DSO a 0x6A (prototipo: STEVAL-MKI196V1 DIL-24); in definitiva valutare ISM330 −40…+105 °C | fissaggio rigido, assi indicati in serigrafia; stesso chip del logger (D-033) |
| -U10 | RTC (opzionale) | DS3231 a 0x68 | utile per i timestamp del dataset |
| -U11 | Programmazione | USB-seriale con reset automatico, oppure connettore a 6 poli | aggiornamenti senza smontare |
| -K1/K2 | Audio (D-028) | un relè a doppio scambio per canale, pilotato a transistor con diodo di ricircolo | a riposo radio → altoparlanti; uscite radio a ponte mai a massa |
| -J1 | Verso l'auto | **Molex Micro-Fit 3.0, 24 vie** (D-044): sulla scheda 43045-2400, sul cablaggio 43025-2400 | ritenuta meccanica e codifica contro l'inserimento errato |
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
| 26 | ventola 12 V, PWM (D-031) | tramite MOSFET lato basso |
| 14 | giri ventola (tachimetrica) | ingresso con pull-up |
| 36 / 32 | NTC vicino al display / NTC sulla scheda | ADC1 |
| 18 / 19 / 23 / 27 | MicroSD opzionale | stessi pin del logger: la scheda madre può fare anche da registratore |

Evitati i pin di avvio (0, 2, 5, 12, 15) e quelli della flash (6-11).

## Raffreddamento e dominio sempre acceso (D-031)

- **Due domini di alimentazione.** Sempre acceso: regolatore lineare a bassissimo
  consumo dal +12 V protetto, front-end in sonno con risveglio periodico, NTC,
  misura della batteria, comando ventola. Principale: buck 5 V e S3, accesi con
  chiave e mantenimento (D-030).
- **Ventola 12 V** alimentata direttamente dal +12 V protetto (nessun bisogno del
  buck a motore spento), MOSFET in PWM su GPIO26, giri su GPIO14 per rilevare il blocco.
  Cuscinetti a sfera, temperatura nominale ≥ 70 °C, preferibilmente 4 fili.
- **Logica di partenza** (soglie da tarare): motore acceso e display > 60 °C →
  ventola proporzionale; motore spento, display > 55 °C e batteria a riposo
  > 12,3 V → ventola accesa; sotto 12,3 V spenta e bloccata fino al successivo
  avviamento; isteresi 5 °C; tempo massimo a motore spento 6 h.
- Limiti del pannello dichiarati dal rivenditore: funzionamento −20…+70 °C,
  magazzinaggio −30…+80 °C. Al sole d'estate la protezione principale resta
  passiva (schermatura, distanza dalla copertura, dissipatore); efficacia da
  misurare la prossima estate.

## Ingombro (C3AI-CR-PL-001)

**Contorno definitivo (D-045, 24/10/2026)** dal modello 3D del cruscotto dell'utente:
[`cruscotto/meccanica/scheda-madre-contorno.dxf`](../meccanica/scheda-madre-contorno.dxf),
**178,7 × 74 mm**, 6 fori di fissaggio Ø3 in (±80, 13), (±75, 48), (±30, 79) mm, due
rientranze laterali. La scheda madre sta **direttamente dietro la S3**. Il generatore dello
studio legge il DXF e controlla che ogni zona stia nel contorno, lontana dai fori, dalla
ventola e dagli interruttori.

- **Ventola** (D-031): foro Ø38 al centro con ventola 40 × 40 × 10 a 12 V sul lato
  opposto, che soffia verso la S3; in alternativa 30 × 30 con foro Ø28.
- **Interruttori -S1/-S2** ai due estremi, azionati dai pulsanti del quadro originale;
  posizione indicativa alle rientranze laterali, tipo e corsa da scegliere sul modello 3D.
- **-J1** Micro-Fit 2×12 (D-044) al bordo inferiore, al centro; **-J2** verso la S3 al
  bordo superiore, al centro.

| Voce | Area |
| --- | --- |
| Blocchi di base, netto | ≈ 3 680 mm² |
| Base con piste e distanze (× 1,5) | ≈ 5 520 mm² |
| Facoltativi (RTC + CR2032, MicroSD) | ≈ 705 mm² netti |
| Contorno meno foro della ventola | ≈ 9 510 mm² |

Conclusione preliminare: tutti i blocchi di base e i facoltativi RTC/MicroSD stanno su una
sola faccia attorno alla ventola. Il supercondensatore di riserva (36 × 24 mm, misura P5
della prova sulla presa OBD) non trova posto su questa faccia: retro o fuori scheda, da
decidere. Da rilevare sul pezzo: posizione relativa delle due schede, connettori P1/P2/P6
e altezze dei componenti sul retro della S3.

## Montaggio a mano e raffreddamento dei componenti (D-046)

- Si fa produrre **solo il circuito stampato**; i componenti li salda l'utente.
- Componenti ammessi: foro passante; SMD con passivi **0805 o più grandi**, integrati in
  **SOIC, SOT, TSSOP**; moduli con piazzole sul bordo (WROOM). **Esclusi QFN, BGA, LGA**:
  l'IMU (LGA) resta su modulo o adattatore con connettore (es. STEVAL-MKI196V1 o il suo
  equivalente definitivo, D-033). Ogni scelta di componente va controllata con questa regola.
- **Componenti che scaldano di più sulla faccia interna**, rivolta verso la S3, attorno al
  foro della ventola (D-045): convertitore 12 → 5 V, regolatore 3,3 V, protezioni d'ingresso,
  front-end. Il flusso della ventola li investe prima di uscire tra le due schede.
- Distanza tra scheda madre e S3: da fissare a progetto completato, simulando nel modello 3D
  lo spessore della scheda con i componenti.

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

## Connettore verso l'auto (-J1, Micro-Fit 3.0 24 vie, D-044)

Tipo deciso il 23/10/2026 (D-044); assegnazione delle vie ancora bozza. Lo stesso cablaggio
dell'auto (femmina 43025-2400) si innesta prima nella spina volante del prototipo a banco
(43020-2400, tavola C3AI-DL-EL-004) e poi nel connettore della scheda definitiva (43045-2400).

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
| 17-24 | riserva (es. luci, comandi, segnali futuri) | |

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
6. Rilievo sul pezzo S3: connettori P1/P2/P6, USB-C, MicroSD, altezze dei
   componenti sul retro, zona antenna Wi-Fi; scelta dei distanziali con dissipatore.
7. Misura della temperatura dietro il quadro; scelta di connettori e componenti
   con temperatura e vibrazioni adatte.
8. Strumento di progetto del circuito stampato: KiCad (gratuito, open source, D-003); produzione del solo
   circuito stampato e montaggio a mano (D-046).
