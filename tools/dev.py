"""Ingresso portabile per setup, controlli e compilazione; non carica firmware."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = ROOT / '.tools/pio-venv'
LOGGER = ROOT / 'data-logger/firmware/logger'
HOST_TEST = LOGGER / 'host-tests/test_logic.cpp'


def python_path():
    return ENVIRONMENT / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def run(*args, env=None):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, env=env, check=True)


def cpp_compiler(environ=None, which=shutil.which):
    """Compilatore C++ del PC: CXX se impostato, altrimenti g++, clang++ o c++."""
    env = os.environ if environ is None else environ
    if env.get('CXX'):
        return env['CXX']
    for name in ('g++', 'clang++', 'c++'):
        if which(name):
            return name
    return None


def run_host_tests(required=False):
    """Test della logica firmware sul PC (D-023); non sostituiscono la build ESP32."""
    compiler = cpp_compiler()
    if not compiler:
        message = 'Test C++ host non eseguiti: nessun compilatore C++ trovato (la CI li esegue).'
        if required:
            raise SystemExit(message)
        print(message, flush=True)
        return
    output = ROOT / '.tools/host-tests' / ('test_logic.exe' if os.name == 'nt' else 'test_logic')
    output.parent.mkdir(parents=True, exist_ok=True)
    run(compiler, '-std=gnu++14', '-Wall', '-Wextra', '-Werror', '-O1',
        '-I', LOGGER / 'include', HOST_TEST, '-o', output)
    run(output)


def run_lint():
    """Analisi statica cppcheck dei sorgenti logger (D-023)."""
    cppcheck = shutil.which('cppcheck')
    if not cppcheck:
        raise SystemExit('cppcheck non trovato: installarlo (gratuito, open source) o affidarsi alla CI.')
    common = [cppcheck, '--std=c++14', '--language=c++', '--enable=warning,performance,portability',
              '--inline-suppr', '--error-exitcode=1', '--quiet',
              '--suppress=missingIncludeSystem', '--suppress=missingInclude',
              '--suppress=unmatchedSuppression', '-I', LOGGER / 'include']
    for profile in (['-DLOGGER_ENABLE_KWP=0', '-DLOGGER_ENABLE_VAN=0'],
                    ['-DLOGGER_ENABLE_KWP=1', '-DLOGGER_ENABLE_VAN=1']):
        run(*common, *profile, LOGGER / 'src', HOST_TEST)


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
    parser.add_argument('action', choices=('setup', 'check', 'build', 'lint', 'paths'))
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
        run_host_tests(required=bool(os.environ.get('CI')))
    elif args.action == 'lint':
        run_lint()
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
