# Open Questions Integration Audit

Audit date: 2026-09-18  
Audited files:

- `resources/external/open-questions-scapping/hogwarts-open-questions-enriched.yaml`
- `resources/external/open-questions-scapping/hogwarts-open-questions-codex-guide.md`

Canonical comparison file: `project-control/structured-sources/open-questions.yaml`  
Authoritative authoring structure: `authoring/editions/1984/table-of-contents.yaml`

## A. Executive summary

The two new files are **not ready to integrate**. Their preservation of the
canonical question records is excellent, and their general warnings about the
1984 knowledge boundary, uncertain history, house-elf omission, and selective
retrieval agree with the current authoring policy. However, adoption is blocked
by four material problems:

1. The guide incorrectly says that only Chapters 1–3 are established. The
   repository's authoritative, if still provisional, 1984 table of contents
   defines twenty numbered chapters. The new destination register omits six of
   those chapters and assigns many questions to broad placeholder buckets or to
   Chapters 2 and 3 contrary to their stated boundaries.
2. The enriched file records 23 findings but records **zero verified evidence
   IDs**. Fifteen external leads and all four PDF corpora are already present
   locally and extracted. Several questions marked research-pending are already
   wholly or partly answered by indexed evidence.
3. The enriched YAML duplicates all canonical question content while adding an
   unvalidated editorial schema. Existing validators and index builders do not
   validate or index its new `research`, `editorial`, registry, or destination
   fields. Replacing the canonical YAML would therefore create two authorities
   without enforcement.
4. The proposed "creative reconstruction" language is broader than the current
   editorial policy, which says not to invent missing historical details. The
   useful modes are historical question, bounded inference, later editorial
   context, and exclusion. Any fictional flourish must remain rhetorical and
   must not add an event, actor, procedure, source, date, or mechanism.

The recommended design is a **separate editorial overlay keyed only by canonical
question ID**, joined to canonical questions at query time. It should use stable
chapter IDs from the authoritative table of contents, canonical evidence IDs,
manifest source IDs, and separately validated fields for event date, narrator
access, and source-revelation date.

### Authority map used in this audit

| Repository material | Audit treatment |
|---|---|
| `AGENTS.md`; `authoring/AGENTS.md` | Binding project instructions. |
| `project-control/structured-sources/open-questions.yaml` | Canonical open-question data. |
| `sources/**/*.yaml` | Canonical evidence records. |
| `project-control/entry-index.yaml`, `source-index.yaml`, `tag-index.yaml` | Generated compact indexes; discovery aids, not substitute evidence. |
| `resources/manifests/external-sources.yaml` | Canonical external-source provenance and authority inventory. |
| `authoring/editions/1984/table-of-contents.yaml` | Authoritative authoring architecture; status remains `provisional`. |
| `authoring/editions/1984/project-control/chapter-status.yaml` | Current workflow status: Chapter 1 `drafted`, Chapters 2–20 `planned`. |
| Chapter 1 workspace and Chapter 2 preparation package | Current authoring work. Chapter 2's package is preparation, not an approved manuscript chapter. |
| `project-control/book-seed-order.yaml` | Historical provisional extraction-era order; explicitly not the authoring outline. |
| `book-seed/hogwarts-a-history-seed.md`, `appendix/generated/*` | Generated discovery/reference views; not authoritative chapter structure. |

The draft README still says no chapter exists, but the more specific current
chapter-status file and the populated Chapter 1 workspace show that this line is
stale. The new guide should not repeat that kind of conversational or historical
state as authority.

## B. Coverage and compatibility

### Record preservation

| Check | Result |
|---|---:|
| Canonical questions | 386 |
| Enriched questions | 386 |
| Declared `question_count` | 386 |
| Unique canonical IDs | 386 |
| Unique enriched IDs | 386 |
| Missing IDs | 0 |
| Added IDs | 0 |
| Duplicate IDs | 0 |
| Changed `id`, `topic`, `question`, `status`, `source`, or `related_entries` values | 0 |
| Records whose original tags are not an exact prefix of enriched tags | 0 |
| Existing related-entry references | 8 across 4 questions |
| Related-entry references unresolved in `entry-index.yaml` | 0 |

Every enriched record has the same nine keys: the seven canonical fields plus
`research` and `editorial`. This is internally consistent. All `search_first`
values resolve to the local `source_registry`; all destination keys resolve to
the local destination register; all actual tags are normalized lowercase
hyphenated strings; and the mode/cutoff/destination tags agree with their
corresponding fields.

### Semantic and schema conflicts

- `derived_from` names `Pasted text(4).txt`, not the canonical repository path,
  version, or hash. The exact comparison proves preservation today, but the file
  does not carry durable provenance.
- All 386 canonical `status` values remain `open`. That preserves the source but
  does not accurately express the enriched layer's own 23 partial findings or
  known editorial dispositions. Canonical status should remain untouched; the
  overlay needs a separate controlled `resolution_status`.
- Research states are 357 `requires_targeted_verification`, 23
  `specific_source_lead_identified`, and 6 `not_for_prose`. The 23 findings have
  no `evidence_ids_verified`; no record has a negative-search log. A finding
  without a canonical evidence reference is not auditable.
- Existing source validators validate `sources/**/*.yaml`, compact indexes, and
  generated files. They do **not** validate enriched-question keys, enums,
  chapter references, source-registry references, or evidence-reference
  integrity.
- `generate_appendices.py` reads only the canonical open-question path and uses
  only question/topic/tags/related entries. If the enriched file replaced the
  canonical file, the generator would silently ignore its research/editorial
  structures while emitting the many `oq-*` tags into the human appendix.
- Entry and tag query tools index evidence entries, not questions. None of the
  new tags is currently retrievable through `query_entries.py`.
- The source registry invents parallel types (`authorial`,
  `official_reference`, `official_feature`) instead of referring to manifest
  `logical_id`, `source_class`, and `authority`. This can drift from the
  canonical provenance model, as already happened for the Marauder's Map.
- The guide's safety check literally contains `**{len(Q)} of {len(Q)}**`, an
  unrendered template placeholder rather than an executable or meaningful
  check.

### Direct extension versus editorial layer

Do not extend the canonical YAML in place. The canonical file is already used
by appendix generation and has a deliberately small record shape. The smallest
compatible design is an overlay containing only additions keyed by `id`. This
avoids duplicating the question text and original metadata, permits independent
editorial status, and makes drift detectable by a join validator.

## C. Source verification

### Inventory result

The current canonical inventory contains 374 source YAML units and 1,828 indexed
evidence entries: 1,314 entries from the seven novels, 29 from *Beedle*, 37 from
*Quidditch Through the Ages*, 61 from *Fantastic Beasts*, 111 from *Cursed
Child*, and 276 from external sources.

The new registry contains 30 source keys:

- All four PDF leads (`P-NOVELS`, `P-QUIDDITCH`, `P-BEEDLE`, `P-BEASTS`) are
  **verified locally** and **already extracted**.
- Fifteen web leads exactly match locally captured, hash-bound, Authority-A
  official Rowling snapshots and canonical evidence YAML: `W-SORT`,
  `W-HATSTALL`, `W-BOOK`, `W-PEEVES`, `W-SWORD`, `W-CHAMBER`, `W-PENSIEVE`,
  `W-TRAIN`, `W-KINGS`, `W-GHOSTS`, `W-PORTRAITS`, `W-LUPIN`, `W-POTTER`,
  `W-MCG`, and `W-MIRROR`. They are **verified locally** and **already
  extracted**. This audit did not re-check the live publisher pages.
- `W-MAP` uses an uncaptured fact-file URL, but the stronger Rowling-original
  source is already captured and extracted as A11 at
  `sources/external/official-rowling/a11-the-marauder-s-map.yaml`. The lead is
  therefore **already extracted under a different canonical source** and its
  registry record is wrong.
- `W-WILLOW` and `W-PASSAGES` are **candidates** as exact external pages, but
  their material claims are substantially **already extracted** from the novels
  and A10. They must not be described as verified external pages in this audit.
- `W-HALL`, `W-HONEY`, `W-HOGSMEADE`, `W-FOUNDERS`, `W-LEAKY`, `W-CROSS`,
  `W-ROR`, and `W-QUCOMP` are **candidates/unavailable locally** as the exact
  URLs named. Their reputation or official branding does not verify a question.
  `W-CROSS` and `W-ROR` are also unused by every question.

No fan wiki is registered. That is correct. The absent official-reference and
feature pages must still be treated as unverified leads, not as extracted
evidence.

### Verified and overlooked evidence

The following table records the material discrepancies found. "Narrow" means
the cited evidence answers part of the question but not the remaining date,
mechanism, provenance, or narrator-access issue.

| Question ID(s) | Classification and exact evidence | What the evidence establishes | Required correction |
|---|---|---|---|
| `sorting-ceremony-001` | Already extracted: `ext-a02-001`, `sources/external/official-rowling/a02-the-sorting-hat.yaml`, opening paragraph | The Hat's origin is founder-era tradition; it does not date every ceremony detail. | Record `ext-a02-001`; narrow the open question to the start/date of the ceremony's later form. |
| `sorting-ceremony-005`, `-006` | Already extracted: `ext-a08-001`, `ext-a08-004`; corroborated by `dh-ch07-006`, *DH* ch. 7, PDF p. 3083 | Godric's sword and the worthiness rule are supported. The first Hat linkage and mechanism remain unknown. | Add all three IDs; do not present the whole compound question as open. |
| `castle-navigation-and-magical-architecture-009`–`-012` | Already extracted: `ext-a11-002`, `ext-a11-004`; `poa-ch17-004`, PDF p. 864; `poa-ch17-005`, PDF p. 866 | Canonical A11 identifies the Homonculous Charm and confiscation; PoA identifies a maker and shows detection under a Cloak and of Animagi. The deeper mechanism and ward interaction remain unknown. | Replace `W-MAP` with canonical A11 and evidence IDs; split supported facts from residual mechanism questions. |
| `castle-navigation-and-magical-architecture-015` | Already extracted: `poa-ch10-003`, *PoA* ch. 10, PDF p. 734 | The map displays castle/grounds and seven Hogsmeade passages; the passage establishes the Harry-era Filch knowledge claim. Earlier awareness remains unproved. | Cite the novel entry first; keep only pre-Harry staff-awareness history open. |
| `castle-navigation-and-magical-architecture-018`, `-019` | Already extracted: `ext-a14-001`, `ext-a14-003`, `ext-a14-004` | Maker and arrival remain unknown; roughly a century of Room-of-Requirement storage predates 1991; the modified Stone protection is post-cutoff. | Add the IDs and split pre-cutoff existence from 1991 use and narrator access. |
| `castle-navigation-and-magical-architecture-022` | Already extracted: `ext-a05-003`, fourth paragraph | Head portraits are trained before death to carry knowledge forward; the custom's origin and exact formal powers remain unknown. | Record the partial answer and narrow the question. |
| `castle-navigation-and-magical-architecture-025`, `protective-magic-and-security-101`, `-102`, `-104` | Already extracted: `ext-a01-001`–`003`; `cos-ch09-005`–`006`, *CoS* ch. 9, PDF pp. 408–409 | Slytherin's Chamber purpose/access, eighteenth-century plumbing alteration, and repeated failed searches are supported; searcher names/dates and narrator access remain limited. | Add exact IDs. Move substantive Chamber treatment to Chapter 5, not Chapter 3. |
| `castle-rooms-and-displays-013`, `-015`; related Willow/accommodation questions | Already extracted: `poa-ch10-002`, PDF p. 729; `poa-ch18-003`, PDF p. 870; `ext-a10-001` | Lupin dates the tree to his arrival; PoA and A10 explain the Willow/tunnel/Shack as his accommodation. A formal authorization record is not supplied. | Treat purpose and relative date as documented; retain calendar year, records, and narrator access as open. |
| `ghosts-and-magical-residents-001` | Already extracted: `ext-a16-001`, `ext-a16-004` | Peeves is a poltergeist associated with Hogwarts since its early history; the 1876 removal attempt is documented by the retrospective source. | Replace generic open status in the overlay with documented answer plus access qualification. |
| `ghosts-and-magical-residents-004` | Already extracted: `ext-a06-005`; `gof-ch25-004`, *GoF* ch. 25, PDF p. 1335 | Myrtle died as a pupil, returned to haunt Olive Hornby, and remained in the toilet; the exact year is not supplied by A06. | Split the answered "why" from the still-uncertain exact date and knowledge route. |
| `ghosts-and-magical-residents-006` | Already extracted: `ext-a06-006`; corroborated by `ps-ch08-005` | Binns died after sleeping by the staffroom fire and continued teaching. No precise date is supplied. | Record the manner/continuity answer and leave only date/duration open. |
| `pre-hogwarts-historical-context-007`, `-017` | Already extracted: `ext-a03-001`–`003` | Founders installed the Book and Quill; they are the selection mechanism and react to a child's first magic. Letter addressing/logistics remain separate. | Add evidence IDs; narrow both questions and separate later authorial revelation from 1984 access. |
| `feasts-and-school-traditions-003` | Already extracted: `ext-a04-002`, `ext-a04-004`, `ext-a04-005`, `ext-a19-002` | The transport problem follows the 1692 Statute; the train's precise acquisition is expressly unproven; compulsory use followed approval; the concealed London platform is attributable to Orpington's 1849–1855 ministry. | Record the bounded chronology and preserve uncertainty around exact acquisition/service dates. |
| `feasts-and-school-traditions-038` | Already extracted and already related: `beedle-ch02-001`, `-002`, `-005`, PDF pp. 26–28 | Beery, young Transfiguration teacher Dumbledore, Dippet, the failed production, and the ban are supported; no exact school year is given. | Copy related IDs into verified evidence and retain only the precise-year question. |
| `protective-magic-and-security-033` | Already extracted: `ext-a14-004` | Dumbledore's modified Mirror protection is a 1991 one-off in the evidence and is excluded from the original body. | Mark later editorial/excluded from 1984 body; do not seek a generalized historic security class without evidence. |
| `protective-magic-and-security-115` | Overlooked decisive evidence: `ootp-ch37-005`, *OotP* ch. 37, PDF p. 2373; existing related `ootp-ch02-006`, PDF p. 1607 | Dumbledore explains the blood protection and explicitly connects the Howler to Petunia's earlier pact. | Add `ootp-ch37-005`; classify as documented later context, not research-pending. |
| `protective-magic-and-security-116` | Overlooked decisive evidence: `ootp-ch06-007`, *OotP* ch. 6, PDF p. 1679 | Grimmauld Place is Unplottable and Dumbledore is Secret-Keeper; current related entries only cover arrival/concealment observations. | Add `ootp-ch06-007`; classify as documented later context. |
| `protective-magic-and-security-117` | Overlooked decisive evidence: `ootp-ch32-007`, *OotP* ch. 32, PDF p. 2283; existing related `ootp-ch08-006` raises but does not answer the issue | Umbridge privately admits ordering the Dementor attack. | Add `ootp-ch32-007`; classify as documented later context and retain the source's private-confession limitation. |
| `source-processing-001` | Already implemented repository behavior: `docs/instructions/schema-reference.md`; `scripts/validate_source_yaml.py`; external content hashes and Cursed Child passage hashes | Current source records use PDF page plus text anchors; external snapshots are content-hash bound; CC passages add offset/hash locators. | Resolve as repository-only. If a general PDF passage hash remains desired, create a separate tooling proposal rather than a lore question. |

### Unsupported or still-unverified lead claims

- `W-HALL` can at most support the observed ceiling behavior if acquired; it
  does not establish maker, age, maintenance, or spellwork.
- `W-WILLOW` cannot replace the stronger locally extracted PoA/A10 evidence and
  does not by itself establish formal authorization records.
- `W-PASSAGES`, `W-HONEY`, and `W-HOGSMEADE` may summarize places, but a modern
  official summary cannot prove construction dates or 1984-historian access.
- `W-FOUNDERS` is described by the new file itself as an official synthesis, not
  a charter or dated contemporary source.
- `W-QUCOMP` concerns international competition. It cannot establish Hogwarts
  match rules without school-specific evidence.
- `W-LEAKY` may describe wider travel history. It does not prove that Hogwarts
  mandated the Leaky Cauldron route.

## D. Chronology and editorial conflicts

The repository's authoritative rule is clear: 1984 is an approximate editorial
cutoff, not the book's proven publication date; authorship is undetermined;
Bathilda Bagshot must not be named as author without evidence. The new
`scope_note` correctly repeats these points.

The plan nevertheless needs three distinct fields rather than one
`cutoff_review` string:

1. `event_period`: when the event or feature existed.
2. `narrator_access`: how the circa-1984 historian could plausibly know it.
3. `revelation_period`: when the supporting source revealed the information.

The following cases show why:

| Case | Event timing | Narrator access | Revelation timing / treatment |
|---|---|---|---|
| Marauder's Map | Created before 1984 | Private student artifact, later confiscated; access not established | A11 published in 2015; PoA revelations are later. Use only with an explicit access argument or later note. |
| Whomping Willow accommodation | Pre-1984, during Lupin's pupil years | Purpose was deliberately confidential | Revealed later by Lupin/A10. The tree's existence is not the same as public knowledge of its purpose. |
| Chamber plumbing alteration | Eighteenth century | Secret Gaunt intervention; narrator access unproved | A01 published in 2015. Pre-cutoff event does not make it original-book knowledge. |
| Mirror of Erised | At Hogwarts roughly a century before 1991 | Hidden storage and institutional knowledge are unclear | A14 is retrospective; the 1991 modification is explicitly post-cutoff. |
| Myrtle's death/return | Before 1984 | Later first-person and retrospective accounts; official-record access unclear | Do not convert later testimony into a precise contemporaneous record. |
| Peeves 1876 removal attempt | 1876 | Potentially institutional history, but only a later retrospective source is indexed | Can support canon truth; original-body use still needs an access decision. |
| Hogwarts Express/platform | Historical reforms are pre-cutoff | Plausibly public institutional history, but exact archival route is unstated | A04/A19 are 2015 retrospective sources; preserve the Express-origin uncertainty expressed by A04. |
| Beery pantomime | During Dippet's headship and Dumbledore's teaching career | The evidence is Dumbledore's later commentary | Do not manufacture an exact year or presume availability to the original historian. |

The new top-level instructions state the correct principle, but 341 records use
the broad `date_and_author_access_unverified` value and 348 allow original-body
use conditionally. That is too coarse to prevent accidental promotion of later
private knowledge. A chapter writer should see the three temporal dimensions
and the exact evidence before any body-use decision.

## E. Chapter mapping

### Current authoritative structure

`authoring/editions/1984/table-of-contents.yaml` defines Chapters 1–20. Its notes
explicitly say that it is the authoritative authoring structure and that
extraction-era placement metadata does not override it. The status is
`provisional`, which means it may change through authoring governance, not that
the older 14-part seed should replace it.

The new guide's statement that only Chapters 1–3 have established numbers is
therefore false. Its destination register has no direct destination for:

- Chapter 5, *The Departure of Salazar Slytherin*;
- Chapter 15, *Hogwarts and the Wider Wizarding World*;
- Chapter 16, *The Triwizard Tournament*;
- Chapter 18, *Headmasters and Reformers*;
- Chapter 19, *Hogwarts in the Modern Age*; or
- Chapter 20, *From Dippet to Dumbledore*.

### Destination audit

| New key | Questions | Current disposition |
|---|---:|---|
| `C2` | 7 | Use stable chapter ID 2. Several entries need Chapter 4 or 5/later-context treatment instead. |
| `C3` | 17 | Use stable chapter ID 3 only for actual foundation process. Most Chamber/crisis questions belong in Chapter 5, Chapter 17, or exclusion. |
| `SORTING` | 4 | Split between Chapter 4 (House system/Sorting) and Chapter 13 (ceremony/tradition); lake arrival belongs in Chapter 10 or Chapter 13 depending argument. |
| `CASTLE` | 26 | Usually Chapter 6. Preserve Chapter 6's ban on exhaustive room lists. |
| `GROUNDS` | 23 | Usually Chapter 7; security consequences may cross-reference Chapter 17. |
| `GOVERNANCE` | 56 | Usually Chapter 8, but pupil discipline/routine may belong in Chapter 10 and leadership change in Chapters 18 or 20. |
| `ACADEMICS` | 56 | Usually Chapter 9. Harry-era teacher-specific incidents may be later context or excluded. |
| `ADMISSIONS` | 30 | Usually Chapter 10; historical transport modernization can belong in Chapter 19 and Hogsmeade relations in Chapter 15. |
| `LIBRARY` | 26 | Usually Chapter 11. Avoid named-book catalogue treatment. |
| `GHOSTS` | 19 | Usually Chapter 12; grounds residents require Chapter 7 cross-reference. |
| `TRADITIONS` | 12 | Usually Chapter 13. |
| `SPORT` | 28 | Usually Chapter 14; wider/international Quidditch is outside the chapter boundary unless it explains Hogwarts practice. |
| `SECURITY` | 60 | Usually Chapter 17; governance and grounds cross-references should not duplicate narrative. |
| `LATER` | 16 | No current numbered chapter. This is an editorial disposition, not a destination. Keep out of the 1984 body unless a separately evidenced older institutional fact is selected elsewhere. |
| `OMISSION` | 5 | Correctly no manuscript destination. Preserve house-elf omission. |
| `CONTROL` | 1 | Correctly no manuscript destination; resolve as tooling metadata. |

Only `founding-and-the-four-houses-003` is a clean Chapter 3 fit among the 17
records currently assigned to `C3`. Chamber tradition and Slytherin's departure
belong principally to Chapter 5; the 1991 Stone defences and 1992–1993 crisis
belong to later context or Chapter 17, not the foundation chapter. Likewise,
the Chapter 2 preparation package explicitly reserves Slytherin's departure for
Chapter 5, House mechanics for Chapter 4, and later private discoveries from the
1984 body. The enriched mapping does not reflect that completed preparation
work.

Recommended mapping values are stable numeric chapter IDs plus optional
cross-reference IDs, not prose titles or a second destination vocabulary.
`destination_confirmed` should mean reviewed against the current table of
contents revision, not merely one of C1–C3.

## F. Creative-use assessment

The plan's useful editorial distinctions are compatible in principle:

- documented answer;
- narrower unresolved question;
- bounded historical inference;
- explicit uncertainty;
- later editorial context;
- exclusion; and
- repository-only cleanup.

The implementation needs correction in four areas:

1. The current policy says evidence gaps should not be filled with invented lore
   and missing historical details must not be invented to smooth prose.
   "Creative reconstruction" must therefore be renamed or defined as
   **rhetorical/interpretive framing only**. It may not create an event, custom,
   actor, procedure, motive, source, office, rule, spell, date, quotation, or
   witness.
2. Questions must be allowed to remain unanswered. The modes
   `ask_or_qualified_reconstruction` and `research_then_bounded_inference`
   should not imply that every record produces prose.
3. The `creative_seed` field is highly repetitive: 380 non-null values collapse
   to only 23 distinct strings, including one reused for 116 security questions,
   one for all 54 pre-Hogwarts-context questions, and one for all 32 curriculum
   questions. These are generic style prompts, not individualized editorial
   guidance. Move the shared guidance to one policy/workflow document and keep
   only genuine question-specific cautions in the overlay.
4. The five house-elf questions are correctly tagged `excluded_topic`, sent to
   `OMISSION`, given no creative seed, and barred from body/footnote use. Keep
   that hard exclusion. Do not let cross-references from kitchens, governance,
   or magical residents reintroduce the omitted material.

Appropriate modes for the verified examples are:

- explicit uncertainty: ceiling maker/maintenance, exact founding year, exact
  pantomime year, Binns's death year;
- documented answer plus residual question: Sorting Hat origin, sword
  worthiness, Willow purpose, Chamber plumbing, portrait training;
- bounded inference only after access review: why an institution might retain
  or forget an old object or route;
- later editorial context/exclude from original: 1991 Mirror protection,
  Harry-era Chamber crisis mechanics, Privet Drive/Grimmauld/Umbridge answers;
- exclude: house-elves; and
- repository-only resolved: `source-processing-001`.

## G. Required corrections

| Priority | Question/section | Existing value or instruction | Evidence | Recommended replacement/change |
|---|---|---|---|---|
| **Blocking** | Guide destination register; top-level `book_outline_status` | Only Chapters 1–3 are confirmed; all other destinations are placeholders. | `authoring/editions/1984/table-of-contents.yaml` defines the authoritative 20-chapter structure. | Replace the parallel register with stable IDs 1–20 loaded from the TOC; record its path/schema revision. |
| **Blocking** | All 386 `editorial.primary_destination` values | Parallel keys such as `SECURITY`, `ACADEMICS`, and `LATER`. | Current TOC and chapter boundaries. | Remap to numeric chapter IDs; treat later/exclude/control as dispositions, not chapters. |
| **Blocking** | `C3` records, especially Chamber and Harry-era IDs | Seventeen records assigned to Chapter 3. | TOC boundaries and Chapter 2 preparation package. | Keep only foundation-process material in Ch. 3; move Chamber tradition/departure to Ch. 5, security history to Ch. 17, and post-cutoff events out of the body. |
| **Blocking** | `research.finding` and `evidence_ids_verified` | 23 findings, zero verified IDs. | Exact evidence table in Section C. | No non-null finding without at least one canonical evidence ID and locator; label source-only leads separately. |
| **Blocking** | Provenance | `derived_from: Pasted text(4).txt`. | Canonical path and exact preservation result. | Store canonical path, schema/version, and content hash; validate the join on every run. |
| **Blocking** | Storage architecture | Full duplicate of canonical records. | Existing generator and validator behavior. | Use a separate ID-keyed editorial overlay; do not replace or copy canonical fields. |
| **Blocking** | Cutoff fields | One coarse `cutoff_review`. | Edition bible, evidence policy, cases in Section D. | Add `event_period`, `narrator_access`, `revelation_period`, and explicit body eligibility with rationale. |
| **Blocking** | Creative-use wording | Permits an "explicitly speculative flourish"/creative reconstruction. | Editorial policy rules 3, 4, and 7; authoring runtime invariant 10. | Limit to rhetorical framing and bounded interpretation; prohibit invented historical particulars. |
| **Important** | `W-MAP` | Fact-file URL and `official_reference`. | Canonical A11 Authority-A Rowling-original snapshot and `ext-a11-001`–`004`. | Replace with manifest logical ID A11, canonical YAML/snapshot path, source class, authority, and original URL. |
| **Important** | Eleven absent exact web leads | Written as registry sources with substantive `use_and_limit` claims. | No matching local snapshot/YAML for the exact URLs. | Mark `availability: candidate_unverified`; do not state content as inspected. Prefer already extracted novel evidence where available. |
| **Important** | `protective-magic-and-security-115`–`117` | Research-pending/later-context records omit decisive evidence. | `ootp-ch37-005`, `ootp-ch06-007`, `ootp-ch32-007`. | Add evidence IDs and mark documented later context with source limitations. |
| **Important** | `source-processing-001` | Open repository question. | Current schema, validator, hashes, anchors. | Resolve as technical-only; move any remaining enhancement to a tooling issue. |
| **Important** | Guide safety check 1 | Literal `{len(Q)} of {len(Q)}`. | Actual comparison: 386/386. | Replace with a real validation command/script and expected invariant, not interpolated prose. |
| **Important** | Per-chapter resolution log | Guide instructs a new artifact not defined by the chapter state machine. | `authoring/shared/chapter-workflow.md` defines the workspace artifacts. | Put question outcomes in `evidence-gaps.md` or `evidence-selection.yaml`, or formally approve a new artifact before use. |
| **Important** | Status semantics | All canonical statuses remain `open`. | Existing partial/full answers. | Preserve canonical status; add overlay enum such as `unreviewed`, `lead_only`, `partially_answered`, `answered`, `editorially_resolved`, `excluded`. |
| **Important** | Guide chapter/draft state | Implies conversational state and warns against a "final" Chapter 1. | Chapter status says Chapter 1 is `drafted`, not editor-approved; Chapters 2–20 planned. | Read chapter status at runtime; do not hard-code draft/final claims. |
| **Optional** | Shared instructions/creative seeds | 386 unique full strings constructed from heavily repeated templates; only 23 distinct non-null seeds. | Structural analysis in Section F. | Store compact reusable workflow once; keep only question-specific focus, cautions, and residual unknowns. |
| **Optional** | Unused registry sources | `W-PENSIEVE`, `W-POTTER`, `W-CROSS`, `W-ROR` are unused. | Search of every `research.search_first`. | Remove from this overlay or move to a global source catalog referenced by manifest ID. |

## H. Integration proposal

### Minimal data model

Keep `project-control/structured-sources/open-questions.yaml` unchanged. Create a
separate authoring/editorial overlay, preferably under the 1984 authoring layer,
with records shaped approximately as follows:

```yaml
schema_version: 1
canonical_questions:
  path: project-control/structured-sources/open-questions.yaml
  version: 1
  sha256: <validated hash>
chapter_plan:
  path: authoring/editions/1984/table-of-contents.yaml
  schema_version: 1
questions:
  - id: sorting-ceremony-001
    resolution_status: partially_answered
    verified_evidence_ids: [ext-a02-001]
    candidate_source_ids: []
    residual_question: When did the later ceremonial form begin?
    event_period: founders-era tradition
    narrator_access: unverified
    revelation_period: post-1984-authorial-source
    body_eligibility: requires_editorial_review
    primary_chapter_id: 4
    secondary_chapter_ids: [13]
    treatment: explicit_uncertainty
    question_specific_note: Distinguish the Hat's origin from later ceremony details.
```

Do not copy `topic`, `question`, original tags, canonical status, source, or
related entries. Resolve those through the canonical join.

### Required validator

A read-only validator should enforce:

1. overlay IDs are unique and resolve to canonical IDs;
2. canonical version/hash matches;
3. evidence IDs resolve in `entry-index.yaml` and their canonical YAML exists;
4. source IDs resolve through `resources/manifests/external-sources.yaml` or the
   local PDF/source inventory;
5. chapter IDs resolve in the current TOC;
6. enums for resolution, treatment, access, and eligibility are controlled;
7. a finding marked answered/partial has evidence IDs;
8. a candidate lead cannot be called verified without local/external inspection
   metadata;
9. house-elf records remain excluded;
10. no later/post-cutoff evidence is body-eligible without a separate older fact
    and narrator-access rationale.

### Retrieval workflow

For each chapter iteration:

1. Read the current TOC entry and chapter status.
2. Join only overlay records whose primary or secondary chapter ID matches the
   chapter.
3. Load compact evidence-index rows for their verified evidence IDs.
4. Query only unresolved concepts; inspect exact canonical YAML and source
   snapshot/PDF locators as needed.
5. Assign one reviewed outcome per selected question.
6. Record the outcome in the existing evidence-selection/evidence-gaps workflow.
7. Draft only after evidence review and outline approval.

This prevents loading 19,552 lines and 386 instruction blocks on every chapter
run. It also preserves the current query-first authoring architecture.

## I. Validation results

### Existing checks run

| Command/check | Actual result |
|---|---|
| `just validate` | Exit 0: `Source YAML validation passed.` This validates canonical source/index/generated infrastructure; it does not validate the new enriched schema. |
| `just test` | Exit 0: 81 tests ran in 5.887 seconds, `OK`. The suite prints one expected fixture-level validator failure for a deliberately missing duplicate target; the unittest run itself passed. |
| YAML parse of canonical and enriched files | Both parsed successfully with the repository virtual environment's YAML library. |
| Full ID/field/tag-prefix comparison | 386/386 IDs; no missing, added, or duplicate IDs; no changes to the six scalar/list canonical fields checked plus related entries; all original tag lists preserved as prefixes. |
| Related-entry integrity | All 8 references resolve in the 1,828-entry compact index. |
| Enriched cross-field checks | All `search_first` keys, destination keys, destination titles, destination tags, mode tags, and cutoff tags are internally consistent; all actual tags pass normalized syntax. |
| Working-tree mutation check after validation/tests | No tracked files changed. Only the pre-existing untracked open-question directory, including this requested report, is present. |

### Limits of validation

No download, scrape, or live external verification was performed, as required.
The eleven exact external URLs absent from the local corpus remain candidates.
No generator or index rebuild was run against the enriched file, because doing
so would either be irrelevant (the scripts do not read it) or would violate the
read-only audit scope. The initial ad hoc query invocation used a positional tag
and returned CLI usage errors; rerunning with the documented `--tag` option
succeeded and is the basis for the evidence lookups above. That invocation
mistake is not a repository validation failure.

## Concise implementation proposal

Before adoption:

1. Correct the guide to use the authoritative 20-chapter TOC and current chapter
   status.
2. Replace the duplicated enriched YAML with a validated ID-keyed editorial
   overlay.
3. Populate exact canonical evidence IDs for every asserted finding, beginning
   with the discrepancies in Section C.
4. Separate event date, narrator access, and revelation date.
5. Remap destinations to stable chapter IDs and separate destination from
   later/exclude/control disposition.
6. Restrict creative treatment to evidence-bounded interpretation and explicit
   uncertainty.
7. Add the join/reference validator and a chapter-filtered retrieval command.
8. Integrate reviewed outcomes into the existing evidence-selection and
   evidence-gaps artifacts; do not introduce a parallel chapter-writing state
   machine.

Until those changes are made, the new files should remain an unadopted proposal
under `resources/external/`, not part of the normal Codex chapter-writing
workflow.
