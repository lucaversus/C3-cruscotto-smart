# Modelli 3D dei moduli

File STEP (AP214) disegnati dall'utente in SolidWorks e inoltrati il 24/10/2026, copiati senza
modifiche da `Dropbox/Progetti/C3 Cockpit PRO/3d`. Servono per la scheda madre del cruscotto
(D-045, D-051) e per il Data Logger (D-042). Unità mm; modelli semplificati: le misure vanno
confermate sul pezzo prima di fissare fori e altezze.

| File | Pezzo | Ingombro (mm) | Note dal modello |
| --- | --- | --- | --- |
| `modulo-sd.step` | lettore MicroSD (HW-SD-MODULE) | 17,8 × 26,6 × 11,5 | circuito 17,8 × 17,8 × 1,5; 6 pin dritti in fila, passo circa 2,5 (da confermare 2,54), a 1,25 mm dal bordo; scheda MicroSD sporgente 8,8 mm sul lato opposto |
| `modulo-rtc.step` | RTC DS3231 con portapila (HW-RTC) | 45,0 × 28,9 × 14,3 | per il Data Logger; sulla scheda madre l'RTC è il chip (D-051) |
| `modulo-oled-1.9inch.step` | OLED 1,9" (HW-OLED) | 26,0 × 26,0 × 11,1 | per il Data Logger |
| `tft-5inch.step` | scheda S3 ESP32-S3 8048S050 (HW-DASH-DISPLAY) | 137,0 × 84,0 × 9,7 | stesso modello usato nell'assieme `../assieme-cruscotto.step`; presa USB-C al centro del lato corto |
| `modulo-van.step` | modulo VAN blu SN65HVD230 (HW-CAN-VP230), inoltrato il 31/10/2026 | 28,5 × 11,0 × 12,6 | circuito 28,5 × 11,0 × 1,6; 4 pin dritti a passo 2,54 lungo il lato corto, a 1,25 mm dal bordo e centrati sulla larghezza, da −1,0 a +8,0 mm (sporgono 6,4 mm dal lato componenti); morsetto CANH/CANL 7,5 × 10,5 × 10 sul lato opposto ai pin, a 0,2 mm dal bordo corto; circuiti integrati non modellati. Misure confermate dall'utente il 31/10/2026 (la stima precedente era circa 35 × 13): impronta J8 aggiornata |

STEVAL-MKI196V1 (HW-IMU-LSM6DSO), senza modello 3D: dai Gerber ST (2018) scheda 18,0 × 30,5 mm (misurata sul pezzo il 28/10/2026: 18,5 × 30,9 mm),
24 pin su due file da 12 a passo 2,54 con interasse 15,0 mm, piedino 1 in alto a sinistra;
impronta `../../pcb/scheda-madre/scheda-madre.pretty/ST_DIL24_Adapter_W15.0mm.kicad_mod`.
Fonte: `steval-mki196v1_gerber.zip` dalla pagina ST del prodotto (sezione CAD Resources), scaricato
il 24/10/2026, SHA-256 `8c31f3b56b9041de996ca1ad56279de293fdfd34bb8090424bb4ed2f1a6b8f46`. Non è nel
repository (materiale ST senza licenza di ridistribuzione, D-034): copia locale in `.local/terzi/st/`,
esclusa da git.

Mancano ancora: modulo VAN blu (HW-CAN-VP230), ventola 40 × 40 (da identificare).
