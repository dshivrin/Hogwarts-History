#!/usr/bin/env python3
"""Validate canonical source YAML, compact indexes, and generated support files."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Iterable
import hashlib

import yaml

try:
    from scripts.source_files import discover_source_yaml
except ModuleNotFoundError:  # Direct script execution.
    from source_files import discover_source_yaml


ROOT = Path(__file__).resolve().parents[1]

BOOK_SOURCE_UNIT_REQUIRED = {
    "source_file",
    "book",
    "chapter",
    "chapter_start_pdf_page",
    "chapter_end_pdf_page",
    "processed_date",
}
EXTERNAL_SOURCE_UNIT_REQUIRED = {
    "source_kind",
    "source_id",
    "source_file",
    "title",
    "author",
    "source_site",
    "source_class",
    "authority",
    "publication_date",
    "original_url",
    "retrieval_url",
    "capture_completeness",
    "content_sha256",
    "processed_date",
    "processor_notes",
}
ENTRY_REQUIRED = {
    "id",
    "pdf_page",
    "text_anchor",
    "quote_excerpt_short",
    "source_note",
    "reference_type",
    "era_classification",
    "topic_tags",
    "candidate_part",
    "candidate_chapter",
    "candidate_section",
    "duplicate_check",
    "confidence",
    "limitations",
}
EXTERNAL_ENTRY_REQUIRED = {
    "source_file",
    "source_id",
    "source_url",
    "source_section",
    "printed_page",
    "extracted_text_lines",
    "nearby_context",
    "match_terms",
    "reason_for_placement",
    "relevance_to_hogwarts_a_history",
}
CONFIDENCE_VALUES = {"high", "medium", "low"}
BOOK_SOURCE_NAME_RE = re.compile(
    r"^book-(?:\d{2}|qtta|beedle|fb|cc)/chapter-\d{2}-[a-z0-9-]+\.yaml$"
)
EXTERNAL_SOURCE_NAME_RE = re.compile(
    r"^external/(?:official-rowling|official-editorial|interviews)/[a-z0-9-]+\.yaml$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def load_yaml(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def word_count(value: object) -> int:
    return len(re.findall(r"\b[\w'-]+\b", str(value or "")))


def schema_values(root: Path, heading: str) -> set[str]:
    path = root / "docs" / "instructions" / "schema-reference.md"
    if not path.exists():
        return set()
    values: set[str] = set()
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line.strip() == f"## {heading}"
            continue
        if not in_section:
            continue
        match = re.match(r"- `([^`]+)`", line.strip())
        if match:
            values.add(match.group(1))
    return values


def duplicate_targets(value: object) -> list[str]:
    if value in (None, "", False):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return [
        target.strip()
        for target in re.split(r"[;,]", str(value))
        if target.strip()
    ]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def snapshot_body_sha256(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("snapshot is missing YAML front matter")
    _, header, body = text.split("---\n", 2)
    metadata = yaml.safe_load(header) or {}
    if not isinstance(metadata, dict):
        raise ValueError("snapshot front matter must be a mapping")
    rendered = body.lstrip("\n")
    if "\n\n" not in rendered:
        raise ValueError("snapshot is missing the body after its title")
    source_body = rendered.split("\n\n", 1)[1].rstrip("\n")
    return metadata, hashlib.sha256(source_body.encode("utf-8")).hexdigest()


def validate_external_source_unit(
    root: Path,
    rel_path: str,
    source_unit: dict,
    entries: list,
) -> list[str]:
    errors: list[str] = []
    source_id = str(source_unit.get("source_id") or "")
    if not re.fullmatch(r"[A-Z]\d{2}", source_id):
        errors.append(f"{rel_path}: source_unit source_id must match A01-style form")
    if source_unit.get("capture_completeness") != "complete":
        errors.append(f"{rel_path}: source_unit capture_completeness must be 'complete'")
    if not source_unit.get("retrieval_url"):
        errors.append(f"{rel_path}: source_unit retrieval_url must be populated")

    expected_hash = str(source_unit.get("content_sha256") or "")
    if not SHA256_RE.fullmatch(expected_hash):
        errors.append(f"{rel_path}: source_unit content_sha256 must be 64 lowercase hex characters")

    source_file = str(source_unit.get("source_file") or "")
    snapshot_text = ""
    snapshot_path = root / source_file
    if not source_file or not snapshot_path.is_file():
        errors.append(f"{rel_path}: external snapshot does not exist: {source_file!r}")
    else:
        try:
            metadata, actual_hash = snapshot_body_sha256(snapshot_path)
            snapshot_text = snapshot_path.read_text(encoding="utf-8")
        except Exception as exc:
            errors.append(f"{rel_path}: invalid external snapshot: {exc}")
        else:
            if actual_hash != expected_hash:
                errors.append(f"{rel_path}: content_sha256 does not match snapshot body")
            if metadata.get("sha256") != actual_hash:
                errors.append(f"{rel_path}: snapshot sha256 does not match snapshot body")
            if metadata.get("id") != source_id:
                errors.append(f"{rel_path}: snapshot id does not match source_unit source_id")
            if metadata.get("capture_completeness") != source_unit.get(
                "capture_completeness"
            ):
                errors.append(
                    f"{rel_path}: snapshot capture_completeness does not match source_unit"
                )

    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue
        label = f"{rel_path}: entry {index}"
        missing = sorted(EXTERNAL_ENTRY_REQUIRED - set(entry))
        if missing:
            errors.append(f"{label}: missing {', '.join(missing)}")
        expected_id_prefix = f"ext-{source_id.lower()}-"
        if not re.fullmatch(rf"{re.escape(expected_id_prefix)}\d{{3}}", str(entry.get("id") or "")):
            errors.append(f"{label}: external id must match {expected_id_prefix}NNN")
        if entry.get("source_id") != source_id:
            errors.append(f"{label}: source_id must match source_unit source_id")
        if entry.get("source_file") != source_file:
            errors.append(f"{label}: source_file must match source_unit source_file")
        if not entry.get("source_url"):
            errors.append(f"{label}: source_url must be populated")
        for locator in ("pdf_page", "printed_page", "extracted_text_lines"):
            if entry.get(locator) is not None:
                errors.append(f"{label}: {locator} must be null for external evidence")
        anchor = entry.get("text_anchor")
        if not isinstance(anchor, dict) or not all(
            anchor.get(key)
            for key in ("start_phrase", "end_phrase", "local_occurrence_note")
        ):
            errors.append(f"{label}: text_anchor must contain start, end, and occurrence notes")
        elif snapshot_text:
            for key in ("start_phrase", "end_phrase"):
                if str(anchor[key]) not in snapshot_text:
                    errors.append(
                        f"{label}: text_anchor {key} does not occur in snapshot"
                    )
    return errors


def validate_source_files(
    root: Path,
    strict: bool,
    reference_types: set[str],
    era_classifications: set[str],
) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    duplicate_refs: list[tuple[Path, str, str]] = []

    for path in discover_source_yaml(root):
        rel_path = rel(path, root)
        source_name = path.relative_to(root / "sources").as_posix()
        is_external = source_name.startswith("external/")
        name_re = EXTERNAL_SOURCE_NAME_RE if is_external else BOOK_SOURCE_NAME_RE
        if not name_re.match(source_name):
            errors.append(
                f"{rel_path}: source YAML filename must be "
                "a supported book chapter or external evidence path"
            )
        try:
            data = load_yaml(path)
        except Exception as exc:
            errors.append(f"{rel_path}: YAML parse error: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{rel_path}: top-level YAML must be a mapping")
            continue

        source_unit = data.get("source_unit")
        entries = data.get("entries")
        if not isinstance(source_unit, dict):
            errors.append(f"{rel_path}: missing source_unit mapping")
            source_unit = {}
        else:
            required = EXTERNAL_SOURCE_UNIT_REQUIRED if is_external else BOOK_SOURCE_UNIT_REQUIRED
            missing = sorted(required - set(source_unit))
            if missing:
                errors.append(f"{rel_path}: source_unit missing {', '.join(missing)}")
        if not isinstance(entries, list):
            errors.append(f"{rel_path}: entries must be a list")
            continue

        if is_external:
            errors.extend(validate_external_source_unit(root, rel_path, source_unit, entries))

        for index, entry in enumerate(entries, start=1):
            label = f"{rel_path}: entry {index}"
            if not isinstance(entry, dict):
                errors.append(f"{label}: entry must be a mapping")
                continue
            entry_id = str(entry.get("id") or "")
            if not entry_id:
                errors.append(f"{label}: missing id")
            elif entry_id in seen_ids:
                errors.append(
                    f"{label}: duplicate id {entry_id} also in {rel(seen_ids[entry_id], root)}"
                )
            else:
                seen_ids[entry_id] = path

            missing = sorted(ENTRY_REQUIRED - set(entry))
            if missing:
                errors.append(f"{label}: missing {', '.join(missing)}")
            if reference_types and entry.get("reference_type") not in reference_types:
                errors.append(f"{label}: invalid reference_type {entry.get('reference_type')!r}")
            if era_classifications and entry.get("era_classification") not in era_classifications:
                errors.append(
                    f"{label}: invalid era_classification {entry.get('era_classification')!r}"
                )
            if entry.get("confidence") not in CONFIDENCE_VALUES:
                errors.append(f"{label}: invalid confidence {entry.get('confidence')!r}")
            if word_count(entry.get("quote_excerpt_short")) >= 25:
                errors.append(f"{label}: quote_excerpt_short must be under 25 words")

            duplicate_check = entry.get("duplicate_check")
            if not isinstance(duplicate_check, dict):
                errors.append(f"{label}: duplicate_check must be a mapping")
                duplicate_check = {}
            for target in duplicate_targets(duplicate_check.get("duplicate_of")):
                duplicate_refs.append((path, entry_id or f"entry-{index}", target))

            if strict:
                tags = entry.get("topic_tags")
                tag_count = len(tags) if isinstance(tags, list) else 0
                if tag_count < 3 or tag_count > 8:
                    errors.append(f"{label}: strict topic_tags count must be 3-8")
                if word_count(entry.get("source_note")) > 60:
                    errors.append(f"{label}: strict source_note must be 60 words or fewer")
                if duplicate_check.get("possible_duplicate") is True and not duplicate_targets(
                    duplicate_check.get("duplicate_of")
                ):
                    errors.append(
                        f"{label}: strict possible_duplicate true requires duplicate_of"
                    )

    for path, entry_id, target in duplicate_refs:
        if target not in seen_ids:
            errors.append(
                f"{rel(path, root)}: entry {entry_id} duplicate_of target {target!r} not found"
            )
    return errors


def validate_generated_files(root: Path) -> list[str]:
    errors: list[str] = []
    generated = root / "appendix" / "generated"
    if not generated.exists():
        return errors
    for path in sorted(generated.glob("*.md")):
        if not path.read_text(encoding="utf-8").startswith("# Generated File"):
            errors.append(f"{rel(path, root)}: generated appendix must start with # Generated File")
    return errors


def count_source_entries(root: Path) -> int:
    count = 0
    for path in discover_source_yaml(root):
        try:
            data = load_yaml(path)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        entries = data.get("entries") or []
        if isinstance(entries, list):
            count += len([entry for entry in entries if isinstance(entry, dict)])
    return count


def validate_book_seed(root: Path, source_entry_count: int) -> list[str]:
    errors: list[str] = []
    path = root / "book-seed" / "hogwarts-a-history-seed.md"
    if source_entry_count > 0 and not path.exists():
        return ["book-seed/hogwarts-a-history-seed.md: generated seed is missing"]
    if not path.exists():
        return errors

    text = path.read_text(encoding="utf-8")
    rel_path = rel(path, root)
    if not text.startswith("# Generated File"):
        errors.append(f"{rel_path}: generated seed must start with # Generated File")
    if "# Hogwarts: A History - Evidence-Backed Seed" not in text:
        errors.append(f"{rel_path}: missing evidence-backed seed heading")
    if source_entry_count > 0 and "## Part:" not in text:
        errors.append(f"{rel_path}: missing rendered part headings")
    for old_label in [
        "**Fact:**",
        "**Duplicate / corroboration:**",
        "possible_duplicate=false",
    ]:
        if old_label in text:
            errors.append(f"{rel_path}: old output label remains: {old_label}")

    appendix = root / "appendix" / "generated" / "explicit-hogwarts-a-history-references.md"
    if appendix.exists() and not appendix.read_text(encoding="utf-8").startswith("# Generated File"):
        errors.append(
            "appendix/generated/explicit-hogwarts-a-history-references.md: "
            "generated appendix must start with # Generated File"
        )
    return errors


def validate_index_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "project-control").glob("*index.yaml")):
        try:
            load_yaml(path)
        except Exception as exc:
            errors.append(f"{rel(path, root)}: YAML parse error: {exc}")
    return errors


def validate_script_entry(entry: dict, scene: dict, known_ids: set[str]) -> list[str]:
    """Additional provenance checks for script entries using the book schema."""
    errors = []
    label = str(entry.get('id', 'CC entry'))
    for key in ('source_id', 'scene_id', 'part', 'act', 'scene', 'speaker',
                'evidence_mode', 'historical_period', 'information_available',
                'character_knowledge', 'bagshot_1984_access', 'timeline', 'timeline_detail'):
        if entry.get(key) in (None, ''):
            errors.append(f'{label}: missing script field {key}')
    if entry.get('source_id') != 'CC':
        errors.append(f'{label}: source_id must be CC')
    for key in ('scene_id', 'part', 'act', 'scene'):
        if entry.get(key) != scene.get(key):
            errors.append(f'{label}: {key} disagrees with manifest')
    if scene.get('source_file'):
        expected = {'source_file': scene['source_file'],
                    'chapter_start_pdf_page': scene['page_start'],
                    'chapter_end_pdf_page': scene['page_end']}
        for key, value in expected.items():
            if entry.get(key) != value:
                errors.append(f'{label}: {key} disagrees with manifest')
    prefix = str(scene.get('scene_id', '')).lower()
    if not re.fullmatch(re.escape(prefix) + r'-\d{3}', label):
        errors.append(f'{label}: ID must use scene prefix and three-digit ordinal')
    page = entry.get('pdf_page')
    if not isinstance(page, int) or not scene['page_start'] <= page <= scene['page_end']:
        errors.append(f'{label}: PDF page outside scene range')
    if entry.get('timeline') not in {'primary', 'altered', 'historical_visit', 'remembered_reported_hypothetical'}:
        errors.append(f'{label}: invalid timeline')
    if entry.get('evidence_mode') not in {'dialogue_claim', 'stage_direction', 'transition', 'editorial_inference'}:
        errors.append(f'{label}: invalid evidence_mode')
    if entry.get('timeline') == 'altered' and entry.get('era_classification') not in {
            'later_editorial_note', 'post_1984_excluded_from_original', 'unknown_or_uncertain'}:
        errors.append(f'{label}: altered timeline cannot establish original-book history')
    comparison = entry.get('comparison') or {}
    if not isinstance(comparison, dict):
        return errors + [f'{label}: comparison must be a mapping']
    if comparison.get('relation') not in {'new_information', 'corroboration', 'contradiction', 'out_of_scope'}:
        errors.append(f'{label}: invalid comparison relation')
    targets = comparison.get('related_ids') or []
    if not isinstance(targets, list):
        return errors + [f'{label}: comparison related_ids must be a list']
    for target in targets:
        if target not in known_ids:
            errors.append(f'{label}: unknown comparison target {target}')
    return errors


def validate_script_passage(entry: dict, text: str) -> list[str]:
    """Verify a compact passage locator without reproducing the script."""
    label = entry.get('id', 'CC entry')
    locator = entry.get('passage_locator')
    if not isinstance(locator, dict):
        return [f'{label}: passage_locator must be a mapping']
    start, end = locator.get('char_start'), locator.get('char_end')
    if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(text):
        return [f'{label}: invalid passage character range']
    actual = hashlib.sha256(text[start:end].encode()).hexdigest()
    if actual != locator.get('text_sha256'):
        return [f'{label}: passage hash mismatch']
    return []


def validate_script_manifest(root: Path) -> list[str]:
    """Check scene coverage against embedded headings in the original carrier."""
    manifest_path = root / 'resources/manifests/cursed-child.yaml'
    if not manifest_path.exists():
        if (root / 'sources/book-cc').exists():
            return ['CC: source manifest missing']
        return []
    from pypdf import PdfReader
    errors = []
    try:
        manifest = load_yaml(manifest_path)
        pdf_path = root / manifest['source_file']
        if hashlib.sha256(pdf_path.read_bytes()).hexdigest() != manifest['sha256']:
            errors.append('CC: original PDF hash mismatch')
        reader = PdfReader(pdf_path)
        if len(reader.pages) != manifest['pdf_pages']:
            errors.append('CC: PDF page count mismatch')
        texts = [re.sub(r'\s+', ' ', page.extract_text() or '').strip() for page in reader.pages]
        words = ['ZERO','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE','TEN',
                 'ELEVEN','TWELVE','THIRTEEN','FOURTEEN','FIFTEEN','SIXTEEN','SEVENTEEN',
                 'EIGHTEEN','NINETEEN','TWENTY','TWENTY-ONE']
        headings = []
        for page, text in enumerate(texts,1):
            match = re.search(r'ACT (ONE|TWO|THREE|FOUR), SCENE ([A-Z-]+)', text)
            if match:
                act, number = words.index(match[1]), words.index(match[2])
                headings.append((1 if act <= 2 else 2, act, number, page))
        scenes = manifest['scenes']
        scene_by_id = {s['scene_id']: s for s in scenes}
        actual = [(s['part'],s['act'],s['scene'],s['page_start']) for s in scenes]
        if actual != headings or len(scenes) != manifest['scene_count']:
            errors.append('CC: scene manifest does not exactly cover PDF headings')
        if len({s['part'] for s in scenes}) != manifest['parts'] or len({s['act'] for s in scenes}) != manifest['acts']:
            errors.append('CC: part/act counts disagree')
        for act in range(1,5):
            numbers = [s['scene'] for s in scenes if s['act'] == act]
            if numbers != list(range(1,len(numbers)+1)):
                errors.append(f'CC: nonconsecutive scenes in act {act}')
        known_ids = set()
        for path in discover_source_yaml(root):
            data = load_yaml(path)
            if not isinstance(data, dict) or not isinstance(data.get('entries'), list):
                continue  # Already reported by the canonical source validator.
            for entry in data['entries']:
                if isinstance(entry, dict) and isinstance(entry.get('id'), str):
                    known_ids.add(entry['id'])
        listed_paths = set()
        for index, scene in enumerate(scenes):
            label = scene['scene_id']
            expected_id = f"CC-P{scene['part']}-A{scene['act']}-S{scene['scene']:02}"
            if label != expected_id:
                errors.append(f'{label}: unstable scene identifier')
            expected_end = scenes[index+1]['page_start']-1 if index+1 < len(scenes) else manifest['narrative_end_pdf_page']
            if scene['page_end'] != expected_end:
                errors.append(f'{label}: invalid scene end boundary')
            if scene.get('status') != 'complete' or not scene.get('review_note'):
                errors.append(f'{label}: scene review incomplete')
            path = root / scene['output_file']
            listed_paths.add(path)
            if not path.is_file():
                errors.append(f'{label}: scene YAML missing')
                continue
            data = load_yaml(path)
            if not isinstance(data, dict) or not isinstance(data.get('source_unit'), dict) or not isinstance(data.get('entries'), list):
                errors.append(f'{label}: malformed scene source YAML')
                continue
            unit = data['source_unit']
            for key in ('source_id','source_file'):
                if unit.get(key) != manifest[key]:
                    errors.append(f'{label}: source_unit {key} mismatch')
            if unit.get('scene_id') != label or unit.get('chapter_start_pdf_page') != scene['page_start'] or unit.get('chapter_end_pdf_page') != scene['page_end']:
                errors.append(f'{label}: source_unit scene range mismatch')
            for key in ('part', 'act', 'scene'):
                if unit.get(key) != scene[key]:
                    errors.append(f'{label}: source_unit {key} mismatch')
            if len(data['entries']) != scene.get('entry_count'):
                errors.append(f'{label}: entry count mismatch')
            for ordinal, entry in enumerate(data['entries'],1):
                if not isinstance(entry, dict):
                    errors.append(f'{label}: entry must be a mapping')
                    continue
                errors.extend(validate_script_entry(entry,dict(scene, source_file=manifest['source_file']),known_ids))
                if entry.get('id') != f'{label.lower()}-{ordinal:03}':
                    errors.append(f'{label}: nonconsecutive evidence ID')
                page = entry.get('pdf_page')
                if isinstance(page,int) and 1 <= page <= len(texts):
                    errors.extend(validate_script_passage(entry, texts[page-1]))
                    anchor = entry.get('text_anchor')
                    if not isinstance(anchor, dict):
                        errors.append(f'{label}: text_anchor must be a mapping')
                        continue
                    for key in ('start_phrase','end_phrase'):
                        phrase = re.sub(r'\s+',' ',str(anchor.get(key) or '')).strip()
                        if not phrase or phrase not in texts[page-1]:
                            errors.append(f"{entry['id']}: {key} absent from cited page")
                for support in entry.get('supporting_locations') or []:
                    target = scene_by_id.get(support.get('scene_id'))
                    support_page = support.get('pdf_page')
                    if not target or not isinstance(support_page, int) or not target['page_start'] <= support_page <= target['page_end']:
                        errors.append(f'{label}: supporting location outside its scene')
                    if not support.get('timeline') or not support.get('timeline_detail') or not support.get('note'):
                        errors.append(f'{label}: supporting location lacks timeline or interpretation')
        if listed_paths != set((root / 'sources/book-cc').glob('*.yaml')):
            errors.append('CC: unregistered or missing scene files')
    except (OSError, KeyError, TypeError, ValueError, AttributeError, yaml.YAMLError) as exc:
        errors.append(f'CC: invalid manifest or source: {exc}')
    return errors


def validate(root: Path, strict: bool) -> list[str]:
    reference_types = schema_values(root, "Reference Types")
    era_classifications = schema_values(root, "Era Classifications")
    errors: list[str] = []
    errors.extend(validate_source_files(root, strict, reference_types, era_classifications))
    source_entry_count = count_source_entries(root)
    errors.extend(validate_generated_files(root))
    errors.extend(validate_book_seed(root, source_entry_count))
    errors.extend(validate_index_files(root))
    errors.extend(validate_script_manifest(root))
    return errors


def print_errors(errors: Iterable[str]) -> None:
    print("Source YAML validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    errors = validate(root, args.strict)
    if errors:
        print_errors(errors)
        return 1
    print("Source YAML validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
