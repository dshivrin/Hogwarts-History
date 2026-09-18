# Cursed Child — Source 8 research report

Completed 18 September 2026. **Ready for editorial consolidation, with seven recorded questions and no unresolved extraction failures.** No finished or in-progress chapter was edited.

## Source and method

The supplied PDF is preserved unmodified as [the source carrier](../../pdfs/harry-potter-and-the-cursed-child.pdf). Its title page identifies the **Special Rehearsal Edition**, official script of the original West End production; the colophon identifies the Pottermore digital edition (2016), ISBN 978-1-78110-704-1. The carrier is a calibre reflow with a third-party download notice, not a claim of a publisher-issued PDF. The play is by Jack Thorne from an original story by J.K. Rowling, John Tiffany and Jack Thorne.

- Source URL: [supplied PDF](https://kvdrdolibrary.wordpress.com/wp-content/uploads/2021/08/harry_potter_and_the_cursed_child.pdf)
- SHA-256: `259885808602501bb4930e56f38f85b58200b7bb0da9c07410bc0c479defb1f6`
- Registration and full scene audit: [manifest](cursed-child.yaml).
- Counts, cross-references, hashes, questions and exact file inventory: [research record](cursed-child-research-record.yaml).

The existing pypdf extractor supplied embedded text; every scene was read in sequence within its act. No OCR was needed. Scene headings were checked against all PDF pages; title and priority passages were also rendered and inspected (pp. 4, 24, 99–100, 123, 194). Narrative scenes occupy pp. 14–235, with inter-act divider pages included in preceding ranges; front/back matter is separately identified. Sparse excerpts, paraphrases, named-speaker anchors and hashed page-character spans keep evidence relocatable without reproducing the script.

## Results

| Metric | Result |
|---|---:|
| Verified PDF pages | 276 |
| Parts / acts / scenes | 2 / 4 / 75 |
| Scenes processed | 75/75 (100%) |
| New evidence entries | 111 |
| Existing entries corroborated | 47 distinct IDs through 37 new supporting entries |
| Pre-1984 historical candidates | 2, provisional |
| Original-book core entries approved | 0 |
| Later editorial notes | 74 |
| Explicitly excluded from original | 34 |
| Unknown/uncertain era | 1 |
| Alternate-timeline entries | 44 |
| Potential contradictions requiring review | 1 |
| Unresolved editorial questions | 7 |
| Unresolved extraction failures | 0 |
| Explicit Hogwarts: A History references | 0 |

Acts 1–4 contain 19, 20, 21 and 15 scenes respectively. The entry relationships are 73 new-information records, 37 corroborating records and one potential contradiction; these are classifications of the 111 new entries, not additional rows. “New information” means new to the indexed claim, not necessarily absent from every novel passage.

There are 72 links to older entries across all comparison types. No older entry or confidence classification was overwritten. Timeline counts are 40 primary, 44 altered, 16 historical visits and 11 remembered/reported/hypothetical; the last category also explicitly identifies the staged 1981 rescue rather than inventing a traveler viewpoint.

## Baseline and preservation

Canonical evidence increased from **1,717 to 1,828 entries**, and source units from **299 to 374**. The 1,314-entry seven-novel baseline remains intact; subsequent additions before this task comprise 127 companion-book entries and 276 external-source entries. The older 1,683-entry handoff predates 34 additional external entries.

Twelve pre-existing numbered copies in book-04 contained 73 repeated rows, making raw disk totals 1,790 before and 1,901 after this task. Every copy remains byte-for-byte intact. Shared source discovery now omits a numbered copy only when its bytes equal the unsuffixed original; divergent/orphaned copies remain visible to validation. This resolves the baseline duplicate-ID failure without deleting or rewriting evidence.

Hashes verify all 311 pre-existing source YAML files and all 96 checked authoring Markdown/YAML files unchanged. The source plan has only the added CC registration; existing queues, editorial selections and draft files were not advanced or rewritten. Generated research indexes, appendices and book seed were refreshed, not chapter prose.

## Findings and implications for planned chapters

| Topic | Evidence / PDF page | Editorial implication |
|---|---|---|
| Longstanding Sorting role | `cc-p1-a1-s04-001`, p24 | Corroborates ancient service and thought assessment; supplies no precise founding date or new founder biography. Potential support for the Four Founders/Sorting discussion only after the 1984 access check. |
| Express appointment and security | `cc-p1-a1-s11-001`–`003`, pp49–50 | Adds a claimed Ottaline Gambol appointment and qualified anti-escape history. Do not derive a fixed founding year from a student’s arithmetic. |
| Postwar centaur territory | `cc-p1-a2-s05-001`, p85 | Bane reports recognition of centaur land after the Battle. A later Forest/governance note, not a pre-1984 settlement or independently verified legal instrument. |
| Headmasters’ portraits | `cc-p1-a2-s10-002`, pp99–100 | Advisory/memoir description belongs to the first altered world. Keep it separate from primary-world portrait evidence. |
| Bathroom plumbing | `cc-p1-a2-s19-005`, p123 | Specific sink-to-lake route and alleged bylaw breach are altered-world testimony; earlier ghost pipe travel only partially supports the background. |
| House access covenant | `cc-p2-a3-s15-001`, p166 | Later primary-world rule claim; the sentence stops before naming who grants permission. Relevant to House life/governance, not an invented historical rule. |
| Bagshot in 1981 | `cc-p2-a4-s03-001`, p194 | Identifies residence and A History of Magic authorship; does not show a conversation, future-information transfer, or authorship of Hogwarts: A History. |

No material was incorporated into Chapter 1 or Chapter 2. The strongest possible original-book contribution is additional support for already-known Sorting/transport history, not a revision of the finished founding narrative. Later chapters on portraits, ghosts, buildings, governance and the Forest should consult the qualified entries rather than importing alternate outcomes.

## Open questions

- **CC-Q01** What records independently date the Trolley Witch’s claimed original appointment and test Scorpius’s 190-year inference? (`cc-p1-a1-s11-001`, `cc-p1-a1-s11-002`)
- **CC-Q02** Does the witch’s absolute anti-exit boast conflict with Luna’s forced abduction, or distinguish voluntary escape from forcible removal? Preserve both claims. (`cc-p1-a1-s11-003`, `dh-ch25-007`)
- **CC-Q03** Can independent pre-1984 public tradition or accessible records establish Bagshot’s knowledge of the two historical candidates? Neither entry is approved original-book copy. (`cc-p1-a1-s04-001`, `cc-p1-a1-s11-001`)
- **CC-Q04** Which details of the altered-world portrait account and specific sink route can be independently established in the primary timeline? Do not transfer the new details merely because background lore matches. (`cc-p1-a2-s10-002`, `cc-p1-a2-s19-005`)
- **CC-Q05** Who grants express permission under the House-quarters covenant? Craig is interrupted; no authority or exemption is established. (`cc-p2-a3-s15-001`)
- **CC-Q06** Are Augureys actually taught in Care of Magical Creatures? Delphi asks but the boys do not confirm. (`cc-p2-a3-s16-002`)
- **CC-Q07** Can anything independently establish the Bagshot door rumor or tentative basement inventory? Neither is evidence of her access to the travelers’ future knowledge. (`cc-p2-a4-s05-002`, `cc-p2-a4-s10-002`)

The potential contradiction is the Trolley Witch’s boast versus Luna’s forced removal from the Express (`dh-ch25-007`); voluntary escape and abduction may differ. Both claims remain. Variant world events are not themselves treated as contradictions with primary history.

## Validation and decisions

- `just validate`: passed, including unique IDs, PDF hash/page count, all scene headings, required fields, locators, timeline constraints and reference targets.
- `just test`: 81 tests passed. The printed missing-ID error is an intentional negative fixture followed by an overall successful result.
- Both index-query commands returned CC evidence with correct scene/page/timeline context. Regenerated output identifies CC as a script rather than an untitled external source.
- Independent scoped review confirmed the portrait, plumbing, covenant and Bagshot qualifications and the provenance validation fixes.
- Ruling: the explicit whole-source request overrides the automation-only one-unit limit. Existing queue pointers remain unchanged.
- Ruling: the sandbox denied worktree creation; work proceeded in place, preserving unrelated authoring changes.
- Ruling: additive scene/timeline fields retain the existing book schema and deterministic IDs. The risk of existing tools dropping context was addressed in indexes, queries, seed and appendix labels.
- Ruling: exact duplicate copies are excluded only after byte equality, with all original files preserved and inventoried.

## Files created or modified

The following inventory excludes pre-existing user authoring changes. Disposable text, image and review caches under `.tmp/cursed-child/` are not deliverables.

<details><summary>Created files (81)</summary>

- `pdfs/harry-potter-and-the-cursed-child.pdf`
- `resources/manifests/cursed-child.yaml`
- `resources/manifests/cursed-child-research-record.yaml`
- `resources/manifests/cursed-child-research-report.md`
- `tests/test_script_source.py`
- `tests/test_source_copy_discovery.py`
- `sources/book-cc/chapter-01-p1-a1-s01.yaml`
- `sources/book-cc/chapter-02-p1-a1-s02.yaml`
- `sources/book-cc/chapter-03-p1-a1-s03.yaml`
- `sources/book-cc/chapter-04-p1-a1-s04.yaml`
- `sources/book-cc/chapter-05-p1-a1-s05.yaml`
- `sources/book-cc/chapter-06-p1-a1-s06.yaml`
- `sources/book-cc/chapter-07-p1-a1-s07.yaml`
- `sources/book-cc/chapter-08-p1-a1-s08.yaml`
- `sources/book-cc/chapter-09-p1-a1-s09.yaml`
- `sources/book-cc/chapter-10-p1-a1-s10.yaml`
- `sources/book-cc/chapter-11-p1-a1-s11.yaml`
- `sources/book-cc/chapter-12-p1-a1-s12.yaml`
- `sources/book-cc/chapter-13-p1-a1-s13.yaml`
- `sources/book-cc/chapter-14-p1-a1-s14.yaml`
- `sources/book-cc/chapter-15-p1-a1-s15.yaml`
- `sources/book-cc/chapter-16-p1-a1-s16.yaml`
- `sources/book-cc/chapter-17-p1-a1-s17.yaml`
- `sources/book-cc/chapter-18-p1-a1-s18.yaml`
- `sources/book-cc/chapter-19-p1-a1-s19.yaml`
- `sources/book-cc/chapter-20-p1-a2-s01.yaml`
- `sources/book-cc/chapter-21-p1-a2-s02.yaml`
- `sources/book-cc/chapter-22-p1-a2-s03.yaml`
- `sources/book-cc/chapter-23-p1-a2-s04.yaml`
- `sources/book-cc/chapter-24-p1-a2-s05.yaml`
- `sources/book-cc/chapter-25-p1-a2-s06.yaml`
- `sources/book-cc/chapter-26-p1-a2-s07.yaml`
- `sources/book-cc/chapter-27-p1-a2-s08.yaml`
- `sources/book-cc/chapter-28-p1-a2-s09.yaml`
- `sources/book-cc/chapter-29-p1-a2-s10.yaml`
- `sources/book-cc/chapter-30-p1-a2-s11.yaml`
- `sources/book-cc/chapter-31-p1-a2-s12.yaml`
- `sources/book-cc/chapter-32-p1-a2-s13.yaml`
- `sources/book-cc/chapter-33-p1-a2-s14.yaml`
- `sources/book-cc/chapter-34-p1-a2-s15.yaml`
- `sources/book-cc/chapter-35-p1-a2-s16.yaml`
- `sources/book-cc/chapter-36-p1-a2-s17.yaml`
- `sources/book-cc/chapter-37-p1-a2-s18.yaml`
- `sources/book-cc/chapter-38-p1-a2-s19.yaml`
- `sources/book-cc/chapter-39-p1-a2-s20.yaml`
- `sources/book-cc/chapter-40-p2-a3-s01.yaml`
- `sources/book-cc/chapter-41-p2-a3-s02.yaml`
- `sources/book-cc/chapter-42-p2-a3-s03.yaml`
- `sources/book-cc/chapter-43-p2-a3-s04.yaml`
- `sources/book-cc/chapter-44-p2-a3-s05.yaml`
- `sources/book-cc/chapter-45-p2-a3-s06.yaml`
- `sources/book-cc/chapter-46-p2-a3-s07.yaml`
- `sources/book-cc/chapter-47-p2-a3-s08.yaml`
- `sources/book-cc/chapter-48-p2-a3-s09.yaml`
- `sources/book-cc/chapter-49-p2-a3-s10.yaml`
- `sources/book-cc/chapter-50-p2-a3-s11.yaml`
- `sources/book-cc/chapter-51-p2-a3-s12.yaml`
- `sources/book-cc/chapter-52-p2-a3-s13.yaml`
- `sources/book-cc/chapter-53-p2-a3-s14.yaml`
- `sources/book-cc/chapter-54-p2-a3-s15.yaml`
- `sources/book-cc/chapter-55-p2-a3-s16.yaml`
- `sources/book-cc/chapter-56-p2-a3-s17.yaml`
- `sources/book-cc/chapter-57-p2-a3-s18.yaml`
- `sources/book-cc/chapter-58-p2-a3-s19.yaml`
- `sources/book-cc/chapter-59-p2-a3-s20.yaml`
- `sources/book-cc/chapter-60-p2-a3-s21.yaml`
- `sources/book-cc/chapter-61-p2-a4-s01.yaml`
- `sources/book-cc/chapter-62-p2-a4-s02.yaml`
- `sources/book-cc/chapter-63-p2-a4-s03.yaml`
- `sources/book-cc/chapter-64-p2-a4-s04.yaml`
- `sources/book-cc/chapter-65-p2-a4-s05.yaml`
- `sources/book-cc/chapter-66-p2-a4-s06.yaml`
- `sources/book-cc/chapter-67-p2-a4-s07.yaml`
- `sources/book-cc/chapter-68-p2-a4-s08.yaml`
- `sources/book-cc/chapter-69-p2-a4-s09.yaml`
- `sources/book-cc/chapter-70-p2-a4-s10.yaml`
- `sources/book-cc/chapter-71-p2-a4-s11.yaml`
- `sources/book-cc/chapter-72-p2-a4-s12.yaml`
- `sources/book-cc/chapter-73-p2-a4-s13.yaml`
- `sources/book-cc/chapter-74-p2-a4-s14.yaml`
- `sources/book-cc/chapter-75-p2-a4-s15.yaml`

</details>

<details><summary>Modified files</summary>

- `appendix/generated/book-structure-seed.md`
- `appendix/generated/open-questions.md`
- `appendix/generated/project-stats.md`
- `appendix/generated/review-flags.md`
- `appendix/generated/source-index.md`
- `book-seed/hogwarts-a-history-seed.md`
- `docs/instructions/schema-reference.md`
- `project-control/duplicate-index.yaml`
- `project-control/entry-index.yaml`
- `project-control/source-index.yaml`
- `project-control/source-plan.yaml`
- `project-control/tag-index.yaml`
- `scripts/build_duplicate_index.py`
- `scripts/build_entry_index.py`
- `scripts/generate_appendices.py`
- `scripts/generate_book_seed.py`
- `scripts/query_duplicates.py`
- `scripts/query_entries.py`
- `scripts/source_files.py`
- `scripts/validate_source_yaml.py`

</details>

**Verdict:** ready for editorial consolidation with the seven explicit qualifications above. The historical cutoff and alternate-world boundaries remain enforced; no narration or chapter drafting was performed.
