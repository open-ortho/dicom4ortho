"""Guard the repository paths that preserve the existing contributor workflow."""

import configparser
import csv
import subprocess
import unittest
from pathlib import Path


PYTHON_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PYTHON_ROOT.parent


class TestRepositoryLayout(unittest.TestCase):
    """Packaging and root entry points must continue to address the Python project."""

    def test_generator_writes_the_relocated_committed_lock(self):
        from tools.generate_codes import OUTPUT

        self.assertEqual(OUTPUT, PYTHON_ROOT / 'dicom4ortho' / '_generated_codes.py')
        self.assertTrue(OUTPUT.is_file())

    def test_existing_make_targets_remain_available(self):
        targets = (
            'help', 'default', 'lint', 'test', 'clean', 'build', 'fetch_resources',
            'update_codes', 'check_codes', 'deploy', 'all', 'install-dev',
        )
        for target in targets:
            with self.subTest(target=target):
                result = subprocess.run(
                    ['make', '--dry-run', target],
                    cwd=REPOSITORY_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_make_recipes_keep_root_artifacts_and_relocated_test_paths(self):
        expected_commands = {
            'lint': '--errors-only python/dicom4ortho',
            'test': 'python3 -m unittest discover -s python/test -t python',
            'build': 'python3 -m build',
            'fetch_resources': 'python/dicom4ortho/resources/views.csv',
            'update_codes': 'python3 tools/generate_codes.py',
            'check_codes': 'python3 tools/generate_codes.py --check',
            'deploy': 'python3 -m twine upload --repository pypi dist/*',
        }
        for target, command in expected_commands.items():
            with self.subTest(target=target):
                result = subprocess.run(
                    ['make', '--dry-run', target],
                    cwd=REPOSITORY_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn(command, result.stdout)
                if target == 'test':
                    self.assertIn('python/test/docker-compose.yml', result.stdout)

    def test_version_bump_configuration_tracks_existing_files(self):
        configuration = configparser.ConfigParser(interpolation=None)
        configuration.read(REPOSITORY_ROOT / '.bumpversion.cfg')
        files = [
            section.removeprefix('bumpversion:file:')
            for section in configuration.sections()
            if section.startswith('bumpversion:file:')
        ]
        self.assertEqual(
            files, ['python/dicom4ortho/config.py', 'pyproject.toml', 'README.md'])
        for filename in files:
            self.assertTrue((REPOSITORY_ROOT / filename).is_file(), filename)

    def test_example_images_remain_relative_to_the_csv(self):
        example_directory = PYTHON_ROOT / 'examples'
        with (example_directory / 'input_from.csv').open(encoding='utf-8') as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), 3)
        for row in rows:
            with self.subTest(image_type=row['image_type']):
                self.assertTrue(
                    (example_directory / row['input_image_filename']).is_file())

    def test_root_packaging_is_the_single_metadata_entry_point(self):
        self.assertTrue((REPOSITORY_ROOT / 'pyproject.toml').is_file())
        self.assertFalse((PYTHON_ROOT / 'pyproject.toml').exists())
        self.assertTrue((REPOSITORY_ROOT / 'LICENSE').is_file())
        self.assertTrue((REPOSITORY_ROOT / 'tools' / 'generate_codes.py').is_file())

    def test_fixed_dicom_fixture_is_preserved(self):
        self.assertTrue((PYTHON_ROOT / 'test' / 'resources' / 'test.dcm').is_file())


if __name__ == '__main__':
    unittest.main()
