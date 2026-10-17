# Data logger per Citroën C3

Primo sottoprogetto da sviluppare prima del cruscotto digitale.
Prevede una scheda da installare nell'auto per acquisire e registrare dati.

## Stato

Struttura iniziale del progetto. La motivazione e i requisiti dettagliati
devono ancora essere raccolti; non sono presenti firmware o test eseguibili.
L'ESP32-S3 e il display previsti per il cruscotto non sono automaticamente
le scelte hardware del data logger.

## Decisioni da definire

- Scopo delle registrazioni e modalità d'uso in auto.
- Segnali da acquisire, relative interfacce e frequenze di campionamento.
- Scheda, alimentazione e collegamenti al veicolo.
- Supporto di memorizzazione, formato dei dati e riferimento temporale.
- Modalità di recupero delle registrazioni e analisi su PC.
- Prove a banco e criteri di verifica prima dell'installazione.

Hardware, protocolli, dipendenze e struttura del firmware verranno scelti
dopo aver definito questi requisiti.

## Organizzazione iniziale

- `docs/`: requisiti e documentazione tecnica del data logger.
- Questo README: stato del sottoprogetto e decisioni ancora aperte.

La documentazione generale del cruscotto rimane nel [README principale](../README.md).
