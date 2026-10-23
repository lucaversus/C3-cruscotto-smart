"""Prepara i file per aggiornare il firmware del Data Logger dalla MicroSD.

Uso: python tools/prepara-aggiornamento-sd.py [ambiente]   (predefinito: esp32-hw394-vehicle)
Compila da sé il solo ambiente richiesto (la cartella di compilazione è condivisa tra i
progetti e `dev.py build` la riusa per tutti). Crea .tools/aggiornamento-sd/update/ con
c3_logger.bin e c3_logger.sha256: copiare la cartella `update` nella radice della MicroSD
del logger, poi riaccendere. Il firmware verifica l'impronta prima di installare.
"""
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    env_name = sys.argv[1] if len(sys.argv) > 1 else 'esp32-hw394-vehicle'
    spec = importlib.util.spec_from_file_location('dev', ROOT / 'tools/dev.py')
    dev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dev)
    env = dev.build_environment()
    dev.run(dev.python_path(), '-m', 'platformio', 'run', '--project-dir', dev.LOGGER, '-e', env_name, env=env)
    base = Path(env['PLATFORMIO_WORKSPACE_DIR']) if 'PLATFORMIO_WORKSPACE_DIR' in env else dev.LOGGER / '.pio'
    source = base / 'build' / env_name / 'firmware.bin'
    if not source.is_file():
        raise SystemExit(f'firmware.bin di {env_name} non trovato in {source.parent}')
    out = ROOT / '.tools/aggiornamento-sd/update'
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'c3_logger.bin'
    shutil.copyfile(source, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (out / 'c3_logger.sha256').write_text(f'{digest}  c3_logger.bin\n', encoding='ascii', newline='\n')
    print(f'{out}\n  c3_logger.bin {target.stat().st_size} byte\n  sha256 {digest}')
    print('Copiare la cartella "update" nella radice della MicroSD del logger e riaccendere.')


if __name__ == '__main__':
    main()
