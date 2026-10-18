# Documentazione del data logger

Questa cartella raccoglierà requisiti, scelte hardware, collegamenti,
formato delle registrazioni e procedure di collaudo quando saranno definiti.

Per lo stato attuale vedere il [README del sottoprogetto](../README.md).

## Fonti da consultare prima di decidere

- [Inventario hardware](hardware-inventory.md), generato da [hardware.json](hardware.json).
- [Decisioni definitive nel README principale](../../README.md#decisioni-definitive).
- [Procedura di continuità e aggiornamento](procedura-progetto.md).

I moduli HW-CAN-MCP2515 e HW-CAN-VP230 sono già presenti dichiarati:
verificarli prima di proporre altri acquisti. RTC, MicroSD e OLED sono ordinati,
non ancora ricevuti. Il controllo `python tools/project_preflight.py` dalla radice
verifica coerenza dei registri e della proposta GPIO; 11 test di regressione
eseguiti con esito positivo. Non certifica l'hardware.

## Hardware verificato

- [Backup e identificazione ESP32 HW-394](../backups/esp32-hw394/README.md).

## Schema del sistema

- [Schema elettrico di collegamento Rev. D](schema-collegamenti.svg),
  con [anteprima PNG](schema-collegamenti.png): proposta pin per pin a livello
  di moduli, per alimentazione USB a banco. Fili continui collegano i terminali;
  un punto pieno indica una giunzione, gli incroci senza punto non sono collegati.
  Non è ancora validato sul materiale ricevuto.
  GPIO21/22 per I2C, GPIO18/23/19 per SPI, GPIO27 per CS MicroSD,
  GPIO32/33 per pulsanti opzionali sono scelte nuove di progetto, non
  collegamenti già realizzati o configurati nel firmware 0.1.0.
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
  esecutivo e non assegna pin. Solo ESP32 e diagnostica seriale sono verificati;
  moduli, rete BSI, parametri CAN OBD e protezioni richiedono ulteriori verifiche.

## Formato dei documenti visivi

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
