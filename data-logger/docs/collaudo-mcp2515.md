# Registro di verifica HW-CAN-MCP2515

Cruscotto C3+AI / Data Logger — revisione 1, 18/10/2026.

Consultare [inventario](hardware-inventory.md) e
[foto archiviate](hardware-photos/README.md) prima di indicare i punti di misura.
Strumento disponibile: UNI-T UT210E, identificato dalla foto dell'utente.
Nessuna misura ancora acquisita; il modulo non è dichiarato compatibile con ESP32.

## Misura M-001 — resistenza tra H e L

- Modulo completamente scollegato da alimentazione, ESP32, veicolo e altri moduli.
- Ponticelli nello stato trovato: non spostare J1/J3 senza identificarne il circuito.
- Puntale nero nella presa COM; rosso nella presa per tensione/resistenza.
- Selettore sulla funzione resistenza, display con simbolo ohm (Ω);
  usare SELECT se occorre cambiare la funzione condivisa. Non usare la pinza.
- Un puntale per ciascuno dei due contatti metallici del morsetto blu H/L.
  Non usare i pin SPI o VCC per questa misura.
- Registrare valore e unità esatti (Ω, kΩ, MΩ oppure OL) e stabilità del valore.

| Misura | Stato | Risultato utente | Interpretazione |
| --- | --- | --- | --- |
| M-001, H–L, modulo isolato e spento | in attesa | non fornito | non formulata |

Il risultato descriverà soltanto la resistenza tra le linee nelle condizioni
della prova. Non prova tensioni interne, livelli SPI, bitrate o funzionamento CAN.
Le verifiche successive dipendono da questa misura e dall'identificazione del circuito.

Riferimento strumento: [pagina manuale UNI-T UT210E](https://meters.uni-trend.com/download/ut210e-user-manual/).
