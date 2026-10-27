"""Constrain local writes to an explicitly selected root; not a race-free sandbox."""
from pathlib import Path


def installation_root(module_file):
    resource_root = Path(module_file).resolve().parents[2]
    skill_root = resource_root.parent
    if (resource_root / 'resource-manifest.json').is_file() and (skill_root / 'SKILL.md').is_file():
        plugin_root = skill_root.parent.parent
        if skill_root.parent.name == 'skills' and ((plugin_root / 'plugin.json').is_file()
                or (plugin_root / '.claude-plugin/plugin.json').is_file()):
            return plugin_root
        return skill_root
    return resource_root


def destination(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ValueError('Destination must be a nonempty relative path without ..')
    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Destination must not traverse a symlink: {relative}')
        if index < len(relative.parts) - 1 and current.exists() and not current.is_dir():
            raise ValueError(f'Destination parent is not a directory: {relative}')
    if not current.resolve().is_relative_to(root):
        raise ValueError('Destination is outside the selected root')
    return current


def directory(root, relative):
    path = destination(root, relative)
    if path.exists() and not path.is_dir():
        raise ValueError(f'Destination is not a directory: {relative}')
    return path
