# Lista acquisti — scheda madre del cruscotto

Revisione A — 28/10/2026. Lista completa per costruire la scheda madre: dove si compra ogni pezzo. Prezzi IVA
esclusa del 27-28/10/2026, da ricontrollare al momento dell'ordine. Riferimenti, valori e verifiche in
`distinta-scheda-madre.md`; viti, filo, guaina e stagno esclusi (materiale di consumo). Niente è ancora ordinato.

| Fornitore | Righe | Merce | Spedizione | Note |
| --- | --- | --- | --- | --- |
| LCSC | 55 | 84.52 $ | 13 $ | carrello dell'utente; pezzi costosi per una scheda |
| Farnell | 16 | circa 29.78 € | da verificare | `ordine-farnell-scheda-madre.csv` |
| DigiKey | 2 | circa 13,60 € | circa 18 € | L1 e ventola: solo qui (scelta da confermare) |
| Amazon o fornitore abituale | 2 | — | — | secondo modulo MicroSD e secondo modulo VAN |
| Produttore di circuiti stampati | 1 | preventivo | — | dopo serigrafia e Gerber (D-057) |

## 1. LCSC (`ordine-lcsc-scheda-madre.csv`)

Carrello del 28/10/2026 senza le tre righe a prezzo zero (1 µF, 22 µF, 10 kΩ, presi da Farnell) e senza
l'AP2112K di TECH PUBLIC (preso originale da Farnell). Produttori diversi dall'originale ma stesso componente:
AO3400A ElecSuper, MMBT3904 FUXINSEMI, SMBJ26CA R+O, BAT54J Blue Rocket.

| Codice LCSC | Qtà | Componente |
| --- | --- | --- |
| C137592 | 100 | RC0805FR-0713KL (YAGEO) |
| C55151 | 6 | CL32B225KCJSNNE (Samsung Electro-Mechanics) |
| C397312 | 4 | GRM32ER61A476KE20L (muRata) |
| C97954 | 5 | GRM31CR71C106KA12L (muRata) |
| C77068 | 20 | GRM2195C1H682JA01D (muRata) |
| C107117 | 50 | CC0805JRNPO9BN390 (YAGEO) |
| C96346 | 100 | RC0805FR-07100KL (YAGEO) |
| C95781 | 100 | RC0805FR-071KL (YAGEO) |
| C60816 | 100 | RC0805FR-074K7L (YAGEO) |
| C84375 | 100 | RC0805FR-075K1L (YAGEO) |
| C273984 | 100 | RC0805FR-0710K2L (YAGEO) |
| C273888 | 100 | RC0805FR-07162KL (YAGEO) |
| C2167405 | 5 | C0805C224K1RACTU (KEMET) |
| C273920 | 100 | RC0805FR-0784K5L (YAGEO) |
| C137525 | 100 | RC0805FR-0743K2L (YAGEO) |
| C89104 | 100 | RC0805FR-07470KL (YAGEO) |
| C114550 | 100 | RC0805FR-076K8L (YAGEO) |
| C126351 | 100 | RC0805FR-0747KL (YAGEO) |
| C114548 | 100 | RC0805FR-0768KL (YAGEO) |
| C114558 | 100 | RC0805FR-07150KL (YAGEO) |
| C114528 | 100 | RC0805FR-07330KL (YAGEO) |
| C105577 | 100 | RC0805FR-07100RL (YAGEO) |
| C96345 | 100 | RC0805JR-070RL (YAGEO) |
| C485674 | 2 | 430252400 (MOLEX) |
| C293530 | 25 | 430300007 (MOLEX) |
| C84681 | 2 | CH340C (WCH) |
| C165948 | 5 | TYPE-C-31-M-12 (Korean Hroparts Elec) |
| C85098 | 10 | B340A-13-F (DIODES) |
| C1355730 | 2 | TPS54360BDDA (TI) |
| C1858393 | 2 | LMR36510ADDAR (TI) |
| C2653623 | 2 | LM74700QDBVTQ1 (TI) |
| C5456174 | 2 | LM2903BYDT (ST) |
| C722469 | 1 | DS3231SN# (MAXIM) |
| C154761 | 2 | ZXMP6A13FTA (DIODES) |
| C5224194 | 20 | AO3400A (ElecSuper) |
| C77760 | 20 | MMBTA06LT1G (onsemi) |
| C7422625 | 50 | MMBT3904LT1G (FUXINSEMI) |
| C41095 | 20 | MMBT5551LT1G (onsemi) |
| C151280 | 5 | SMCJ26CA (Littelfuse) |
| C19077581 | 10 | SMBJ26CA (R+O) |
| C85100 | 5 | B560C-13-F (DIODES) |
| C3013935 | 1 | ESP32-WROOM-32E-H4 (ESPRESSIF) |
| C83528 | 20 | 1N4148W-7-F (DIODES) |
| C358488 | 50 | BAT54J (BLUE ROCKET) |
| C83574 | 5 | BAT54S-7-F (DIODES) |
| C14486 | 5 | NUP2105LT1G (onsemi) |
| C5875740 | 5 | APT2012CGCK (Kingbright) |
| C2044314 | 5 | SRN6045TA-220M (BOURNS) |
| C668306 | 5 | BLM31KN601SN1L (muRata) |
| C277384 | 1 | 430452400 (MOLEX) |
| C1524519 | 2 | G2RL-2 DC5 (OMRON) |
| C93157 | 5 | B3F-1000 (OMRON) |
| C336241 | 5 | EEEHB1C100R (PANASONIC) |
| C49678 | 40 | CC0805KRX7R9BB104 (YAGEO) |
| C3151888 | 20 | C0805C104K1RACTU (KEMET) |

## 2. Farnell (`ordine-farnell-scheda-madre.csv`)

Da incollare in «Aggiungi rapidamente» del carrello (codice, quantità); Farnell può arrotondare ai suoi minimi.

| Codice Farnell | Qtà | Componente | Per |
| --- | --- | --- | --- |
| 2803392 | 2 | INFINEON IPD50N06S4L12ATMA2 | Q1 |
| 2508133 | 2 | PANASONIC EEUFR1H221 | C3 |
| 1458903 | 12 | YAGEO CC0805KKX7R8BB105 | C13 C22 C25 C26 C31 C32 |
| 2695995 | 8 | MURATA GRM31CR71A226KE15L | C15 C16 C17 C20 |
| 2421936 | 24 | YAGEO RC0805FR-0710KL | R7 R15 R16 R25 R26 R28 R35 R36 R41 R43 R49 R56 |
| 3951634 | 2 | YAGEO RC0805FR-0753K6L | R1 |
| 4062544 | 2 | YAGEO RC0805FR-07523KL | R5 |
| 9237798 | 2 | YAGEO RC0805FR-0722KL | R12 |
| 9237429 | 2 | YAGEO RC0805FR-07330RL | R38 |
| 4356874 | 4 | OMRON / PARTNER STOCK B3F-1050 | S1 S2 |
| 2747614 | 2 | VISHAY NTCS0805E3104FXT | RT1 |
| 1187033 | 2 | VISHAY NTCLE100E3104JB0 | NTC display |
| 3257429 | 4 | DIODES INC. AP2112K-3.3TRG1 | U5 U9 |
| 2987032 | 1 | STMICROELECTRONICS STEVAL-MKI196V1 | J6 (IMU) |
| 634712 | 1 | MOLEX 43020-2400 | spina volante per il banco (D-044) |
| 4234086 | 12 | MOLEX 43031-0007 | contatti maschio della spina |

## 3. DigiKey (oppure alternativa da decidere)

| Codice produttore | Qtà | Per | Note |
| --- | --- | --- | --- |
| SRR1260-8R2Y (Bourns) | 2 | L1 | non su Farnell né su LCSC; Mouser ne ha solo 5 |
| AFB0412VA-00 (Delta) | 1 | ventola (D-052) | Farnell ha solo la AFB0412HA-A, più veloce e rumorosa |

## 4. Moduli da ricomprare

| Modulo | Qtà | Per | Note |
| --- | --- | --- | --- |
| Lettore MicroSD SPI 3,3 V, stesso modello di HW-SD-MODULE | 1 | J7 | quello in possesso è del logger |
| Modulo CAN blu SN65HVD230, stesso tipo di HW-CAN-VP230 | 1 | J8, J9 | da modificare come il primo (resistenza 121 tolta) |

## 5. Già in possesso

- Spine MX1.25 lato S3 (HW-MX125-PLUGS); scheda S3 con display (HW-DASH-DISPLAY).
- LM2903BYDT e EEEHB1C100R in arrivo con l'ordine del logger: utilizzabili come scorta.
- STEVAL-MKI196V1: 1 già ordinata (HW-IMU-LSM6DSO); quella della lista Farnell è la seconda (logger e cruscotto, D-033).

## 6. Circuito stampato

4 strati, 178,7 × 74 mm, 1,6 mm: preventivo e ordine dopo la sistemazione della serigrafia, i file Gerber e le
verifiche aperte di `scheda-madre.md` (profondità dietro la scheda, interasse del modulo VAN, misure della STEVAL).
