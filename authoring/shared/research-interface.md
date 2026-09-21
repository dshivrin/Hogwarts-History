# Research Interface for Authoring

Future authoring tasks should retrieve narrow, relevant evidence from the
existing repository rather than loading the whole corpus. The research layer is
canonical and read-only from authoring.

## Compact context

These references are useful starting points:

```text
docs/instructions/background-guide.md
docs/instructions/schema-reference.md
appendix/generated/explicit-hogwarts-a-history-references.md
```

`project-control/book-seed-order.yaml` records historical, provisional editorial
work from the extraction phase. It is not the authoritative outline for the new
book. The authoritative authoring architecture begins with the applicable
edition's `table-of-contents.yaml`.

## Preferred retrieval pattern

```text
concept
↓
just query / just query-entries
↓
candidate evidence IDs
↓
inspect exact source YAML
↓
inspect source PDF/snapshot only when required
```

For a common tag, use the stable command surface:

```sh
just query-entries <tag>
```

For entry, source, chapter/source-unit, or combined-tag lookup, use the reusable
query interface:

```sh
just query --id <entry-id>
just query --source <source-id>
just query --chapter <chapter-or-source-unit>
just query --tag <tag> --tag <second-tag>
```

The underlying tool also supports classification, reference-type, confidence,
source-unit, output-YAML, and result-limit filters. Query results provide
evidence IDs and `output_yaml` paths; open only the exact canonical YAML records
needed to assess the claim.

Use duplicate and corroboration lookup after likely tags are known:

```sh
just query-dupes <tag> <tag>
```

The duplicate result is a candidate set, not an instruction to discard repeated
records. Inspect the referenced YAML before deciding whether records duplicate,
corroborate, extend, or remain distinct from one another.

Open source PDFs or preserved external snapshots only when the YAML locator,
wording, context, provenance, or interpretation must be checked against the
source. Generated appendices and open-question views are discovery aids; the
canonical source YAML remains the evidence record.

## Context limits and discovery metadata

Do not load `book-seed/hogwarts-a-history-seed.md` as routine chapter context.
It is approximately 1.87 MB and represents all 1,683 current evidence entries,
far beyond the useful context for one chapter.

Extraction-era `candidate_part`, `candidate_chapter`, and `candidate_section`
values are discovery metadata. They may help locate material, but they must not
override the edition's table of contents, chapter boundaries, or later editorial
decisions.

If source review exposes a research defect or gap, record it in the chapter's
authoring artifacts. Do not edit the research layer from an authoring task.

## Authoring control and integrity

Use the read-only authoring commands instead of parsing chapter control data or
recreating hash scripts:

```sh
just author-status <chapter-number>
just author-next
just chapter-approved <chapter-number>
just chapter-hashes <chapter-number>
just verify-chapter <chapter-number>
just author-brief-context <chapter-number>
```

`author-brief-context` prints bounded orientation only. It does not create or
overwrite `brief.md` or any other authoring artifact.
