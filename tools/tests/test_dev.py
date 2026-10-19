"""Regressioni dei percorsi che devono funzionare anche in clone profondi."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('dev', Path(__file__).resolve().parents[1] / 'dev.py')
dev = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dev)


class EnvironmentTests(unittest.TestCase):
    def test_deep_windows_checkout_uses_short_external_workspace(self):
        root = Path('very-long-directory-' * 15) / 'checkout'
        env = dev.build_environment(root=root, windows=True, environ={})
        workspace = Path(env['PLATFORMIO_WORKSPACE_DIR'])
        self.assertEqual(workspace.parent, Path(env['PLATFORMIO_CORE_DIR']) / 'workspaces')
        self.assertEqual(len(workspace.name), 12)
        self.assertNotIn('very-long-directory', str(workspace))

    def test_independent_checkouts_do_not_share_workspace(self):
        first = dev.build_environment(root=Path('agent-a'), windows=True, environ={})
        second = dev.build_environment(root=Path('agent-b'), windows=True, environ={})
        self.assertNotEqual(first['PLATFORMIO_WORKSPACE_DIR'], second['PLATFORMIO_WORKSPACE_DIR'])

    def test_user_overrides_are_preserved_without_changing_source_environment(self):
        source = {'PLATFORMIO_CORE_DIR': '/custom/core', 'PLATFORMIO_WORKSPACE_DIR': '/custom/work'}
        expected = source.copy()
        self.assertEqual(dev.build_environment(windows=True, environ=source), expected)
        self.assertEqual(source, expected)

    def test_linux_has_no_unrequested_windows_workspace(self):
        root = Path('clone')
        env = dev.build_environment(root=root, windows=False, environ={})
        self.assertEqual(env['PLATFORMIO_CORE_DIR'], str(root / '.tools/pio-core'))
        self.assertNotIn('PLATFORMIO_WORKSPACE_DIR', env)


class CompilerTests(unittest.TestCase):
    def test_cxx_variable_has_priority(self):
        self.assertEqual(dev.cpp_compiler(environ={'CXX': 'my-c++'}, which=lambda name: None), 'my-c++')

    def test_first_available_compiler_is_chosen(self):
        found = {'clang++'}
        self.assertEqual(dev.cpp_compiler(environ={}, which=lambda name: name if name in found else None), 'clang++')

    def test_missing_compiler_is_reported_as_none(self):
        self.assertIsNone(dev.cpp_compiler(environ={}, which=lambda name: None))
