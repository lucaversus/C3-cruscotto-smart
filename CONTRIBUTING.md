# Riprendere il progetto da un altro PC o agente

Vale per persone e agenti AI. Usare il solo repository `lucaversus/C3-cruscotto-smart`.
Leggere [AGENTS.md](AGENTS.md) prima di modificare file; se lo strumento non lo
carica automaticamente, aprirlo esplicitamente. Le skill installate sul PC di
Luca non sono prerequisiti: istruzioni, fonti e controlli necessari sono nel repository.

## Avvio da clone nuovo

Servono Git, Python 3.13 con pip e venv, accesso Internet per scaricare dipendenze.
I controlli senza compilazione richiedono soltanto Python >= 3.10 e Git.
Aprire un terminale nella radice del clone, su Windows, Linux o macOS:

```text
python tools/dev.py setup
python tools/dev.py check
python tools/dev.py build
```

Usare `python3` se questo e il nome dell'interprete sul sistema. Su Windows si
puo usare `py -3.13`. Su Linux il pacchetto venv della distribuzione deve essere
disponibile. Nessun comando richiede di attivare manualmente l'ambiente virtuale.
`setup` crea `.tools/pio-venv` e installa [le versioni degli strumenti](tools/requirements-dev.txt).
Non modifica l'installazione Python globale. Piattaforma ESP32 e librerie firmware
sono fissate in [platformio.ini](data-logger/firmware/logger/platformio.ini).
Le dipendenze Python transitive sono risolte da pip: non e un lock completo del sistema.

`check` esegue preflight, test Python, test C++ host della logica firmware
(se e disponibile un compilatore C++: g++, clang++ o `CXX`) e controllo whitespace.
`lint` esegue cppcheck sui sorgenti del logger, se installato; la CI esegue entrambi. Funziona anche prima
di `setup`, senza USB, rete o manuali originali. `build` compila i profili banco
e veicolo, compresi i controlli statici C++; **non carica firmware**.
La prima build scarica toolchain e dipendenze. Su Windows la cache corta predefinita
e `%USERPROFILE%/Documents/Codex/pio-c3`; altrove `.tools/pio-core`.
Per scegliere una cache diversa impostare `PLATFORMIO_CORE_DIR` prima di `build`.
Su Windows anche librerie e output finiscono in un workspace corto sotto
`pio-c3/workspaces/<id-checkout>` per evitare il limite dei percorsi; due checkout
diversi non condividono gli stessi output. `python tools/dev.py paths` mostra
i percorsi effettivi. `PLATFORMIO_WORKSPACE_DIR`, se impostato, viene rispettato.
Il caricatore visibile usa gli stessi percorsi; i vecchi `.pio/build` possono
rimanere come artefatti storici e non sono necessariamente l'ultima build.
Cache, ambiente virtuale, dati privati e log rimangono esclusi da Git.

## Come trovare il punto di ripresa

- Decisioni e vincoli: [README principale](README.md#decisioni-definitive).
- Firmware attualmente caricato e limiti: [Data Logger](data-logger/README.md#stato-e-organizzazione).
- Cruscotto: firmware di prova in `cruscotto/firmware/` (display-test, ui-test, speak-test),
  documenti e disegni in `cruscotto/docs/`; firmware caricato sulla scheda S3 indicato
  nella voce HW-DASH-DISPLAY dell'inventario.
- Materiale e verifiche aperte: [inventario](data-logger/docs/hardware-inventory.md),
  generato da `hardware.json`; foto collegate nello stesso registro.
- Collegamenti correnti per la prova USB: [EL-003](data-logger/docs/collegamenti-banco-030.md).
- Risultati reali delle prove: [registro moduli](data-logger/docs/verifiche-moduli.md).
- Fonti del veicolo: [indice manuali](docs/manuali/indice.md). Gli originali sono
  esclusi dal repository; non servono per check/build. La rigenerazione facoltativa
  dell'indice richiede gli originali autorizzati e pypdf, non installato dal setup base.

Disegni (D-024): ogni SVG ha un generatore Python in `tools/` o `data-logger/docs/tools/`
basato su `iso_drawing.py`; l'anteprima PNG a 200 dpi si rigenera con
`python tools/render_png.py <file.svg>` (richiede Chrome o Edge in modalità headless).
Aggiornare SVG, PNG e cartiglio nello stesso cambiamento.

Controlli: `check` e `lint` coprono preflight, test Python e logica del logger; i
firmware del cruscotto sono per ora soltanto compilati da `build`.

Non rieseguire prove hardware per ricostruire il contesto quando esiste gia un
risultato documentato. Distinguere sempre proposto, compilato, caricato e collaudato.

## Collaborazione e chiusura

Controllare `git status --short --branch` all'inizio e preservare modifiche altrui.
Con agenti contemporanei assegnare file distinti o usare checkout/worktree separati;
non includere automaticamente il lavoro di un altro agente nel proprio commit.
Prima di ogni pubblicazione eseguire il controllo di compatibilita D-021:
`check` e riscontro delle modifiche con decisioni, inventario e configurazioni.
Eseguire anche `build` per modifiche firmware, dipendenze, GPIO/interfacce,
ambiente di compilazione o CI, oppure se manca un esito valido per i sorgenti.
Per sole modifiche documentali si puo riutilizzare una build invariata e gia
verificata, dichiarandolo. Le verifiche hardware aperte non diventano superate
con questi comandi; sorgenti e proposte non collaudati restano versionabili.
Prima di pubblicare confrontare il ref remoto attuale e preservare nuovi commit.
Non fare force-push; riportare commit, controlli e verifiche hardware non eseguite.
La chiusura comprende il controllo della pipeline sul commit pubblicato:
se in corso, non disponibile o fallita, indicarne lo stato effettivo.

Il caricamento e una fase separata, da svolgere solo nell'ambito richiesto
dall'utente e con hardware identificato. Su Windows usare il terminale visibile
descritto nel [README firmware](data-logger/firmware/logger/README.md#caricamento-con-terminale-visibile).
COM3 e la porta riscontrata sul PC di Luca, non una scelta automatica per altri PC.

## Controlli GitHub

[Workflow](.github/workflows/project-checks.yml): push su `main`, pull request e
avvio manuale. Esegue gli stessi `check` e `build` su Ubuntu con Python 3.13,
permessi di sola lettura e nessun accesso USB o segreto. Non pubblica artefatti,
non usa cache GitHub e non installa nulla sulla vettura.
Azioni fissate a commit; non dichiarare riuscita una pipeline soltanto perche
il file YAML e presente. Verificare il risultato della run sul commit pubblicato.
