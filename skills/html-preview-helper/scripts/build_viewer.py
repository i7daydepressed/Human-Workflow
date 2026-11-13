#!/usr/bin/env python3
"""Собрать HTML-обзор явно выбранных файлов без изменения исходников."""

import argparse
import base64
import hashlib
import json
from datetime import datetime
from pathlib import Path


IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
MARKER_START = '<script type="application/json" id="ed-data">'


class RussianHelpFormatter(argparse.HelpFormatter):
    """Показать заголовок справки на языке черновика."""

    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix="Использование: ")


def build_snapshot(root, names, title):
    """Прочитать только перечисленные файлы внутри выбранной папки."""
    files = []
    seen = set()
    for name in names:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Нужен относительный путь внутри папки материалов: {name}")
        source = (root / relative).resolve(strict=True)
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f"Файл должен находиться внутри папки материалов: {name}")
        file_id = relative.as_posix()
        if file_id == "@guide":
            raise ValueError("Имя @guide зарезервировано для справки обозревателя")
        if file_id in seen:
            continue
        seen.add(file_id)
        raw = source.read_bytes()
        item = {
            "id": file_id,
            "group": "materials",
            "path": file_id,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "purpose": "Содержимое файла на момент сборки снимка.",
        }
        mime = IMAGE_TYPES.get(source.suffix.lower())
        if mime:
            item.update(
                type="image",
                preview=f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}",
            )
        else:
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"Нужен текст UTF-8 либо поддерживаемое изображение: {name}") from exc
            if "\x00" in text:
                raise ValueError(f"В текстовом файле есть нулевые байты: {name}")
            item.update(type="text", content=text)
        files.append(item)
    return {
        "title": title,
        "snapshot": datetime.now().astimezone().isoformat(timespec="seconds"),
        "groups": [{"id": "materials", "label": "Выбранные материалы"}],
        "files": files,
        "initial": files[0]["id"] if files else "@guide",
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, add_help=False, formatter_class=RussianHelpFormatter,
    )
    parser._positionals.title = "Позиционные аргументы"
    parser._optionals.title = "Параметры"
    parser.add_argument("-h", "--help", action="help", help="Показать справку и завершить работу")
    parser.add_argument("--root", required=True, type=Path, help="Папка выбранных материалов")
    parser.add_argument("--output", required=True, type=Path, help="Новый HTML-файл; существующий не перезаписывается")
    parser.add_argument("--title", default="Обзор файлов", help="Название обзора")
    parser.add_argument("files", nargs="+", help="Относительные пути файлов внутри --root")
    args = parser.parse_args()
    try:
        root = args.root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Путь --root должен указывать на папку")
        output = args.output.expanduser().absolute()
        if output.exists() or output.is_symlink():
            raise ValueError(f"Выходной файл уже существует: {output}")
        template_path = Path(__file__).resolve().parent.parent / "resources" / "file-viewer.html"
        template = template_path.read_text(encoding="utf-8")
        start = template.index(MARKER_START) + len(MARKER_START)
        end = template.index("</script>", start)
        snapshot = build_snapshot(root, args.files, args.title)
        # В HTML-парсере закрывающий тег иначе оборвёт блок JSON даже внутри строки.
        encoded = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        encoded = encoded.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        rendered = template[:start] + encoded + template[end:]
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as target:
            target.write(rendered)
        print(f"Обзор создан: {output}")
        print(f"Файлов: {len(snapshot['files'])}; размер HTML: {output.stat().st_size} байт")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Ошибка: {exc}\n")


if __name__ == "__main__":
    main()
