# External Source Acquisition Report

**Retrieval date:** 2026-08-15  
**Contract:** `pdfs/hogwarts-external-source-acquisition.md`  
**Manifest:** `resources/manifests/external-sources.yaml`

## Outcome

This pass added 63 traceable, non-empty Markdown source snapshots without extracting claims into the existing book evidence:

| Carrier group | Logical sources | Authority | Source class |
|---|---:|---|---|
| HarryPotter.com J.K. Rowling Originals | 37 | A | `official_rowling_original` |
| Accio Quote interview/chat/broadcast preservation transcripts | 26 | D | `preservation_transcription` |
| **Total** | **63** |  |  |

The snapshots contain approximately 151,996 words and 877,381 bytes including their provenance headers. All 63 requested public URLs returned a non-empty carrier, and all 63 passed source-specific extraction.

The acquisition contract itself received an append-only supplementary queue of 52 entries:

- 22 additional official Rowling-original pages, A16-A37;
- 16 additional interview/chat/broadcast transcripts, B11-B26;
- 10 published or legacy source families, E01-E10;
- 4 additional discovery/preservation tools, D06-D09.

Of those supplementary entries, 38 public A/B sources were acquired in this pass. The E and D entries remain bibliography or recovery inputs and are not represented as corroborating evidence.

## Provenance and authority decisions

- A01-A37 retain the direct HarryPotter.com page as both original and retrieval URL. Each carrier identifies J.K. Rowling as author and exposes its article body in first-party page data.
- B01-B26 retain Accio Quote as the retrieval URL and the named publisher, broadcaster, interviewer, or event as `original_publisher`. `original_url` remains null because the original carrier was not acquired and verified in this pass.
- Accio transcripts remain authority D even though the underlying statements are Rowling's. They are one preservation carrier per logical transcript, not independent corroboration.
- B05-B07 are three parts of one MuggleNet/The Leaky Cauldron interview set.
- B10 is one PotterCast interview whose surviving Leaky Cauldron publication spans at least two transcript pages; the Accio copy is retained as the single acquired preservation carrier.
- Official web pages that also appear in the three *Pottermore Presents* ebooks are carrier duplicates. Future extraction must map equivalent sections before weighting evidence.

## Validation performed

- 63 manifest records load as YAML and have 63 unique logical IDs.
- 37 records are authority A and 26 are authority D.
- Every manifest local path exists and points to UTF-8 Markdown.
- Every snapshot has populated provenance fields, a non-empty body, and a matching SHA-256 body digest.
- Every manifest record and snapshot uses `capture_completeness`; `complete` means all readable content exposed by that retrieval carrier was captured, not that evidence processing or source discovery is finished.
- The official extractor reads only the first-party article payload; the transcript extractor reads only the Accio `#content` container rather than site navigation or footer chrome.
- Focused acquisition tests cover catalog parsing, missing URL overrides, duplicate IDs, official extraction, transcript extraction, provenance rendering, corpus writes, and the catalog CLI.

## Sources not acquired

The following were deliberately not copied as source text:

- E01-E05 and E08-E10: commercial ebooks, screenplays, a charity anthology, a published interview, and a documentary requiring legitimate editions or lawful recordings.
- E06-E07: the original Famous Wizard Cards and four *Daily Prophet* newsletters; discovery indexes were verified, but the primary artifacts still need lawful carrier recovery and edition-level provenance.
- Corpus C: old `jkrowling.com` pages. Secondary indexes were inspected, but archived original captures were not recovered during this pass.
- Original publisher or broadcaster carriers for B01-B26. The preservation transcripts are usable for discovery and provisional evidence, but primary-carrier recovery remains open.

No A/B URL failed. The unresolved status is about provenance level, archive completeness, or lawful access—not a failed attempt to bypass access controls.

## Acceptance-criteria status

- [x] Existing repository conventions inspected.
- [x] All A01-A15 seed pages acquired.
- [x] Additional high-relevance HarryPotter.com pages A16-A37 acquired.
- [x] All B01-B10 seed transcripts acquired, including the resolved B02 URL.
- [x] Additional transcripts B11-B26 acquired.
- [x] Manifest, provenance metadata, authority, relevance tags, hashes, and local paths produced.
- [x] No book drafting, evidence extraction, taxonomy refactor, or deletion performed.
- [ ] Exhaustive enumeration of every paginated HarryPotter.com Rowling Original independently verified.
- [ ] Accio Quote thematic and chronological indexes exhausted.
- [ ] Original publisher/broadcaster carriers recovered for the transcript corpus.
- [ ] Old `jkrowling.com` primary captures recovered.
- [ ] Published and physical legacy sources acquired from legitimate editions.

## Recommended next extraction batch

1. A16 Peeves, A17 Pensieve, A18 Hogwarts School Subjects, and A19 King's Cross Station.
2. A01-A09 for founders, admissions, transport, portraits, ghosts, House space, relics, and grounds.
3. A20-A28 for Sorting, student life, communications, security, and comparative school context.
4. B01-B04 and B11-B20 after claim-level transcript attribution and original-carrier checks.
5. B05-B10 and B21-B26 only after multi-part and duplicate-carrier grouping is preserved.

Do not merge any extracted statement into the 1,314-entry evidence seed until that separate phase is explicitly authorized.

---

## Targeted runes, potions, plants, and early-culture supplement

**Retrieval date:** 2026-09-15

**Extraction completed:** 2026-09-16

**Authorization:** Research/evidence-layer task to audit, acquire, and extract the identified official sources without editing `authoring/` or Chapter 1.

### Audit result

The Pensieve source was already present as A17 and fully extracted. Its four entries already distinguish:

- the generations of Hogwarts heads who used it;
- the carved-stone basin, modified Saxon runes, and explicit pre-Hogwarts date;
- the unsubstantiated Founders discovery legend;
- the burial custom associated with the artefact.

No A17 acquisition or evidence changes were required.

The eight other named Rowling Original pages were absent. One official editorial added a distinct, explicitly speculative Ancient Runes claim. All nine missing carriers were fetched from their canonical public HTTPS URLs, returned non-empty official page data, and had unique body hashes, canonical URLs, logical IDs, and local paths relative to the existing 63-source manifest.

| ID | Title | Authority | Class | Evidence entries |
|---|---|---:|---|---:|
| A38 | The Potter Family | A | `official_rowling_original` | 5 |
| A39 | Potions | A | `official_rowling_original` | 4 |
| A40 | Cauldrons | A | `official_rowling_original` | 4 |
| A41 | Mr Ollivander | A | `official_rowling_original` | 3 |
| A42 | Wand Woods | A | `official_rowling_original` | 5 |
| A43 | Fourteenth Century – Seventeenth Century | A | `official_rowling_original` | 4 |
| A44 | Seventeenth Century and Beyond | A | `official_rowling_original` | 3 |
| A45 | Technology | A | `official_rowling_original` | 4 |
| F01 | The Hogwarts classes that you might have forgotten about | E | `secondary_reference` | 2 |
| **Supplement total** |  |  |  | **34** |

The Rowling Original page “Alchemy” was also audited because F01 links to it. Its authorial note discusses real-world alchemical symbolism and Rowling's imagined sixth- and seventh-year study. The institutional proposition is already represented by A18-003, and the page does not support F01's distinct editorial statement that alchemy has roots in potion-making. It was therefore not acquired as a repetitive carrier. Other modern listicles and derivative potion pages were likewise excluded where they added no distinct historical, institutional, or source-critical evidence.

### Authority and chronology decisions

- A38-A45 retain authority A and `official_rowling_original`.
- F01 is stored separately under `official-editorial`, retains authority E and `secondary_reference`, and is not counted as Rowling Original Writing.
- F01's Bronze/Iron Age runes hypothesis and alchemy description are `weak_context_only`, `later_editorial_note`, and low confidence. Its speculative language is preserved in both entries.
- A38's Linfred material is twelfth-century, post-foundation comparison rather than pre-Hogwarts evidence.
- A43 and A44 are later, non-British comparative history and cannot establish early British or Hogwarts practice.
- Undated technical descriptions in A39, A40, and A42 remain `unknown_or_uncertain` where the sources do not establish origins.
- A45's pre-Statute transport claim is not narrowed to the tenth century.

### Incremental acquisition support

The existing acquisition runtime now supports selected-ID append operations. It rejects logical-ID, URL, and snapshot-path collisions, writes snapshots and the manifest atomically, and assigns explicit profiles to Rowling Originals, preservation transcripts, and official editorials. Queue initialization appends newly manifested units while preserving completed-unit state and history. The validator and queue route F-family official editorials to their own canonical source group.

### Corpus outcome

- External manifest: 72 records — 45 authority A Rowling Originals, 26 authority D preservation transcripts, and 1 authority E official editorial.
- External evidence: 72 source units and 276 evidence entries.
- Full evidence corpus: 299 source units and 1,717 evidence entries.
- Supplement contribution: 9 source units and 34 evidence entries.

All nine supplement units completed through the canonical claim/stage/complete queue. Duplicate candidates were reviewed and recorded per entry. Canonical duplicate, entry, source, and tag indexes plus the normal seed and appendix artifacts were regenerated.

### Validation evidence

- Canonical source YAML validator: passed.
- Repository `unittest` suite: 69 tests passed.
- Focused acquisition and queue `pytest` suite: 47 tests passed.
- External queue: 72 done, 0 pending, 0 in progress, 0 blocked.
- `git diff --check`: clean.
- `authoring/`: no changed paths.
