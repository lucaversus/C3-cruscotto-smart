# Alimentazione e STOP manuale — Cruscotto C3+AI / Data Logger

Revisione D, 20/10/2026: aggiunti i punti di prelievo del cruscotto (D-030). Revisione C: prove a banco D-022. Scelta utente D-015: logger temporaneo per pochi giorni.

La precedente proposta rev A di +12 permanente, IGN separato, MOSFET mantenuto,
TVS dedicato e arresto automatico e ritirata per questa versione. Non comprare
quel circuito di mantenimento o un UPS per il logger temporaneo. Pololu escluso D-014.

## Materiale della versione semplificata

- 1 convertitore Uadme GYVRM-K240505/B0BFFDSNRC, 5 V, gia proposto: candidato,
  non dichiarato ordinato o collaudato;
- 1 portafusibile in linea e fusibile di ramo: proposta 2 A, da verificare con
  carico/cablaggio effettivo; non sostituisce la verifica del punto di prelievo;
- 1 pulsante momentaneo normalmente aperto STOP;
- fili, morsetti, fissaggio e contenitore isolante per il montaggio temporaneo.

Nessun secondo filo IGN richiesto per una funzione di arresto automatico.
Il punto di alimentazione che si disattiva con l'auto resta da identificare,
come richiesto dall'utente; non si presume disponibile un pin del quadro o OBD.

## Funzionamento richiesto

All'avvio comincia a registrare automaticamente (D-004). Premendo STOP:
fermare interrogazioni e acquisizione, svuotare buffer e chiudere i file SD;
solo dopo mostrare SALVATO - PUOI SPEGNERE e restare nello stato ARRESTATO.
La stessa pressione non deve riavviare la registrazione. Se il salvataggio
fallisce, mostrare ERRORE SD e non SALVATO. Gestire rimbalzo e pressione mantenuta.

Il pulsante e un ingresso logico a 3,3 V, non un interruttore che taglia corrente.
Il sistema resta alimentato ma inattivo fino allo spegnimento dell'auto.
Non chiamare questo stato disconnessione elettrica; deep sleep e facoltativo.
Il display deve dare conferma leggibile prima di qualsiasi sua disattivazione.

Nessun UPS o chiusura automatica richiesti. Se viene tolta corrente senza STOP,
o prima della conferma, il file puo essere incompleto o la SD corrotta.
Verificare uscita 5 V del buck e non portare 12 V ai GPIO. Non alimentare insieme
USB e 5 V esterni senza prima verificare il percorso della scheda ESP32.
Il modulo economico non e stato qualificato automotive: uso breve non ne
cambia i limiti elettrici. Nessun montaggio, firmware STOP o collaudo eseguito.

## Prove a banco prima dell'auto — rev C, 20/10/2026 (D-022)

D-015 resta valida. Le due prove seguenti verificano con dati reali che
l'arresto manuale sia sufficiente; si eseguono a banco, con SD montata e logger
in registrazione, prima di qualsiasi installazione. Esiti nel registro moduli.

**P-001 — interruzione senza STOP.** Togliere alimentazione durante la
registrazione 20-30 volte, a istanti diversi (anche entro 1 s da un `sync`).
Dopo ogni prova riavviare: il logger deve montare la SD e aprire un nuovo file.
A fine serie controllare la scheda al PC (controllo errori del filesystem) e
che i file precedenti siano leggibili fino all'ultima riga sincronizzata.
Criterio: nessun errore di filesystem e nessun file illeggibile. In caso di
errori, valutare con l'utente una modifica a D-015; non decidere autonomamente.

**P-002 — calo di tensione all'avviamento.** Con alimentatore da banco regolabile
a monte del convertitore 5 V, simulare un abbassamento breve verso 6-7 V
(avviamento del diesel con candelette e motorino). Annotare se l'ESP32 si riavvia.
Un riavvio produce un nuovo file e lascia il precedente senza footer: è accettabile
solo se P-001 è superata. Se si riavvia, registrare la soglia osservata.

Entrambe richiedono alimentatore da banco non ancora censito come disponibile.

## Punti di prelievo per il cruscotto (D-029, D-030) — 20/10/2026

Fonte: MAN-017 PDF 2, pag. 91, tabella vie della presa diagnosi C001 e tabella
fusibili abitacolo (testo del manuale, non ancora misurato sulla vettura).

| Presa diagnosi C001 | Funzione dichiarata dal manuale |
| --- | --- |
| via 16 | + batteria (permanente) |
| via 1 | + dopo contatto (sotto chiave) |
| vie 4 e 5 | massa scocca |
| via 7 | linea K, controllo motore |
| vie 11 / 12 | linea K3 BSI / K4 ABS-ESP |

Conseguenza: la presa OBD, situata sopra la BSI sotto il coperchio fusibili,
offre in un solo punto **+12 V permanente, segnale chiave, massa e K-line**. La
derivazione posteriore della presa (HW-OBD-HARNESS, fronte libero D-007) diventa
il candidato principale per l'alimentazione D-030 e per la K-line. La via 1 non
è standard OBD: la sua presenza sull'esemplare va verificata.

Fusibili correlati (stessa tabella): F1 15 A e F6 10 A "connettore diagnosi";
F15 15 A "quadro, frontalino climatizzatore, autoradio, ..." (tipo di linea non
indicato); F22 30 A accendisigari e prese 12 V. Il ramo del cruscotto richiede
comunque un proprio fusibile in linea vicino al prelievo (HW-FUSE-HOLDER).

**Verifica proposta all'utente, sicura:** tester in V DC, nero su via 4 o 5,
rosso su via 16 (atteso ~12 V sempre) e su via 1 (atteso ~12 V solo con chiave
inserita). Puntali solo su quelle vie; non toccare le vie 7, 11, 12 né cortocircuitare
contatti vicini. La stessa via 16 è adatta anche alla misura del calo
all'avviamento: l'accendisigari potrebbe essere escluso durante l'avviamento e
falsare la misura.
