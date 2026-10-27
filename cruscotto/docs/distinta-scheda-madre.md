# Distinta materiali — scheda madre del cruscotto

Revisione A — 27/10/2026. Riferimento: schema C3AI-CR-EL-001…005 e circuito stampato sbrogliato
(`cruscotto/pcb/scheda-madre/`, D-057). Quantità **per una scheda**. Non è un ordine: i componenti
non sono ordinati né collaudati; disponibilità e stato dei moduli restano in `data-logger/docs/hardware.json`.
Fornitori da consultare per primi: Farnell, Future, RS, Mouser, DigiKey, TME.

Elenco completo generato dallo schema, con riferimenti e impronte: `cruscotto/pcb/scheda-madre/distinta-materiali.csv`
(rigenerare con `kicad-cli sch export bom`, vedi il README della scheda). Montaggio a mano (D-046): passivi 0805
o più grandi, impronte HandSolder.

## 1. Circuito stampato

| Qtà | Voce | Note |
| --- | --- | --- |
| 1 | Circuito stampato 4 strati, 178,7 × 74 mm, 1,6 mm, rame 35 µm, foro minimo 0,2 mm, pista minima 0,15 mm | Solo dopo serigrafia sistemata, Gerber e verifiche aperte di `scheda-madre.md`; preventivo da fare (D-057) |

## 2. Già presenti o già ordinati: non ricomprare

| Rif. | Voce | Stato (inventario) |
| --- | --- | --- |
| J8, J9 | Modulo VAN blu SN65HVD230 (resistenza 121 tolta) | HW-CAN-VP230, presente, prove a banco 1-4 superate |
| J7 | Modulo MicroSD SPI 3,3 V | HW-SD-MODULE, presente (stesso tipo del Data Logger) |
| J6 | STEVAL-MKI196V1 (LSM6DSO su DIL-24) | HW-IMU-LSM6DSO, ordinato, non ancora arrivato |
| J10-J12 | Spine MX1.25 per i cavetti verso la S3 | HW-MX125-PLUGS, presenti |
| — | Scheda S3 con display 5" | HW-DASH-DISPLAY, presente |

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
| 1 | IPD50N06S4L-12 | TO-252 | Q1 | MOSFET N 60 V del diodo ideale, **da confermare** |
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
| 1 | NTC 100 kΩ B3950, 0805 | RT1 (temperatura della scheda) |
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
| 1 | 220 µF 50 V elettrolitico radiale Ø10 passo 5, alta temperatura | C3 (riserva per l'avviamento, **capacità da confermare**) |
| 1 | 8,2 µH, Isat ≥ 5 A (es. Bourns SRR1260-8R2Y) | L1, **corrente di saturazione da verificare** |
| 1 | 22 µH, Isat ≥ 1,5 A (es. Bourns SRN6045TA-220M) | L2, **da verificare** |
| 1 | Ferrite ≥ 3 A, 1206 | FB1 |

## 5. Connettori ed elettromeccanici sulla scheda

| Qtà | Componente | Rif. | Note |
| --- | --- | --- | --- |
| 1 | Molex Micro-Fit 3.0 43045-2400, 2 × 12, orizzontale | J1 | verso l'auto (D-044) |
| 1 | USB-C HRO TYPE-C-31-M-12 | J3 | passo 0,5 mm, saldatura a trascinamento |
| 2 | Molex PicoBlade 53048-0410, 4 vie, ad angolo retto | J10, J11 | verso P1 e P2 della S3 |
| 1 | Molex PicoBlade 53048-0210, 2 vie, ad angolo retto | J12 | verso Speak della S3 |
| 1 | Connettore ventola 4 vie passo 2,54 (FanPinHeader) | J4 | per la Delta AFB0412VA-00 |
| 1 | JST XH B2B-XH-A, 2 vie | J5 | NTC del display |
| 2 | Strip femmina 1 × 12 passo 2,54 | J6 | zoccolo per la STEVAL (file a 15,0 mm) |
| 1 + 1 + 1 | Strip 1 × 6, 1 × 4, 1 × 2 passo 2,54 | J7, J8, J9 | femmina se i moduli si innestano, oppure moduli saldati direttamente: da decidere |
| 2 | Relè Omron G2RL-2 DC5 | K1, K2 | |
| 2 | Pulsante tattile 6 × 6, alto 7,3 mm | S1, S2 | sotto i pulsanti del quadro (D-054) |
| 2 | Pulsante tattile 6 × 6 | SW3, SW4 | RESET e BOOT del front-end |

## 6. Fuori dalla scheda: cablaggi e montaggio

| Qtà | Voce | Note |
| --- | --- | --- |
| 1 | Ventola Delta AFB0412VA-00, 40 × 40 × 10, 12 V, 4 fili | HW-DASH-FAN, scelta (D-052), non ordinata |
| 4 | Viti per la ventola (fori Ø3,2) | lunghezza dal montaggio |
| 6 | Viti di fissaggio della scheda (fori Ø3) | dal telaio del quadro |
| 1 + 12 | Femmina Micro-Fit 43025-2400 e contatti 43030-0007 (più scorta) | cablaggio dell'auto (HW-J1-MICROFIT24); per il banco anche spina 43020-2400 e contatti 43031-0007 |
| 2 + 1 | Alloggiamenti PicoBlade 51021-0400 e 51021-0200, con contatti a crimpare 50079-8000 (circa 12) | cavetti verso la S3, dal lato scheda madre; codici da confermare sulla scheda tecnica Molex |
| 1 | Alloggiamento JST XHP-2 con 2 contatti SXH-001T-P0.6 | NTC del display |
| 1 | Sonda NTC 100 kΩ B3950 con fili | sul display |
| — | Filo 20-24 AWG per J1, 26-28 AWG per i cavetti PicoBlade | |

## Da chiudere prima dell'ordine

- Valori **da confermare**: Q1, L1, L2, C3 (segnati sopra).
- Strip dei moduli (J7-J9): innesto o saldatura diretta.
- Verifiche aperte in `cruscotto/docs/scheda-madre.md`: profondità dietro la scheda (relè e C3 sul retro),
  interasse del modulo VAN, misure della STEVAL, telaio, audio, temperatura della ventola, massa VAN.
- Codici d'ordine e prezzi dai fornitori: non ancora cercati, salvo quelli di J1 già in inventario.
