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

## Prosecuzione senza vista delle piste posteriori

Utente: retro verniciato di nero, nessun dettaglio utile visibile. Non rimuovere
il rivestimento. Procedere con misure non invasive a modulo isolato.

| Misura | Stato | Risultato | Condizioni richieste |
| --- | --- | --- | --- |
| M-006, resistenza VCC-GND | riferita | circa 9 kΩ (testo utente: “9komh”) | Modulo scollegato da tutto, tester Ω, nero GND e rosso VCC del connettore SPI; lettura dopo circa 5 secondi |

## Controllo mirato compatibilità ESP32 — M-007 in attesa

Richiesto dall’utente: concentrarsi su alimentazione e livelli SPI. Modulo
spento e isolato, tester Ω: misura tra VCC del connettore e pin 3 (VCC)
del transceiver U1 marcato VP230. Per contare i pin identificare prima
il riferimento del pin 1, poi procedere 1–2–3 lungo lo stesso lato. Se il
riferimento non è identificabile non indovinare l’orientamento. Nessun
risultato ancora acquisito. Riferimento: datasheet TI SN65HVD230, pin 3 VCC.
La misura riguarda il percorso di alimentazione del transceiver; restano da
verificare alimentazione MCP2515 e livelli SPI, prima di collegare ESP32.

M-007: utente riferisce “0” dopo istruzione di misura in Ω tra VCC connettore
e pin 3 U1 VP230. Indicazione di collegamento diretto: non alimentare il
modulo a 5 V. Il VP230 corrisponde al SN65HVD230 a 3,3 V secondo il datasheet TI.
Non è ancora verificata alimentazione del MCP2515 né comunicazione SPI.

M-008 in attesa: resistenza tra VCC connettore e VDD del MCP2515.
Il controller fotografato ha 20 pin (TSSOP): VDD è il pin 20, di fronte
al pin 1 sul lato opposto, alla stessa estremità del corpo. Non usare
il pin 18 della diversa variante a 18 pin. Modulo isolato, tester Ω.
Fonte: datasheet Microchip DS20001801J, tabella 1-1, pagina 4.

M-008: risposta utente “arriva”, registrata come conferma qualitativa di
collegamento; nessun valore numerico attribuito. Compatibilità logica SPI
ancora non provata.

M-009 proposta, in attesa: scollegare USB ESP32, collegare soltanto 3V3→VCC
e GND→GND, poi alimentare ESP32 via USB. CAN H/L e SPI restano liberi.
Tester su tensione continua (V DC), nero GND, rosso VCC del modulo:
registrare la tensione effettiva. Non applicare 5 V e non misurare Ω sul
circuito alimentato. Il controllo riguarda solo alimentazione a banco.

M-009 esito riferito il 18/10/2026: utente “c'e 3.3V”. Registrati 3,3 V
tra VCC e GND del modulo nella prova a banco richiesta. Conferma della
tensione presente sul modulo alimentato; non dimostra funzionamento del
controller, comunicazione SPI, stabilità prolungata o funzionamento CAN.

Prova successiva M-010 preparata, non eseguita: firmware separato
[collaudo SPI](../firmware/mcp2515-spi-test/README.md), alimentazione 3,3 V,
SCK18/MISO19/MOSI23/CS26. RESET, modalità configurazione e confronto CNF1
con tre pattern e ripristino; nessuna trasmissione CAN. GPIO per solo banco,
non assegnazione definitiva del logger. Nessun esito hardware acquisito.

18/10/2026: caricamento mcp2515-spi-test 0.1.0 su COM3 riuscito con BOOT
manuale, hash dei segmenti verificati da esptool. Primo tentativo automatico
fallito prima della scrittura (boot 0x13). Risultato M-010 ancora in attesa;
richiesti rilascio BOOT e pressione EN per avvio normale.

## Esito M-010 — 18/10/2026

Dopo rilascio BOOT e pressione EN riferiti dall’utente, lettura diretta di COM3
a 115200 con DTR/RTS inattivi per 7 secondi:

```text
status SPI_TEST=PASS uptime_ms=15545
```

Il risultato memorizzato dal firmware richiede modalità configurazione,
scrittura/rilettura CNF1 con 0x55/0xAA/0x00 e ripristino del valore iniziale.
Banner e letture dei singoli registri non catturati. Alimentazione 3,3 V
riferita in M-009; SPI 100 kHz mode 0, CAN H/L scollegati.
Verificato il percorso SPI a banco; non transceiver, bitrate, terminazione,
rete auto o stabilità prolungata. Nessun frame CAN trasmesso dal firmware.
