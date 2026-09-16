#!/usr/bin/env python3
"""Build provenance-rich Markdown snapshots from cached external source pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml


SOURCE_HEADING_RE = re.compile(r"^### ([A-Z]\d{2}) — (.+)$", re.MULTILINE)
URL_RE = re.compile(r"https://[^\s`)<>\"]+")

INTERVIEW_PUBLISHERS = {
    "B01": "Scholastic.com",
    "B02": "Scholastic.com",
    "B03": "AOL.com",
    "B04": "World Book Day",
    "B05": "MuggleNet / The Leaky Cauldron",
    "B06": "MuggleNet / The Leaky Cauldron",
    "B07": "MuggleNet / The Leaky Cauldron",
    "B08": "ITV / Edinburgh press conference",
    "B09": "Bloomsbury",
    "B10": "PotterCast / The Leaky Cauldron",
    "B11": "The Herald",
    "B12": "Guardian Unlimited",
    "B13": "Salon",
    "B14": "Barnes & Noble",
    "B15": "Barnes & Noble",
    "B16": "Boston Globe / Student NewsLine",
    "B17": "WBUR Radio",
    "B18": "WAMU",
    "B19": "South West News Service",
    "B20": "Barnes & Noble / Yahoo!",
    "B21": "Raincoast Books",
    "B22": "BBC Blue Peter",
    "B23": "BBC",
    "B24": "BBC",
    "B25": "BBC Radio 4",
    "B26": "Radio City Music Hall event",
}

DEFAULT_URL_OVERRIDES = {
    "B02": "https://www.accio-quote.org/articles/2000/1000-scholastic-chat.htm"
}

SOURCE_PROFILES = {
    "A": {
        "extractor": "official",
        "subdirectory": Path("official-rowling/harrypotter-com"),
        "source_site": "HarryPotter.com",
        "source_class": "official_rowling_original",
        "authority": "A",
        "is_primary": True,
        "is_official": True,
        "carrier_type": "original",
        "relevance": ["hogwarts", "rowling_original", "institutional_history"],
        "notes": "Official Rowling Original; carrier may note prior Pottermore publication.",
    },
    "B": {
        "extractor": "accio",
        "subdirectory": Path("interviews/accio-quote"),
        "source_site": "Accio Quote",
        "source_class": "preservation_transcription",
        "authority": "D",
        "is_primary": False,
        "is_official": False,
        "carrier_type": "preservation_transcript",
        "relevance": ["hogwarts", "rowling_interview", "author_commentary"],
    },
    "F": {
        "extractor": "official",
        "subdirectory": Path("official-editorial/harrypotter-com"),
        "source_site": "HarryPotter.com",
        "source_class": "secondary_reference",
        "authority": "E",
        "is_primary": False,
        "is_official": True,
        "carrier_type": "official_editorial",
        "relevance": ["hogwarts", "official_editorial", "source_critical_context"],
        "notes": "Official editorial material; preserve speculative language and do not treat as Rowling Original writing.",
    },
}


def _display_title(source_id: str, heading: str) -> str:
    if source_id.startswith("B") and " — " in heading:
        return heading.rsplit(" — ", 1)[0]
    return heading


def parse_plan(
    path: Path, url_overrides: dict[str, str] | None = None
) -> list[dict[str, str]]:
    """Read A/B source records from the acquisition contract."""
    text = Path(path).read_text(encoding="utf-8")
    headings = list(SOURCE_HEADING_RE.finditer(text))
    overrides = url_overrides or {}
    records: list[dict[str, str]] = []
    seen: set[str] = set()

    for index, match in enumerate(headings):
        source_id, heading = match.groups()
        if source_id[:1] not in SOURCE_PROFILES:
            continue
        if source_id in seen:
            raise ValueError(f"duplicate source id: {source_id}")
        seen.add(source_id)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        segment = text[match.end() : end]
        url_match = URL_RE.search(segment)
        url = overrides.get(source_id) or (url_match.group(0) if url_match else None)
        if not url:
            raise ValueError(f"missing source URL: {source_id}")
        records.append(
            {
                "id": source_id,
                "title": _display_title(source_id, heading),
                "heading": heading,
                "original_url": url,
            }
        )

    return records


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T.*)?", value):
        return value[:10]
    cleaned = re.sub(r"(\d+)(?:st|nd|rd|th)", r"\1", value)
    for pattern in ("%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(cleaned, pattern).date().isoformat()
        except ValueError:
            pass
    return value


def _collect_section_text(value: Any) -> list[str]:
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_collect_section_text(item))
        return result
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return [value["text"].strip()]
        result = []
        for child in value.values():
            result.extend(_collect_section_text(child))
        return result
    return []


def extract_official(html: str) -> dict[str, str | None]:
    """Extract a HarryPotter.com Rowling Original from embedded page JSON."""
    match = re.search(
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not match:
        raise ValueError("HarryPotter.com page has no __NEXT_DATA__ payload")
    payload = json.loads(match.group(1))
    content = payload["props"]["pageProps"]["content"]
    article = content[0]["body"] if isinstance(content, list) else content
    paragraphs: list[str] = []
    intro = article.get("intro")
    if isinstance(intro, str) and intro.strip():
        paragraphs.append(intro.strip())
    paragraphs.extend(part for part in _collect_section_text(article.get("section", [])) if part)
    body = "\n\n".join(paragraphs).strip()
    if not body:
        raise ValueError("HarryPotter.com article body is empty")
    author = article.get("author") or {}
    return {
        "title": article.get("displayTitle"),
        "author": author.get("title") or "J.K. Rowling",
        "publication_date": _normalize_date(article.get("activationDate")),
        "body": body,
    }


class _AccioContentParser(HTMLParser):
    BLOCK_TAGS = {"div", "p", "h1", "h2", "h3", "h4", "li", "blockquote"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.current: list[str] = []
        self.blocks: list[str] = []

    def _flush(self) -> None:
        value = re.sub(r"\s+", " ", " ".join(self.current)).strip()
        if value and (not self.blocks or value != self.blocks[-1]):
            self.blocks.append(value)
        self.current = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if not self.depth:
            if tag == "div" and attributes.get("id") == "content":
                self.depth = 1
            return
        if tag == "div":
            self.depth += 1
        if tag in self.BLOCK_TAGS:
            self._flush()
        elif tag == "br":
            self.current.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.depth:
            return
        if tag in self.BLOCK_TAGS:
            self._flush()
        if tag == "div":
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.depth and data.strip():
            self.current.append(data)


def extract_accio(html: str) -> dict[str, str]:
    """Extract the content container from an Accio Quote carrier."""
    parser = _AccioContentParser()
    parser.feed(html)
    parser.close()
    parser._flush()
    if not parser.blocks:
        raise ValueError("Accio page has no non-empty #content container")
    return {"title": parser.blocks[0], "body": "\n\n".join(parser.blocks)}


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(str(value), ensure_ascii=False)


def render_snapshot(record: dict[str, Any], extracted: dict[str, Any]) -> str:
    """Render one extracted carrier as Markdown with provenance front matter."""
    body = extracted["body"].strip()
    sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()
    metadata = {
        "id": record["id"],
        "title": extracted.get("title") or record["title"],
        "author": extracted.get("author") or "J.K. Rowling",
        "source_site": record["source_site"],
        "original_publisher": record.get("original_publisher"),
        "source_class": record["source_class"],
        "authority": record["authority"],
        "publication_date": extracted.get("publication_date"),
        "original_url": record["original_url"],
        "retrieval_url": record["retrieval_url"],
        "retrieved_at": record["retrieved_at"],
        "archive_url": record.get("archive_url"),
        "carrier_type": record.get("carrier_type"),
        "is_primary": record["is_primary"],
        "is_official": record["is_official"],
        "capture_completeness": record["capture_completeness"],
        "sha256": sha256,
        "local_path": record["local_path"],
        "relevance": record["relevance"],
        "notes": record.get("notes"),
    }
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {_yaml_scalar(item)}" for item in value)
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.extend(["---", "", f"# {metadata['title']}", "", body, ""])
    return "\n".join(lines)


def _slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def _decode_html(raw: bytes) -> str:
    head = raw[:2048].decode("ascii", errors="ignore")
    match = re.search(r"charset=[\"']?([A-Za-z0-9._-]+)", head, re.IGNORECASE)
    encoding = match.group(1) if match else "utf-8"
    aliases = {"iso-8859-1": "cp1252", "latin-1": "cp1252"}
    try:
        return raw.decode(aliases.get(encoding.lower(), encoding))
    except (LookupError, UnicodeDecodeError):
        return raw.decode("utf-8", errors="replace")


def _heading_date(source_id: str, heading: str) -> str | None:
    if not source_id.startswith("B") or " — " not in heading:
        return None
    return heading.rsplit(" — ", 1)[1]


def _relative_or_absolute(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _manifest_yaml(records: list[dict[str, Any]], retrieved_at: str) -> str:
    lines = [
        "schema_version: 1",
        f"retrieved_at: {_yaml_scalar(retrieved_at)}",
        "sources:",
    ]
    field_order = [
        "id",
        "logical_id",
        "title",
        "author",
        "source_site",
        "original_publisher",
        "source_class",
        "authority",
        "publication_date",
        "original_url",
        "retrieval_url",
        "retrieved_at",
        "archive_url",
        "carrier_type",
        "is_primary",
        "is_official",
        "capture_completeness",
        "sha256",
        "local_path",
        "relevance",
        "notes",
    ]
    for record in records:
        first = field_order[0]
        lines.append(f"  - {first}: {_yaml_scalar(record.get(first))}")
        for key in field_order[1:]:
            value = record.get(key)
            if isinstance(value, list):
                lines.append(f"    {key}:")
                lines.extend(f"      - {_yaml_scalar(item)}" for item in value)
            else:
                lines.append(f"    {key}: {_yaml_scalar(value)}")
    lines.append("")
    return "\n".join(lines)


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _normalize_markdown_body(body: str) -> str:
    """Remove transport-only trailing whitespace without changing line structure."""
    return "\n".join(line.rstrip() for line in body.splitlines()).strip()


def build_corpus(
    *,
    plan_path: Path,
    cache_dir: Path,
    output_root: Path,
    manifest_path: Path,
    retrieved_at: str,
    url_overrides: dict[str, str] | None = None,
    selected_ids: set[str] | None = None,
    append: bool = False,
) -> dict[str, Any]:
    """Build Markdown snapshots and a logical-source manifest from cached HTML."""
    candidates = parse_plan(plan_path, url_overrides=url_overrides)
    if selected_ids is not None:
        requested = {source_id.upper() for source_id in selected_ids}
        available = {candidate["id"] for candidate in candidates}
        missing = sorted(requested - available)
        if missing:
            raise ValueError(f"source IDs not found in acquisition plan: {', '.join(missing)}")
        candidates = [candidate for candidate in candidates if candidate["id"] in requested]

    manifest_records: list[dict[str, Any]] = []
    if append and manifest_path.exists():
        existing_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        if not isinstance(existing_manifest, dict) or not isinstance(
            existing_manifest.get("sources"), list
        ):
            raise ValueError("existing external manifest must contain a sources list")
        manifest_records = list(existing_manifest["sources"])

    existing_ids = {str(record.get("logical_id") or "") for record in manifest_records}
    existing_urls = {
        str(value)
        for record in manifest_records
        for value in (record.get("original_url"), record.get("retrieval_url"))
        if value
    }
    existing_paths = {str(record.get("local_path") or "") for record in manifest_records}
    for candidate in candidates:
        source_id = candidate["id"]
        if source_id in existing_ids:
            raise ValueError(f"external source already exists: {source_id}")
        if candidate["original_url"] in existing_urls:
            raise ValueError(f"external source URL already exists: {candidate['original_url']}")
        profile = SOURCE_PROFILES[source_id[0]]
        candidate_path = (
            Path(output_root)
            / profile["subdirectory"]
            / f"{source_id.lower()}-{_slugify(candidate['title'])}.md"
        )
        relative_path = _relative_or_absolute(candidate_path)
        if relative_path in existing_paths or candidate_path.exists():
            raise ValueError(f"external snapshot path already exists: {relative_path}")

    failed: list[dict[str, str]] = []

    for candidate in candidates:
        source_id = candidate["id"]
        cache_path = Path(cache_dir) / f"{source_id.lower()}.html"
        if not cache_path.is_file() or cache_path.stat().st_size == 0:
            failed.append({"id": source_id, "reason": "missing or empty cached HTML"})
            continue
        try:
            html = _decode_html(cache_path.read_bytes())
            profile = SOURCE_PROFILES[source_id[0]]
            extracted = (
                extract_official(html)
                if profile["extractor"] == "official"
                else extract_accio(html)
            )
            extracted["body"] = _normalize_markdown_body(extracted["body"])
            if profile["extractor"] == "accio":
                extracted["author"] = "J.K. Rowling"
                extracted["publication_date"] = _heading_date(source_id, candidate["heading"])
            filename = f"{source_id.lower()}-{_slugify(candidate['title'])}.md"
            output_path = Path(output_root) / profile["subdirectory"] / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            publisher = (
                INTERVIEW_PUBLISHERS.get(source_id)
                if profile["extractor"] == "accio"
                else None
            )
            record = {
                **candidate,
                "retrieval_url": candidate["original_url"],
                "original_url": (
                    None if profile["extractor"] == "accio" else candidate["original_url"]
                ),
                "local_path": _relative_or_absolute(output_path),
                "source_site": profile["source_site"],
                "original_publisher": publisher,
                "source_class": profile["source_class"],
                "authority": profile["authority"],
                "is_primary": profile["is_primary"],
                "is_official": profile["is_official"],
                "carrier_type": profile["carrier_type"],
                "capture_completeness": "complete",
                "retrieved_at": retrieved_at,
                "relevance": profile["relevance"],
                "notes": profile.get("notes")
                or f"Accio Quote preservation carrier; original outlet: {publisher or 'unresolved'}.",
            }
            snapshot = render_snapshot(record, extracted)
            _atomic_write_text(output_path, snapshot)
            body_hash = hashlib.sha256(extracted["body"].strip().encode("utf-8")).hexdigest()
            manifest_records.append(
                {
                    **record,
                    "id": f"external-{source_id}",
                    "logical_id": source_id,
                    "title": extracted.get("title") or candidate["title"],
                    "author": extracted.get("author") or "J.K. Rowling",
                    "publication_date": extracted.get("publication_date"),
                    "sha256": body_hash,
                }
            )
        except Exception as exc:  # Keep one bad carrier from discarding successful work.
            failed.append({"id": source_id, "reason": f"{type(exc).__name__}: {exc}"})

    _atomic_write_text(Path(manifest_path), _manifest_yaml(manifest_records, retrieved_at))
    return {"acquired": len(candidates) - len(failed), "failed": failed}


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser("catalog", help="print the A/B fetch catalog as JSON")
    catalog.add_argument("--plan", type=Path, required=True)

    build = subparsers.add_parser("build", help="build snapshots from a populated HTML cache")
    build.add_argument("--plan", type=Path, required=True)
    build.add_argument("--cache", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.add_argument("--manifest", type=Path, required=True)
    build.add_argument("--retrieved-at", required=True)
    build.add_argument("--ids", nargs="+")
    build.add_argument("--append", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    if args.command == "catalog":
        records = parse_plan(args.plan, url_overrides=DEFAULT_URL_OVERRIDES)
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    result = build_corpus(
        plan_path=args.plan,
        cache_dir=args.cache,
        output_root=args.output_root,
        manifest_path=args.manifest,
        retrieved_at=args.retrieved_at,
        url_overrides=DEFAULT_URL_OVERRIDES,
        selected_ids=set(args.ids) if args.ids else None,
        append=args.append,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
