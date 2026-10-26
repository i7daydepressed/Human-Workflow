#!/usr/bin/env python3
"""Build a Claude preview from the same allowlisted source; never install or publish."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from build_source import ROOT, allowed_files
from build_plugin import payload, encoded, output_path, save_new, zip_bytes


def claude_payload(root):
    source = allowed_files(root)
    files, identity = payload(root)
    provenance = json.loads(files.pop('PACKAGE-MANIFEST.json'))['files']
    removed = ['plugin.json', 'skills/human-step/agents/openai.yaml', 'skills/md-word/agents/openai.yaml']
    for name in removed:
        del files[name]
        del provenance[name]
    replacements = {
        '.claude-plugin/plugin.json': '.claude-plugin/plugin.json',
        'README.md': 'packaging/claude-readme.en.md',
        'README.ru.md': 'packaging/claude-readme.ru.md',
        'docs/claude-preview.en.md': 'docs/claude-preview.en.md',
        'docs/claude-preview.ru.md': 'docs/claude-preview.ru.md',
    }
    for target, origin in replacements.items():
        files[target] = source[origin]
        provenance[target] = {'source': origin, 'sha256': hashlib.sha256(files[target]).hexdigest()}
    manifest = json.loads(files['.claude-plugin/plugin.json'])
    if (set(manifest) != {'name', 'displayName', 'version', 'description', 'license'}
            or manifest['name'] != identity or manifest['version'] != '0.0.0-i05'
            or manifest['license'] != json.loads(source['plugin.json'])['license']
            or not all(isinstance(v, str) and v for v in manifest.values())):
        raise ValueError('Expected the recorded temporary Claude preview identity')
    files['PACKAGE-MANIFEST.json'] = encoded({
        'kind': 'claude_plugin_preview', 'stage': 'I06', 'base_package_version': '0.0.0-i05',
        'claude_host_validation': 'not run', 'installed': False, 'published': False,
        'public_identity': 'undecided', 'license': manifest['license'],
        'commercial_sales_open': False, 'files': provenance})
    return files


def build(root, output):
    root = root.expanduser().resolve()
    target = output_path(output, root)
    files = claude_payload(root)
    result = save_new(target, zip_bytes(files))
    result.update(kind='claude_plugin_preview', files=len(files), installed=False, published=False)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    try:
        print(json.dumps(build(args.root, args.out), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
