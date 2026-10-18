# Procedura di continuità — Cruscotto C3+AI / Data Logger

Revisione 2, 18/10/2026. Richiesta dall'utente per evitare acquisti duplicati,
decisioni dimenticate e documenti incoerenti tra chat e PC.

## Fonti e precedenza

1. Un'istruzione esplicita nuova dell'utente guida il lavoro: registrarla subito.
2. README principale: decisioni approvate D-xxx e questioni ancora aperte.
3. hardware.json: inventario strutturato con stato, fonte e verifiche aperte.
   hardware-inventory.md è la vista generata, non una seconda fonte manuale.
4. README Data Logger e documenti di collaudo: implementazione e prove reali.
   Per identificazione visiva consultare le foto collegate all'inventario e
   [il dossier fotografico](hardware-photos/README.md). Non richiedere foto
   già disponibili: recuperarle prima dai file e poi archiviarle stabilmente.
5. Schemi e config.h: proposta tecnica; non promuovono un pinout a verificato.
6. Ricordi e riepiloghi di chat: solo indizi per cercare, non autorità sullo stato.

Se due fonti si contraddicono, non cancellare componenti e non comprare sostituti:
conservare l'evidenza e risolvere soltanto l'ambiguità necessaria. Nel caso CAN
l'utente ha già corretto l'inventario: entrambi i moduli iniziali restano presenti
dichiarati, non elettricamente verificati. Il CAN Pal proposto non va acquistato.

## Prima di ogni decisione pertinente

Leggere i quattro documenti richiesti in AGENTS.md ed eseguire dalla radice:

```powershell
python tools/project_preflight.py
```

Il comando controlla struttura/stati dell'inventario, vista Markdown generata,
presenza dei documenti/decisioni obbligatori e coerenza dei GPIO proposti con
config.h. Controlla anche file fotografici e SHA-256 rispetto al manifest.
Stampa un riepilogo del materiale e delle scelte chiave.
Non prova l'hardware e non sostituisce la lettura o il giudizio tecnico.
Se un controllo fallisce, correggere la fonte o la divergenza prima di proseguire
con una scelta che ne dipende. Non cambiare dati corretti solo per far passare un test.

Prima di un acquisto, associare la funzione richiesta agli ID hardware:
presente non collaudato e ordinato non significano assente. Riutilizzare prima;
un sostituto richiede motivazione verificabile e autorizzazione sul cambiamento.
Non chiedere all'utente di reinviare informazioni che sono già nel repository.

## Quando cambia una informazione

Aggiornare hardware.json (fonte, stato, quantità soltanto se nota, prove aperte), poi:

```powershell
python tools/project_preflight.py --render-inventory
```

Per una nuova decisione approvata aggiornare anche la tabella D-xxx nel README;
per una decisione ritirata conservarne la motivazione come superata. Distinguere:
idea, scelta approvata, implementazione, compilazione, caricamento e collaudo.
Una consegna aggiorna lo stato da ordinato a presente, non a verificato.
Una foto dimostra solo ciò che è leggibile: non sostituisce misure di tensione,
resistenza, continuità o prova funzionale. Aggiungere una nuova foto all'archivio,
al manifest e agli ID hardware pertinenti; conservare localmente l'originale
integrale e pubblicare una copia priva di metadati personali. Le foto sorgenti
non devono essere coperte da cartigli: usare il cartiglio nel dossier/derivati.
Aggiornare testi e revisioni dei disegni coinvolti nello stesso cambiamento.

## Verifica e salvataggio

Eseguire preflight, test pertinenti e `git diff --check`. Per modifiche al solo
registro non occorre ricompilare firmware invariato. I controlli del preflight
sono verificabili con `python -m unittest discover -s tools/tests -v`.

Conservare cache e output firmware esclusi da Git. Versionare sorgenti, schemi,
anteprime, inventario e documenti; non inserire token, VIN completo o dati personali.
Pubblicare solo quanto autorizzato; la richiesta attuale autorizza il salvataggio
su GitHub del lavoro di progetto già prodotto e dei nuovi registri.
Usare commit descrittivi senza force-push, verificare ref remoto e corrispondenza
del tree locale. Un commit locale, un fetch vecchio o il messaggio di un comando
non bastano da soli a dichiarare che tutto è pubblicato.

Questa procedura rende i controlli ripetibili. AGENTS.md fornisce le istruzioni
alle future sessioni nel repository; nessun file può garantire da solo che un
assistente in un'altra chat, senza accesso al repository, lo abbia consultato.
