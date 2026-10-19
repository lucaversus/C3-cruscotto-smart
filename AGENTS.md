# Istruzioni permanenti — Cruscotto C3+AI

Per un clone nuovo o un altro PC leggere [CONTRIBUTING.md](CONTRIBUTING.md):
setup portabile, comandi check/build, mappa delle fonti e coordinamento tra agenti.
Non dipendere da skill o ambienti installati soltanto sul PC di Luca.

## Consultazione obbligatoria, prima di decidere

Applicare la consultazione senza ripetizioni inutili: leggere le fonti all'inizio
del blocco di lavoro e rileggerle quando cambiano o prima di una nuova scelta
tecnica. Tra letture successive dello stesso collaudo usare il contenuto già
consultato e aggiornare subito i risultati locali. Non ristampare interi documenti,
non rieseguire preflight e non fare un ciclo completo GitHub per ogni singolo
valore riferito. Eseguire preflight e pubblicazione a fine blocco, prima di una
nuova decisione dipendente o quando l'utente chiede salvataggio/interruzione.
La pubblicazione differita deve essere dichiarata; nessuna perdita di risultati
locali o rinuncia alla consultazione delle fonti.

Per ogni attività che riguarda hardware, acquisti, firmware, GPIO, protocolli,
schemi, alimentazione o collaudo:

1. Leggere **questa versione su disco** di `README.md`,
   `data-logger/README.md`, `data-logger/docs/hardware-inventory.md` e
   `data-logger/docs/procedura-progetto.md`. Non sostituirli con ricordi di chat.
2. Eseguire `python tools/project_preflight.py` dalla radice con un Python
   disponibile. Se segnala incoerenze, risolverle prima della decisione dipendente.
3. Controllare `git status --short --branch`; preservare modifiche preesistenti.
   Se serve lo stato pubblicato, leggere il ref GitHub e confrontarlo: il solo
   `origin/main` locale non prova la sincronizzazione attuale.
4. Collegare la proposta agli ID hardware e alle decisioni D-xxx nel README.
   Per identificazione e misure consultare prima le foto collegate nell'inventario
   e `data-logger/docs/hardware-photos/README.md`. Non richiedere di nuovo foto
   già archiviate; distinguere una vista mancante da quelle disponibili.
   Prima di suggerire acquisti controllare anche materiale presente non collaudato
   e materiale ordinato. Mancanza di collaudo non significa mancanza del modulo.
5. Non trasformare proposte, dichiarazioni commerciali, illustrazioni o una
   compilazione riuscita in decisioni approvate o verifiche hardware.

## Aggiornamento nello stesso passaggio

- Ogni nuova informazione su possesso, ordine, consegna o verifica va aggiornata
  in `data-logger/docs/hardware.json`, con fonte e verifiche ancora aperte.
  Poi eseguire `python tools/project_preflight.py --render-inventory` per
  aggiornare la vista Markdown. Non mantenere un secondo inventario manuale.
- Le decisioni definitive stanno nella tabella D-xxx del README principale.
  Aggiornarla con il fondamento della scelta e la data; una decisione superata
  resta tracciata come superata. Le scelte aperte restano nella sezione separata.
- Aggiornare nello stesso cambiamento documenti, firmware e disegni coinvolti;
  i disegni devono avere cartiglio e revisione coerenti. Non cambiare una scelta
  dell'utente autonomamente: chiedere solo per il vero conflitto irrisolto.
- Un'affermazione generica ambigua non elimina componenti già identificati:
  conservarli con stato incerto e risolvere il dubbio prima di acquisti/collegamenti.

## Controllo obbligatorio di compatibilità — D-021

A fine blocco e **prima di ogni pubblicazione su GitHub**, eseguire
`python tools/dev.py check`. Verificare che le modifiche siano compatibili con
le decisioni D-xxx, l'hardware inventariato, i GPIO/protocolli configurati e le
versioni di strumenti e librerie. Rileggere le sole fonti coinvolte se cambiate.

Eseguire anche `python tools/dev.py build` se cambiano firmware, dipendenze,
configurazione GPIO/interfacce, ambiente di compilazione o CI, oppure manca un
esito di build valido per quegli stessi sorgenti e configurazioni. Per sole
modifiche documentali non ripetere una build già valida: dichiarare il riuso
dell'esito, senza presentarlo come nuova compilazione.

Un controllo software fallito o un conflitto tecnico va risolto prima di
pubblicare le modifiche dipendenti. Le verifiche hardware ancora aperte restano
esplicite nell'inventario: non equivalgono a controlli superati e non impediscono
di versionare sorgenti o proposte correttamente marcati come non collaudati.
Questo controllo non autorizza caricamenti sull'ESP32 o collegamenti al veicolo.

**Dopo la pubblicazione**, verificare ref remoto e risultato della pipeline
`Project checks` sul commit esatto. Se fallisce, correggere e ripetere i soli
controlli interessati; se è in corso o non disponibile, dichiararlo, senza
considerare verificata la compatibilità remota. Registrare nel resoconto commit,
controlli effettuati, risultati riutilizzati e limiti. Evitare cicli per ogni
singola misura: raggruppare il controllo alla chiusura del blocco di lavoro.

## Chiusura e GitHub

Eseguire preflight, controlli pertinenti e `git diff --check`. Quando l'utente
richiede salvataggio/pubblicazione, includere tutti i file necessari per rendere
la modifica riproducibile, senza cache, credenziali o dati personali del veicolo.
Non fare force-push, reset distruttivi o sovrascrivere modifiche altrui.
Se git push non è autenticato, usare il connettore GitHub già autorizzato e
sincronizzare il checkout verificando SHA e tree. Non richiedere di riconfigurare
Git inutilmente. Dichiarare pubblicato solo dopo verifica del ref remoto.
Nel resoconto indicare commit, verifiche reali e limiti; distinguere compilato,
caricato e collaudato. Se non pubblicato, dirlo esplicitamente.

## Procedure guidate nel repository — D-023

`.claude/skills/` contiene procedure in Markdown, leggibili da qualsiasi agente
o persona, non solo da Claude: `chiusura-blocco` (pubblicazione D-021),
`registro-collaudo` (misure a banco) e `revisione-firmware` (checklist modifiche).
Riassumono le regole di questo file senza sostituirle: in caso di differenze vale AGENTS.md.

## Vincoli del progetto

Italiano, risposte brevi, un passaggio alla volta. Software gratuito, preferibilmente
open source. Unico repository: lucaversus/C3-cruscotto-smart. Data Logger prima
del cruscotto. Nessun collegamento veicolo basato su pin/protocolli presunti.
Non comprare un altro modulo CAN senza prima valutare HW-CAN-MCP2515 e HW-CAN-VP230.
