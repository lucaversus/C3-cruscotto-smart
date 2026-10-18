# Inventario hardware — Cruscotto C3+AI / Data Logger

Aggiornato: **2026-10-18**. Vista generata da [hardware.json](hardware.json).
Non modificare manualmente: usare `python tools/project_preflight.py --render-inventory`.

Il materiale presente ma non collaudato va valutato prima di proporre acquisti sostitutivi.
Le decisioni definitive restano nel [README principale](../../README.md#decisioni-definitive).

## Stati

- `present_verified`: Presente; verifiche effettivamente eseguite indicate nella voce.
- `present_declared`: Presente secondo il contesto utente; non equivale a verifica elettrica.
- `ordered_pending`: Ordinato dall’utente, non ancora arrivato.
- `not_confirmed`: Disponibilità o ordine non confermati: non presumere possesso né assenza.
- `candidate`: Solo ipotesi di progetto; non confondere con materiale acquistato.

## Materiale e fonti

### HW-ESP32 — ESP32 HW-394 a 30 pin, modulo marcato ESP-32D

**Stato:** `present_verified` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Identificazione e collaudo a banco nella chat; data-logger/backups/esp32-hw394/README.md e firmware/diagnostic/README.md. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json.

**Foto archiviate:** [esp32-hw394-fronte.jpg](hardware-photos/esp32-hw394-fronte.jpg)

**Verifiche documentate:**

- esptool: ESP32-D0WD-V3 rev. 3.1, flash 4 MB, quarzo 40 MHz
- COM3 CH340; diagnostica 0.1.0 caricata, avvio e oltre 70 s osservati
- Backup flash completo con SHA-256 verificato; ripristino non provato
- Foto frontale archiviata: HW-394 / ESP-32D e basetta di espansione a morsetti visibili; nessuna verifica elettrica della basetta.

**Da verificare:**

- Piedinatura fisica HW-394 e corrente disponibile per i moduli esterni
- Basetta a morsetti visibile in foto: continuità e corrispondenza delle etichette non ancora provate.

### HW-CAN-MCP2515 — Modulo MCP2515, quarzo 8 MHz, transceiver marcato VP230

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Inventario iniziale fornito dall’utente; successiva correzione “ma non abbiamo già il modulo can?” il 18/10/2026. Il precedente “non possiedo altro” non annulla più questa voce. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json.

**Foto archiviate:** [mcp2515-fronte.jpg](hardware-photos/mcp2515-fronte.jpg), [mcp2515-dettaglio.jpg](hardware-photos/mcp2515-dettaglio.jpg)

**Verifiche documentate:**

- Foto fronte e dettaglio archiviate: MCP2515, quarzo 8.000 e marcatura VP230 leggibili; connettori J1/J3 non ancora identificati elettricamente.
- M-001 / M-002: resistenza H-L riferita 51,8 kOhm e ripetuta dopo controllo C-001 dei puntali (0 riferito). Nessuna conclusione su compatibilità o funzionamento CAN.
- M-003: utente riferisce 119 Ohm direttamente su R2 (marcata 121).
- M-004a/b: utente riferisce circa 52 kOhm da L a ciascuna delle due estremità di R2; non indica un collegamento diretto a bassa resistenza verso L nelle condizioni della prova.
- M-005a/b: H verso R2 lato POW riferito 0 (Ω richiesto), lato J1 120 Ohm; compatibile con collegamento diretto del lato POW a H. A modulo spento H-L resta circa 52 kOhm; circuito e alimentazione non ancora validati.

**Da verificare:**

- Venditore dichiara 5 V: alimentazione interna e livelli SPI non verificati
- Identità effettiva del transceiver, terminazione e compatibilità ESP32 da verificare
- Non collegare né decidere un sostituto prima della verifica
- Foto retro non disponibile nell’archivio; prima di alimentare, identificare con tester VCC interno e funzione dei ponticelli senza presumerne il circuito.
- Acquisire il retro del modulo, non ancora archiviato, per identificare piste, alimentazione e funzione dei ponticelli prima di alimentare.

### HW-CAN-VP230 — Modulo CAN blu VP230 / SN65HVD230

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Inventario iniziale utente e correzione sul CAN del 18/10/2026. Nessun collaudo del modulo documentato. Foto recuperate dai Download il 18/10/2026, archiviate con SHA-256 in docs/hardware-photos/manifest.json.

**Foto archiviate:** [can-vp230-fronte.jpg](hardware-photos/can-vp230-fronte.jpg), [can-vp230-dettaglio.jpg](hardware-photos/can-vp230-dettaglio.jpg)

**Verifiche documentate:**

- Foto fronte e dettaglio archiviate: marcatura VP230 e serigrafie 3.3V/GND/RX/TX; resistenza con codice 121 e serigrafia 120R visibili, valore non misurato.

**Da verificare:**

- Alimentazione indicata 3,3 V: da verificare sul modulo
- Resistenza 120 ohm apparentemente fissa: da misurare; non aggiungere terminazione al bus auto senza verifica
- Possibile uso col controller TWAI interno ESP32: scelta subordinata a verifica elettrica

### HW-SD-MODULE — Lettore MicroSD SPI 3,3 V — riferimento consigliato Create idea B0DRWPJ1T5

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link precedente; utente conferma “quelli che avevi consigliato tu”, poi “non sono arrivati” il 18/10/2026. Riferimento di acquisto non verificato fisicamente.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Quantità, modello e serigrafie del materiale ricevuto
- Alimentazione, livelli SPI e picchi di corrente

### HW-RTC — RTC DS3231 / AT24C32 — riferimento consigliato TECNOIOT B07LH592FM

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Link e conferma ordine in chat; “non sono arrivati” il 18/10/2026. Nessuna batteria confermata.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Modello, quantità, pull-up I2C e circuito di ricarica batteria
- Non inserire una CR2032 non ricaricabile prima di verificare il circuito

### HW-OLED — Display OLED monocromatico I2C consigliato — modello e controller non riscontrati

**Stato:** `ordered_pending` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Conferma ordine dei componenti consigliati; non è disponibile un riepilogo ordine che identifichi esattamente il display. Non richiedere di nuovo tutti i link già in chat.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Distinguere raccomandazione 1,3 pollici e link 0,96/0,91; non inventare modello definitivo
- Controller, risoluzione, ordine dei pin e compatibilità 3,3 V sul pezzo ricevuto

### HW-SCANNER — Launch Creader 3001

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger — strumento di verifica

**Fonte:** Foto fornite e conferma utente che si tratta della stessa C3 e che dispone ancora del lettore.

**Verifiche documentate:**

- Foto del lettore sulla stessa C3: “Protocol Type CAN”

**Da verificare:**

- Bitrate, identificativi CAN 11/29 bit e accesso BSI non determinati dalla foto

### HW-SD-CARD — Scheda MicroSD (supporto di memoria, distinta dal lettore)

**Stato:** `not_confirmed` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Nessuna conferma esplicita nel contesto disponibile.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso, capacità e formattazione da confermare prima di ordinare un duplicato

### HW-AUTO-POWER — Alimentazione automotive, protezioni e arresto controllato

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Discussione alimentazione dal quadro: possibilità richiesta, non decisione approvata su circuito o pin.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Modello convertitore, fusibile, protezioni, punto di prelievo e chiusura file SD non definiti

### HW-OBD-HARNESS — Derivazione dietro la presa OBD

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Data Logger

**Fonte:** Preferenza utente: lasciare libera frontalmente la presa OBD; adattatore non identificato né ordinato.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Connettore posteriore C3, accesso fisico, lunghezza derivazione e massa di riferimento

### HW-DASH-DISPLAY — Scheda RCmall ESP32-S3 con display 5 pollici — variante da identificare

**Stato:** `candidate` · **Quantità:** non confermata · **Ambito:** Cruscotto futuro

**Fonte:** Osservazioni preliminari nel README originale; non attestano un ordine o un collaudo.

**Verifiche documentate:**

- Nessun collaudo elettrico del modulo documentato.

**Da verificare:**

- Possesso e modello non confermati per questa fase; non trasferire i dati della variante 1,9 pollici
- PCB, flash, PSRAM, interfaccia display e pinout da verificare

### HW-MULTIMETER — UNI-T UT210E — multimetro / pinza amperometrica

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger — strumento di verifica

**Fonte:** Utente il 18/10/2026: “ho il tester per verificare il modulo con mcp2515”. Foto tester.jpg fornita il 18/10/2026: modello identificato visivamente; lettura M-001 successivamente riferita dall’utente, controllo puntali C-001 successivamente riferito 0, H-L ripetuta con lo stesso valore.

**Foto archiviate:** [tester-unit-ut210e.jpg](hardware-photos/tester-unit-ut210e.jpg)

**Verifiche documentate:**

- Identificazione visiva UNI-T UT210E nella foto tester.jpg, archiviata con SHA-256.
- Contatto diretto tra i puntali: utente riferisce 0 in risposta al controllo C-001 richiesto in modalità Ω.

**Da verificare:**

- Taratura assoluta e stato completo dello strumento non verificati.

### HW-ESP32-TERMINAL-BASE — Basetta di espansione a morsetti per ESP32 HW-394, visibile in foto

**Stato:** `present_declared` · **Quantità:** 1 · **Ambito:** Data Logger

**Fonte:** Foto originale PXL_20261017_202948899.jpg già fornita, recuperata dai Download e archiviata il 18/10/2026.

**Foto archiviate:** [esp32-hw394-fronte.jpg](hardware-photos/esp32-hw394-fronte.jpg)

**Verifiche documentate:**

- Presenza visibile nella fotografia esp32-hw394-fronte.jpg

**Da verificare:**

- Continuità tra morsetti e socket, etichette e compatibilità meccanica da verificare

## Proposta di collegamento — non validata fisicamente

GPIO proposti nel firmware 0.2.0, non cablaggio fisico approvato. GPIO32/33 illustrati per pulsanti eventuali, non inizializzati.

| Funzione firmware | GPIO proposto |
| --- | --- |
| `kSda` | 21 |
| `kScl` | 22 |
| `kSck` | 18 |
| `kMiso` | 19 |
| `kMosi` | 23 |
| `kSdCs` | 27 |

L'illustrazione dei moduli non è la disposizione fisica dei pin.
