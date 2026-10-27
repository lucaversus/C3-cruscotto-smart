# Distinta materiali — scheda madre del cruscotto

Revisione B — 27/10/2026. Riferimento: schema C3AI-CR-EL-001…005 e circuito stampato sbrogliato
(`cruscotto/pcb/scheda-madre/`, D-057). Quantità **per una scheda**. Non è un ordine: i componenti
non sono ordinati né collaudati; disponibilità e stato dei moduli restano in `data-logger/docs/hardware.json`.
Fornitori da consultare per primi: Farnell, Future, RS, Mouser, DigiKey, TME.

Elenco completo generato dallo schema, con riferimenti e impronte: `cruscotto/pcb/scheda-madre/distinta-materiali.csv`
(rigenerare con `kicad-cli sch export bom`, vedi il README della scheda). Montaggio a mano (D-046): passivi 0805
o più grandi, impronte HandSolder. Cavi saldati direttamente alla scheda e moduli saldati senza zoccoli (D-059).
Comprende tutto il necessario tranne il materiale di consumo (viti, filo, guaina, stagno).

## 1. Circuito stampato

| Qtà | Voce | Note |
| --- | --- | --- |
| 1 | Circuito stampato 4 strati, 178,7 × 74 mm, 1,6 mm, rame 35 µm, foro minimo 0,2 mm, pista minima 0,15 mm | Solo dopo serigrafia sistemata, Gerber e verifiche aperte di `scheda-madre.md`; preventivo da fare (D-057) |

## 2. Già in possesso o ordinati (anche per il Data Logger)

Confronto con l'inventario e con l'ordine Farnell del Data Logger del 22/10/2026 (HW-KLINE-INTERFACE,
consegna non ancora riscontrata). Quantità da riscontrare all'arrivo.

| Rif. | Voce | Stato | Per la scheda madre |
| --- | --- | --- | --- |
| U7 | LM2903BYDT SOIC-8 | 2 ordinati per la K-line del logger, che ne usa 1 | **usare il secondo** |
| C29 | Elettrolitico 10 µF 16 V Panasonic EEEHB1C100R (SMD 4 × 5,4) | nel carrello del logger; versione ordinata (SMD o THT) da riscontrare | utilizzabile se arrivato SMD |
| J8, J9 | Modulo VAN blu SN65HVD230 | HW-CAN-VP230: 1 pezzo, quello del logger (resistenza 121 tolta, prove 1-4) | **serve un secondo modulo**, modificato allo stesso modo |
| J7 | Modulo MicroSD SPI 3,3 V | HW-SD-MODULE: presente, quantità non riscontrata | serve un esemplare distinto da quello del logger |
| J6 | STEVAL-MKI196V1 (LSM6DSO su DIL-24) | HW-IMU-LSM6DSO: 1 ordinato, non arrivato | se ne serve uno anche al logger (D-033), ne manca uno |
| — | Spine MX1.25 sul lato S3 dei cavetti (P1, P2, Speak) | HW-MX125-PLUGS, presenti | sì |
| — | Scheda S3 con display 5" | HW-DASH-DISPLAY, presente | sì |

Non utilizzabili per questa scheda: 2N5551BU (TO-92, qui MMBT5551 SOT-23), resistenze a foro passante della
K-line, modulo RTC DS3231 (qui il chip DS3231SN), ESP32 HW-394 (qui il modulo WROOM).

## 3. Semiconduttori

| Qtà | Componente | Contenitore | Rif. | Note |
| --- | --- | --- | --- | --- |
| 1 | ESP32-WROOM-32E-H4 (o H8) | modulo | U4 | -40…+105 °C, senza PSRAM (HW-FE-MODULE) |
| 1 | TPS54360B | SO-PowerPAD-8 | U2 | buck 5 V 3,5 A, piazzola termica saldata dal retro (D-048) |
| 1 | LMR36510 (variante delle tabelle 8-1/8-3 del datasheet, come nello schema) | HTSOP-8 | U3 | buck 3,3 V sempre acceso |
| 1 | LM74700-Q1 | SOT-23-6 | U1 | diodo ideale |
| 2 | AP2112K-3.3 | SOT-23-5 | U5, U9 | LDO USB e 3,3 V a quadro |
| 1 | CH340C | SOIC-16 | U6 | USB-seriale, solo a banco |
| 1 | LM2903B | SOIC-8 | U7 | comparatore K-line |
| 1 | DS3231SN | SOIC-16W | U10 | RTC senza pila (D-056) |
| 1 | IPD50N06S4L-12 | TO-252 | Q1 | MOSFET N 60 V del diodo ideale, verificato (sezione 9) |
| 1 | ZXMP6A13F | SOT-23 | Q3 | P-MOSFET 60 V, stacco ventola |
| 1 | AO3400A | SOT-23 | Q9 | pilota bobine relè |
| 1 | MMBTA06 | SOT-23 | Q4 | |
| 3 | MMBT3904 | SOT-23 | Q5-Q7 | |
| 1 | MMBT5551 | SOT-23 | Q8 | K-line |
| 1 | SMCJ26CA | SMC | D1 | TVS ingresso |
| 1 | SMBJ26CA | SMB | D8 | TVS linea K |
| 1 | B560C | SMC | D2 | diodo del buck 5 V |
| 1 | B340A | SMA | D13 | ritorno 5 V dalla USB della S3 |
| 4 | 1N4148W | SOD-123 | D3, D9, D11, D12 | |
| 1 | BAT54J | SOD-323F | D4 | |
| 2 | BAT54S | SOT-23 | D5, D6 | |
| 1 | NUP2105L | SOT-23 | D10 | protezione linee VAN |
| 1 | LED verde | 0805 | D7 | |

## 4. Passivi

Resistenze: 0805, 1 %, almeno 0,125 W. Condensatori ceramici: X7R (C0G per C9 e C10), 0805 salvo dove indicato;
tensione minima ricavata dalle reti dello schema.

| Qtà | Valore | Rif. |
| --- | --- | --- |
| 12 | 10 kΩ | R7, R15, R16, R25, R26, R28, R35, R36, R41, R43, R49, R56 |
| 9 | 100 kΩ | R8, R9, R11, R14, R22, R23, R27, R47, R55 |
| 6 | 1 kΩ | R17, R20, R21, R29, R30, R46 |
| 5 | 4,7 kΩ | R18, R19, R33, R34, R45 |
| 2 | 5,1 kΩ | R31, R32 (CC della USB-C) |
| 1 ciascuna | 53,6 k, 10,2 k, 162 k, 13,0 k, 523 k, 84,5 k, 43,2 k | R1-R6, R10 (convertitori: valori E96) |
| 1 ciascuna | 22 k, 470 k, 6,8 k, 47 k, 68 k, 150 k, 330 k, 330 Ω, 100 Ω, 0 Ω | R12, R13, R24, R39, R40, R42, R44, R38, R54, R37 |
| 1 | NTC Vishay NTCS0805E3104FXT, 100 kΩ 1 %, 0805 | RT1 (temperatura della scheda); valore B dalla scheda tecnica nel firmware |
| 13 | 100 nF 50 V | C6, C14, C18, C19, C21, C23, C24, C27, C28, C30, C33, C34, C36 (un solo codice a 50 V anche dove basterebbe meno) |
| 1 | 100 nF 100 V | C1 (VBAT_IN) |
| 1 | 100 nF 25 V | C2 |
| 1 | 220 nF 100 V | C12 (+12V_F) |
| 6 | 1 µF 25 V | C13, C22, C25, C26, C31, C32 |
| 3 | 2,2 µF 100 V, 1210 | C4, C5, C11 (+12V_F) |
| 4 | 22 µF 10 V, 1206 | C15, C16, C17, C20 |
| 2 | 47 µF 10 V, 1210 | C7, C8 (uscita 5 V) |
| 1 | 10 µF 16 V, 1206 | C35 |
| 1 | 10 µF 16 V elettrolitico SMD 4 × 5,4 | C29 |
| 1 | 6,8 nF C0G 50 V | C9 |
| 1 | 39 pF C0G 50 V | C10 |
| 1 | Panasonic EEU-FR1H221, 220 µF 50 V radiale Ø10 passo 5, alto 17,5 mm | C3, verificato (sezione 9): montarlo coricato |
| 1 | Bourns SRR1260-8R2Y, 8,2 µH, Isat 5,8 A | L1, verificata (sezione 9) |
| 1 | Bourns SRN6045TA-220M, 22 µH, Isat 3,3 A | L2, verificata (sezione 9) |
| 1 | Ferrite ≥ 3 A, 1206 | FB1 |

## 5. Connettori ed elettromeccanici sulla scheda

| Qtà | Componente | Rif. | Note |
| --- | --- | --- | --- |
| 1 | Molex Micro-Fit 3.0 43045-2400, 2 × 12, orizzontale | J1 | verso l'auto (D-044) |
| 1 | USB-C HRO TYPE-C-31-M-12 | J3 | passo 0,5 mm, saldatura a trascinamento |
| — | Piazzole per filo 26 AWG, nessun componente | J4, J5, J10-J12 | ventola, NTC del display, cavetti verso la S3 (D-059) |
| — | Moduli saldati direttamente con i loro pin | J6-J9 | STEVAL, MicroSD, VAN (D-059) |
| 2 | Relè Omron G2RL-2 DC5 | K1, K2 | |
| 2 | Omron B3F-1050, tattile 6 × 6 alto 7,3 mm, 100 gf | S1, S2 | sotto i pulsanti del quadro (D-054) |
| 2 | Pulsante tattile 6 × 6 | SW3, SW4 | RESET e BOOT del front-end |

## 6. Fuori dalla scheda

| Qtà | Voce | Note |
| --- | --- | --- |
| 1 | Ventola Delta AFB0412VA-00, 40 × 40 × 10, 12 V, 4 fili | HW-DASH-FAN, scelta (D-052), non ordinata |
| 1 + 19 | Femmina Micro-Fit 43025-2400 e fili Molex già crimpati 214761 (2 da 18 AWG per +batteria e massa, 15 da 22 AWG), 300 mm | cablaggio dell'auto (HW-J1-MICROFIT24), senza pinza a crimpare; per il banco spina 43020-2400 con fili maschio 214763 |
| 1 | NTC Vishay NTCLE100E3104JB0, 100 kΩ a reofori | incollata al display, fili saldati a J5; valore B dalla scheda tecnica |

## 7. Disponibilità presso i fornitori (27/10/2026)

Codici d'ordine in `distinta-scheda-madre-codici.csv`; controlli con le API ufficiali (credenziali personali
fuori dal repository): `tools/controlla-distinta-farnell.py` → `distinta-scheda-madre-codici-farnell.csv`,
`tools/controlla-distinta-mouser-digikey.py` sui pezzi mancanti (`distinta-scheda-madre-da-cercare.csv` →
`…-da-cercare-mouser-digikey.csv`). Fotografia del giorno: giacenze e prezzi cambiano.

- **Farnell**: passivi, AP2112K, LM2903B, DS3231SN, IPD50N06S4L-12, transistor, diodi e TVS, NUP2105L, L2,
  ferrite, J1 con femmina e contatti, relè G2RL-2, pulsanti B3F-1000, C3, C29 (circa 100 € IVA esclusa).
- **Mouser / DigiKey** per quello che Farnell non ha:

| Rif. | Codice da ordinare | Dove (giacenza) |
| --- | --- | --- |
| U4 | ESP32-WROOM-32E-H4 | Mouser 216, DigiKey 226 (circa 4,60 €) |
| U2 | TPS54360BDDA (tubetto; la bobina BDDAR è a zero) | Mouser 981, DigiKey 2300; in alternativa TPS54360BQDDARQ1 (Mouser 19 033) |
| U3 | LMR36510ADDAR | DigiKey 12 931, Mouser 472 |
| U1 | LM74700QDBVTQ1 (bobina piccola, stesso chip) | Mouser 99 |
| L1 | SRR1260-8R2Y | DigiKey 604 |
| Q9 | AO3400A | DigiKey 210 799 |
| C4, C5, C11 | Samsung CL32B225KCJSNNE (2,2 µF 100 V X7R 1210) | DigiKey 69 933 |
| C7, C8 | GRM32ER61A476KE20L (47 µF 10 V X5R 1210) | DigiKey 28: scorte basse |
| ventola | Delta AFB0412VA-00 | DigiKey 310 (12,61 €) |

- **LCSC** (account dell'utente dal 27/10/2026) per i pezzi che gli altri non hanno: CH340C (LCSC C84681),
  USB-C HRO TYPE-C-31-M-12 (LCSC C165948); codici LCSC da confermare sul sito.
- **Senza giacenza ovunque** (Farnell, Mouser, DigiKey): ZXMP6A13F (Q3) e BAT54J (D4): controllare LCSC,
  altrimenti scegliere equivalenti nello stesso contenitore (P-MOSFET 60 V SOT-23, Schottky singolo SOD-323).
- **Pulsanti** S1, S2: Omron B3F-1050 (Mouser 23 157, DigiKey 23 831). **NTC**: Vishay NTCS0805E3104FXT e
  NTCLE100E3104JB0 (Mouser, DigiKey); il valore B (circa 4100-4200 K, da confermare in scheda tecnica) va nel
  firmware, che non ha ancora la conversione.
- **LCSC** (carrello dell'utente del 28/10/2026, 86,37 $ più 13 $ di spedizione): quasi tutta la distinta, per
  una scheda sui pezzi più costosi; da altri fornitori Q1, L1, C3, R5, R38, ventola, 22 µF 1206, 10 kΩ e
  100 kΩ (senza giacenza su LCSC). AP2112K del carrello di TECH PUBLIC: preferire l'originale Diodes.

## 8. Piano d'acquisto (28/10/2026)

- **LCSC**: carrello dell'utente, 59 righe, 85,08 $ più 13 $ di spedizione (pezzi costosi per una scheda).
- **Farnell**: 13 voci in `ordine-farnell-scheda-madre.csv` (codici Farnell e quantità per 2 schede, circa 11 €
  IVA esclusa; Farnell arrotonda ai propri minimi d'ordine): Q1, C3, 1 µF, 22 µF, 10 kΩ, R1, R5, R12, R38,
  B3F-1050, le due NTC, AP2112K originale Diodes (togliere dal carrello LCSC la copia TECH PUBLIC).
- **Non su Farnell né su LCSC**: L1 SRR1260-8R2Y (DigiKey 604, Mouser 5) e ventola AFB0412VA-00 (DigiKey 310;
  Farnell ha solo la AFB0412HA-A). Su Farnell la SRR1280-8R2Y è alta 8 mm, troppo per la faccia F; la
  SRR1260-100M da 10 µH cambierebbe il dimensionamento del convertitore 5 V.

## 9. Verifica dei componenti di potenza (28/10/2026)

Dati: parametri DigiKey (API) e pagine TI; carico dal bilancio di `scheda-madre.md` (5 V fino a 2 A, 3,3 V sempre
acceso fino a 0,3 A, ventola 0,6 W, totale circa 13 W dalla batteria); ingresso 6-42 V (calo d'avviamento, TVS D1).

| Pezzo | Dato | Calcolo | Esito |
| --- | --- | --- | --- |
| Q1 IPD50N06S4L-12 | 60 V, RDSon ≤ 12 mΩ a 10 V, VGS max ±16 V | corrente d'ingresso ≤ 2,2 A (13 W a 6 V): 2,2² × 0,012 = 0,06 W; comando dell'LM74700 12,1-13 V (pompa di carica), sotto i 16 V; 42 V di picco sotto i 60 V; C2 100 nF ≥ 10 × Ciss (29 nF) | adatto |
| L1 SRR1260-8R2Y | 8,2 µH ±30 %, Isat 5,8 A, Irms 5,7 A, 19,5 mΩ, alta 6,5 mm | ondulazione a 42 V e 600 kHz: 5 × (1 − 5/42) / (8,2 µH × 600 kHz) = 0,9 A; picco 2,45 A a 2 A di carico, 3,95 A al massimo del TPS54360B (3,5 A); perdite 0,08 W | adatta; in cortocircuito il limite del chip (minimo 4,5 A) si avvicina all'Isat: protezione affidata al limite di corrente |
| L2 SRN6045TA-220M | 22 µH, Isat 3,3 A, Irms 2,3 A, AEC-Q200 | ondulazione a 42 V e 400 kHz: 3,3 × (1 − 3,3/42) / (22 µH × 400 kHz) = 0,35 A; picco 1,17 A a 1 A | adatta, margine ampio sul limite di un convertitore da 1 A |
| C3 EEU-FR1H221 | 220 µF 50 V, 30 mΩ, 1,65 A di ondulazione, alto 17,5 mm | a 13 W e 12 V (1,1 A) scende di 1,1 A / 220 µF = 5 V/ms: copre interruzioni di circa 1 ms; i cali dell'avviamento (minimo misurato 9,0 V) li reggono i convertitori, che funzionano fino a circa 5,5-6 V per il 5 V e 4,2 V per il 3,3 V | adatto come condensatore d'ingresso; una riserva lunga (supercondensatore, -C1) servirebbe solo se l'oscilloscopio mostrasse cali sotto i 6 V |

Conseguenze: **C3 alto 17,5 mm** è il pezzo più alto del retro (relè 15,7 mm): montarlo coricato sulla scheda o
verificare la profondità disponibile (verifica aperta 1). FB1 (2,9 A) e D2 B560C (5 A, 60 V) adatti alle stesse
correnti.

## Da chiudere prima dell'ordine

- Verifiche aperte in `cruscotto/docs/scheda-madre.md`: profondità dietro la scheda (relè e C3 sul retro),
  interasse del modulo VAN, misure della STEVAL, telaio, audio, temperatura della ventola, massa VAN.
- Lista acquisti completa per fornitore: `lista-acquisti-scheda-madre.md`.
