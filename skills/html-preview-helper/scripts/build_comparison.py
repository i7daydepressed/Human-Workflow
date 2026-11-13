#!/usr/bin/env python3
"""Собрать сравнение изображений и материалов без изменения исходников."""

import argparse
import base64
import binascii
import hashlib
import json
import math
import re
import struct
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote


MARKER = '<script type="application/json" id="comparison-data">'
DATA_IMAGE = re.compile(r"^data:(image/(?:png|jpeg|webp|gif));base64,([A-Za-z0-9+/=]+)$")
EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}


class RussianHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix="Использование: ")


class JsonBlock(HTMLParser):
    """Прочитать один блок данных, не исполняя HTML или JavaScript."""

    def __init__(self, block_id):
        super().__init__(convert_charrefs=False)
        self.block_id = block_id
        self.active = False
        self.count = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("id") == self.block_id:
            if attrs.get("type") != "application/json":
                raise ValueError("Блок данных должен иметь тип application/json")
            self.count += 1
            self.active = True

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False


def object_value(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"Ожидается объект: {label}")
    return value


def list_value(value, label):
    if not isinstance(value, list):
        raise ValueError(f"Ожидается список: {label}")
    return value


def string_value(value, label, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()) or "\x00" in value:
        raise ValueError(f"Нужна строка{' (может быть пустой)' if empty else ''}: {label}")
    return value


def positive_integer(value, label):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"Нужно положительное целое число: {label}")
    return value


def local_file(root, name):
    name = string_value(name, "относительный путь")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", name):
        raise ValueError(f"Нужен относительный путь внутри --root: {name}")
    resolved = (root / path).resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError(f"Файл должен находиться внутри --root: {name}")
    return resolved


def raster_info(raw):
    """Распознать формат и размеры по заголовку; пиксели не преобразуются."""
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24 and raw[12:16] == b"IHDR":
        width, height = struct.unpack(">II", raw[16:24])
        mime = "image/png"
    elif raw[:6] in (b"GIF87a", b"GIF89a") and len(raw) >= 10:
        width, height = struct.unpack("<HH", raw[6:10])
        mime = "image/gif"
    elif raw.startswith(b"\xff\xd8"):
        offset = 2
        width = height = None
        while offset < len(raw):
            if raw[offset] != 255:
                raise ValueError("Некорректный заголовок JPEG")
            while offset < len(raw) and raw[offset] == 255:
                offset += 1
            if offset >= len(raw):
                break
            marker = raw[offset]
            offset += 1
            if marker in (0xD9, 0xDA):
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD8:
                continue
            if offset + 2 > len(raw):
                break
            size = int.from_bytes(raw[offset:offset + 2], "big")
            if size < 2 or offset + size > len(raw):
                raise ValueError("Неполный заголовок JPEG")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                if size < 8:
                    raise ValueError("Некорректные размеры JPEG")
                height, width = struct.unpack(">HH", raw[offset + 3:offset + 7])
                break
            offset += size
        if width is None:
            raise ValueError("Размеры JPEG не найдены")
        mime = "image/jpeg"
    elif len(raw) >= 20 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        end = int.from_bytes(raw[4:8], "little") + 8
        if end > len(raw):
            raise ValueError("Неполный контейнер WEBP")
        offset = 12
        width = height = None
        while offset + 8 <= end:
            kind = raw[offset:offset + 4]
            size = int.from_bytes(raw[offset + 4:offset + 8], "little")
            if offset + 8 + size > end:
                raise ValueError("Неполный блок WEBP")
            data = raw[offset + 8:offset + 8 + size]
            if kind == b"VP8X" and len(data) >= 10:
                width = 1 + int.from_bytes(data[4:7], "little")
                height = 1 + int.from_bytes(data[7:10], "little")
            elif kind == b"VP8 " and len(data) >= 10 and data[3:6] == b"\x9d\x01\x2a":
                width = int.from_bytes(data[6:8], "little") & 16383
                height = int.from_bytes(data[8:10], "little") & 16383
            elif kind == b"VP8L" and len(data) >= 5 and data[0] == 47:
                packed = int.from_bytes(data[1:5], "little")
                width, height = (packed & 16383) + 1, ((packed >> 14) & 16383) + 1
            if width is not None:
                break
            offset += 8 + size + size % 2
        if width is None:
            raise ValueError("Размеры WEBP не найдены")
        mime = "image/webp"
    else:
        raise ValueError("Поддерживаются только PNG, JPEG, WEBP и GIF")
    positive_integer(width, "ширина изображения")
    positive_integer(height, "высота изображения")
    return mime, width, height


def image_bytes(src, root):
    src = string_value(src, "src изображения")
    match = DATA_IMAGE.fullmatch(src)
    if match:
        try:
            raw = base64.b64decode(match[2], validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("Некорректные данные Base64 изображения") from exc
        mime, width, height = raster_info(raw)
        if mime != match[1]:
            raise ValueError("Формат изображения не совпадает с типом data URI")
        return raw, mime, width, height
    if src.startswith("data:"):
        raise ValueError("Нужен data URI PNG/JPEG/WEBP/GIF в Base64")
    if root is None:
        raise ValueError("В импортируемом HTML изображения должны быть встроены как data URI")
    raw = local_file(root, src).read_bytes()
    mime, width, height = raster_info(raw)
    return raw, mime, width, height


def cbk_config(path):
    parser = JsonBlock("cbk06-data")
    parser.feed(path.read_text(encoding="utf-8"))
    if parser.count != 1:
        raise ValueError("Нужен ровно один блок cbk06-data")
    data = object_value(json.loads("".join(parser.parts)), "cbk06-data")
    source = object_value(data.get("source"), "source")
    config = {"title": "ЧБК06 · Сравнение изображений и материалов", "images": [], "owners": [], "documents": []}

    def add_image(image_id, label, image, owner=None, strategy=None):
        image = object_value(image, "изображение CBK")
        entry = {"id": image_id, "label": label, "src": image.get("preview"), "sourcePath": image.get("path"), "width": image.get("width"), "height": image.get("height"), "isPreview": True}
        if owner is not None:
            entry.update(ownerId=owner, strategy=strategy)
        config["images"].append(entry)

    def add_document(owner, kind, label, document, strategy=None):
        document = object_value(document, "документ CBK")
        entry = {"id": f"{owner}/document/{kind}" + (f"/{strategy}" if strategy else ""), "ownerId": owner, "kind": kind, "label": label, "text": document.get("text"), "sourcePath": document.get("path")}
        config["documents"].append(entry)

    add_image("source", "Исходник", source)
    strategies = {"preserve": "Сохранение цветов", "harmonize": "Согласование волос"}
    for participant in list_value(data.get("participants"), "participants"):
        participant = object_value(participant, "участник")
        owner = string_value(participant.get("id"), "id участника")
        label = string_value(participant.get("label"), "название участника")
        config["owners"].append({"id": owner, "label": label})
        for key, caption in [("log", "Журнал работы"), ("notes", "Текущее состояние")]:
            if key in participant:
                add_document(owner, key, caption, participant[key])
        for strategy, case in object_value(participant.get("cases"), "cases").items():
            strategy = string_value(strategy, "стратегия")
            case = object_value(case, "вариант CBK")
            caption = strategies.get(strategy, strategy)
            add_image(f"{owner}/{strategy}", f"{label} · {caption}", case.get("image"), owner, strategy)
            if "prompt" in case:
                add_document(owner, "prompt", f"Промпт · {caption}", case["prompt"], strategy)
    config.update(defaultLeft="source", defaultRight="root/preserve" if any(x["id"] == "root/preserve" for x in config["images"]) else config["images"][min(1, len(config["images"]) - 1)]["id"])
    if config["owners"]:
        config["defaultOwner"] = "root" if any(x["id"] == "root" for x in config["owners"]) else config["owners"][0]["id"]
    config["regions"] = [{"id": "full", "label": "Полный кадр", "box": [0, 0, 1, 1]}, {"id": "face", "label": "Лицо", "box": [.27, .13, .77, .46]}, {"id": "eyes", "label": "Глаза", "box": [.30, .18, .74, .29]}]
    return config


def prepare(config, root=None, title=None):
    config = object_value(config, "конфигурация")
    if root is not None:
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Папка материалов должна указывать на каталог")
    result = {"title": string_value(title if title is not None else config.get("title", "Сравнение изображений"), "title"), "snapshot": datetime.now().astimezone().isoformat(timespec="seconds"), "images": [], "owners": [], "documents": [], "regions": []}
    image_ids, owner_ids, document_ids, region_ids = set(), set(), set(), set()
    blobs = {}

    def unique(entry, ids, label):
        value = string_value(entry.get("id"), f"id {label}")
        if value in ids:
            raise ValueError(f"Повтор id {label}: {value}")
        ids.add(value)
        return value

    for owner in list_value(config.get("owners", []), "owners"):
        owner = object_value(owner, "участник")
        result["owners"].append({"id": unique(owner, owner_ids, "участника"), "label": string_value(owner.get("label"), "название участника")})
    for image in list_value(config.get("images", []), "images"):
        image = object_value(image, "изображение")
        image_id = unique(image, image_ids, "изображения")
        raw, mime, preview_width, preview_height = image_bytes(image.get("src"), root)
        if ("width" in image) != ("height" in image):
            raise ValueError("Оригинальные width и height задаются вместе")
        width = positive_integer(image.get("width", preview_width), "width")
        height = positive_integer(image.get("height", preview_height), "height")
        for key, actual in [("previewWidth", preview_width), ("previewHeight", preview_height)]:
            if key in image and positive_integer(image[key], key) != actual:
                raise ValueError(f"{key} не совпадает с размерами встроенного изображения")
        is_preview = image.get("isPreview", (width, height) != (preview_width, preview_height))
        if not isinstance(is_preview, bool) or (not is_preview and (width, height) != (preview_width, preview_height)):
            raise ValueError("isPreview противоречит размерам изображения")
        entry = {"id": image_id, "label": string_value(image.get("label"), "название изображения"), "src": f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}", "sourcePath": string_value(image.get("sourcePath", image.get("src") if not image.get("src", "").startswith("data:") else ""), "sourcePath", empty=True), "width": width, "height": height, "previewWidth": preview_width, "previewHeight": preview_height, "isPreview": is_preview}
        if "ownerId" in image:
            owner = string_value(image["ownerId"], "ownerId изображения")
            if owner not in owner_ids:
                raise ValueError("ownerId изображения отсутствует в owners")
            entry["ownerId"] = owner
        if "strategy" in image:
            entry["strategy"] = string_value(image["strategy"], "strategy")
        result["images"].append(entry)
        blobs[image_id] = (raw, mime)
    for document in list_value(config.get("documents", []), "documents"):
        document = object_value(document, "документ")
        document_id = unique(document, document_ids, "документа")
        owner = string_value(document.get("ownerId"), "ownerId документа")
        if owner not in owner_ids:
            raise ValueError("ownerId документа отсутствует в owners")
        if ("text" in document) == ("file" in document):
            raise ValueError("Документ должен содержать ровно одно поле text или file")
        if "file" in document:
            if root is None:
                raise ValueError("Для чтения файла документа требуется --root")
            text = local_file(root, document["file"]).read_bytes().decode("utf-8")
        else:
            text = document["text"]
        entry = {"id": document_id, "label": string_value(document.get("label"), "название документа"), "ownerId": owner, "kind": string_value(document.get("kind"), "kind документа"), "text": string_value(text, "text документа", empty=True), "sourcePath": string_value(document.get("sourcePath", document.get("file", "")), "sourcePath документа", empty=True)}
        if "strategy" in document:
            entry["strategy"] = string_value(document["strategy"], "strategy документа")
        result["documents"].append(entry)
    for region in list_value(config.get("regions", []), "regions"):
        region = object_value(region, "область")
        region_id = unique(region, region_ids, "области")
        box = region.get("box")
        if not isinstance(box, list) or len(box) != 4 or any(not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) for x in box) or not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1):
            raise ValueError("box области должен задавать прямоугольник [x0,y0,x1,y1] внутри 0…1")
        result["regions"].append({"id": region_id, "label": string_value(region.get("label"), "название области"), "box": box})
    for key, ids in [("defaultLeft", image_ids), ("defaultRight", image_ids), ("defaultOwner", owner_ids)]:
        if key in config:
            value = string_value(config[key], key)
            if value not in ids:
                raise ValueError(f"{key} ссылается на отсутствующий элемент")
            result[key] = value
    if result["images"]:
        result.setdefault("defaultLeft", result["images"][0]["id"])
        result.setdefault("defaultRight", result["images"][min(1, len(result["images"]) - 1)]["id"])
    if result["owners"]:
        result.setdefault("defaultOwner", result["owners"][0]["id"])
    return result, blobs


def render(template, data):
    if template.count(MARKER) != 1:
        raise ValueError("В оболочке нужен ровно один блок comparison-data")
    start = template.index(MARKER) + len(MARKER)
    end = template.index("</script>", start)
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template[:start] + encoded + template[end:]


def write_result(output, data, blobs, assets=False):
    if output.exists() or output.is_symlink():
        raise ValueError(f"Выходной файл уже существует: {output}")
    asset_dir = output.parent / (output.stem + "_assets")
    if assets and any(char in asset_dir.name for char in ":\\"):
        raise ValueError("Для упаковки --assets имя выходного файла не должно содержать двоеточие или обратную косую черту")
    if assets and (asset_dir.exists() or asset_dir.is_symlink()):
        raise ValueError(f"Папка ресурсов уже существует: {asset_dir}")
    template = (Path(__file__).resolve().parent.parent / "resources/image-compare.html").read_text(encoding="utf-8")
    data = dict(data)
    data["images"] = [dict(image) for image in data["images"]]
    created = []
    made_folder = made_output = False
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        if assets:
            asset_dir.mkdir()
            made_folder = True
            for image in data["images"]:
                raw, mime = blobs[image["id"]]
                name = hashlib.sha256(raw).hexdigest() + EXTENSIONS[mime]
                target = asset_dir / name
                if target not in created:
                    with target.open("xb") as stream:
                        created.append(target)
                        stream.write(raw)
                image["src"] = quote(asset_dir.name + "/" + name, safe="/")
        html = render(template, data)
        with output.open("x", encoding="utf-8") as target:
            made_output = True
            target.write(html)
    except Exception:
        if made_output:
            output.unlink(missing_ok=True)
        for path in created:
            path.unlink(missing_ok=True)
        if made_folder:
            try:
                asset_dir.rmdir()
            except OSError:
                pass
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False, formatter_class=RussianHelpFormatter)
    parser._optionals.title = "Параметры"
    parser.add_argument("-h", "--help", action="help", help="Показать справку и завершить работу")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--from-cbk", type=Path, metavar="HTML", help="Прочитать данные cbk06-data из предоставленного HTML")
    source.add_argument("--config", type=Path, metavar="JSON", help="Прочитать общую конфигурацию сравнения")
    parser.add_argument("--root", type=Path, metavar="ПАПКА", help="Разрешённая папка материалов для --config")
    parser.add_argument("--output", type=Path, required=True, metavar="HTML", help="Новый выходной HTML; существующий не перезаписывается")
    parser.add_argument("--title", metavar="НАЗВАНИЕ", help="Название сравнения")
    parser.add_argument("--assets", action="store_true", help="Сохранить изображения рядом в папке <имя HTML>_assets")
    args = parser.parse_args()
    try:
        if args.config:
            if args.root is None:
                raise ValueError("Для --config требуется --root")
            root = args.root.expanduser().resolve(strict=True)
            if not root.is_dir():
                raise ValueError("--root должен указывать на папку")
            config = json.loads(args.config.expanduser().read_text(encoding="utf-8"))
        else:
            if args.root is not None:
                raise ValueError("--root используется только вместе с --config")
            root = None
            config = cbk_config(args.from_cbk.expanduser())
        data, blobs = prepare(config, root, args.title)
        output = args.output.expanduser().absolute()
        write_result(output, data, blobs, args.assets)
        print(f"Сравнение создано: {output}")
        print(f"Изображений: {len(data['images'])}; документов: {len(data['documents'])}; размер HTML: {output.stat().st_size} байт")
        if args.assets:
            print(f"Папка изображений: {output.parent / (output.stem + '_assets')}")
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        parser.exit(1, f"Ошибка: {exc}\n")


if __name__ == "__main__":
    main()
