#!/usr/bin/env python3
"""Build provenance-rich Markdown snapshots from cached external source pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


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
        if source_id[:1] not in {"A", "B"}:
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


def build_corpus(
    *,
    plan_path: Path,
    cache_dir: Path,
    output_root: Path,
    manifest_path: Path,
    retrieved_at: str,
    url_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build Markdown snapshots and a logical-source manifest from cached HTML."""
    candidates = parse_plan(plan_path, url_overrides=url_overrides)
    manifest_records: list[dict[str, Any]] = []
    failed: list[dict[str, str]] = []

    for candidate in candidates:
        source_id = candidate["id"]
        cache_path = Path(cache_dir) / f"{source_id.lower()}.html"
        if not cache_path.is_file() or cache_path.stat().st_size == 0:
            failed.append({"id": source_id, "reason": "missing or empty cached HTML"})
            continue
        try:
            html = _decode_html(cache_path.read_bytes())
            is_official = source_id.startswith("A")
            extracted = extract_official(html) if is_official else extract_accio(html)
            if not is_official:
                extracted["author"] = "J.K. Rowling"
                extracted["publication_date"] = _heading_date(source_id, candidate["heading"])
            subdirectory = (
                Path("official-rowling/harrypotter-com")
                if is_official
                else Path("interviews/accio-quote")
            )
            filename = f"{source_id.lower()}-{_slugify(candidate['title'])}.md"
            output_path = Path(output_root) / subdirectory / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            publisher = None if is_official else INTERVIEW_PUBLISHERS.get(source_id)
            record = {
                **candidate,
                "retrieval_url": candidate["original_url"],
                "original_url": candidate["original_url"] if is_official else None,
                "local_path": _relative_or_absolute(output_path),
                "source_site": "HarryPotter.com" if is_official else "Accio Quote",
                "original_publisher": publisher,
                "source_class": (
                    "official_rowling_original" if is_official else "preservation_transcription"
                ),
                "authority": "A" if is_official else "D",
                "is_primary": is_official,
                "is_official": is_official,
                "carrier_type": "original" if is_official else "preservation_transcript",
                "capture_completeness": "complete",
                "retrieved_at": retrieved_at,
                "relevance": (
                    ["hogwarts", "rowling_original", "institutional_history"]
                    if is_official
                    else ["hogwarts", "rowling_interview", "author_commentary"]
                ),
                "notes": (
                    "Official Rowling Original; carrier may note prior Pottermore publication."
                    if is_official
                    else f"Accio Quote preservation carrier; original outlet: {publisher or 'unresolved'}."
                ),
            }
            snapshot = render_snapshot(record, extracted)
            output_path.write_text(snapshot, encoding="utf-8")
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

    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
    Path(manifest_path).write_text(
        _manifest_yaml(manifest_records, retrieved_at), encoding="utf-8"
    )
    return {"acquired": len(manifest_records), "failed": failed}


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
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
