# Shared Evidence Policy

This policy interprets the repository's controlled evidence classifications for
the Unified Expanded Edition. It is subordinate to
`authoring/editorial-policy.md`. Classification does not replace direct source
review, and extraction-era era labels do not by themselves decide inclusion.

## Era classifications

### `original_book_core_candidate`

A strong candidate for direct use in the reconstructed historical text, subject
to review of the exact source, chronology, authority, and chapter relevance.

### `pre_1984_historical_candidate`

Historical material about events or conditions before 1984. Review chronology,
relevance, source authority, and knowledge access before assigning it to either
the reconstructed Bagshot narrative or a later editorial addition.

### `harry_era_confirmation`

May establish that an older institution, location, enchantment, practice, or
object continued to exist. By itself it does not establish:

- the feature's origin date;
- that the 1984 narrator knew about a later discovery;
- the interpretation later characters gave it.

### `later_editorial_note`

Consider this material for an attributable editorial addition in the relevant
chapter or addendum. Do not place it in the reconstructed Bagshot narrative or
imply that Bagshot knew it.

### `post_1984_excluded_from_original`

Exclude this material from the reconstructed Bagshot narrative, but reconsider
it for the unified edition. Use an integrated editorial addition when it fits
the chapter's chronology and flow; otherwise reserve it for an addendum.

### `unknown_or_uncertain`

Require explicit editorial review before use.

## Independent dimensions

Confidence, era, reference type, source authority, tentative placement, and
duplication or corroboration are independent dimensions. Do not flatten them
into a single quality score. A high-confidence observation may still be outside
Bagshot's plausible knowledge; a lower-authority carrier may still preserve
useful testimony; and a duplicate may strengthen a claim without deserving
repeated prose.

## Evidence consolidation

Raw selected evidence is not chapter structure. Before outlining, consolidate
the selected evidence into the smallest set of historically meaningful claims
that preserves every material distinction. The number of evidence entries does
not determine the amount of prose: several entries may support one claim, while
one unusually consequential source may require substantial treatment.

Similarity alone is not enough to merge entries. For each proposed group,
determine whether the sources:

- establish the same fact;
- independently confirm it;
- add a distinct detail or chronology;
- limit or qualify its interpretation;
- conflict with it; or
- merely concern the same subject while supporting different claims.

Conceptual consolidation must never erase provenance. Retain every evidence ID
and assign each source its function under the claim it supports. Use source
roles such as `establishes`, `independently_confirms`, `adds_detail`,
`adds_chronology`, `limits_interpretation`,
`later_retrospective_confirmation`, `attributed_tradition`, and `conflicts`.
These roles describe a source's contribution; they do not replace the existing
confidence, chronology, knowledge-access, or authority classifications.

Each consolidated claim must state the historical conclusion, classification,
supporting evidence with source roles, limitations, intended primary section,
cross-chapter status, and exactly one disposition:

- `advance_to_outline` — supported and in scope for the current revision;
- `omit_from_revision` — unnecessary or unsupported material excluded from the
  current revision;
- `defer` — valid or potentially useful material reserved for another chapter
  or revision; or
- `blocked_pending_verification` — material that cannot advance until a
  specified source question is resolved.

## Verification without assumption

If the relationship between sources cannot be established from inspected
material, record `VERIFY_SOURCE_RELATIONSHIP`. If a claim depends on source
content that has not been inspected, record `VERIFY_SOURCE`. Each entry must
identify the evidence and source IDs, the exact passage or fact to inspect, the
exact question, why the answer matters, the affected claim, and one scope:

- `blocking` — the affected claim cannot enter an outline or manuscript until
  the question is resolved;
- `omittable` — exclude the unsupported detail; an independently supported
  remainder of the claim may proceed; or
- `deferable` — move the affected claim or material to deferred evidence and
  exclude it from the current outline and manuscript.

Never fill an unresolved relationship or missing passage from memory,
inference, assumed canon, fan-maintained reference material, or similarity of
wording. An unresolved item blocks only the material it governs unless that
material is necessary to the chapter's chronology, argument, or structure.

## Evidence-coverage reconciliation

Every evidence ID in the chapter's selected evidence must appear in at least
one of:

- a consolidated claim;
- a source-verification item; or
- deferred evidence.

An ID may appear in more than one destination. The requirement is coverage,
not a one-to-one partition. A synthesis with an orphaned selected evidence ID
cannot pass validation.

Deferred evidence must retain the evidence ID, the reason for deferral, and the
likely future topic or chapter. Deferral preserves relevant evidence without
forcing it into the current manuscript or discarding it.

## Required chapter-level classifications

For every material chapter claim, record both:

1. **Event chronology:** when the described event or condition occurred.
2. **Knowledge access:** whether it is a plausible candidate for the
   reconstructed Bagshot narrative, a later discovery about an earlier event, a
   later historical event, an unverified or disputed account, or an editorial
   interpretation.

Source publication date is provenance, not event chronology. A post-1984 source
may document a founder-era event without making that evidence available to
Bagshot.

## Source authority

The external-source manifest distinguishes official first-party Rowling
originals (`source_class: official_rowling_original`, authority A, original
carrier) from preserved interview transcripts (`source_class:
preservation_transcription`, authority D, preservation carrier). Treat official
first-party text as a higher-authority direct source. Treat a preserved interview
transcript as a secondary carrier of attributed speech: review its original
outlet, date, completeness, transcription limits, and provenance before relying
on exact wording. Do not erase this distinction merely because both may contain
statements attributed to the same speaker.

## From evidence to prose

> Evidence can support what the historian says; it does not automatically
> determine how the historian says it.

Evidence selection establishes the support and limits for historical claims.
Voice, emphasis, causation, and narrative shape remain editorial decisions, and
must not turn uncertainty into fact, later knowledge into Bagshot knowledge, or
source language into unexamined prose.
