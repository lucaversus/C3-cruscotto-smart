# Biblioteca tecnica — Cruscotto C3+AI

Revisione 1, 19/10/2026. Ambito: progetto generale, Data Logger e futuro cruscotto.

## Stato reale della consultazione

21 file catalogati nelle due cartelle Drive: 20 PDF e 1 immagine. Download locale
completato per tutti; originali esclusi da Git in `.tools/manuali-c3/`.
13 PDF testuali distinti indicizzati per parole chiave, piu una copia identica;
5 PDF scansionati senza testo (incluso un documento non indicizzato per privacy),
1 PDF danneggiato e 1 immagine non ancora esaminata. Estrazione automatica non
significa lettura tecnica completa o verifica di ogni schema.

Fonti: cartella C3 fornita dall'utente e sottocartella `manuale tecnico`.
Gli URL delle fonti sono nel catalogo. Alcuni vecchi file richiedono la chiave
presente nel collegamento originale condiviso dall'utente: aprirli dalla cartella
Drive gia autorizzata. Non rendere pubblica la chiave della cartella, che contiene
anche documenti personali. Non copiare manuali, immagini, VIN o targhe nel repository.

## Consultazione rapida per il progetto

Le pagine PDF partono da 1; la pagina stampata puo essere diversa. I riferimenti
seguenti sono stati letti nel testo; la tabella diagnosi del capitolo elettrico e
stata verificata anche sul rendering della pagina. Gli altri schemi grafici vanno
aperti e verificati visivamente prima di ricavarne un collegamento.

| Cercare | Documento e pagina PDF | Pagina stampata | Uso / limite |
| --- | --- | --- | --- |
| Fusibili e presa diagnosi | MAN-017, PDF 2 | 91 | Tabella diagnosi distingue K motore, K3 BSI e K4 ABS/ESP; non e uno schema della specifica auto gia verificato |
| BSI e rete verso quadro | MAN-017, PDF 3 | 92 | Descrizione VAN, DATA/DATAB e collegamento BSI-quadro; non assegna i pin del nostro quadro |
| Legenda schemi | MAN-017, PDF 4 | 93 | BSI1, C001, 0004 e codici colore: consultarla prima degli schemi |
| Ricollegamento batteria | MAN-017, PDF 14 | 103 | Rinvio alla procedura, da confrontare con PH 7905 e variante; non mescolare istruzioni di versioni diverse |
| Schema motore DV4TD | MAN-011, PDF 11 | 19 | Priorita per 1.4 HDi 8 valvole; PDF 12-13 sono DV4TED4, non equivalenti |
| Raffreddamento DV4TD | MAN-011, PDF 14-15 | 22-23 | Riferimenti per futuro dataset temperatura; non implicano PID OBD disponibili |
| Sensori e gestione DV4 | MAN-011, PDF 17-21 | 25-29 | Separare DV4TD da DV4TED4, centraline e allestimenti prima di adottare soglie |
| Identificazione C3 / 8HZ | MAN-003, PDF 2-3 e 11-13 | Tabelle iniziali e 3-5 | PH 7905, anno 2005, Volume 1; copre anche C2/Pluriel e altre motorizzazioni |
| Dopo ricollegamento batteria | MAN-003, PDF 16-17 | 8-9 | Fonte costruttore per operazioni successive a interventi |
| Capacita e lubrificanti C3 | MAN-003, PDF 20 e indice PDF 7-8 | 12 e rinvii | Leggere la riga DV4TD/8HZ e gli intervalli OPR; non tutte le righe si applicano |
| Controllo pressione olio | MAN-003, PDF 141 | 133 | Procedura di misura, non sensore aggiuntivo o segnale gia acquisibile |
| Sovralimentazione DV4TD | MAN-003, PDF 146 | 138 | Riferimento di officina per misure e condizioni; non confondere pressione relativa e assoluta |
| EGR DV4TD | MAN-003, PDF 151 | 143 | Procedura specifica; presenza nella documentazione non prova disponibilita OBD |
| Smontaggio quadro | MAN-006, PDF 106 | 108 | Disponibile per il progetto futuro; D-017 mantiene fili volanti, non occorre comprare un connettore |
| Fusibili, VAN e diagnosi nel manuale completo | MAN-006, PDF 88-91 | 90-93 | Stessa materia di MAN-017, con diversa numerazione PDF |
| Schema servosterzo | MAN-016, PDF 1-4 | 62-65 | Altro sottosistema: non trasferire i suoi pin CAN al quadro |
| Comandi e spie per futura UI | MAN-004 e MAN-005 | Doppie pagine scansionate | Prima parte: copertina + PDF 2-4 lette; seconda parte PDF 1 = stampate 68-69, ESP/parcheggio. Servono lettura visiva/OCR e riscontro delle dotazioni |

## Come usare le informazioni senza confonderle con prove sul veicolo

D-008 e D-016 restano validi: diagnosi OBD di sola lettura e ricezione passiva
sulla linea dietro al quadro. La documentazione rafforza il percorso K-line/VAN,
ma non risolve da sola il conflitto delle schermate diagnostiche precedenti e non
certifica cablaggio, bitrate, centralina esatta o singoli parametri disponibili.
Usare sempre la variante DV4TD/8HZ e l'OPR del veicolo quando la fonte lo richiede.
Non assumere che tutti i dati del motore circolino sulla linea del quadro.

Per una nuova proposta: indicare ID MAN, pagina PDF, pagina stampata, variante,
fatto documentato e controllo ancora necessario. Confrontare la proposta con le
decisioni D-xxx e l'inventario. Non cambiare acquisti, GPIO o schemi automaticamente.

## Catalogo completo

Stati: **testo indicizzato** = testo estratto e ricercabile, non tutti i disegni
validati; **scansione parziale** = pagine indicate esaminate visivamente;
**non indicizzato** = nessuna deduzione dai contenuti; **danneggiato** = lettura fallita.

| ID | File / fonte | Pagine PDF | Stato e contenuto verificato |
| --- | --- | --- | --- |
| MAN-001 | [C3 - 0230 07 857001A -.pdf](https://drive.google.com/file/d/0BzErIAgsdW3CM2lJTW1KOHRZM3c/view) | 3 | scan_visual_partial: Esploso ricambi vano portaoggetti, cassetto e serratura; guida a sinistra. Prima pagina verificata visivamente; applicabilita alla C3 2005 non provata. |
| MAN-002 | libretto C3.pdf (riferimento privato omesso) | 1 | private_unindexed: Documento scansionato di una pagina: non trascritto e non indicizzato per contenuti personali. |
| MAN-003 | [Manuale officina C2 C3 Pluriel_2005.pdf](https://drive.google.com/file/d/12YGFvTjmEJFmcBzKlW3INXz8LPhrIZaS/view) | 271 | text_indexed: Citroen PH 7905, Volume 1, 2005; C2/C3/Pluriel e piu motori. Tabelle 8HX/8HZ presenti; distinguere C3 e DV4TD dalle altre varianti. |
| MAN-004 | [manuale parte 1.pdf](https://drive.google.com/file/d/0BzErIAgsdW3CNWZodDVXSE1WMFk/view) | 33 | scan_visual_partial: Scansioni del manuale Uso e manutenzione C3. Copertina e PDF 2-4 verificate visivamente: telecomando, chiavi, chiusura e allarme. Nessun testo ricercabile. |
| MAN-005 | [manuale parte 2.pdf](https://drive.google.com/file/d/0BzErIAgsdW3CV3FMLS01Smh2WmM/view) | 31 | scan_visual_partial: Continuazione scansionata del manuale d uso. PDF 1 verificata: pagine stampate 68-69, ESP e assistenza parcheggio. Nessun testo ricercabile. |
| MAN-006 | [Manuale tecnico C3 HDI.pdf](https://drive.google.com/file/d/12_ZNz0WnvBmJO-pCnx7OMGYWqVFoPK4D/view) | 128 | text_indexed: Manuale tecnico C3, motori DV4TD e DV4TED4; 128 pagine PDF. Sommario e pagine elettriche pertinenti consultate; testo estratto interamente, schemi non tutti verificati visivamente. |
| MAN-007 | [manutenzione.pdf](https://drive.google.com/file/d/0BzErIAgsdW3Cc091X3B6RGp2dTA/view) | 8 | scan_visual_partial: Libretto manutenzione, servizi e garanzia; copertina verificata visivamente. Scansione, pagine interne non trascritte. |
| MAN-008 | [specifiche olio motore.jpg](https://drive.google.com/file/d/10pqDJN_elk5Gu5jcOCrxxI5LMvZ9n8Q8/view) | non determinato | image_unreviewed: Immagine; contenuto non ancora verificato. Non ricavare specifiche olio dal solo nome. |
| MAN-009 | [Manuale C3 HDI (1).pdf](https://drive.google.com/file/d/10kDxyXBypli180TqqUMwk2MAk-NEYR6X/view) | 128 | text_indexed: Duplicato byte per byte del Manuale tecnico C3 HDI.pdf, verificato SHA-256. |
| MAN-010 | [R2009-155-00-indice.pdf](https://drive.google.com/file/d/1c9XCR2Z3N-H6nb80iVahTTN-T9vwqvfg/view) | 2 | text_indexed: Sommario RTA n.155; 2 pagine lette, con rinvii alle pagine stampate del manuale. |
| MAN-011 | [R2009-155-01-dati motore.pdf](https://drive.google.com/file/d/1cyWHqkCvPqriW47bIxi2SqeQ8xXD0F2t/view) | 37 | text_indexed: Motori DV4TD e DV4TED4; PDF 1-37 = stampate 9-45. Gestione motore DV4TD a PDF 11 / stampata 19; non confondere schemi DV4TED4 delle pagine successive. |
| MAN-012 | [R2009-155-02-frizione.pdf](https://drive.google.com/file/d/1gzXeryEUrgwZ_qnCNiTlWPrgx56t-12y/view) | 3 | text_indexed: Frizione, dati e procedure; PDF 1-3 = stampate 46-48. Testo estratto; revisione tecnica mirata da eseguire prima dell uso. |
| MAN-013 | [R2009-155-03-cambio.pdf](https://drive.google.com/file/d/15Hfx28Odv2dWNhNbNgzVOsF6kKkMbRs8/view) | 10 | text_indexed: Cambi MA e BE; PDF 1-10 = stampate 49-58. Non implica che entrambe le varianti siano presenti sulla vettura. |
| MAN-014 | [R2009-155-04-riscaldamento clima.pdf](https://drive.google.com/file/d/1KhU1frOtKQIjWhCQCJcfZhR55RLdc044/view) | 11 | text_indexed: Riscaldamento e climatizzazione; PDF 1-11 = stampate 112-122. Testo estratto; schemi da esaminare visivamente quando servono. |
| MAN-015 | [R2009-155-05-trasmissione.pdf](https://drive.google.com/file/d/1vMB_RMW89SEOK6Vjk-y1fQ7Ha0J6darZ/view) | 3 | text_indexed: Trasmissione; PDF 1-3 = stampate 59-61. Testo estratto. |
| MAN-016 | [R2009-155-06-sterzo.pdf](https://drive.google.com/file/d/1mHKKs3s8QPtw5B35WjKqiDxVqtxwURAg/view) | 6 | text_indexed: Servosterzo e connessioni; PDF 1-6 = stampate 62-67. Non usare i pin del servosterzo per il quadro strumenti. |
| MAN-017 | [R2009-155-10-equipaggiamento elettrico.pdf](https://drive.google.com/file/d/1dFN9QO0U2vlWHbHNCzJEiErAcawD01Q7/view) | 15 | text_indexed: Capitolo elettrico, PDF 1-15 = stampate 90-104. Testo estratto completo; PDF 2 controllata anche come immagine: fusibili e diagnosi. PDF 3 descrive BSI e VAN DATA/DATAB. |
| MAN-018 | [R2009-155-12-carrozzeria.pdf](https://drive.google.com/file/d/1zFXeC5qsZ8vVLfB4JHNnAqV5o9lNiswR/view) | 8 | text_indexed: Carrozzeria; PDF 1-8 = stampate 123-130. Testo estratto. |
| MAN-019 | [R2009-155-14_recovered.pdf](https://drive.google.com/file/d/10jLHrR2-FQtRKGfc6_1eH0oSnwx6KOQI/view) | 1 | text_indexed: Unica pagina recuperata: stampata 105, plancia-airbag. Non sostituisce l intero capitolo; consultare il manuale completo. |
| MAN-020 | [R2009-155-14.pdf](https://drive.google.com/file/d/1cPH5Pzr8NmL0DaPET5KlnWAJ0EgZTUGe/view) | non determinato | damaged: PDF danneggiato: pypdf segnala Invalid object in /Pages e PDFium non lo apre. Non trattarlo come consultato. |
| MAN-021 | [R2009-155-99.pdf](https://drive.google.com/file/d/1lBoyuSPVRznkUYe38axkhS0P3-EwKPsa/view) | 4 | text_indexed: Presentazione, identificazione e manutenzione introduttiva; 4 pagine. Testo estratto. |

## Ricerca e riproducibilita

- [Catalogo strutturato](catalogo.json): ID stabili, stato, fonte e SHA-256 degli originali tecnici.
- [Indice per argomenti](indice-argomenti.json): corrispondenze per parola chiave e pagine PDF;
  possono essere falsi positivi o varianti non applicabili. Non contiene il testo integrale.
- Generatore: `tools/index_vehicle_manuals.py`, Python con `pypdf`, nessun servizio a pagamento.

Rigenerazione dalla radice, dopo aver recuperato gli originali autorizzati in
`.tools/manuali-c3/<drive_id>.pdf`:

```powershell
python tools/index_vehicle_manuals.py --cache .tools/manuali-c3
```

Il generatore verifica SHA-256 e numero pagine, scarta solo per la lettura gli
eventuali byte precedenti a `%PDF`, conservando l'originale invariato. Il prefisso
anomalo esiste in alcuni PDF RTA: offset registrato nel catalogo. Esclude
scansioni senza testo, duplicato, documento personale e PDF danneggiato.
I documenti rimanenti scansionati richiedono consultazione visiva mirata/OCR;
non e dichiarata una lettura integrale di tutte le 21 fonti.
