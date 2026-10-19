"""Check the project sources before hardware/firmware decisions. Python stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = Path("data-logger/docs/hardware.json")
VIEW = Path("data-logger/docs/hardware-inventory.md")
REQUIRED_DOCS = (
    "AGENTS.md", "README.md", "data-logger/README.md",
    "data-logger/docs/procedura-progetto.md",
)
REQUIRED_IDS = {"HW-ESP32", "HW-CAN-MCP2515", "HW-CAN-VP230", "HW-SD-MODULE", "HW-RTC", "HW-OLED"}
STATUSES = {"present_verified", "present_declared", "ordered_pending", "not_confirmed", "candidate"}


def load_inventory(root):
    return json.loads((root / INVENTORY).read_text(encoding="utf-8-sig"))


def inventory_errors(data):
    errors = []
    if not isinstance(data, dict):
        return ["L'inventario deve essere un oggetto JSON."]
    for field in ("project", "subproject", "updated"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"Campo inventario mancante: {field}")
    definitions = data.get("status_definitions")
    if not isinstance(definitions, dict) or set(definitions) != STATUSES:
        errors.append("Definizioni degli stati inventario mancanti o non riconosciute.")
    items = data.get("items")
    if not isinstance(items, list):
        return errors + ["items deve essere una lista."]
    ids = set()
    for number, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"Voce {number}: atteso oggetto.")
            continue
        key = item.get("id")
        if not isinstance(key, str) or not re.fullmatch(r"HW-[A-Z0-9-]+", key):
            errors.append(f"Voce {number}: ID hardware non valido.")
        elif key in ids:
            errors.append(f"ID hardware duplicato: {key}")
        else:
            ids.add(key)
        for field in ("name", "scope", "evidence"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{key}: manca {field}.")
        if item.get("status") not in STATUSES:
            errors.append(f"{key}: stato hardware non riconosciuto.")
        if "quantity" not in item or (item["quantity"] is not None and
                (type(item["quantity"]) is not int or item["quantity"] < 1)):
            errors.append(f"{key}: quantità deve essere positiva o null se ignota.")
        for field in ("verified", "open_checks"):
            values = item.get(field)
            if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
                errors.append(f"{key}: {field} deve contenere testi non vuoti.")
        if item.get("status") == "present_verified" and not item.get("verified"):
            errors.append(f"{key}: verificato senza evidenze di verifica.")
        photos = item.get("photos", [])
        if not isinstance(photos, list) or any(not isinstance(p, str) or
                not p.startswith("data-logger/docs/hardware-photos/") or
                ".." in Path(p).parts for p in photos):
            errors.append(f"{key}: riferimenti foto non validi.")
    if REQUIRED_IDS - ids:
        errors.append("Hardware necessario scomparso dal registro: " + ", ".join(sorted(REQUIRED_IDS - ids)))
    proposal = data.get("wiring_proposal")
    if not isinstance(proposal, dict) or not isinstance(proposal.get("pins"), dict):
        errors.append("Proposta GPIO mancante.")
    else:
        pins = proposal["pins"]
        if set(pins) != {"kSda", "kScl", "kSck", "kMiso", "kMosi", "kSdCs", "kStopPin", "kKwpRx", "kKwpTx", "kVanRx", "kUnusedCanCs"}:
            errors.append("La proposta GPIO non contiene tutte le funzioni previste.")
        if any(type(pin) is not int or pin < 0 or pin > 39 for pin in pins.values()):
            errors.append("Valore GPIO non valido per ESP32 classico.")
        elif len(set(pins.values())) != len(pins):
            errors.append("GPIO duplicato nella proposta di cablaggio.")
        if any(type(pins.get(key)) is int and pins[key] >= 34 for key in ("kSda", "kScl", "kSck", "kMosi", "kSdCs", "kKwpTx", "kUnusedCanCs")):
            errors.append("GPIO di sola entrata assegnato a una uscita.")
        if proposal.get("status") != "proposed_not_hardware_validated":
            errors.append("Stato GPIO cambiato: aggiornare esplicitamente procedura e collaudo.")
        if not isinstance(proposal.get("firmware"), str):
            errors.append("Percorso config firmware mancante.")
    return errors


def render_inventory(data):
    lines = ["# Inventario hardware — Cruscotto C3+AI / Data Logger", "",
             f"Aggiornato: **{data['updated']}**. Vista generata da [hardware.json](hardware.json).",
             "Non modificare manualmente: usare `python tools/project_preflight.py --render-inventory`.", "",
             "Il materiale presente ma non collaudato va valutato prima di proporre acquisti sostitutivi.",
             "Le decisioni definitive restano nel [README principale](../../README.md#decisioni-definitive).", "",
             "## Stati", ""]
    for status, description in data["status_definitions"].items():
        lines.append(f"- `{status}`: {description}")
    lines += ["", "## Materiale e fonti", ""]
    for item in data["items"]:
        quantity = item["quantity"] if item["quantity"] is not None else "non confermata"
        lines += [f"### {item['id']} — {item['name']}", "",
                  f"**Stato:** `{item['status']}` · **Quantità:** {quantity} · **Ambito:** {item['scope']}", "",
                  f"**Fonte:** {item['evidence']}", "", "**Verifiche documentate:**", ""]
        photos = item.get("photos", [])
        if photos:
            lines[-2:] = ["**Foto archiviate:** " + ", ".join(
                f"[{Path(photo).name}]({photo.removeprefix('data-logger/docs/')})" for photo in photos),
                "", "**Verifiche documentate:**", ""]
        lines += ["- " + value for value in item["verified"]] or ["- Nessun collaudo elettrico del modulo documentato."]
        lines += ["", "**Da verificare:**", ""]
        lines += ["- " + value for value in item["open_checks"]] or ["- Nessuna verifica ulteriore registrata."]
        lines.append("")
    proposal = data["wiring_proposal"]
    lines += ["## Proposta di collegamento — non validata fisicamente", "", proposal["note"], "",
              "| Funzione firmware | GPIO proposto |", "| --- | --- |"]
    lines += [f"| `{key}` | {pin} |" for key, pin in proposal["pins"].items()]
    lines += ["", "L'illustrazione dei moduli non è la disposizione fisica dei pin.", ""]
    return "\n".join(lines)


def validate(root):
    errors = []
    for name in REQUIRED_DOCS:
        if not (root / name).is_file():
            errors.append(f"Documento obbligatorio assente: {name}")
    try:
        data = load_inventory(root)
    except (OSError, ValueError) as exc:
        return errors + [f"Inventario non leggibile: {exc}"], None
    errors += inventory_errors(data)
    if errors:
        return errors, data
    if not (root / VIEW).is_file() or (root / VIEW).read_text(encoding="utf-8-sig") != render_inventory(data):
        errors.append("Vista hardware-inventory.md non aggiornata: rigenerarla dall'inventario.")
    # Archived visual evidence must remain available and byte-identical.
    photo_root = root / "data-logger/docs/hardware-photos"
    try:
        manifest = json.loads((photo_root / "manifest.json").read_text(encoding="utf-8"))
        indexed = {}
        for entry in manifest["photos"]:
            name = entry["file"]
            if not isinstance(name, str) or Path(name).name != name or name in indexed:
                raise ValueError("Nome foto non valido o duplicato")
            indexed[name] = entry
            path = photo_root / name
            if not path.is_file():
                errors.append(f"Foto archiviata assente: {name}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                errors.append(f"SHA-256 foto differente dal manifest: {name}")
        for item in data["items"]:
            for photo in item.get("photos", []):
                if Path(photo).name not in indexed:
                    errors.append(f"Foto inventario non indicizzata: {photo}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Manifest foto non valido o assente: {exc}")
    readme = (root / "README.md").read_text(encoding="utf-8-sig")
    decisions = re.findall(r"^\| (D-\d{3}) \| (approvata|superata) \|", readme, re.MULTILINE)
    ids = [key for key, _ in decisions]
    if len(ids) != len(set(ids)):
        errors.append("ID decisione duplicato nel README.")
    missing = {f"D-{number:03}" for number in range(1, 13)} - set(ids)
    if missing:
        errors.append("Decisioni mancanti dal README: " + ", ".join(sorted(missing)))
    config = root / data["wiring_proposal"]["firmware"]
    if not config.is_file():
        errors.append("Config firmware collegata all'inventario assente.")
    else:
        code = config.read_text(encoding="utf-8-sig")
        for key, expected in data["wiring_proposal"]["pins"].items():
            matches = re.findall(rf"\b{re.escape(key)}\s*=\s*(\d+)\b", code)
            if matches != [str(expected)]:
                errors.append(f"GPIO incoerente {key}: registro={expected}, firmware={matches}")
    return errors, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-inventory", action="store_true", help="Rigenera solo la vista Markdown dal JSON.")
    args = parser.parse_args()
    if args.render_inventory:
        try:
            data = load_inventory(ROOT)
            errors = inventory_errors(data)
            if errors:
                raise ValueError("; ".join(errors))
            (ROOT / VIEW).write_text(render_inventory(data), encoding="utf-8")
        except (OSError, ValueError) as exc:
            print(f"ERRORE: {exc}")
            return 1
    errors, data = validate(ROOT)
    if errors:
        for error in errors:
            print("ERRORE: " + error)
        return 1
    print("OK: inventario, foto con SHA-256, vista Markdown, decisioni obbligatorie e GPIO coerenti.")
    for item in data["items"]:
        print(f"  {item['id']}: {item['status']} — {item['name']}")
    print("Leggere README + inventario + procedura prima di decidere; non è una verifica hardware.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
