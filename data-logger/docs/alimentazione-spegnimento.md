# Alimentazione e STOP manuale — Cruscotto C3+AI / Data Logger

Revisione B, 18/10/2026. Scelta utente D-015: logger temporaneo per pochi giorni.

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
