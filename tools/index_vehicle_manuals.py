"""Index local Drive PDF copies without publishing source text or personal data.

Requires pypdf. Example: python tools/index_vehicle_manuals.py --cache .tools/manuali-c3
"""
import argparse
import hashlib
import io
import json
import logging
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
    "BSI": r"\bBSI\b|centralina (?:abitacolo|di servizio)",
    "VAN": r"\bVAN\b|\bDATAB\b",
    "CAN": r"\bCAN\b",
    "K-line e diagnosi": r"linea\s*K\b|presa diagnosi|connettore diagnosi",
    "Quadro strumenti": r"quadro strumenti|quadro stumenti",
    "Alimentazione e batteria": r"batteria|alimentazion|dopo contatto",
    "Fusibili": r"fusibil",
    "Temperatura e raffreddamento": r"temperatura|raffreddamento",
    "Pressione e sovralimentazione": r"pressione|sovralimentazione",
    "Aria ed EGR": r"flussometro|portata.*aria|\bEGR\b|riciclaggio.*gas",
    "Motore DV4TD e 8HZ": r"\bDV4TD\b|\b8HZ\b",
    "Identificazione e OPR": r"identificazione|\bOPR\b|\bRPO\b",
    "Olio e manutenzione": r"olio|manutenzione|lubrificant",
    "Velocita e regime": r"velocit|regime|giri/min|contagiri",
}


def main():
    from pypdf import PdfReader

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    folder = ROOT / "docs/manuali"
    catalog = json.loads((folder / "catalogo.json").read_text(encoding="utf-8"))
    result = {"revision": 1, "date": catalog["date"],
              "page_numbering": "PDF, one-based; keyword candidates, not verified pinouts",
              "documents": []}
    for item in catalog["documents"]:
        if item["status"] != "text_indexed" or item.get("duplicate_of"):
            continue
        source = args.cache / (item["drive_id"] + ".pdf")
        content = source.read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError("Source hash mismatch: " + item["id"])
        offset = content.find(b"%PDF")
        if offset != item["pdf_offset"] or offset < 0:
            raise ValueError("Unexpected PDF header: " + item["id"])
        reader = PdfReader(io.BytesIO(content[offset:]), strict=False)
        if len(reader.pages) != item["page_count"]:
            raise ValueError("Page count mismatch: " + item["id"])
        pages = [page.extract_text() or "" for page in reader.pages]
        hits = {topic: [i + 1 for i, text in enumerate(pages)
                        if re.search(pattern, text, flags=re.IGNORECASE)]
                for topic, pattern in TOPICS.items()}
        result["documents"].append({"id": item["id"], "source_sha256": item["sha256"],
                                    "pdf_pages": len(pages),
                                    "topics": {k: v for k, v in hits.items() if v}})
    target = folder / "indice-argomenti.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {len(result['documents'])} distinct textual PDFs; scans and personal document excluded.")


if __name__ == "__main__":
    main()
