# C3-cruscotto-smart

Cruscotto digitale custom per Citroën C3 Phase 1, 1.4 HDi, motore DV4TD / 8HZ.

## Sottoprogetti e ordine di lavoro

Il repository ospita due attività collegate:

1. **[Data logger](data-logger/README.md)**: primo progetto da sviluppare,
   con una scheda da installare nell'auto per registrare dati. Finalità
   dettagliata, segnali e hardware saranno definiti nei prossimi passi.
2. **Cruscotto digitale**: progetto successivo, descritto nelle sezioni seguenti.

Il data logger è un sottoprogetto nello stesso repository e condivide la sua
cronologia Git; non è un repository separato né un submodule.

## Obiettivo e sviluppo previsto

Dashboard ad alto contrasto, leggibile di giorno e di notte, su display da 5″
800×480 con ESP32-S3 e interfaccia LVGL. Lo sviluppo previsto usa PlatformIO e
C++, con un simulatore PC basato su SDL per provare la UI prima del flash.

La logica della dashboard dovrà ricevere gli stessi parametri da sorgenti
intercambiabili: dati simulati, modalità demo e ingressi reali. Sono previsti
filtri software (media mobile/EMA), soglie di allarme e test a banco con
potenziometri e generatori di segnali. I 60 FPS sono un obiettivo da misurare
sull'hardware, non una prestazione già verificata.

## Hardware: osservazioni preliminari

La scheda scelta è un modulo integrato RCmall ESP32 + display da 5″, ancora in
attesa di diagnosi diretta. La foto del venditore mostra un modulo indicato come
ESP32-S3-WROOM, USB-C, slot microSD, pulsanti BOOT/RESET, connettori di espansione
e un connettore di alimentazione. La sigla del PCB sembra ESP32-8048S050:
identificazione e revisione restano da confermare.

Il display da 5″ è previsto come RGB 800×480; pin, temporizzazioni, memoria e
controller touch non sono ancora verificati. La foto annotata descrive la
disposizione dei componenti, ma non sostituisce uno schema elettrico.

La documentazione della variante da 1,9″ riporta:

| Caratteristica | Dato dichiarato per la sola variante 1,9″ |
| --- | --- |
| Scheda | ESP32-1732S019 |
| Display | ST7789, 170×320 pixel |
| Collegamento | SPI, con segnali CS/SCK/DC |
| Memoria | Sigla ESP32-S3-R8N16: 8 MB PSRAM e 16 MB flash dichiarati |

Questi dati non sono trasferibili automaticamente alla variante da 5″.
L'affermazione del venditore secondo cui cambia soltanto la dimensione non è
sufficiente per scegliere driver o assegnare GPIO: SPI e RGB richiedono
configurazioni diverse.

La descrizione commerciale generale contiene incongruenze: cita Bluetooth
Classic BR/EDR e 520 KB di SRAM, mentre ESP32-S3 supporta Bluetooth LE e dispone
di 512 KB di SRAM interna. Non viene quindi usata come riferimento definitivo
per la configurazione.

Un framebuffer 800×480 RGB565 occupa 750 KiB; due occupano circa 1,46 MiB,
oltre alla memoria dell'applicazione. Quantità, tipo e funzionamento della
PSRAM della scheda da 5″ dovranno essere verificati.

## Diagnosi all'arrivo della scheda

1. Fotografare e leggere le sigle di PCB e modulo ESP32, inclusa la revisione.
2. Recuperare lo schema, la tabella dei pin e l'esempio Arduino/LVGL specifico
   per la variante da 5″ dal venditore.
3. Identificare il chip e verificare flash e PSRAM con strumenti diagnostici
   e un firmware minimo, senza sovrascrivere alla cieca il firmware di fabbrica.
4. Confermare i GPIO del display RGB, le temporizzazioni, il controllo della
   retroilluminazione e il controller touch con i relativi collegamenti.
5. Verificare alimentazione e ingressi utilizzabili; i segnali automobilistici
   e i 12 V richiedono circuiti di alimentazione/protezione e adattamento,
   prima di raggiungere la scheda o i suoi GPIO.
6. Provare prima il display con l'esempio del produttore, poi configurare
   PlatformIO/LVGL e misurare fluidità, memoria e stabilità in modalità demo.

## Stato del repository

Il repository contiene per ora la documentazione del progetto. Non sono ancora
presenti firmware, configurazione PlatformIO, simulatore o test eseguibili.
Le versioni delle dipendenze e la configurazione hardware verranno fissate
dopo l'identificazione della scheda. Il layout della UI e il simulatore PC
possono essere sviluppati prima dell'arrivo dell'hardware.
