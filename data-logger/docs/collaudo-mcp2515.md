# Registro di verifica HW-CAN-MCP2515

Cruscotto C3+AI / Data Logger — revisione 3, 18/10/2026.

Consultare [inventario](hardware-inventory.md) e
[foto archiviate](hardware-photos/README.md) prima di indicare i punti di misura.
Strumento disponibile: UNI-T UT210E, identificato dalla foto dell'utente.
Prima lettura riferita dall’utente registrata sotto; il modulo non è dichiarato compatibile con ESP32.

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
| M-001, H–L, richiesto modulo isolato e spento | riferita e successivamente ripetuta | 51,8 kΩ (testo utente: “51.8Komh”) | Nessuna conclusione definitiva sul circuito |
| C-001, contatto diretto tra i puntali in modalità Ω | riferita | 0; unità non ripetuta, Ω richiesto nella procedura | Contatto dei puntali riscontrato; non è taratura |
| M-002, ripetizione H–L dopo C-001 | riferita | “stesso valore”, cioè 51,8 kΩ | Resistenza H–L ripetuta, senza dedurre guasto o compatibilità |
| M-003, direttamente sulle estremità di R2 | in attesa | non fornito | Da acquisire prima di interpretare la terminazione |

Il risultato descriverà soltanto la resistenza tra le linee nelle condizioni
della prova. Non prova tensioni interne, livelli SPI, bitrate o funzionamento CAN.
Le verifiche successive dipendono da questa misura e dall'identificazione del circuito.

Riferimento strumento: [pagina manuale UNI-T UT210E](https://meters.uni-trend.com/download/ut210e-user-manual/).

Per C-001 tenere il modulo scollegato e appoggiare soltanto tra loro le punte
metalliche dei due puntali, lasciando la funzione Ω. Registrare valore e unità.
Un valore vicino a zero è atteso per il contatto diretto; non prova la taratura
assoluta del tester. Non modificare ponticelli né alimentare il modulo.

Per M-003 mantenere il modulo isolato e spento, tester su Ω, senza spostare
ponticelli. Sulla foto frontale R2 è in basso, a destra del LED POW e a sinistra
di J1, con codice 121: appoggiare un puntale a ciascuna delle sue due estremità
metalliche, senza premere o forzare il componente. Registrare valore e unità.
