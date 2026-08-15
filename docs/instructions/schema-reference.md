# Schema Reference

Use this file when validation fails or a field/classification is uncertain.

## Source YAML Shape

### Book and companion PDF sources

```yaml
source_unit:
  source_file:
  book:
  chapter:
  chapter_start_pdf_page:
  chapter_end_pdf_page:
  boundary_confidence:
  boundary_notes:
  processed_date:
  processor_notes:

entries:
  - id:
    source_file:
    book:
    chapter:
    chapter_start_pdf_page:
    chapter_end_pdf_page:
    pdf_page:
    printed_page:
    extracted_text_lines:
    text_anchor:
      start_phrase:
      end_phrase:
      local_occurrence_note:
    nearby_context:
    match_terms:
    quote_excerpt_short:
    source_note:
    reference_type:
    era_classification:
    topic_tags:
    candidate_part:
    candidate_chapter:
    candidate_section:
    reason_for_placement:
    relevance_to_hogwarts_a_history:
    duplicate_check:
      possible_duplicate:
      duplicate_of:
      notes:
    confidence:
    limitations:
```

### External Markdown sources

```yaml
source_unit:
  source_kind: external_markdown
  source_id: A01
  source_file: resources/external/official-rowling/harrypotter-com/a01-chamber-of-secrets.md
  title: Chamber of Secrets
  author: J.K. Rowling
  source_site: HarryPotter.com
  source_class: official_rowling_original
  authority: A
  publication_date: '2015-08-10'
  original_url: https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
  retrieval_url: https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
  capture_completeness: complete
  content_sha256: 64-character-lowercase-sha256
  processed_date: '2026-08-15'
  processor_notes: Complete snapshot read and evidence extracted.

entries:
  - id: ext-a01-001
    source_file: resources/external/official-rowling/harrypotter-com/a01-chamber-of-secrets.md
    source_id: A01
    source_url: https://www.harrypotter.com/writing-by-jk-rowling/chamber-of-secrets
    source_section: null
    pdf_page: null
    printed_page: null
    extracted_text_lines: null
    text_anchor:
      start_phrase: short local start phrase
      end_phrase: short local end phrase
      local_occurrence_note: where the passage occurs in the snapshot
    nearby_context: concise context
    match_terms:
      - normalized search term
    quote_excerpt_short: fewer than 25 words
    source_note: concise paraphrase
    reference_type: historical_claim
    era_classification: pre_1984_historical_candidate
    topic_tags:
      - normalized-tag
    candidate_part: existing candidate part
    candidate_chapter: existing candidate chapter
    candidate_section: specific candidate section
    reason_for_placement: placement rationale
    relevance_to_hogwarts_a_history: intended use and temporal qualification
    duplicate_check:
      possible_duplicate: false
      duplicate_of: null
      notes: indexed lookup result
      audit:
        query_tags:
          - normalized-tag-used-for-latest-index-recheck
        candidate_ids:
          - indexed-entry-id-reviewed
    confidence: high
    limitations: source and interpretation limits
```

## Reference Types

Use only:

- `explicit_hogwarts_a_history`
- `explicit_in_universe_source`
- `direct_observed_setting`
- `institutional_custom`
- `historical_claim`
- `magical_architecture`
- `school_rule_or_policy`
- `curriculum_or_subject`
- `house_system`
- `portrait_or_ghost_lore`
- `security_or_protection`
- `cross_reference_candidate`
- `weak_context_only`

## Era Classifications

Use only:

- `original_book_core_candidate`
- `pre_1984_historical_candidate`
- `harry_era_confirmation`
- `later_editorial_note`
- `post_1984_excluded_from_original`
- `unknown_or_uncertain`

## Field Guidance

- Current source YAML is intentionally self-contained. Source metadata may repeat per entry so each entry remains portable and auditable. A compact inherited-location schema may be introduced later only after validators, index builders, query scripts, and generators support both shapes.
- `text_anchor` is a relocation aid using local start/end phrases and a short occurrence note.
- For external sources, `capture_completeness: complete` means all readable content exposed by the retrieval carrier was captured. Queue `status`, not this field, records evidence-processing progress.
- External entries use `source_id`, `source_url`, `source_section`, and `text_anchor` as locators. Their PDF-specific locator fields remain present and null for compatibility.
- `quote_excerpt_short` must be a short identifying excerpt under 25 words.
- `source_note` paraphrases the evidence.
- `candidate_part`, `candidate_chapter`, and `candidate_section` are tentative structure suggestions.
- `duplicate_check` records whether the same fact already appears elsewhere, without deleting repeated evidence. For external queue completion, its `audit.query_tags` and `audit.candidate_ids` record the current compact-index comparison; every listed candidate must be returned by that latest index, and `duplicate_of` must be one of those candidates.
- `confidence` should be `high`, `medium`, or `low`.
