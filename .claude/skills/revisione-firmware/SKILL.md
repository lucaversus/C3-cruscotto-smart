---
name: revisione-firmware
description: Checklist di revisione per modifiche al firmware del Data Logger C3 (ESP32, KWP/K-line, VAN via RMT, MicroSD, RTC, STOP). Usare prima di proporre, scrivere o approvare una modifica in data-logger/firmware.
---

# Revisione di una modifica firmware

Leggere prima `data-logger/firmware/logger/README.md` e `include/config.h`.
Ogni punto si risponde con "verificato in codice", "verificato da test",
"da misurare sull'hardware" oppure "non applicabile".

## Sicurezza verso il veicolo

- OBD solo lettura: nessun servizio diverso da 0x01 (e 0x81 per l'avvio) senza
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
