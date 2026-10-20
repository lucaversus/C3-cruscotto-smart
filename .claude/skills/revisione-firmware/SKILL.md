---
name: revisione-firmware
description: Checklist di revisione per modifiche al firmware del Data Logger e del cruscotto C3 (ESP32 front-end, ESP32-S3; KWP/K-line, VAN via RMT, MicroSD, RTC, STOP, display, audio, ventola). Usare prima di proporre, scrivere o approvare una modifica in data-logger/firmware o cruscotto/firmware.
---

# Revisione di una modifica firmware

Leggere prima `data-logger/firmware/logger/README.md` e `include/config.h`.
Ogni punto si risponde con "verificato in codice", "verificato da test",
"da misurare sull'hardware" oppure "non applicabile".

## Sicurezza verso il veicolo

- OBD solo lettura: servizi ammessi 0x01, 0x02 e 0x03 (D-035) e 0x81 per l'avvio; altri servizi solo con
  decisione D-xxx; mai cancellazione DTC, attuatori o scritture.
- VAN solo ricezione: nessun GPIO collegato al TX del transceiver.
- Nessun pin, bitrate o protocollo del veicolo dedotto senza fonte (D-008).
- STOP: nessuna sequenza può far ripartire la registrazione dopo l'arresto;
  SALVATO solo dopo sync, chiusura e rilettura riuscite.

## Tempi ISO 14230 (K-line)

- Fast init: bus libero W5 ≥ 300 ms, poi 25 ms basso e 25 ms alto.
- P3: pausa tra fine risposta e richiesta successiva ≥ 55 ms, ≤ 5 s.
- P4: pausa tra byte del tester 0–20 ms; eco di ogni byte verificata.
- Timeout risposta coerente con P2; risposte negative e frammenti conservati grezzi.

## Concorrenza e memoria

- Dati condivisi tra task: `std::atomic` o coda FreeRTOS, mai variabili semplici.
- Nessuna chiamata bloccante lunga nel task di salvataggio; coda piena → contatore
  `dropped` incrementato, mai blocco silenzioso.
- Stack dei task sufficiente per i buffer locali (es. 260 byte in receiveKwp).
- Nessuna allocazione dinamica nel percorso di acquisizione.

## MicroSD e formato dati

- Ogni errore di write/sync/close porta allo stato errore, senza SALVATO.
- Cambi al CSV: aggiornare `schema_version`, header e README nella stessa modifica.
- Throughput: stimare righe al secondo per sorgente rispetto alla frequenza SPI.

## Test e consegna

- Logica pura (parsing, CRC, pianificazione, calendario) in header `constexpr`,
  coperta da `static_assert` in `logic_checks.cpp` e da test in `host-tests/`.
  Per ogni correzione aggiungere un test che fallirebbe senza di essa.
- `python tools/dev.py check`, `build` e, se possibile, `lint`.
- Versione in `config.h`, README e `VERIFICA.md`; distinguere compilato,
  caricato e collaudato. Pubblicazione con la skill `chiusura-blocco`.

## Firmware del cruscotto (cruscotto/firmware, D-026…D-031)

- Pinout della scheda S3 solo da `cruscotto/firmware/common/include/board_8048s050.h`
  (verificato DSP-M001); MicroSD dell'S3 esclusa con IO10 alto finché vale la ripartizione D-029.
- L'S3 non ha collegamenti diretti al veicolo (D-029): ogni dato dell'auto arriva dal
  front-end; nessun pin dell'S3 verso fili dell'auto.
- Relè audio (D-028) e ventola (D-031) spenti al reset e in caso di errore; nessuna
  uscita attiva prima dell'inizializzazione.
- Funzionamento a motore spento (D-031): rispettare soglia di guardia della batteria,
  isteresi e tempo massimo; consumo a riposo verificato, non presunto.
- Display: retroilluminazione ridotta con temperatura alta; valori dell'auto distinti
  da quelli simulati (scritta DEMO nei firmware di prova).
