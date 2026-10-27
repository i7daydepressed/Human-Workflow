"""Distribution/containment checks; these do not emulate a Claude host."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class ClaudePreview(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)

    def build(self, path, expected=0, root=ROOT):
        p = subprocess.run([sys.executable, '-B', str(ROOT/'tools/build_claude_preview.py'),
                            '--root', str(root), '--out', str(path)], cwd='/', capture_output=True, text=True)
        self.assertEqual(p.returncode, expected, p.stdout+p.stderr)

    def test_complete_payload_retains_source_resources_and_excludes_identity_claims(self):
        target = self.area/'plugin.zip'
        self.build(target)
        with ZipFile(target) as z:
            self.assertIsNone(z.testzip())
            m = json.loads(z.read('.claude-plugin/plugin.json'))
            self.assertEqual(m['name'], 'human-workflow')
            self.assertNotIn('author', m)
            self.assertEqual(m['version'], '0.0.7')
            self.assertEqual(m['displayName'], 'Human-workflow-v0.0.7')
            self.assertEqual(m['license'], 'Apache-2.0')
            self.assertEqual(m['license'], json.loads((ROOT / 'plugin.json').read_text())['license'])
            for name in ['LICENSE', 'docs/licensing.en.md', 'docs/licensing.ru.md']:
                self.assertEqual(z.read(name), (ROOT / name).read_bytes())
            self.assertNotIn('plugin.json', z.namelist())
            p = json.loads(z.read('PACKAGE-MANIFEST.json'))
            self.assertEqual(set(z.namelist()), set(p['files']) | {'PACKAGE-MANIFEST.json'})
            self.assertEqual(p['package']['name'], m['name'])
            self.assertEqual(p['package']['version'], m['version'])
            self.assertEqual(p['package']['display_name'], m['displayName'])
            self.assertEqual(p['base_package_version'], m['version'])
            self.assertEqual(p['license'], 'Apache-2.0')
            self.assertFalse(p['installed'])
            self.assertFalse(p['published'])
            for skill in ('human-step', 'md-word'):
                self.assertEqual(z.read('skills/' + skill + '/resources/LICENSE'), z.read('LICENSE'))
            self.assertFalse(any(Path(n).name in ('COMMERCIAL-LICENSE.md', 'COMMERCIAL-LICENSE.ru.md')
                                 for n in z.namelist()))
            self.assertEqual(len([n for n in z.namelist() if n.endswith('/SKILL.md')]), 2)
            for name, info in p['files'].items():
                self.assertEqual(z.read(name), (ROOT/info['source']).read_bytes())
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), info['sha256'])
            for name in z.namelist():
                self.assertFalse(name.startswith(('tests/','tools/','private/','originals/','bin/')))

    def test_mismatched_claude_manifest_is_rejected_before_output(self):
        source = self.area / 'source'
        for name in json.loads((ROOT / 'packaging/source-allowlist.json').read_text()):
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        path = source / '.claude-plugin/plugin.json'
        baseline = json.loads(path.read_text())
        for key, value in [('name', 'other-plugin'), ('version', '0.0.8'),
                           ('displayName', 'Other display'), ('license', 'MIT')]:
            with self.subTest(field=key):
                manifest = dict(baseline)
                manifest[key] = value
                path.write_text(json.dumps(manifest))
                output = self.area / (key + '.zip')
                self.build(output, expected=2, root=source)
                self.assertFalse(output.exists())

    def test_relocated_links_resolve_with_generated_runtime_copies(self):
        target = self.area/'plugin.zip'
        self.build(target)
        folder = self.area/'relocated'
        with ZipFile(target) as z:
            z.extractall(folder)
        for path in folder.rglob('*.md'):
            for value in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if re.match(r'^[a-z]+:', value) or value.startswith('#'):
                    continue
                resolved = (path.parent/value.split('#',1)[0]).resolve()
                self.assertTrue(resolved.is_relative_to(folder.resolve()))
                self.assertTrue(resolved.is_file(), str(path)+': '+value)
        for skill in ('human-step', 'md-word'):
            self.assertEqual((folder / 'skills' / skill / 'resources/shared/scripts/report_workspace.py').read_bytes(),
                             (folder / 'shared/scripts/report_workspace.py').read_bytes())
        self.assertEqual((folder/'shared/assets/word/base.docx').read_bytes(), (ROOT/'shared/assets/word/base.docx').read_bytes())

    def test_build_is_byte_reproducible(self):
        a,b = self.area/'a.zip',self.area/'b.zip'
        self.build(a); self.build(b)
        self.assertEqual(a.read_bytes(),b.read_bytes())

    def test_existing_or_redirected_output_is_preserved(self):
        target = self.area/'existing.zip'
        target.write_bytes(b'synthetic existing data')
        self.build(target, expected=2)
        self.assertEqual(target.read_bytes(),b'synthetic existing data')
        link = self.area/'redirect'
        link.symlink_to(self.area,target_is_directory=True)
        self.build(link/'new.zip',expected=2)
        self.assertFalse((self.area/'new.zip').exists())


if __name__ == '__main__':
    unittest.main()
