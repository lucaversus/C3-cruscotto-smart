"""Regression tests for the failure modes that caused project-state drift."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("preflight", ROOT / "tools/project_preflight.py")
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class ProjectPreflightTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        paths = list(preflight.REQUIRED_DOCS) + [str(preflight.INVENTORY), str(preflight.VIEW),
                "data-logger/firmware/logger/include/config.h"]
        for name in paths:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        shutil.copytree(ROOT / "data-logger/docs/hardware-photos",
                        self.root / "data-logger/docs/hardware-photos")

    def change_inventory(self, mutate, render=True):
        data = preflight.load_inventory(self.root)
        mutate(data)
        (self.root / preflight.INVENTORY).write_text(json.dumps(data), encoding="utf-8")
        if render and not preflight.inventory_errors(data):
            (self.root / preflight.VIEW).write_text(preflight.render_inventory(data), encoding="utf-8")

    def errors(self):
        return "\n".join(preflight.validate(self.root)[0])

    def test_current_project_passes(self):
        self.assertEqual("", self.errors())

    def test_can_module_cannot_disappear_silently(self):
        self.change_inventory(lambda d: d["items"].__setitem__(slice(None),
                              [i for i in d["items"] if i["id"] != "HW-CAN-VP230"]))
        self.assertIn("HW-CAN-VP230", self.errors())

    def test_duplicate_hardware_ids_are_rejected(self):
        self.change_inventory(lambda d: d["items"].append(d["items"][0].copy()))
        self.assertIn("duplicato", self.errors())

    def test_claimed_verification_needs_evidence(self):
        self.change_inventory(lambda d: d["items"][1].update(status="present_verified", verified=[]))
        self.assertIn("senza evidenze", self.errors())

    def test_changed_status_requires_updated_markdown(self):
        self.change_inventory(lambda d: d["items"][3].update(evidence=d["items"][3]["evidence"] + " nuova evidenza"), render=False)
        self.assertIn("non aggiornata", self.errors())

    def test_delivery_can_be_recorded_consistently(self):
        self.change_inventory(lambda d: d["items"][3].update(status="present_declared", evidence="Consegna confermata dall'utente."))
        self.assertEqual("", self.errors())

    def test_wrong_gpio_in_firmware_is_detected(self):
        path = self.root / "data-logger/firmware/logger/include/config.h"
        path.write_text(path.read_text(encoding="utf-8-sig").replace("kSdCs = 27", "kSdCs = 5"), encoding="utf-8")
        self.assertIn("GPIO incoerente kSdCs", self.errors())

    def test_output_cannot_use_input_only_gpio(self):
        self.change_inventory(lambda d: d["wiring_proposal"]["pins"].update(kKwpTx=35))
        self.assertIn("sola entrata", self.errors())

    def test_duplicate_capture_gpio_is_rejected(self):
        self.change_inventory(lambda d: d["wiring_proposal"]["pins"].update(kVanRx=16))
        self.assertIn("GPIO duplicato", self.errors())

    def test_missing_decision_is_detected(self):
        path = self.root / "README.md"
        path.write_text("\n".join(row for row in path.read_text(encoding="utf-8").splitlines()
                                  if not row.startswith("| D-006 |")), encoding="utf-8")
        self.assertIn("D-006", self.errors())

    def test_missing_mandatory_document_is_detected(self):
        (self.root / "AGENTS.md").unlink()
        self.assertIn("Documento obbligatorio assente", self.errors())

    def test_malformed_json_is_detected(self):
        (self.root / preflight.INVENTORY).write_text("{", encoding="utf-8")
        self.assertIn("non leggibile", self.errors())

    def test_unknown_is_not_a_fake_quantity(self):
        self.change_inventory(lambda d: d["items"][3].update(quantity=0))
        self.assertIn("quantità", self.errors())

    def test_missing_archived_photo_is_detected(self):
        (self.root / "data-logger/docs/hardware-photos/mcp2515-fronte.jpg").unlink()
        self.assertIn("Foto archiviata assente", self.errors())

    def test_changed_photo_bytes_are_detected(self):
        path = self.root / "data-logger/docs/hardware-photos/mcp2515-fronte.jpg"
        path.write_bytes(path.read_bytes() + b"modified")
        self.assertIn("SHA-256 foto differente", self.errors())


if __name__ == "__main__":
    unittest.main()
