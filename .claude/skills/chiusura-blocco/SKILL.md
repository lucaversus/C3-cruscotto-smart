---
name: chiusura-blocco
description: Chiude un blocco di lavoro del progetto Cruscotto C3+AI e lo pubblica su GitHub secondo D-021 (check, build, branch e PR, verifica CI, unione in main). Usare quando l'utente chiede di salvare, pubblicare o aggiornare il Git.
---

# Chiusura blocco e pubblicazione (D-021)

Regole vincolanti in `AGENTS.md` (sezioni "Controllo obbligatorio di compatibilità"
e "Chiusura e GitHub"). Questa skill le esegue in ordine; in caso di dubbio vale AGENTS.md.

## 1. Stato di partenza

- `git status --short --branch`: elencare i file modificati. Includere solo il
  lavoro del blocco; modifiche di altri agenti non vanno nel commit senza accordo.
- `git fetch origin main` e confronto con il ref remoto (`git ls-remote origin refs/heads/main`):
  se main è avanzato, aggiornare il branch prima di proseguire. Mai force-push.

## 2. Coerenza delle fonti

- Nuove informazioni hardware → `data-logger/docs/hardware.json`, poi
  `python tools/project_preflight.py --render-inventory`.
- Nuova scelta dell'utente → riga D-xxx nel README principale, con citazione e data.
  Proposte non approvate restano nelle questioni aperte.
- Disegni modificati: revisione e data aggiornate nel cartiglio, SVG e PNG insieme.
- Firmware modificato: versione in `config.h` e README firmware coerenti;
  esito in `VERIFICA.md` distinguendo compilato, caricato e collaudato.

## 3. Controlli

- Sempre: `python tools/dev.py check` (preflight, test Python, test C++ host, whitespace).
- Se cambiano firmware, dipendenze, GPIO, ambiente di build o CI:
  `python tools/dev.py build`. Se l'ambiente non può compilare (rete, PlatformIO),
  dichiararlo e affidare la build alla pipeline del branch **prima** dell'unione.
- Facoltativo se disponibile: `python tools/dev.py lint` (cppcheck); la CI lo esegue sempre.
- Sole modifiche documentali: si può riusare una build valida, dichiarandolo.

## 4. Pubblicazione

1. Branch `claude/<argomento>` (o nome concordato), commit descrittivo con
   elenco delle modifiche e dei limiti (cosa non è caricato o collaudato).
2. Push del branch e apertura PR verso `main` (REST: `gh api repos/{owner}/{repo}/pulls`;
   GraphQL non sempre disponibile).
3. Attendere la run `Project checks` sul **commit esatto** della PR
   (`gh api "repos/{owner}/{repo}/actions/runs?head_sha=<sha>"`).
4. Solo con esito `success`: unione della PR (merge commit), poi verifica del ref
   remoto di main e della run `push` sul commit di unione.
5. Se la CI fallisce: correggere sul branch, ripetere i soli controlli interessati.

## 5. Resoconto all'utente

Breve, in italiano: commit e PR, controlli eseguiti e riusati, esito CI su branch
e main, e che cosa resta da fare sull'hardware. Mai dichiarare pubblicato senza
aver letto il ref remoto; mai presentare una compilazione come collaudo.
