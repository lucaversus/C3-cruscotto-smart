# Archivio fotografico hardware

| Cartiglio del dossier | Valore |
| --- | --- |
| Progetto | **Cruscotto C3+AI** |
| Sottoprogetto | **Data Logger** |
| Documento | C3AI-DL-PH-001 |
| Revisione | A — 18/10/2026 |
| Stato | Identificazione visiva; nessun collaudo elettrico dei moduli CAN |

Foto già fornite dall'utente, recuperate dai Download e archiviate qui per
consultarle anche nelle sessioni future. Consultare queste immagini e
[l'inventario](../hardware-inventory.md) prima di chiedere di ripetere una foto.
Non sostituire un modulo perché la sua documentazione non era stata archiviata.

Le immagini sono evidenze sorgenti: non sovrapporre disegni o cartigli ai dettagli
originali. Il cartiglio appartiene a questo dossier; gli schemi derivati conservano
il proprio cartiglio. Le copie pubblicate hanno EXIF/XMP/IPTC e commenti rimossi
**senza ricompressione dei pixel**. Gli originali integrali sono conservati soltanto
localmente nella cartella ignorata `.tools/hardware-photo-originals/`.
[manifest.json](manifest.json) conserva nomi sorgenti e SHA-256 di origine/archivio;
il preflight controlla presenza e integrità delle copie versionate.

## HW-CAN-MCP2515 — fronte e dettaglio

![Modulo MCP2515, fronte](mcp2515-fronte.jpg)

![Modulo MCP2515, dettaglio](mcp2515-dettaglio.jpg)

Si vedono il controller MCP2515, il quarzo con indicazione 8.000, la marcatura
VP230, i terminali H/L e le etichette SPI/alimentazione. Le sigle non certificano
la tensione interna o la compatibilità elettrica. J1 e J3 vanno identificati:
non presumere che siano terminazioni o selettori di alimentazione e non spostarli
alla cieca. Il retro non è presente in questo archivio.

## HW-CAN-VP230 — fronte e dettaglio

![Modulo CAN blu, fronte](can-vp230-fronte.jpg)

![Modulo CAN blu, dettaglio](can-vp230-dettaglio.jpg)

Visibili serigrafie 3.3V, GND, RX, TX, CANH/CANL e marcatura VP230. La resistenza
con codice 121 e serigrafia 120R indica un valore nominale, non ancora misurato.
Non confondere il connettore giallo CANH/CANL con un ponticello da cortocircuitare.

## HW-ESP32 e basetta a morsetti

![ESP32 HW-394 e basetta a morsetti](esp32-hw394-fronte.jpg)

Serigrafie HW-394 / ESP-32D e basetta di espansione a morsetti visibili.
La continuità tra morsetti e socket non è stata verificata. Usare nomi GPIO,
non posizioni dedotte dalle illustrazioni dello schema generale.

## Evidenze mancanti

Non sono archiviate foto del retro dei moduli né del modello/selettore del tester.
Chiedere una vista aggiuntiva solo se necessaria per una misura specifica;
non richiedere nuovamente le cinque immagini già disponibili qui.
