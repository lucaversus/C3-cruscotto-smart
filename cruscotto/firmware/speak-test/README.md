# Prova U1 / P6 "Speak" ESP32-8048S050 — versione 0.1.1

Cruscotto C3+AI, HW-DASH-DISPLAY (D-026, D-028). Scopo: capire se U1
(marcatura riferita "AKK 7HG", collegato a P6) è pilotato da IO17 o IO18.
Stato: **0.1.1 caricata il 20/10/2026**; esiti DSP-M005 e DSP-M006 non conclusivi (il tester non rileva il segnale nemmeno sul pin di origine). Prova da ripetere con un altoparlante su P6.

Ciclo continuo: tono 200 Hz (0.1.0: 1 kHz) onda quadra per 10 s su IO17, poi 10 s su IO18,
poi 10 s di pausa; la fase corrente è stampata sulla seriale a 115200 baud
(`speak_test version=0.1.1 fase=TONO_IO17 ...`). Retroilluminazione spenta,
IO10 alto (MicroSD esclusa).

Misura: UT210E in V~ sui due contatti di P6, nient'altro collegato a P6, P3, P4
o P5. Tensione presente solo in una fase = pin che pilota U1. La lettura di un
tester a 1 kHz è indicativa: serve a distinguere presenza/assenza di segnale.
