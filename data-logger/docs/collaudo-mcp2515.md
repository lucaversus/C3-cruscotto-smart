# Registro di verifica HW-CAN-MCP2515

Cruscotto C3+AI / Data Logger — revisione 6, 18/10/2026.

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
| M-003, direttamente sulle estremità di R2 | riferita | 119 Ω (testo utente: “119 omh”) | Misura sulla resistenza; collegamento verso H/L non ancora determinato |
| M-004a/b, terminale L verso le due estremità di R2 | riferite | entrambe circa 52 kΩ (testo utente: “entrambi 52komh”) | Nessun percorso diretto a bassa resistenza verso L riscontrato in queste misure |
| M-005a, H verso R2 lato POW | riferita | 0; unità non ripetuta, Ω richiesto | Compatibile con collegamento diretto a H |
| M-005b, H verso R2 lato J1 | riferita | 120 Ω (testo utente: “lato j1 120omh”) | Coerente con attraversamento di R2, senza identificare il resto del circuito |

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

Per M-004 mantenere il puntale nero sul contatto metallico del morsetto L,
modulo sempre isolato e spento, tester su Ω. Misurare col rosso prima
l’estremità di R2 dal lato del LED POW, poi quella dal lato di J1.
Registrare separatamente i due valori con unità, oppure OL, senza dedurre
la funzione dei ponticelli prima di aver identificato i collegamenti.

Per M-005 spostare soltanto il puntale nero da L al contatto metallico H.
Modulo sempre scollegato, tester su Ω e ponticelli invariati. Con il rosso
ripetere sulle estremità R2 lato POW e lato J1; riportare i due valori e unità.

## Esito parziale dopo M-005

Le misure riferite indicano R2 circa 119–120 Ω e un collegamento diretto
della sua estremità lato POW a H. A modulo spento H-L risulta invece circa
52 kΩ: non è stato misurato un percorso da 120 Ω tra i morsetti in queste
condizioni. Non dedurre comportamento a modulo alimentato, guasto o
compatibilità elettrica con ESP32. Prossimo dato necessario: foto del retro
del modulo MCP2515; nell’archivio sono presenti solo fronte e dettaglio.

Il controllo di lentezza della chat ha interrotto il passaggio alla foto:
le due letture M-005 sono state conservate, senza avviare altre misure.
