# Schema Reference

Use this file when validation fails or a field/classification is uncertain.

## Source YAML Shape

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

- `text_anchor` is a relocation aid using local start/end phrases and a short occurrence note.
- `quote_excerpt_short` must be a short identifying excerpt under 25 words.
- `source_note` paraphrases the evidence.
- `candidate_part`, `candidate_chapter`, and `candidate_section` are tentative structure suggestions.
- `duplicate_check` records whether the same fact already appears elsewhere, without deleting repeated evidence.
- `confidence` should be `high`, `medium`, or `low`.
