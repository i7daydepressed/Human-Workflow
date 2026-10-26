"""Portable payload checks, not host discovery or installation tests."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

SOURCE = Path(__file__).resolve().parents[1]


class PortablePlugin(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)

    def clone(self):
        root = self.area / 'source'
        for name in json.loads((SOURCE / 'packaging/source-allowlist.json').read_text()):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((SOURCE / name).read_bytes())
        return root

    def run_builder(self, root=SOURCE, name='plugin.zip', marketplace=None, expected=0):
        output = self.area / name
        command = [sys.executable, str(SOURCE / 'tools/build_plugin.py'), '--root', str(root), '--out', str(output)]
        if marketplace is not None:
            command += ['--marketplace-out', str(self.area / marketplace)]
        result = subprocess.run(command, cwd='/', capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return output

    def unpack(self):
        output = self.run_builder()
        root = self.area / 'relocated plugin'
        with ZipFile(output) as archive:
            archive.extractall(root)
        return root

    def helper(self, root, name, args, expected=0):
        result = subprocess.run([sys.executable, '-B', str(root / 'shared/scripts' / name), *map(str, args)],
                                cwd='/', capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_payload_allowlist_bytes_and_portable_identity(self):
        source = self.clone()
        (source / 'personal-profile.json').write_text('Synthetic excluded sentinel')
        output = self.run_builder(source)
        mapping = json.loads((source / 'packaging/plugin-files.json').read_text())
        with ZipFile(output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), set(mapping) | {'PACKAGE-MANIFEST.json'})
            manifest = json.loads(archive.read('plugin.json'))
            self.assertEqual(manifest['name'], 'workflow-tools-preview')
            self.assertEqual(manifest['version'], '0.0.0-i05')
            self.assertTrue(manifest['$schema'].endswith('/1.0.0/plugin.schema.json'))
            self.assertEqual(manifest['license'], 'PolyForm-Noncommercial-1.0.0 OR LicenseRef-Workflow-Tools-Commercial')
            for name in ['LICENSE', 'COMMERCIAL-LICENSE.md', 'COMMERCIAL-LICENSE.ru.md',
                         'docs/licensing.en.md', 'docs/licensing.ru.md']:
                self.assertEqual(archive.read(name), (source / name).read_bytes())
            for key in ['author', 'repository', 'mcpServers', 'skills']:
                self.assertNotIn(key, manifest)
            recorded = json.loads(archive.read('PACKAGE-MANIFEST.json'))
            self.assertFalse(recorded['host_installation_verified'])
            for target, origin in mapping.items():
                content = archive.read(target)
                self.assertEqual(content, (source / origin).read_bytes())
                self.assertEqual(hashlib.sha256(content).hexdigest(), recorded['files'][target]['sha256'])
            for name in archive.namelist():
                self.assertFalse(name.startswith(('tests/', 'tools/', 'packaging/', 'entrypoints/')))
            self.assertEqual(len([n for n in archive.namelist() if n.endswith('/SKILL.md')]), 2)
            self.assertEqual(len([n for n in archive.namelist() if n.endswith('/report_workspace.py')]), 1)

    def test_plugin_and_marketplace_are_reproducible(self):
        a = self.run_builder(name='a.zip', marketplace='ma.zip')
        b = self.run_builder(name='b.zip', marketplace='mb.zip')
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual((self.area / 'ma.zip').read_bytes(), (self.area / 'mb.zip').read_bytes())

    def test_marketplace_resolves_inside_its_root_to_identical_plugin(self):
        plugin = self.run_builder(marketplace='repo.zip')
        repo = self.area / 'repo'
        with ZipFile(self.area / 'repo.zip') as archive:
            archive.extractall(repo)
        catalog = json.loads((repo / '.agents/plugins/marketplace.json').read_text())
        self.assertEqual(len(catalog['plugins']), 1)
        entry = catalog['plugins'][0]
        path = entry['source']['path']
        self.assertTrue(path.startswith('./'))
        target = (repo / path).resolve()
        self.assertTrue(target.is_relative_to(repo.resolve()))
        self.assertEqual(json.loads((target / 'plugin.json').read_text())['name'], entry['name'])
        with ZipFile(plugin) as archive:
            for name in archive.namelist():
                self.assertEqual((target / name).read_bytes(), archive.read(name))

    def test_relocated_markdown_links_stay_in_complete_package(self):
        root = self.unpack()
        for path in root.rglob('*.md'):
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if re.match(r'^[a-z]+:', target) or target.startswith('#'):
                    continue
                value = (path.parent / target.split('#', 1)[0]).resolve()
                self.assertTrue(value.is_relative_to(root.resolve()), str(path) + ': ' + target)
                self.assertTrue(value.is_file(), str(path) + ': ' + target)
        data = json.loads((root / 'shared/examples/historical-candidates.json').read_text())
        self.assertEqual(data['representation_decision'], 'retain_both_narrative_and_json')
        self.assertFalse(data['runtime_input'])
        for case in data['cases']:
            for narrative in case['narratives'].values():
                self.assertTrue((root / narrative).is_file())

    def test_relocated_helpers_and_profile_survive_separate_update_staging(self):
        root = self.unpack()
        private = self.area / 'private-profile'
        task = self.area / 'task'
        self.helper(root, 'profile.py', ['init', private, '--instruction-language', 'en', '--output-language', 'ru'])
        before = (private / 'profile.json').read_bytes()
        self.helper(root, 'report_workspace.py', ['init', task, '--mode', 'accompany', '--language', 'ru'])
        self.assertEqual(sorted(p.name for p in task.iterdir()), ['agent-logs', 'project.md'])
        later = self.area / 'new package cache'
        shutil.copytree(root, later)
        self.helper(later, 'profile.py', ['init', private, '--instruction-language', 'ru'])
        self.helper(later, 'profile.py', ['validate', private])
        self.assertEqual(before, (private / 'profile.json').read_bytes())
        profile = json.loads(before)
        self.assertEqual(profile['instruction_language'], 'en')
        self.assertEqual(profile['word']['layout']['source'], 'unselected')
        self.assertEqual(profile['word']['cover']['source'], 'unselected')
        self.helper(later, 'profile.py', ['init', later / 'wrong-profile'], expected=2)
        self.assertFalse((later / 'wrong-profile').exists())
        for name in ['base.docx', 'cover.docx']:
            result = self.helper(later, 'docx_package.py', [later / 'shared/assets/word' / name, '--public-preset'])
            self.assertTrue(result['pass'])

    def test_mapping_cannot_import_unlisted_or_escape(self):
        root = self.clone()
        mapping = root / 'packaging/plugin-files.json'
        for value in [{'../leak': 'README.md'}, {'ok': 'private-profile.json'}, {'.': 'README.md'},
                      {'PACKAGE-MANIFEST.json': 'README.md'}]:
            mapping.write_text(json.dumps(value))
            output = self.run_builder(root, expected=2)
            self.assertFalse(output.exists())

    def test_mapped_symlink_and_source_output_rejected(self):
        root = self.clone()
        target = root / 'shared/templates/en/report.md'
        target.unlink()
        outside = self.area / 'outside'
        outside.write_text('Synthetic external sentinel')
        target.symlink_to(outside)
        self.assertFalse(self.run_builder(root, expected=2).exists())
        self.assertFalse(self.run_builder(name=str(SOURCE / 'unwanted-preview.zip'), expected=2).exists())

    def test_existing_destination_and_symlink_destination_preserved(self):
        output = self.area / 'existing.zip'
        output.write_bytes(b'synthetic user content')
        self.run_builder(name='existing.zip', expected=2)
        self.assertEqual(output.read_bytes(), b'synthetic user content')
        redirect = self.area / 'redirect'
        redirect.symlink_to(self.area, target_is_directory=True)
        self.assertFalse(self.run_builder(name='redirect/new.zip', expected=2).exists())
        self.assertFalse(self.run_builder(name='same.zip', marketplace='same.zip', expected=2).exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
