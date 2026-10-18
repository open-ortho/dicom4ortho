"""Exercise development-shell setup without installing packages or touching a real venv."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SETUP_SCRIPT = Path(__file__).resolve().parents[2] / 'tools' / 'setup-python-env.sh'


class TestDevelopmentEnvironment(unittest.TestCase):
    """A moved environment must fail clearly instead of activating the old checkout."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bin_directory = self.root / '.venv' / 'bin'
        self.bin_directory.mkdir(parents=True)
        self.log = self.root / 'interpreter-calls.txt'
        interpreter = self.bin_directory / 'python'
        interpreter.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$SETUP_CALL_LOG"\n'
            'exit "${SETUP_PIP_STATUS:-0}"\n', encoding='utf-8')
        interpreter.chmod(0o755)

    def _activate_from(self, directory: Path) -> None:
        (self.bin_directory / 'activate').write_text(
            f'export VIRTUAL_ENV="{directory}"\n'
            'export PATH="$VIRTUAL_ENV/bin:$PATH"\n'
            'hash -r 2>/dev/null\n', encoding='utf-8')

    def _run_setup(
        self, pip_status: int = 0, hashing_enabled: bool = True
    ) -> subprocess.CompletedProcess:
        environment = dict(os.environ)
        environment['SETUP_CALL_LOG'] = str(self.log)
        environment['SETUP_PIP_STATUS'] = str(pip_status)
        shell_flags = 'set -h; ' if hashing_enabled else 'set +h; '
        return subprocess.run(
            ['bash', '-c', shell_flags +
             'source "$1" && printf "ACTIVE=%s\\nFLAGS=%s\\n" "$VIRTUAL_ENV" "$-"',
             'setup-test', str(SETUP_SCRIPT)],
            cwd=self.root, env=environment, capture_output=True, text=True, check=False,
        )

    def test_moved_environment_is_preserved_and_rejected_before_install(self):
        self._activate_from(self.root / 'old-checkout' / '.venv')
        result = self._run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('another checkout path', result.stderr)
        self.assertIn('backup', result.stderr)
        self.assertFalse(self.log.exists())
        self.assertTrue((self.bin_directory / 'activate').is_file())

    def test_current_environment_installs_through_python_not_pip_script(self):
        self._activate_from(self.bin_directory.parent)
        (self.bin_directory / 'pip').write_text(
            '#!/missing/old-checkout/python\n', encoding='utf-8')
        result = self._run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text(encoding='utf-8'),
                         '-m pip install --quiet -e .[dev]\n')
        self.assertIn(f'ACTIVE={self.bin_directory.parent}', result.stdout)

    def test_dependency_install_failure_stops_before_activation(self):
        self._activate_from(self.bin_directory.parent)
        result = self._run_setup(pip_status=7)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('ACTIVE=', result.stdout)

    def test_activation_succeeds_with_nix_command_hashing_disabled(self):
        self._activate_from(self.bin_directory.parent)
        result = self._run_setup(hashing_enabled=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'ACTIVE={self.bin_directory.parent}', result.stdout)
        flags = next(line for line in result.stdout.splitlines() if line.startswith('FLAGS='))
        self.assertNotIn('h', flags.removeprefix('FLAGS='))
