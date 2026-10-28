# Materiale acquistato e avanzi — Data Logger e scheda madre del cruscotto

Revisione A — 28/10/2026. Per proporre ad altri progetti i componenti che avanzano. Dati da
`data-logger/docs/hardware.json` (possesso, ordini) e dagli ordini preparati per la scheda madre
(`cruscotto/docs/lista-acquisti-scheda-madre.md`). Quantità usate: un Data Logger e una scheda madre. Dove la
quantità non è registrata è scritto «da riscontrare»: non è stimata. Elenco anche in `materiale-e-avanzi.csv`.
Dal 28/10/2026 giacenze, impegni per progetto e ordini sono tenuti anche nel magazzino condiviso
`lucaversus/DB-componenti-elettronici` (progetti `c3-data-logger` e `c3-scheda-madre`).

## 1. In possesso o già ordinato

| Articolo | Inventario | Presi | Usati logger | Usati scheda madre | Avanzo | Note |
| --- | --- | --- | --- | --- | --- | --- |
| ESP32 HW-394 (ESP-32D, 30 pin) | HW-ESP32 | 1 | 1 | — | 0 | scheda del Data Logger |
| Basetta a morsetti per HW-394 | HW-ESP32-TERMINAL-BASE | 1 | 1 | — | 0 |  |
| Modulo MCP2515 (quarzo 8 MHz, VP230) | HW-CAN-MCP2515 | 1 | 0 | 0 | 1 | non usato: il VAN usa il modulo blu (D-022) |
| Modulo CAN blu SN65HVD230 | HW-CAN-VP230 | 2 | 1 | 1 (J8/J9) | 0 | il secondo va modificato come il primo |
| Lettore MicroSD SPI 3,3 V (Create idea B0DRWPJ1T5, Amazon) | HW-SD-MODULE | da riscontrare | 1 | 0 (J7 non montato) | presi − 1 |  |
| Scheda MicroSD | HW-SD-CARD | da riscontrare | 1 | — | presi − 1 |  |
| Modulo RTC DS3231SN + AT24C32 | HW-RTC | da riscontrare | 1 | 0 (sulla scheda il chip) | presi − 1 |  |
| Display OLED I2C | HW-OLED | da riscontrare | 1 | — | presi − 1 | modello da riscontrare |
| Scheda RCmall ESP32-S3 con display 5" | HW-DASH-DISPLAY | 1 | — | 1 | 0 |  |
| Spine MX1.25 per i cavetti verso la S3 | HW-MX125-PLUGS | da riscontrare | — | 3 (P1, P2, Speak) | presi − 3 |  |
| STEVAL-MKI196V1 (IMU LSM6DSO), Farnell 2987032 | HW-IMU-LSM6DSO | 1 | — (logger in pausa) | 1 (J6) | 0 | arrivata 28/10/2026; usata sulla scheda madre |
| Altoparlante di prova Multicomp Pro ABS-216-RC, Farnell | HW-AUDIO-SPK-TEST | 1 | — | prova a banco | 0 | arrivato 28/10/2026 |
| Portafusibile | HW-FUSE-HOLDER | ordinato, quantità da riscontrare | 1 | — |  | modello da riscontrare |
| LM2903BYDT (SOIC-8), Farnell 22/10/2026 | HW-KLINE-INTERFACE | 2 | 1 | 0 (la scheda usa quello LCSC) | 1 | arrivato 28/10/2026 |
| 2N5551BU (TO-92), Farnell 22/10/2026 | HW-KLINE-INTERFACE | 5 | 1 | 0 (la scheda usa MMBT5551) | 4 | arrivato 28/10/2026 |
| Resistenze a foro passante 330 Ω, 47 kΩ, 510 Ω 1 W, 68 kΩ, 10 kΩ, 150 kΩ, 4,7 kΩ, 1 kΩ, 330 kΩ, Farnell 22/10/2026 | HW-KLINE-INTERFACE | 10 per valore | 1 ciascuna (10 kΩ: 2; 510 Ω solo simulatore) | 0 | 9 per valore (10 kΩ: 8; 510 Ω: 10) | arrivate 28/10/2026, a foro passante |
| Condensatori 100 nF e 10 µF (C1, C2 della K-line), Farnell 22/10/2026 | HW-KLINE-INTERFACE | 10 + 10 | 1 + 1 | 0 | 9 + 9 | arrivati 28/10/2026, a foro passante |
| Millefori Multicomp MC01009 72 × 47 mm, Farnell 22/10/2026 | HW-KLINE-INTERFACE | 5 | 1 | — | 4 | arrivati 28/10/2026 |
| Launch Creader 3001 (scanner) | HW-SCANNER | 1 | strumento | strumento | — |  |
| UNI-T UT210E (multimetro) | HW-MULTIMETER | 1 | strumento | strumento | — |  |
| Alimentatore da banco | HW-BENCH-PSU | 1 | strumento | strumento | — |  |

## 2. Ordini della scheda madre (carrelli pronti, non ancora ordinati)

Avanzo = quantità da ordinare − quantità usata da una scheda. Su LCSC molti passivi hanno confezione minima da 100.

| Fornitore | Codice produttore | Produttore / descrizione | Presi | Usati | Avanzo | Per |
| --- | --- | --- | --- | --- | --- | --- |
| LCSC | RC0805FR-0713KL | YAGEO | 100 | 1 | 99 | R4 |
| LCSC | CL32B225KCJSNNE | Samsung Electro-Mechanics | 6 | 3 | 3 | C4 C5 C11 |
| LCSC | GRM32ER61A476KE20L | muRata | 4 | 2 | 2 | C7 C8 |
| LCSC | GRM31CR71C106KA12L | muRata | 5 | 1 | 4 | C35 |
| LCSC | GRM2195C1H682JA01D | muRata | 20 | 1 | 19 | C9 |
| LCSC | CC0805JRNPO9BN390 | YAGEO | 50 | 1 | 49 | C10 |
| LCSC | RC0805FR-07100KL | YAGEO | 100 | 9 | 91 | R8 R9 R11 R14 R22 R23 R27 R47 R55 |
| LCSC | RC0805FR-071KL | YAGEO | 100 | 6 | 94 | R17 R20 R21 R29 R30 R46 |
| LCSC | RC0805FR-074K7L | YAGEO | 100 | 5 | 95 | R18 R19 R33 R34 R45 |
| LCSC | RC0805FR-075K1L | YAGEO | 100 | 2 | 98 | R31 R32 |
| LCSC | RC0805FR-0710K2L | YAGEO | 100 | 1 | 99 | R2 |
| LCSC | RC0805FR-07162KL | YAGEO | 100 | 1 | 99 | R3 |
| LCSC | C0805C224K1RACTU | KEMET | 5 | 1 | 4 | C12 |
| LCSC | RC0805FR-0784K5L | YAGEO | 100 | 1 | 99 | R6 |
| LCSC | RC0805FR-0743K2L | YAGEO | 100 | 1 | 99 | R10 |
| LCSC | RC0805FR-07470KL | YAGEO | 100 | 1 | 99 | R13 |
| LCSC | RC0805FR-076K8L | YAGEO | 100 | 1 | 99 | R24 |
| LCSC | RC0805FR-0747KL | YAGEO | 100 | 1 | 99 | R39 |
| LCSC | RC0805FR-0768KL | YAGEO | 100 | 1 | 99 | R40 |
| LCSC | RC0805FR-07150KL | YAGEO | 100 | 1 | 99 | R42 |
| LCSC | RC0805FR-07330KL | YAGEO | 100 | 1 | 99 | R44 |
| LCSC | RC0805FR-07100RL | YAGEO | 100 | 1 | 99 | R54 |
| LCSC | RC0805JR-070RL | YAGEO | 100 | 1 | 99 | R37 |
| LCSC | 430252400 | MOLEX | 2 | 1 | 1 | femmina J1 del cablaggio |
| LCSC | CH340C | WCH | 2 | 1 | 1 | U6 |
| LCSC | TYPE-C-31-M-12 | Korean Hroparts Elec | 5 | 1 | 4 | J3 |
| LCSC | B340A-13-F | DIODES | 10 | 1 | 9 | D13 |
| LCSC | TPS54360BDDA | TI | 2 | 1 | 1 | U2 |
| LCSC | LMR36510ADDAR | TI | 2 | 1 | 1 | U3 |
| LCSC | LM74700QDBVTQ1 | TI | 2 | 1 | 1 | U1 |
| LCSC | LM2903BYDT | ST | 2 | 1 | 1 | U7 |
| LCSC | DS3231SN# | MAXIM | 1 | 1 | 0 | U10 |
| LCSC | ZXMP6A13FTA | DIODES | 2 | 1 | 1 | Q3 |
| LCSC | AO3400A | ElecSuper | 20 | 1 | 19 | Q9 |
| LCSC | MMBTA06LT1G | onsemi | 20 | 1 | 19 | Q4 |
| LCSC | MMBT3904LT1G | FUXINSEMI | 50 | 3 | 47 | Q5-Q7 |
| LCSC | MMBT5551LT1G | onsemi | 20 | 1 | 19 | Q8 |
| LCSC | SMCJ26CA | Littelfuse | 5 | 1 | 4 | D1 |
| LCSC | SMBJ26CA | R+O | 10 | 1 | 9 | D8 |
| LCSC | B560C-13-F | DIODES | 5 | 1 | 4 | D2 |
| LCSC | ESP32-WROOM-32E-H4 | ESPRESSIF | 1 | 1 | 0 | U4 |
| LCSC | 1N4148W-7-F | DIODES | 20 | 4 | 16 | D3 D9 D11 D12 |
| LCSC | BAT54J | BLUE ROCKET | 50 | 1 | 49 | D4 |
| LCSC | BAT54S-7-F | DIODES | 5 | 2 | 3 | D5 D6 |
| LCSC | NUP2105LT1G | onsemi | 5 | 1 | 4 | D10 |
| LCSC | APT2012CGCK | Kingbright | 5 | 1 | 4 | D7 |
| LCSC | SRN6045TA-220M | BOURNS | 5 | 1 | 4 | L2 |
| LCSC | BLM31KN601SN1L | muRata | 5 | 1 | 4 | FB1 |
| Farnell | 43045-2412 | MOLEX | 2 | 1 | 1 | J1 |
| LCSC | G2RL-2 DC5 | OMRON | 2 | 2 | 0 | K1 K2 |
| LCSC | B3F-1000 | OMRON | 5 | 2 | 3 | SW3 SW4 |
| LCSC | EEEHB1C100R | PANASONIC | 5 | 1 | 4 | C29 |
| LCSC | CC0805KRX7R9BB104 | YAGEO | 40 | 14 | 26 | C2 C6 C14 C18 C19 C21 C23 C24 C27 C28 C30 C33 C34 C36 |
| LCSC | C0805C104K1RACTU | KEMET | 20 | 1 | 19 | C1 |
| Farnell | IPD50N06S4L12ATMA2 | INFINEON | 2 | 1 | 1 | Q1 |
| Farnell | EEUFR1H221 | PANASONIC | 2 | 1 | 1 | C3 |
| Farnell | CC0805KKX7R8BB105 | YAGEO | 12 | 6 | 6 | C13 C22 C25 C26 C31 C32 |
| Farnell | GRM31CR71A226KE15L | MURATA | 8 | 4 | 4 | C15 C16 C17 C20 |
| Farnell | RC0805FR-0710KL | YAGEO | 24 | 12 | 12 | R7 R15 R16 R25 R26 R28 R35 R36 R41 R43 R49 R56 |
| Farnell | RC0805FR-0753K6L | YAGEO | 2 | 1 | 1 | R1 |
| Farnell | RC0805FR-07523KL | YAGEO | 2 | 1 | 1 | R5 |
| Farnell | RC0805FR-0722KL | YAGEO | 2 | 1 | 1 | R12 |
| Farnell | RC0805FR-07330RL | YAGEO | 2 | 1 | 1 | R38 |
| Farnell | B3F-1050 | OMRON / PARTNER STOCK | 4 | 2 | 2 | S1 S2 |
| Farnell | NTCS0805E3104FXT | VISHAY | 2 | 1 | 1 | RT1 |
| Farnell | NTCLE100E3104JB0 | VISHAY | 2 | 1 | 1 | NTC display |
| Farnell | AP2112K-3.3TRG1 | DIODES INC. | 4 | 2 | 2 | U5 U9 |
| Farnell | 43020-2400 | MOLEX | 1 | 1 | 0 | spina volante da banco |
| DigiKey | 214761-2124 | Molex femmina pre-crimpato 300 mm 18 AWG rosso | 2 | 1 | 1 | cablaggio: +batteria |
| DigiKey | 214761-1124 | Molex femmina pre-crimpato 300 mm 18 AWG nero | 2 | 1 | 1 | cablaggio: massa |
| DigiKey | 214761-1104 | Molex femmina pre-crimpato 300 mm 22 AWG nero | 15 | 13 | 2 | cablaggio: vie 3-15 |
| DigiKey | 214763-2124 | Molex maschio pre-crimpato 300 mm 18 AWG rosso | 2 | 1 | 1 | spina banco: +batteria |
| DigiKey | 214763-1104 | Molex maschio pre-crimpato 300 mm 22 AWG nero | 17 | 14 | 3 | spina banco: massa e vie 3-15 |
| DigiKey | SRR1260-8R2Y | Bourns 8,2 µH | 2 | 1 | 1 | L1 |
| DigiKey | AFB0412VA-00 | Delta ventola 40 x 40 x 10, 12 V, 4 fili | 1 | 1 | 0 | ventola |

Totale pezzi in avanzo dagli ordini della scheda madre: 2066, quasi tutti resistenze 0805 e piccoli semiconduttori.
