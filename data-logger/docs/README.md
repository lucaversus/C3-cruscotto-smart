# Documentazione del data logger

Questa cartella raccoglie inventario, collegamenti, protocolli e prove reali.
Per preparare un altro PC o agente seguire [CONTRIBUTING.md](../../CONTRIBUTING.md).

Per lo stato attuale vedere il [README del sottoprogetto](../README.md).

## Fonti da consultare prima di decidere

- [Inventario hardware](hardware-inventory.md), generato da [hardware.json](hardware.json).
- [Foto hardware archiviate](hardware-photos/README.md), con nomi stabili e SHA-256.
- [Registro verifiche MCP2515](collaudo-mcp2515.md), con risultati distinti dalle prove ancora da fare.
- [Registro moduli e avvio logger](verifiche-moduli.md): SD/RTC, caricamento e stato osservato.
- [Biblioteca tecnica del veicolo](../../docs/manuali/indice.md): riferimenti e limiti delle fonti.
- [Decisioni definitive nel README principale](../../README.md#decisioni-definitive).
- [Procedura di continuità e aggiornamento](procedura-progetto.md).

Per disponibilita e consegna dei moduli fa fede l'inventario, non le note storiche
dei disegni. RTC, lettore MicroSD e OLED sono ricevuti e fotografati; il lettore
SD resta da collegare dopo saldatura dei pin. I due moduli CAN sono gia presenti:
non proporre acquisti sostitutivi senza consultarne le verifiche aperte.
Il profilo banco logger 0.3.0 e stato caricato e avviato; esiti e limiti sono nel
registro moduli. Compilazione o raggiungibilita I2C non equivalgono a collaudo completo.

`python tools/dev.py check` controlla inventario, impronte delle foto, GPIO e
test di regressione. `python tools/dev.py build` compila entrambi i profili.
La suite si trova in `tools/tests`; non duplicare qui un conteggio destinato a cambiare.
I controlli software non certificano l'hardware.

## Hardware verificato

- [Backup e identificazione ESP32 HW-394](../backups/esp32-hw394/README.md).

## Schema del sistema

- **Collegamenti correnti per firmware 0.3.x:** [EL-003 rev. B](collegamenti-banco-030.md),
  con [SVG](collegamenti-banco-030.svg) e [PNG](collegamenti-banco-030.png).
  Banco USB: SD, RTC, OLED, STOP GPIO32. GPIO33 inutilizzato; OBD/VAN scollegati.
  Mappa GPIO proposta coerente con `hardware.json` e `config.h`, non validazione fisica.
- **Disegno storico, sostituito da EL-003:** [EL-001 rev. E](schema-collegamenti.svg),
  con [anteprima PNG](schema-collegamenti.png): proposta pin per pin a livello
  di moduli, per alimentazione USB a banco. Fili continui collegano i terminali;
  un punto pieno indica una giunzione, gli incroci senza punto non sono collegati.
  Non è ancora validato sul materiale ricevuto.
  GPIO21/22 per I2C, GPIO18/23/19 per SPI, GPIO27 per CS MicroSD,
  GPIO32/33 per pulsanti opzionali appartengono alla proposta iniziale;
  non usarli per dedurre il comportamento del firmware 0.3.0.
  I riferimenti MicroSD Create idea e RTC TECNOIOT provengono dalle
  raccomandazioni precedenti, confermate dall'utente come componenti ordinati;
  non da una verifica dei moduli consegnati. Il modello OLED resta da riscontrare.
  Collegamenti auto e alimentazione automotive restano da progettare.

Riferimenti tecnici per la proposta: [datasheet ESP32](https://documentation.espressif.com/esp32_datasheet_en.html)
e [DS3231](https://www.analog.com/en/products/ds3231.html).
Queste fonti descrivono i chip, non certificano serigrafie, alimentazione o
circuito batteria dei moduli commerciali. Prima di cablare verificare i moduli,
le pull-up I2C, la corrente del regolatore e i picchi MicroSD. Non applicare
5 V ai GPIO. La batteria RTC richiede verifica del circuito di ricarica.

- [Schema funzionale SVG modificabile](schema-sistema.svg): componenti previsti,
  interfacce e alimentazione. È preliminare: non è uno schema elettrico
  esecutivo e non assegna pin. Per stato hardware e versione sulla scheda consultare
  inventario e registro moduli; reti del veicolo e protezioni restano da verificare.

## Formato dei documenti visivi — norme applicate (D-024)

Dal 20/10/2026 tutti gli elaborati sono generati da `tools/iso_drawing.py`, che
applica in modo uniforme:

| Aspetto | Norma | Applicazione nel progetto |
| --- | --- | --- |
| Foglio e cornice | ISO 5457 | A3 orizzontale 420 × 297 mm; margine sinistro 20 mm, altri 10 mm; zone 1–8 / A–F; segni di centraggio |
| Cartiglio | ISO 7200 | 180 mm in basso a destra: proprietario, titolo, titolo supplementare, tipo e stato, codice, revisione, data, lingua, foglio, creato/approvato; tabella revisioni sopra |
| Simboli | IEC 60617 | Resistore rettangolare, condensatore (polarizzato con +), NPN con involucro, amplificatore/comparatore in forma rettangolare con uscita a collettore aperto, massa, morsetto, contatto NO a pulsante, unità di alimentazione separata |
| Impostazione schemi | IEC 61082-1 | Collegamenti solo orizzontali/verticali, giunzioni a T con punto, nessuna giunzione a quattro vie, incrocio senza punto = nessun contatto, riferimenti di potenziale per nome, recinzioni a tratto e punto, schemi a blocchi con frecce di flusso |
| Sigle | IEC 81346-1 | Prefisso "-" (-A1, -X1:1, -S1); lettere di classe d'uso corrente (R, C, Q, U) mantenute per coerenza con distinte e firmware |
| Scrittura e linee | ISO 3098, ISO 128 | Testo diritto 2–7 mm; linee 0,25 / 0,35 / 0,7 mm |

Gli SVG sono la fonte; i PNG sono anteprime a 200 dpi in 16 livelli di grigio,
ottenute con resvg (open source) e controllate visivamente. Rigenerare con:

```text
python data-logger/docs/tools/genera-kline-banco.py
python data-logger/docs/tools/genera-schemi.py
python tools/genera-collegamenti-banco.py
```

Elaborati correnti: KL-001 rev F (schema elettrico K-line), EL-003 rev B (schema
di collegamento banco, con tabella dei fili W1–W16), BL-001 rev D (schema a
blocchi aggiornato al 20/10/2026). EL-001 rev E è conservato come storico e
marcato SOSTITUITO: non usarlo per cablare. Il ridisegno non modifica reti,
valori o GPIO e non costituisce verifica del cablaggio.

## Formato dei documenti visivi — regole iniziali (D-009)

Tutti gli elaborati visivi prodotti per il progetto devono avere una cornice
e un cartiglio in basso a destra, coerente tra sorgente ed esportazioni:

- Progetto principale: **Cruscotto C3+AI**.
- Sottoprogetto per questi elaborati: **Data Logger**.
- Titolo, codice univoco del disegno, revisione, data e numero del foglio.
- Stato di validazione esplicito; una revisione grafica non certifica il cablaggio.

Rev. A: prima proposta per reti nominali. Rev. B: fili continui, cornice e
cartiglio; assegnazioni GPIO della proposta invariate. Anche lo schema a blocchi
è portato a Rev. B per l'aggiunta del cartiglio e l'aggiornamento dello stato.
SVG modificabili e PNG sono mantenuti insieme. Per gli schemi è disponibile
[il generatore Python](tools/genera-schemi.py); il rendering PNG usa Sharp.
Entrambe le anteprime Rev. B sono state esaminate visivamente.

Rev. C dello schema collegamenti: componenti illustrati in SVG originale
(PCB, modulo radio, USB, RTC, display, socket MicroSD e pulsanti), mantenendo
le stesse reti della proposta Rev. B. Cornice e cartiglio conservati.
La disposizione illustrata dei componenti e dei terminali non costituisce
un pinout fisico: usare i nomi dei segnali e verificare i moduli effettivi.
La batteria disegnata e il contenuto del display sono illustrativi, non
componenti verificati o funzioni già implementate. Nessuna risorsa esterna
o fotografia usata. Anteprima Rev. C renderizzata e controllata visivamente.

Rev. D collegamenti e Rev. C blocchi: note aggiornate con i moduli CAN già
presenti; nessun nuovo modulo ordinato o cablaggio automotive approvato.
