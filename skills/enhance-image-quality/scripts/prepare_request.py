#!/usr/bin/env python3
"""Assemble one image-edit request from observed source properties."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


OBSERVATION_KEYS = (
    "edge_character", "interior_shading", "eye_details", "face_tones",
    "other_colors", "frame_and_identity", "local_improvement",
)
HAIR_KEYS = ("base_and_existing_colors", "preserve_details", "accent_plan")
STRATEGIES = ("preserve-colors", "harmonize-hair")
CYRILLIC = re.compile(r"[\u0400-\u052f]")
PLACEHOLDER = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
UNFILLED_VALUE = re.compile(r"\{\{|\}\}|\[[^\]\n]+\]|<(?:insert|observed|specific|chosen|describe|todo|placeholder)[^>]*>", re.IGNORECASE)
NOT_VISIBLE_TEXT = "Not visible in the source; keep this region hidden and do not invent its details."


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_digest(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def require_keys(value, keys, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    missing = sorted(set(keys) - value.keys())
    extra = sorted(value.keys() - set(keys))
    if missing or extra:
        raise ValueError(f"{label}: missing keys {missing}; unexpected keys {extra}")


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty English string")
    text = value.strip()
    if CYRILLIC.search(text):
        raise ValueError(f"{label} contains Cyrillic; write prompt observations in English")
    if UNFILLED_VALUE.search(text):
        raise ValueError(f"{label} contains an unfilled template placeholder")
    return text


def load_card(path, strategy):
    raw = path.read_bytes()
    card = json.loads(raw)
    require_keys(card, ("source_image", "observations", "hair"), "card")
    if not isinstance(card["source_image"], str) or not card["source_image"].strip():
        raise ValueError("source_image must name the real source image")
    source = Path(card["source_image"]).expanduser()
    if not source.is_absolute():
        source = path.parent / source
    source = source.resolve()
    if not source.is_file():
        raise ValueError(f"source_image does not exist: {source}")
    require_keys(card["observations"], OBSERVATION_KEYS, "observations")
    require_keys(card["hair"], HAIR_KEYS, "hair")
    observations = {key: require_text(card["observations"][key], f"observations.{key}") for key in OBSERVATION_KEYS}
    hair = {key: require_text(card["hair"][key], f"hair.{key}") for key in HAIR_KEYS}
    for key, value in observations.items():
        if value == "NOT_VISIBLE" and key not in ("eye_details", "face_tones"):
            raise ValueError(f"observations.{key}: NOT_VISIBLE is supported only for eyes and face")
        if value == "NOT_REQUESTED":
            raise ValueError(f"observations.{key}: describe the visible source or use an allowed visibility marker")
    for key in ("base_and_existing_colors", "preserve_details"):
        if hair[key] in ("NOT_VISIBLE", "NOT_REQUESTED"):
            raise ValueError(f"hair.{key}: describe the visible hair or resolve the scope before editing")
    if strategy == "harmonize-hair" and hair["accent_plan"] in ("NOT_REQUESTED", "NOT_VISIBLE"):
        raise ValueError("harmonize-hair requires an actual accent_plan with source shades and placement")
    common = {"observations": observations, "hair": {key: hair[key] for key in ("base_and_existing_colors", "preserve_details")}}
    fields = {key: NOT_VISIBLE_TEXT if value == "NOT_VISIBLE" else value for key, value in observations.items()}
    fields.update({"hair_" + key: value for key, value in hair.items()})
    return raw, source, fields, common


def load_template(path):
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"^```text[ \t]*\n(.*?)^```[ \t]*$", text, flags=re.MULTILINE | re.DOTALL)
    if len(blocks) != 1:
        raise ValueError(f"{path}: expected exactly one fenced text prompt")
    template = blocks[0].strip()
    if CYRILLIC.search(template):
        raise ValueError(f"{path}: the prompt template must be English")
    return template


def shared_sections(template):
    if template.count("\nHAIR OPERATION\n") != 1 or template.count("\nSHARED PRESERVATION\n") != 1:
        raise ValueError("Each template must contain one HAIR OPERATION and one SHARED PRESERVATION section")
    before, hair_and_after = template.split("\nHAIR OPERATION\n", 1)
    hair_operation, after = hair_and_after.split("\nSHARED PRESERVATION\n", 1)
    if not hair_operation.strip():
        raise ValueError("HAIR OPERATION must not be empty")
    return before, after


def prepare(card_path, strategy, out_path, check_only):
    card_path = card_path.resolve()
    raw, source, fields, common = load_card(card_path, strategy)
    reference_dir = Path(__file__).resolve().parent.parent / "references"
    templates = {name: load_template(reference_dir / (name + ".md")) for name in STRATEGIES}
    if shared_sections(templates[STRATEGIES[0]]) != shared_sections(templates[STRATEGIES[1]]):
        raise ValueError("The strategy templates differ outside HAIR OPERATION; restore the shared sections")
    template = templates[strategy]
    expected = set(OBSERVATION_KEYS) | {"hair_base_and_existing_colors", "hair_preserve_details"}
    if strategy == "harmonize-hair":
        expected.add("hair_accent_plan")
    present = set(PLACEHOLDER.findall(template))
    if present != expected:
        raise ValueError(f"Template fields do not match the card: missing {sorted(expected-present)}, unexpected {sorted(present-expected)}")
    prompt = PLACEHOLDER.sub(lambda match: fields[match.group(1)], template) + "\n"
    if "{{" in prompt or "}}" in prompt or CYRILLIC.search(prompt):
        raise ValueError("The assembled prompt contains an unresolved placeholder or Cyrillic")
    out_path = out_path.resolve()
    if out_path in (card_path, source):
        raise ValueError("Output must not replace the source image or observation card")
    if not check_only:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with out_path.open("x", encoding="utf-8") as stream:
                stream.write(prompt)
        except FileExistsError as error:
            raise ValueError(f"Output already exists; choose a new filename: {out_path}") from error
    return {
        "status": "checked" if check_only else "written",
        "strategy": strategy,
        "card_path": str(card_path),
        "source_image": str(source),
        "prompt_path": str(out_path),
        "template_path": str(reference_dir / (strategy + ".md")),
        "source_sha256": digest(source.read_bytes()),
        "card_sha256": digest(raw),
        "common_observations_sha256": canonical_digest(common),
        "prompt_sha256": digest(prompt.encode("utf-8")),
        "prompt_chars": len(prompt),
        "prompt_words": len(prompt.split()),
        "token_usage": None,
        "validation_scope": "schema, English-form checks and exact transfer; visual accuracy not established",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path)
    parser.add_argument("--strategy", required=True, choices=STRATEGIES)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        receipt = prepare(args.card, args.strategy, args.out, args.check_only)
    except (OSError, ValueError, KeyError) as error:
        print(f"Request preparation failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
