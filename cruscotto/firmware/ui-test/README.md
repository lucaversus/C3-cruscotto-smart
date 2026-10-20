# Prova UI LVGL ESP32-8048S050 — versione 0.1.1

Cruscotto C3+AI, HW-DASH-DISPLAY (D-026, D-027). Pinout dalla prova display
DSP-M001, condiviso in `../common/include/board_8048s050.h`.
Stato: **0.1.1 caricata il 20/10/2026, DSP-M003 superata**: 32 FPS dati, 8 ms di rendering, cifre senza sfarfallio (0.1.0: DSP-M002).

## Cosa fa

Schermata ad alto contrasto con **dati simulati** (scritta "DEMO - dati simulati"):
arco contagiri 0–5000 giri/min con valore numerico (0.1.1: quattro celle fisse da 34 px, una per cifra, aggiornate solo se cambiano), barra temperatura acqua
40–130 °C. Valori aggiornati ogni 33 ms con una sinusoide: nessun ingresso dal
veicolo. LVGL 8.3.11 (MIT), due buffer parziali da 40 righe in SRAM interna,
copia nel framebuffer PSRAM tramite esp_lcd. Indicatore LVGL FPS/CPU in basso a destra.

Riga seriale ogni 5 s a 115200 baud:
`ui_test version=0.1.0 panel=ESP_OK fps=... refr_avg_ms=... heap_int_free=... psram_free=...`
`fps` conta i refresh LVGL completati, `refr_avg_ms` la durata media di rendering e copia.

## Criterio di osservazione

Arco e numeri si muovono in modo continuo, senza sfarfallio, strappi o righe
spostate. I valori FPS misurati sono una base di confronto: l'obiettivo 60 FPS
del README resta da raggiungere o rivedere. Con IDF 4.4 non sono disponibili i
bounce buffer: un eventuale spostamento dell'immagine sotto carico PSRAM va annotato.
