"""Exercise copied skill folders without their parent plugin checkout."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IsolatedSkills(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)

    def skill(self, name, parent=None):
        target = (parent or self.area) / name
        shutil.copytree(ROOT / 'skills' / name, target,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        return target

    def run_helper(self, skill, helper, *args, expected=0):
        environment = dict(os.environ)
        environment.pop('PYTHONPATH', None)
        result = subprocess.run([sys.executable, '-B',
                                 str(skill / 'resources/shared/scripts' / helper), *map(str, args)],
                                cwd=self.area, env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_all_local_links_remain_inside_an_isolated_skill(self):
        for name in ('human-step', 'md-word'):
            with self.subTest(skill=name):
                skill = self.skill(name)
                for path in skill.rglob('*.md'):
                    for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                        if re.match(r'^[a-z]+:', link) or link.startswith('#'):
                            continue
                        resolved = (path.parent / link.split('#', 1)[0]).resolve()
                        self.assertTrue(resolved.is_relative_to(skill), str(path) + ': ' + link)
                        self.assertTrue(resolved.is_file(), str(path) + ': ' + link)

    def test_helpers_use_an_external_task_and_preserve_existing_profile(self):
        for name in ('human-step', 'md-word'):
            with self.subTest(skill=name):
                skill = self.skill(name)
                private = self.area / (name + '-profile')
                self.run_helper(skill, 'profile.py', 'init', private, '--instruction-language', 'ru')
                before = (private / 'profile.json').read_bytes()
                self.run_helper(skill, 'profile.py', 'init', private, '--instruction-language', 'en')
                self.run_helper(skill, 'profile.py', 'validate', private)
                self.assertEqual(before, (private / 'profile.json').read_bytes())
                task = self.area / (name + '-task')
                self.run_helper(skill, 'report_workspace.py', 'init', task,
                                '--mode', 'accompany', '--language', 'en')
                self.assertEqual(sorted(p.name for p in task.iterdir()), ['agent-logs', 'project.md'])
                rejected = skill / 'private-profile'
                self.run_helper(skill, 'profile.py', 'init', rejected, expected=2)
                self.assertFalse(rejected.exists())

    def test_installed_bundle_rejects_profiles_anywhere_inside_plugin(self):
        plugin = self.area / 'installed-plugin'
        (plugin / 'skills').mkdir(parents=True)
        (plugin / 'plugin.json').write_text('{"name":"synthetic-plugin"}')
        skill = self.skill('md-word', plugin / 'skills')
        rejected = plugin / 'private-profile'
        self.run_helper(skill, 'profile.py', 'init', rejected, expected=2)
        self.assertFalse(rejected.exists())

    def test_word_resources_and_cover_guard_work_without_the_checkout(self):
        skill = self.skill('md-word')
        for name in ('base.docx', 'cover.docx'):
            result = self.run_helper(skill, 'docx_package.py',
                                     skill / 'resources/shared/assets/word' / name, '--public-preset')
            self.assertTrue(result['pass'])
        result = skill / 'unwanted.docx'
        self.run_helper(skill, 'word_cover.py', '--cover-source', 'builtin', '--out', result, expected=2)
        self.assertFalse(result.exists())

    def test_generated_bytes_have_one_canonical_origin(self):
        registry = json.loads((ROOT / 'packaging/skill-resources.json').read_text())
        for target, record in registry['files'].items():
            self.assertFalse('/resources/' in record['source'])
            data = (ROOT / record['source']).read_bytes()
            self.assertEqual((ROOT / target).read_bytes(), data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])

    def clone_source(self):
        source = self.area / 'source'
        for name in json.loads((ROOT / 'packaging/source-allowlist.json').read_text()):
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        return source

    def test_stale_resources_are_detected_without_mutation_then_regenerated(self):
        source = self.clone_source()
        canonical = source / 'locales/en/human-step/workflow.md'
        copied = source / 'skills/human-step/resources/locales/en/human-step/workflow.md'
        before = copied.read_bytes()
        canonical.write_bytes(canonical.read_bytes() + b'\nSynthetic source revision\n')
        command = [sys.executable, '-B', str(source / 'tools/sync_skill_resources.py')]
        check = subprocess.run([*command, '--check'], capture_output=True, text=True)
        self.assertEqual(check.returncode, 1, check.stdout + check.stderr)
        self.assertEqual(copied.read_bytes(), before)
        sync = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(sync.returncode, 0, sync.stdout + sync.stderr)
        self.assertEqual(copied.read_bytes(), canonical.read_bytes())
        check = subprocess.run([*command, '--check'], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_unknown_resource_files_are_preserved_and_reported(self):
        source = self.clone_source()
        unknown = source / 'skills/md-word/resources/user-note.txt'
        unknown.write_text('Synthetic user note')
        result = subprocess.run([sys.executable, '-B', str(source / 'tools/sync_skill_resources.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(unknown.read_text(), 'Synthetic user note')


if __name__ == '__main__':
    unittest.main()
