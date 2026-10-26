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

    def build(self, path, expected=0):
        p = subprocess.run([sys.executable, '-B', str(ROOT/'tools/build_claude_preview.py'), '--out', str(path)], cwd='/', capture_output=True, text=True)
        self.assertEqual(p.returncode, expected, p.stdout+p.stderr)

    def test_complete_payload_retains_source_resources_and_excludes_identity_claims(self):
        target = self.area/'plugin.zip'
        self.build(target)
        with ZipFile(target) as z:
            self.assertIsNone(z.testzip())
            m = json.loads(z.read('.claude-plugin/plugin.json'))
            self.assertEqual(m['name'], 'workflow-tools-preview')
            self.assertNotIn('author', m)
            self.assertEqual(m['license'], json.loads((ROOT / 'plugin.json').read_text())['license'])
            for name in ['LICENSE', 'COMMERCIAL-LICENSE.md', 'COMMERCIAL-LICENSE.ru.md',
                         'docs/licensing.en.md', 'docs/licensing.ru.md']:
                self.assertEqual(z.read(name), (ROOT / name).read_bytes())
            self.assertNotIn('plugin.json', z.namelist())
            p = json.loads(z.read('PACKAGE-MANIFEST.json'))
            self.assertEqual(set(z.namelist()), set(p['files']) | {'PACKAGE-MANIFEST.json'})
            self.assertEqual(len([n for n in z.namelist() if n.endswith('/SKILL.md')]), 2)
            for name, info in p['files'].items():
                self.assertEqual(z.read(name), (ROOT/info['source']).read_bytes())
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), info['sha256'])
            for name in z.namelist():
                self.assertFalse(name.startswith(('tests/','tools/','private/','originals/','bin/')))

    def test_relocated_links_resolve_with_one_shared_runtime(self):
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
        self.assertEqual(len(list(folder.rglob('report_workspace.py'))), 1)
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
