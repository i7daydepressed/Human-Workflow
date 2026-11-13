#!/usr/bin/env python3
"""Build an HTML view of explicitly selected files without modifying the sources."""

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


class EnglishHelpFormatter(argparse.HelpFormatter):
    """Show help headings in the edition language."""

    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix="Usage: ")


def build_snapshot(root, names, title):
    """Read only the listed files within the selected folder."""
    files = []
    seen = set()
    for name in names:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"A relative path within the materials folder is required: {name}")
        source = (root / relative).resolve(strict=True)
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f"The file must be within the materials folder: {name}")
        file_id = relative.as_posix()
        if file_id == "@guide":
            raise ValueError("The name @guide is reserved for the viewer guide")
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
            "purpose": "File contents at the time the snapshot was built.",
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
                raise ValueError(f"UTF-8 text or a supported image is required: {name}") from exc
            if "\x00" in text:
                raise ValueError(f"The text file contains null bytes: {name}")
            item.update(type="text", content=text)
        files.append(item)
    return {
        "title": title,
        "snapshot": datetime.now().astimezone().isoformat(timespec="seconds"),
        "groups": [{"id": "materials", "label": "Selected materials"}],
        "files": files,
        "initial": files[0]["id"] if files else "@guide",
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, add_help=False, formatter_class=EnglishHelpFormatter,
    )
    parser._positionals.title = "Positional arguments"
    parser._optionals.title = "Options"
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("--root", required=True, type=Path, help="Folder containing the selected materials")
    parser.add_argument("--output", required=True, type=Path, help="New HTML file; existing files are not overwritten")
    parser.add_argument("--title", default="File overview", help="Overview title")
    parser.add_argument("files", nargs="+", help="Relative file paths within --root")
    args = parser.parse_args()
    try:
        root = args.root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("--root must point to a folder")
        output = args.output.expanduser().absolute()
        if output.exists() or output.is_symlink():
            raise ValueError(f"The output file already exists: {output}")
        template_path = Path(__file__).resolve().parent.parent / "resources" / "file-viewer.html"
        template = template_path.read_text(encoding="utf-8")
        start = template.index(MARKER_START) + len(MARKER_START)
        end = template.index("</script>", start)
        snapshot = build_snapshot(root, args.files, args.title)
        # An HTML parser otherwise ends the JSON block at a closing tag, even inside a string.
        encoded = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        encoded = encoded.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        rendered = template[:start] + encoded + template[end:]
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as target:
            target.write(rendered)
        print(f"Overview created: {output}")
        print(f"Files: {len(snapshot['files'])}; HTML size: {output.stat().st_size} bytes")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
