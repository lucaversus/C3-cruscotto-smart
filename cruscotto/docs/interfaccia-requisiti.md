# Interfaccia del cruscotto — requisiti in raccolta

Revisione B, 21/10/2026 (A: prima raccolta). D-027 (nessun touch), D-037, D-038, D-041. Documento di
lavoro: elenco dei contenuti e stili da completare con l'utente; nessuna grafica definita.

## Pagine

1. **Dashboard** (principale): contagiri, velocità e grandezze di uso quotidiano.
   Elenco completo e stile da definire con l'utente.
2. **Tecnica**: valori più tecnici della vettura (es. dati motore OBD).
3. **Diagnostica**: stato del cruscotto, collegamento, sensori e attività dell'IA.

Altre pagine solo se emergeranno. Utente 21/10/2026: "sicuramente più pagine [...]
la dashboard, una seconda pagina con [...] i valori più tecnici [...] una terza [...]
per vedere cosa fa l'intelligenza artificiale".

## Comandi

- Solo i **due pulsanti già presenti sul frontale del quadro** (eventualmente anche i
  comandi al volante): nessun pulsante aggiuntivo. Utente: "vorrei evitare di mettere
  oltre i due pulsanti che già ci sono sul frontale del cruscotto".
- Le **impostazioni** si modificano dall'app (D-038), non dalla dashboard.

## Avvisi

- Anomalie: **riquadro grande in primo piano**; stile da definire.

## Spie dinamiche

Richiesta dell'utente: una spia (es. freccia sinistra) **non occupa spazio quando è
spenta**; quando si accende compare sopra altri elementi grafici, così lo schermo resta
libero per altre informazioni.

Accorgimenti proposti (da confermare):

- **Prova lampade all'avvio**: per 2-3 s tutte le spie compaiono insieme, come nel
  quadro originale, così l'assenza di una spia significa "spenta" e non "schermo o
  dati guasti".
- **Zone di sovrapposizione**: le spie si sovrappongono solo a contenuti secondari, mai
  a velocità, contagiri o riquadro degli avvisi.
- **Dati assenti**: se il collegamento o una fonte non risponde, avviso esplicito
  (come "COLLEGAMENTO ASSENTE" del firmware 0.3.0), perché l'assenza di spie non deve
  essere scambiata per assenza di guasti.
- Le spie di sicurezza (freni, olio, temperatura, batteria) restano sempre visibili
  quando accese, anche con il riquadro di avviso aperto.

Conferma dell'utente (21/10/2026): prova lampade all'avvio sì; zone principali e
secondarie da definire insieme ("quello che avanza è il contenuto secondario");
avviso esplicito di collegamento assente sì; spie di sicurezza sempre visibili sì.

## Sequenza di avvio

Richiesta dell'utente: come nelle auto moderne, all'accensione una breve **animazione
di apertura** (titolo), durante la quale il cruscotto esegue un **controllo di sistema
approfondito** e mostra l'**esito** (superato oppure elenco di ciò che non va), con
eventuale **messaggio vocale** di conferma. Durata allineata alla fase di
preriscaldamento delle candelette del diesel: "quello è il momento in cui [la macchina]
ha fatto il check".

Precisazioni dell'utente (21/10/2026):

- **Stile "Matrix"**: durante l'apertura scorrono i dati che il cruscotto sta
  controllando, con il codice che scende sullo sfondo ("io sono di quegli anni").
  Da progettare insieme quando si creeranno le grafiche.
- **Via libera ("GO") solo quando entrambe le condizioni sono soddisfatte**: fine del
  preriscaldamento delle candelette (dato dell'auto) **e** completamento con esito
  positivo di tutti i controlli del sistema, informatici e del veicolo; il tempo delle
  candelette varia, quindi nessuna delle due condizioni da sola basta.

Proposta di contenuto del controllo: display e memoria, file system, collegamento con
il front-end, ricezione VAN, K-line, IMU, NTC, tensione batteria, audio, modello IA
caricato. Possibile aggancio alla spia candelette letta dal VAN, se presente nei
messaggi. Messaggio vocale subordinato alla verifica dell'uscita audio (U1/P6).

## Stile degli indicatori

- **Indicatori lineari** (barre), non rotativi a lancetta.
- **Colore dell'intera barra** in funzione del valore, non tacche precolorate:
  - temperatura acqua: **bianca** a motore freddo, **azzurra** nella zona normale
    (l'azzurro della barra del firmware di prova, 0x00C0FF, apprezzato dall'utente),
    fino a **rossa** in caso di temperatura alta, con allarme;
  - contagiri: **verde**, che diventa progressivamente **tutta rossa** avvicinandosi
    al limite dei giri, così da capire a colpo d'occhio che i giri sono alti.
- Passaggio di colore preferibilmente **graduale (sfumatura)**, non a scatti: da provare.
