# Verifica software firmware 0.3.x

Cruscotto C3+AI / Data Logger — 19/10/2026.

- 49 static_assert superati, inclusa matrice di 32 combinazioni delle condizioni STOP.
- 15 test Python del preflight superati.
- Preflight inventario/foto/decisioni/GPIO: OK.
- git diff --check: OK.
- Nessun caricamento su ESP32 o collaudo su SD/RTC/OLED/K-line/VAN effettuato per questa release.

| Profilo | RAM statica | Programma | SHA-256 firmware.bin |
| --- | --- | --- | --- |
| esp32-hw394-logger | 31936 byte | 332265 byte | `c67491b85aa2eb245f3b53667c70f8b0203ee9e72e1344ab1d4e222edefb372f` |
| esp32-hw394-vehicle | 32056 byte | 342445 byte | `5cc5d7ebd77819435a1c5eabe085662957c9e22a7b03a395b112039dbcc03c59` |

I binari sono artefatti locali ignorati sotto `.pio/build/<profilo>/`;
ricostruirli dai sorgenti e dalle dipendenze fissate in platformio.ini.
SHA riferiti a questa compilazione locale, non a un firmware caricato.
I test statici non sostituiscono la prova delle temporizzazioni UART/RMT,
la fault injection SD o la misura delle perdite in acquisizione concorrente.

## Aggiornamento hardware 20/10/2026

Profilo banco caricato su COM3 con BOOT manuale, hash verificati da esptool.
Avvio confermato dalla seriale: version=0.3.0, kwp=0 van=0, ATTESA SD,
rtc=oscillator_stop. SD non collegata; nessuna prova di scrittura o arresto SD.
Questo aggiornamento supera il solo stato non caricato del rapporto 19/10.

## Release 0.3.1 — 20/10/2026 (D-022)

- Due nuovi gruppi di static_assert sulla rotazione dei PID non prioritari
  e sull'esclusione di PID bitmap/prioritari; controllo d'intervallo SPI 0,4-25 MHz.
- Controlli logici verificati anche con g++ host (`-std=gnu++14 -fsyntax-only`):
  verifica parziale, non sostituisce la build ESP32.
- Build ESP32 dei due profili affidata alla pipeline `Project checks` sul branch
  di pubblicazione, prima dell'unione in main: nell'ambiente di sviluppo usato
  l'installazione di PlatformIO da PyPI non era consentita.
- Nessun caricamento su ESP32; nessun collaudo KWP, VAN o SD a frequenze > 1 MHz.

## Test host e analisi statica — 20/10/2026 (D-023)

- `host-tests/test_logic.cpp`: 481.849 controlli superati con g++ e clang++
  (`-Wall -Wextra -Werror`). Cinque difetti introdotti di proposito nelle copie
  degli header sono stati tutti rilevati.
- Il CRC-15 del firmware coincide con un'implementazione di riferimento
  indipendente su 2000 sequenze casuali.
- cppcheck eseguito dalla pipeline (non disponibile nell'ambiente di sviluppo usato).
- Sorgenti firmware invariati rispetto alla 0.3.1: nessuna nuova versione.
