# Verifica software firmware 0.3.0

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
