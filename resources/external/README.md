# External Hogwarts Source Corpus

This directory contains a private research corpus built from the acquisition contract at `pdfs/hogwarts-external-source-acquisition.md`.

## Contents

- `official-rowling/harrypotter-com/` — 37 official J.K. Rowling original-writing snapshots.
- `interviews/accio-quote/` — 26 preserved interview, chat, Q&A, and broadcast transcript carriers.
- `unresolved/discovery-backlog.md` — sources that still need a lawful primary carrier, archive recovery, or a legitimate published edition.
- `../manifests/external-sources.yaml` — machine-readable provenance, authority, hash, local-path, and relevance records.
- `../manifests/external-source-acquisition-report.md` — scope, counts, limitations, and recommended extraction order.

Each Markdown snapshot starts with YAML metadata. Its `sha256` is the SHA-256 digest of the normalized source body below the snapshot heading, not of the complete file containing the hash.

`capture_completeness: complete` means the snapshot contains all readable content exposed by the retrieval carrier. It does not mean evidence extraction, corpus discovery, or primary-carrier verification is complete.

The interview files preserve Accio Quote as the retrieval carrier while leaving `original_url` null unless a verified original carrier has been acquired. Their original outlet is recorded separately, and their authority remains `D`; they must not be counted as independent corroboration of a duplicate publisher transcript.

## Rebuild

The catalog and local snapshot builder are implemented in `scripts/external_sources/build_external_corpus.py`.

```bash
.fanfic-venv/bin/python scripts/external_sources/build_external_corpus.py catalog \
  --plan pdfs/hogwarts-external-source-acquisition.md

.fanfic-venv/bin/python scripts/external_sources/build_external_corpus.py build \
  --plan pdfs/hogwarts-external-source-acquisition.md \
  --cache /tmp/hogwarts-external-source-cache \
  --output-root resources/external \
  --manifest resources/manifests/external-sources.yaml \
  --retrieved-at 2026-08-15
```

The cache naming rule is `<logical-id-lowercase>.html`, such as `a16.html` or `b11.html`. Populate it only with direct public requests to each catalog URL. Do not bypass access controls.

Do not publish the acquired corpus. Published books, screenplays, cards, newsletters, recordings, and other non-public source carriers are deliberately excluded until a lawful local copy is available.
