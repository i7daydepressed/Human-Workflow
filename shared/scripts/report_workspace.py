#!/usr/bin/env python3
"""Local report workspace: init, checkpoint, audit. No cloud/network writes."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import uuid
from i18n import message

from safe_paths import destination as checked_destination, directory as checked_directory, external_path

SHARED = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as f:
        h = hashlib.sha256()
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
        return h.hexdigest()


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def initialize(root, title, mode='report', language='ru'):
    root = external_path(root, __file__)
    templates = SHARED / 'templates' / language
    files = {'project.md': (templates / f'project-{mode}.md').read_text(encoding='utf-8').replace('{{title}}', title)}
    folders = ['agent-logs']
    if mode == 'report':
        folders += ['sources', 'assets/cards', 'assets/code', 'assets/screenshots',
                    'checkpoints', 'word-examples', 'output', 'skill-feedback', 'word-conversion']
        for target, source in [('report.md', 'report.md'), ('assets/figure-index.md', 'figure-index.md'),
                               ('word-examples/catalog.md', 'layout-catalog.md')]:
            files[target] = (templates / source).read_text(encoding='utf-8').replace('{{title}}', title)
    # Preflight every target before writing; an existing symlink must not redirect init.
    for name in folders:
        checked_directory(root, name)
    for name in files:
        path = checked_destination(root, name)
        if path.exists() and not path.is_file():
            raise ValueError(f'Expected a regular file: {name}')
    root.mkdir(parents=True, exist_ok=True)
    for name in folders:
        checked_directory(root, name).mkdir(parents=True, exist_ok=True)
    created = []
    for name, content in files.items():
        path = checked_destination(root, name)
        if not path.exists():
            with path.open('x', encoding='utf-8') as f:
                f.write(content)
            created.append(name)
    emit({'root': str(root), 'mode': mode, 'language': language, 'created': created, 'cloud_synced': False})


def visible_lines(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None and line.strip():
            yield number, line.strip()


def image_paths(text):
    # Inline Markdown links. URL titles/spaces require <...>; reference links
    # are flagged for manual review by audit rather than silently resolved.
    pattern = r'!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+["\'][^\n]*?["\'])?\s*\)'
    return [m.group(1) or m.group(2) for m in re.finditer(pattern, text)]


def selected_report(root, name):
    candidate = root / name
    report = candidate.resolve()
    if not report.is_relative_to(root):
        raise ValueError('MD должен находиться внутри папки проекта')
    if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != root and root in p.parents):
        raise ValueError('MD не должен проходить через symlink')
    return report


def audit(root, name='report.md', language='ru'):
    report = selected_report(root, name)
    if not report.is_file():
        raise ValueError(f'{name} отсутствует')
    text = report.read_text(encoding='utf-8')
    lines = list(visible_lines(text))
    content = '\n'.join(line for _, line in lines)
    errors, warnings, images, captions = [], [], [], []
    heading_numbers = []
    for line_number, line in lines:
        match = re.match(r'^#{1,6}\s+(\d+(?:\.\d+)*)(?:\.)?\s+', line)
        if match:
            heading_numbers.append((line_number, tuple(map(int, match.group(1).split('.')))))
    seen = set()
    counters = {}
    for line_number, number in heading_numbers:
        if number in seen:
            errors.append(message(language, 'duplicate_heading', line=line_number, number=number))
        seen.add(number)
        parent = number[:-1]
        if parent and parent not in seen:
            warnings.append(message(language, 'parent_heading', line=line_number, number=number))
        expected = counters.get(parent, 0) + 1
        if number[-1] != expected:
            warnings.append(message(language, 'heading_order', line=line_number, number=number, expected=expected))
        counters[parent] = number[-1]
    pending = []
    caption_seen = False
    groups = []
    if not re.search(r'^#{1,6}\s+(?:Введение|Introduction)\s*$', content, re.MULTILINE | re.IGNORECASE):
        warnings.append(message(language, 'introduction'))
    for line_number, line in lines:
        paths = image_paths(line)
        if paths:
            if pending and caption_seen:
                errors.append(message(language, 'next_figure', line=line_number, first=pending[0]))
                pending = []
            pending.append(line_number)
            caption_seen = False
            for target in paths:
                parsed = urlsplit(target)
                images.append(target)
                if parsed.scheme or parsed.netloc:
                    warnings.append(message(language, 'external_image', line=line_number, target=target))
                    continue
                path = (report.parent / unquote(parsed.path)).resolve()
                if not path.is_relative_to(root):
                    errors.append(message(language, 'outside_image', line=line_number, target=target))
                elif not path.is_file():
                    errors.append(message(language, 'missing_image', line=line_number, target=target))
        elif re.match(r'^(?:Рисунок|Figure)\s+\d+\s*[–—-]', line, re.IGNORECASE):
            captions.append(int(re.match(r'^(?:Рисунок|Figure)\s+(\d+)', line, re.IGNORECASE).group(1)))
            if not pending or caption_seen:
                warnings.append(message(language, 'orphan_caption', line=line_number))
            else:
                groups.append({'caption': captions[-1], 'image_lines': pending.copy()})
            caption_seen = True
        elif pending:
            if not caption_seen and re.fullmatch(r'[а-бa-b][).]', line, flags=re.IGNORECASE):
                continue
            if line.startswith('#') or re.fullmatch(r'[-*_]{3,}', line):
                errors.append(message(language, 'new_block', line=line_number, first=pending[0]))
            elif not caption_seen:
                errors.append(message(language, 'missing_caption', first=pending[0]))
            pending = []
            caption_seen = False
    if pending:
        errors.append(message(language, 'end_explanation', first=pending[0]))
    if captions and captions != list(range(1, len(captions) + 1)):
        errors.append(message(language, 'caption_order', captions=captions))
    if len(groups) != len(captions):
        warnings.append(message(language, 'unmatched_caption'))
    if re.search(r'!\[[^\]]*\]\[', content):
        warnings.append(message(language, 'reference_images'))
    for token in ['TODO', 'TBD', '[заглушка]']:
        if token in content:
            warnings.append(message(language, 'placeholder', token=token))
    result = {'report': str(report), 'images': len(images), 'captions': len(captions), 'figure_groups': groups,
              'numbered_headings': len(heading_numbers), 'language': language, 'errors': errors, 'warnings': warnings}
    emit(result)
    return 1 if errors else 0


def checkpoint(root, label, name='report.md', confirmation=None, mode='report', includes=None):
    root = external_path(root, __file__)
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', label):
        raise ValueError('label: только буквы ASCII, цифры, _ и -; длина 1–64')
    report = selected_report(root, name) if mode == 'report' else None
    if report is not None and not report.is_file():
        raise ValueError(f'{name} отсутствует')
    proof = None
    if label in ['accepted', 'teacher-accepted']:
        if confirmation is None:
            raise ValueError('Для accepted/teacher-accepted нужен --confirmation с user, quote, status=user_confirmed')
        proof = json.loads(confirmation.read_text(encoding='utf-8'))
        if proof.get('status') != 'user_confirmed' or not proof.get('quote') or not proof.get('user'):
            raise ValueError('В подтверждении отсутствует пользователь, дословная цитата или статус')
    source_paths = ([report] if report is not None else []) + [
        root / 'project.md', root / 'assets', root / 'agent-logs', root / 'output',
        root / 'word-conversion', root / 'skill-feedback', root / 'checks']
    for relative in includes or []:
        requested = Path(relative)
        source = root / requested
        resolved = source.resolve()
        if requested.is_absolute() or not resolved.is_relative_to(root) or resolved == root or resolved.is_relative_to(root / 'checkpoints'):
            raise ValueError(f'--include: путь должен быть внутри проекта и вне checkpoints: {relative}')
        if not source.exists():
            raise ValueError(f'--include: отсутствует {relative}')
        if source.is_symlink() or any(parent.is_symlink() for parent in source.parents if parent != root and parent.is_relative_to(root)):
            raise ValueError(f'--include: symlink не поддерживается: {relative}')
        source = resolved
        if source not in source_paths:
            source_paths.append(source)
    # Удалить вложенные дубликаты: явный каталог уже включает свое содержимое
    source_paths = [p for p in source_paths if not any(p != q and q.is_dir() and p.is_relative_to(q) for q in source_paths)]
    if not any(p.is_file() or (p.is_dir() and any(x.is_file() for x in p.rglob('*'))) for p in source_paths):
        raise ValueError('Нет файлов состояния/материалов для снимка')
    for source in source_paths:
        if source.is_symlink() or (source.is_dir() and any(p.is_symlink() for p in source.rglob('*'))):
            raise ValueError(f'Снимок не копирует symlink: {source}')
    destination = checked_directory(root, 'checkpoints')
    destination.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    name = f'{stamp}-{label}'
    final = destination / name
    if final.exists():
        final = destination / f'{name}-{uuid.uuid4().hex[:8]}'
    checked_destination(root, final.relative_to(root))
    with tempfile.TemporaryDirectory(prefix='.building-', dir=destination) as tmp:
        staging = Path(tmp) / 'snapshot'
        staging.mkdir()
        for source in source_paths:
            destination_path = staging / source.relative_to(root)
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination_path)
            elif source.is_file():
                shutil.copy2(source, destination_path)
        hashes = {p.relative_to(staging).as_posix(): digest(p)
                  for p in sorted(staging.rglob('*')) if p.is_file()}
        manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'label': label,
                    'source_root': str(root), 'mode': mode, 'report': report.relative_to(root).as_posix() if report else None,
                    'acceptance_confirmation': proof, 'files_sha256': hashes, 'cloud_synced': False,
                    'included_paths': [p.relative_to(root).as_posix() for p in source_paths if p.exists()],
                    'scope': 'Selected local materials and explicit --include paths; external linked bytes are not automatically included'}
        (staging / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        staging.rename(final)
    emit({'checkpoint': str(final), 'files': len(hashes), 'cloud_synced': False})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('root', type=Path); p.add_argument('--title'); p.add_argument('--language', choices=['ru', 'en'], default='ru'); p.add_argument('--mode', choices=['report', 'accompany'], default='report')
    p = sub.add_parser('checkpoint'); p.add_argument('root', type=Path); p.add_argument('--label', default='draft'); p.add_argument('--report', default='report.md'); p.add_argument('--confirmation', type=Path); p.add_argument('--mode', choices=['report', 'accompany'], default='report'); p.add_argument('--include', action='append', default=[])
    p = sub.add_parser('audit'); p.add_argument('root', type=Path); p.add_argument('--report', default='report.md'); p.add_argument('--language', choices=['ru', 'en'], default='ru')
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    try:
        if args.command == 'init': initialize(root, args.title or ('Work' if args.language == 'en' else 'Работа'), args.mode, args.language)
        elif args.command == 'checkpoint': checkpoint(root, args.label, args.report, args.confirmation, args.mode, args.include)
        else: return audit(root, args.report, args.language)
    except (ValueError, OSError) as exc:
        emit({'error': str(exc)}); return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
