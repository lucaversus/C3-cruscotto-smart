"""Ingresso portabile per setup, controlli e compilazione; non carica firmware."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = ROOT / '.tools/pio-venv'


def python_path():
    return ENVIRONMENT / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def run(*args, env=None):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, env=env, check=True)


def build_environment(root=ROOT, windows=os.name == 'nt', environ=None):
    env = dict(os.environ if environ is None else environ)
    default_core = (Path.home() / 'Documents/Codex/pio-c3' if windows
                    else root / '.tools/pio-core')
    env.setdefault('PLATFORMIO_CORE_DIR', str(default_core))
    if windows:
        key = hashlib.sha256(str(root.resolve()).lower().encode('utf-8')).hexdigest()[:12]
        env.setdefault('PLATFORMIO_WORKSPACE_DIR',
                       str(Path(env['PLATFORMIO_CORE_DIR']) / 'workspaces' / key))
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('setup', 'check', 'build', 'paths'))
    args = parser.parse_args()
    if args.action == 'setup':
        if sys.version_info < (3, 10):
            parser.error('Serve Python >= 3.10; versione verificata e raccomandata: 3.13.')
        if not python_path().is_file():
            venv.EnvBuilder(with_pip=True).create(ENVIRONMENT)
        run(python_path(), '-m', 'pip', 'install', '--disable-pip-version-check',
            '-r', ROOT / 'tools/requirements-dev.txt')
        print('Ambiente pronto:', python_path(), flush=True)
    elif args.action == 'check':
        # Questi controlli usano soltanto la libreria standard Python e Git.
        run(sys.executable, ROOT / 'tools/project_preflight.py')
        run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tools/tests', '-v')
        run('git', '-c', 'core.safecrlf=false', 'diff', '--check')
        run('git', '-c', 'core.safecrlf=false', 'diff', '--cached', '--check')
    elif args.action == 'paths':
        env = build_environment()
        print(json.dumps({key: value for key, value in env.items()
                          if key in ('PLATFORMIO_CORE_DIR', 'PLATFORMIO_WORKSPACE_DIR')}))
    else:
        if not python_path().is_file():
            parser.error('Ambiente assente. Eseguire prima: python tools/dev.py setup')
        env = build_environment()
        run(python_path(), '-m', 'platformio', 'run', '--project-dir',
            ROOT / 'data-logger/firmware/logger', '-e', 'esp32-hw394-logger',
            '-e', 'esp32-hw394-vehicle', env=env)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
