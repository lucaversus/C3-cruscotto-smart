# Dipendenze e attribuzioni — 0.3.0

- Framework Arduino-ESP32 2.0.17 tramite Espressif32 6.12.0 (PlatformIO):
  https://github.com/espressif/arduino-esp32/tree/2.0.17 — LGPL-2.1 e licenze dei componenti ESP-IDF.
- SdFat 2.3.1: https://github.com/greiman/SdFat/tree/cda057318bec196183d4cc92b01bc1dd64bbfb02 — MIT.
- U8g2 Arduino 2.37.1: https://github.com/olikraus/U8g2_Arduino/tree/b3a40de8822187c941b40cbbaaa77604a7ab90c7 — BSD-2-Clause.
  Le distribuzioni scaricate da PlatformIO conservano le rispettive licenze.
- Estrazione enhanced-Manchester e CRC VAN in include/logger_logic.h adattati da
  https://github.com/morcibacsi/esp32_rmt_van_rx/tree/d64064fabf1f342a8cbe1c0022bb0e784a4ceae0
  (Peter Pinter / haxplore), MIT. Driver RMT e gestione sessione integrati nel progetto.
  Adattamento locale con buffer limitati e conservazione dei frame invalidi.

## Licenza del codice VAN adattato

```text
MIT License

Copyright (c) 2018 haxplore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.```
