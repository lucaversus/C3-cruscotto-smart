# Disegni del progetto — Cruscotto C3+AI

Tutti i disegni e le infografiche del progetto in un'unica cartella. Aprendo questa
cartella su GitHub compaiono qui sotto le anteprime: si clicca un'immagine per vederla
grande.

- **File `.png`** (in questa cartella): l'immagine da guardare o stampare.
- **File `.svg`** (in [`sorgenti/`](sorgenti/)): la stessa tavola in formato vettoriale,
  generata dagli script in `tools/`; serve per modificarla e resta nitida a qualsiasi
  ingrandimento. Non va aperta per la consultazione normale.

Codici: `DL` = Data Logger, `CR` = Cruscotto; `BL` schema a blocchi, `EL` collegamenti,
`KL` K-line, `PR` istruzione di prova, `PL` disposizione. Ogni tavola ha il proprio
cartiglio con revisione e stato (D-009, D-024).

## Cruscotto

### CR-BL-001 — Scheda madre, schema a blocchi (rev D, preliminare)
Architettura della scheda madre: alimentazione, front-end, interfacce, audio. Documento: [scheda-madre.md](../cruscotto/docs/scheda-madre.md).

[![CR-BL-001](CR-BL-001_scheda-madre-blocchi.png)](CR-BL-001_scheda-madre-blocchi.png)

### CR-EL-001 — Scheda madre, schema elettrico: alimentazione (rev C, proposta non verificata)
Ingresso 12 V protetto, 5 V principale acceso con chiave o mantenimento, 3,3 V sempre acceso, misure per il front-end. Sorgente KiCad: [scheda-madre.kicad_sch](../cruscotto/pcb/scheda-madre/scheda-madre.kicad_sch), generata da `tools/genera-schema-scheda-madre.py`.

[![CR-EL-001](CR-EL-001_scheda-madre-alimentazione.png)](CR-EL-001_scheda-madre-alimentazione.png)

### CR-EL-002 — Scheda madre, schema elettrico: front-end ESP32 (rev A, proposta non verificata)
Modulo ESP32-WROOM-32E, programmazione USB-C a banco, reset automatico, collegamento con l'S3, NTC, ventola a 4 fili. Sorgente KiCad: [front-end.kicad_sch](../cruscotto/pcb/scheda-madre/front-end.kicad_sch).

[![CR-EL-002](CR-EL-002_scheda-madre-front-end.png)](CR-EL-002_scheda-madre-front-end.png)

### CR-EL-003 — Scheda madre, schema elettrico: interfacce veicolo (rev B, proposta non verificata)
K-line dalla KL-001 rev F con protezioni per l'auto, VAN in sola ricezione con il modulo blu SN65HVD230 su file di pin (D-051). Sorgente KiCad: [interfacce-veicolo.kicad_sch](../cruscotto/pcb/scheda-madre/interfacce-veicolo.kicad_sch).

[![CR-EL-003](CR-EL-003_scheda-madre-interfacce-veicolo.png)](CR-EL-003_scheda-madre-interfacce-veicolo.png)

### CR-EL-004 — Scheda madre, schema elettrico: sensori e memoria (rev B, proposta non verificata)
Zoccolo per il modulo IMU STEVAL-MKI196V1, RTC DS3231SN con CR2032, modulo MicroSD su fila di pin (D-051). Sorgente KiCad: [sensori-memoria.kicad_sch](../cruscotto/pcb/scheda-madre/sensori-memoria.kicad_sch).

[![CR-EL-004](CR-EL-004_scheda-madre-sensori-memoria.png)](CR-EL-004_scheda-madre-sensori-memoria.png)

### CR-EL-005 — Scheda madre, schema elettrico: collegamento S3 e audio (rev A, proposta non verificata)
Cavetti MX1.25 verso P1, P2 e P6 della S3, relè audio con altoparlanti in serie sull'uscita della S3. Sorgente KiCad: [s3-audio.kicad_sch](../cruscotto/pcb/scheda-madre/s3-audio.kicad_sch).

[![CR-EL-005](CR-EL-005_scheda-madre-s3-audio.png)](CR-EL-005_scheda-madre-s3-audio.png)

### CR-PL-001 — Scheda madre, studio d'ingombro (rev E, preliminare)
Zone dei componenti sul contorno definitivo dal modello 3D (178,7 × 74 mm, D-045), foro centrale della ventola e interruttori dei pulsanti del quadro.

[![CR-PL-001](CR-PL-001_scheda-madre-ingombro.png)](CR-PL-001_scheda-madre-ingombro.png)

### CR-PR-001 — Prova sulla presa diagnosi OBD (rev A, eseguita: OBD-M001)
Vie 16/1/4/5 e calo all'avviamento, con tabella da compilare.

[![CR-PR-001](CR-PR-001_prova-presa-obd.png)](CR-PR-001_prova-presa-obd.png)

## Data Logger

### DL-EL-004 — Data Logger completo a banco su millefori (rev C, proposta)
Tutti i moduli disegnati come appaiono: ESP32, K-line con i suoi componenti nelle posizioni di KL-003, RTC con pila, MicroSD, IMU LSM6DSO, OLED, modulo VAN (solo ricezione), STOP e alimentatore da banco; fili saldati tra le basette, numerati W1…W31 (D-042).

[![DL-EL-004](DL-EL-004_logger-completo-millefori.png)](DL-EL-004_logger-completo-millefori.png)

### DL-KL-001 — Interfaccia K-line, schema elettrico (rev F)
Schema tecnico IEC del modulo K-line. Documento: [kline-autocostruita.md](../data-logger/docs/kline-autocostruita.md).

[![DL-KL-001](DL-KL-001_schema-kline.png)](DL-KL-001_schema-kline.png)

### DL-KL-002 — K-line, collegamenti illustrati della prova a banco (rev A)
ESP32, modulo, alimentatore da banco e resistenza del simulatore disegnati come appaiono.

[![DL-KL-002](DL-KL-002_kline-collegamenti-illustrati.png)](DL-KL-002_kline-collegamenti-illustrati.png)

### DL-KL-003 — K-line su millefori (rev A)
Disposizione dei componenti e dei fili sulla basetta, con elenco foro per foro.

[![DL-KL-003](DL-KL-003_kline-millefori.png)](DL-KL-003_kline-millefori.png)

### DL-EL-003 — Collegamenti a banco del logger (rev B)
SD, RTC, OLED e pulsante STOP sull'ESP32 HW-394. Documento: [collegamenti-banco-030.md](../data-logger/docs/collegamenti-banco-030.md).

[![DL-EL-003](DL-EL-003_collegamenti-banco-logger.png)](DL-EL-003_collegamenti-banco-logger.png)

### DL-BL-001 — Architettura funzionale del Data Logger (rev E)

[![DL-BL-001](DL-BL-001_architettura-data-logger.png)](DL-BL-001_architettura-data-logger.png)

### DL-EL-001 — Collegamenti della proposta iniziale (rev E, storico)
Sostituito da DL-EL-003; conservato per tracciabilità.

[![DL-EL-001](DL-EL-001_collegamenti-iniziali-storico.png)](DL-EL-001_collegamenti-iniziali-storico.png)

## Rigenerare un disegno

```powershell
python tools/genera-kline-millefori.py           # scrive disegni/sorgenti/DL-KL-003_kline-millefori.svg
python tools/render_png.py disegni/sorgenti/DL-KL-003_kline-millefori.svg   # anteprima in disegni/
```

Le foto dei componenti restano in [`data-logger/docs/hardware-photos/`](../data-logger/docs/hardware-photos/README.md).
