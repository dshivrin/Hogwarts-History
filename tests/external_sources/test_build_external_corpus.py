import hashlib
import json
from pathlib import Path

from scripts.external_sources.build_external_corpus import (
    build_corpus,
    extract_accio,
    extract_official,
    main,
    parse_plan,
    render_snapshot,
)


def test_parse_plan_collects_unique_primary_sources_and_applies_url_override(tmp_path: Path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        """
### A01 — Chamber of Secrets

https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets

### B02 — Scholastic live chat — 16 October 2000

Discover and acquire via Accio Quote.

### B03 — AOL Live chat — 19 October 2000

https://www.accio-quote.org/articles/2000/1000-aol-chat.htm
""".strip(),
        encoding="utf-8",
    )

    records = parse_plan(
        plan,
        url_overrides={
            "B02": "https://www.accio-quote.org/articles/2000/1000-scholastic-chat.htm"
        },
    )

    assert records == [
        {
            "id": "A01",
            "title": "Chamber of Secrets",
            "heading": "Chamber of Secrets",
            "original_url": "https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets",
        },
        {
            "id": "B02",
            "title": "Scholastic live chat",
            "heading": "Scholastic live chat — 16 October 2000",
            "original_url": "https://www.accio-quote.org/articles/2000/1000-scholastic-chat.htm",
        },
        {
            "id": "B03",
            "title": "AOL Live chat",
            "heading": "AOL Live chat — 19 October 2000",
            "original_url": "https://www.accio-quote.org/articles/2000/1000-aol-chat.htm",
        },
    ]


def test_parse_plan_rejects_duplicate_source_ids(tmp_path: Path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        """
### A01 — First
https://example.com/first
### A01 — Duplicate
https://example.com/duplicate
""".strip(),
        encoding="utf-8",
    )

    try:
        parse_plan(plan)
    except ValueError as exc:
        assert str(exc) == "duplicate source id: A01"
    else:
        raise AssertionError("duplicate source ID was accepted")


def test_extract_official_reads_embedded_article_json_without_page_chrome():
    article = {
        "props": {
            "pageProps": {
                "content": [
                    {
                        "body": {
                            "displayTitle": "Peeves",
                            "activationDate": "Aug 10th 2015",
                            "intro": "Opening paragraph.",
                            "author": {"title": "J.K. Rowling"},
                            "section": [
                                {"text": "First body paragraph."},
                                {"text": "## Author's note\nA final note."},
                            ],
                        }
                    }
                ]
            }
        }
    }
    html = (
        "<nav>Trending searches</nav>"
        '<script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(article)
        + "</script><footer>Shop</footer>"
    )

    extracted = extract_official(html)

    assert extracted == {
        "title": "Peeves",
        "author": "J.K. Rowling",
        "publication_date": "2015-08-10",
        "body": "Opening paragraph.\n\nFirst body paragraph.\n\n## Author's note\nA final note.",
    }
    assert "Trending searches" not in extracted["body"]
    assert "Shop" not in extracted["body"]


def test_extract_accio_keeps_content_container_and_discards_navigation():
    html = """
    <html><head><title>Archive title</title></head><body>
      <nav>Year index</nav>
      <div id="content">
        <div id="title"><strong>Johnstone, Anne. The Herald, 24 June 1997.</strong></div>
        <p>Opening context.</p>
        <p><strong>Question:</strong> Where is Hogwarts?</p>
        <p><strong>Rowling:</strong> Scotland.</p>
      </div>
      <footer>Copyright notice</footer>
    </body></html>
    """

    extracted = extract_accio(html)

    assert extracted == {
        "title": "Johnstone, Anne. The Herald, 24 June 1997.",
        "body": (
            "Johnstone, Anne. The Herald, 24 June 1997.\n\n"
            "Opening context.\n\n"
            "Question: Where is Hogwarts?\n\n"
            "Rowling: Scotland."
        ),
    }
    assert "Year index" not in extracted["body"]
    assert "Copyright notice" not in extracted["body"]


def test_render_snapshot_emits_parseable_metadata_and_body_hash():
    record = {
        "id": "A16",
        "title": "Peeves",
        "heading": "Peeves",
        "original_url": "https://www.harrypotter.com/writing-by-jk-rowling/peeves",
        "retrieval_url": "https://www.harrypotter.com/writing-by-jk-rowling/peeves",
        "local_path": "resources/external/official-rowling/harrypotter-com/a16-peeves.md",
        "source_site": "HarryPotter.com",
        "original_publisher": "HarryPotter.com",
        "source_class": "official_rowling_original",
        "authority": "A",
        "is_primary": True,
        "is_official": True,
        "capture_completeness": "complete",
        "retrieved_at": "2026-08-15",
        "relevance": ["hogwarts", "institutional_history", "pre_1984"],
        "notes": "Originally published on Pottermore.",
    }
    extracted = {
        "title": "Peeves",
        "author": "J.K. Rowling",
        "publication_date": "2015-08-10",
        "body": "Opening paragraph.\n\nBody paragraph.",
    }

    snapshot = render_snapshot(record, extracted)
    _, header, body = snapshot.split("---\n", 2)

    assert 'id: "A16"' in header
    assert 'publication_date: "2015-08-10"' in header
    assert 'original_publisher: "HarryPotter.com"' in header
    assert 'capture_completeness: "complete"' in header
    assert "\ncompleteness:" not in header
    assert f'sha256: "{hashlib.sha256(extracted["body"].encode("utf-8")).hexdigest()}"' in header
    assert f'local_path: "{record["local_path"]}"' in header
    assert body == "\n# Peeves\n\nOpening paragraph.\n\nBody paragraph.\n"


def test_build_corpus_writes_snapshots_and_logical_manifest(tmp_path: Path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        """
### A01 — Chamber of Secrets
https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
### B02 — Scholastic live chat — 16 October 2000
Discover via Accio.
""".strip(),
        encoding="utf-8",
    )
    cache = tmp_path / "cache"
    cache.mkdir()
    official_payload = {
        "props": {
            "pageProps": {
                "content": [
                    {
                        "body": {
                            "displayTitle": "Chamber of Secrets",
                            "activationDate": "Aug 10th 2015",
                            "intro": "Official introduction.",
                            "author": {"title": "J.K. Rowling"},
                            "section": [{"text": "Official body."}],
                        }
                    }
                ]
            }
        }
    }
    (cache / "a01.html").write_text(
        '<script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(official_payload)
        + "</script>",
        encoding="utf-8",
    )
    (cache / "b02.html").write_text(
        '<div id="content"><div id="title">Scholastic transcript</div>'
        "<p>Rowling: Interview body.</p></div>",
        encoding="utf-8",
    )
    output_root = tmp_path / "resources" / "external"
    manifest = tmp_path / "resources" / "manifests" / "external-sources.yaml"

    result = build_corpus(
        plan_path=plan,
        cache_dir=cache,
        output_root=output_root,
        manifest_path=manifest,
        retrieved_at="2026-08-15",
        url_overrides={
            "B02": "https://www.accio-quote.org/articles/2000/1000-scholastic-chat.htm"
        },
    )

    official = output_root / "official-rowling" / "harrypotter-com" / "a01-chamber-of-secrets.md"
    transcript = output_root / "interviews" / "accio-quote" / "b02-scholastic-live-chat.md"
    assert result == {"acquired": 2, "failed": []}
    assert official.is_file()
    assert transcript.is_file()
    assert "Official body." in official.read_text(encoding="utf-8")
    assert "Interview body." in transcript.read_text(encoding="utf-8")
    manifest_text = manifest.read_text(encoding="utf-8")
    assert manifest_text.count("- id:") == 2
    assert 'id: "external-A01"' in manifest_text
    assert 'logical_id: "A01"' in manifest_text
    assert 'authority: "A"' in manifest_text
    assert 'authority: "D"' in manifest_text


def test_catalog_cli_prints_json_records(tmp_path: Path, capsys):
    plan = tmp_path / "plan.md"
    plan.write_text(
        "### A01 — Chamber of Secrets\n"
        "https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets\n",
        encoding="utf-8",
    )

    exit_code = main(["catalog", "--plan", str(plan)])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output == [
        {
            "id": "A01",
            "title": "Chamber of Secrets",
            "heading": "Chamber of Secrets",
            "original_url": "https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets",
        }
    ]
