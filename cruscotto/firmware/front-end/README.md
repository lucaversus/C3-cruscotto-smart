# Front-end del cruscotto — firmware 0.1.0

ESP32 che raccoglie i dati dell'auto e li manda all'S3 (D-029) con il protocollo fe_link v1
([protocollo-fe-s3.md](../../docs/protocollo-fe-s3.md)). A banco gira sull'ESP32 HW-394
(HW-ESP32), in futuro sul modulo della scheda madre (HW-FE-MODULE).

Versione 0.1.0 (23/10/2026): solo il **collegamento reale** con l'S3, con **dati simulati**
(qualità "simulato", stessi andamenti del simulatore interno dell'S3): 15 segnali ogni 33 ms
e battito ogni secondo. K-line, VAN e sensori verranno aggiunti riusando il codice del logger.

## Collegamento a banco (3 fili, entrambe le schede a 3,3 V)

| ESP32 HW-394 | S3 (connettore P2) | Segnale |
| --- | --- | --- |
| GPIO25 (TX) | IO11 (RX dell'S3) | trame front-end → S3 |
| GPIO33 (RX) | IO12 (TX dell'S3) | trame S3 → front-end |
| GND | GND | massa comune |

Ciascuna scheda alimentata dal proprio USB. La MicroSD dell'S3 resta esclusa (IO10 alto,
D-029). L'S3 (firmware 0.9.0) usa il collegamento reale se entro 3 s riceve trame,
altrimenti il simulatore interno; la pagina Diagnostica mostra UART o SIMULATO.

Compilazione: `python tools/dev.py build`. Caricamento sull'HW-394 (sostituisce il firmware
del logger, ricaricabile dai sorgenti): `platformio run -d cruscotto/firmware/front-end -t upload`.
Seriale 115200: righe `c3_front_end sent=... received=... rx_errors=...`.

Stato: compilato, non ancora caricato né provato.
