# Open questions — Codex drafting and research guide

This guide accompanies [`hogwarts-open-questions-enriched.yaml`](hogwarts-open-questions-enriched.yaml). It preserves all **386** original question IDs, questions, original tags, original statuses, sources and related-entry references, then adds research leads, provenance controls, chapter destinations and individualized two-paragraph instructions. The **23** identified source leads are leads, not 23 claims of resolved questions; all original statuses stay `open`. Questions not specifically verified remain **research pending**, not falsely stamped “no source exists.”

## Two paragraphs to apply in every drafting iteration

At the start of each new chapter iteration, open the current approved chapter outline and read only questions whose primary or secondary destination matches that chapter. Confirm the local files and source YAML rather than treating this enriched backlog as new canon. Research specific leads (original seven-novel PDF, three companion PDFs, existing evidence YAML, first-party Rowling material, then carefully labelled secondary discovery sources), log the exact entry ID, chapter, page or archival URL and what the source actually supports. If the current project outline differs from the thematic placeholders, update the placement in the new working copy; do not silently renumber or edit the approved outline, completed chapters or source records.

Before drafting, assign each question one outcome: documented answer, narrower unresolved question, bounded historian inference, explicitly speculative flourish, later editorial annotation, excluded matter or repository-only cleanup. A pre-1984 event is NOT enough for the original book: the narrator must plausibly have access to it, and outside authorial explanations published later are not themselves proof of contemporary access. In the prose use questions sparingly, as purposeful transitions or source-critical observations; any creative details must be identifiable as conjecture and consistent with known magic, dates and voices. Never invent canon sources, direct quotations, official offices, rules, spells or precise dates. Append a per-chapter question-resolution log; leave original question status unchanged until exact evidence or an editorial decision is recorded.

## Destination register

Only Chapters 1–3 have established numbers in the latest conversation: *Before Hogwarts*, *The Four Founders*, *The Founding of Hogwarts*. The repository audit reports an incomplete 14-part order seed rather than an approved comprehensive book outline. Codex must read `project-control/book-seed-order.yaml` **and the current local chapter plan** to map all tentative destinations; do not assume the old alphabetical structure is an approved table of contents. The house-elf topic is preserved for omission awareness but is forbidden from manuscript use. One `source-processing-001` task is a repository QA item.

| Key | Destination | Questions |
|---|---|---:|
| `CASTLE` | Castle Architecture and Enchantments [tentative chapter] | 26 |
| `SORTING` | The Four Houses and Sorting [tentative chapter] | 4 |
| `C2` | Chapter 2 — The Four Founders | 7 |
| `C3` | Chapter 3 — The Founding of Hogwarts | 17 |
| `SECURITY` | Castle Defences and Security [tentative chapter] | 60 |
| `GROUNDS` | Grounds, Lake and Forest [tentative chapter] | 23 |
| `GHOSTS` | Ghosts, Portraits and Other Residents [tentative chapter] | 19 |
| `OMISSION` | Internal research only — excluded subject | 5 |
| `GOVERNANCE` | School Governance, Discipline and Care [tentative chapter] | 56 |
| `ACADEMICS` | Curriculum, Teachers and Examinations [tentative chapter] | 56 |
| `SPORT` | Quidditch and School Recreation [tentative chapter] | 28 |
| `LIBRARY` | Library, Archives and Sources [tentative chapter] | 26 |
| `LATER` | Later Editorial Notes [post-cutoff only] | 16 |
| `ADMISSIONS` | Admissions, Letters and Student Travel [tentative chapter] | 30 |
| `TRADITIONS` | Feasts and School Traditions [tentative chapter] | 12 |
| `CONTROL` | Project control — no manuscript destination | 1 |

## Evidence triage and writing choices

Use `research.search_first` IDs to look up exact links in `source_registry`. Direct textual evidence is not the same as a source lead, and an official modern recap is not interchangeable with the original in-universe text. When research cannot find an answer, append the search terms, local entry IDs and sources examined to `negative_search_log` before choosing a speculative treatment. Keep source `status: open` unless a specific verified answer or reviewed editorial disposition is recorded. In particular, an unknown exact rule is not a licence to write an imaginary Hogwarts bylaw.

A historian's unanswered question can be a strength when it explains a limitation (the ceiling’s maker, a tunnel’s builders, the start of a ceremony). A creative liberty may enrich interpretation — for instance, why a castle would keep a visible sky under a roof — but no imagined archival letter, invented quotation, fictional witness, definitive secret spell or invented exact date should appear as discovered evidence. Use enough questions to create curiosity, not so many that the chapter becomes a questionnaire.

## Selected newly identified source leads

| Question IDs | Source | What changes |
|---|---|---|
| `sorting-ceremony-001`, `sorting-ceremony-005`, `sorting-ceremony-006` | `W-SORT`, `W-SWORD` | Founders’ hat and Godric’s goblin-made sword have official treatments; fine details of ceremony and Hat/sword mechanism remain separate. |
| `castle-navigation-and-magical-architecture-009`, `-012`, `-015` | `W-MAP`, `W-PASSAGES` | Four mapmakers, tracking charm, concealment limitations, and seven passages / four known to Filch are sourced; date of official awareness remains open. |
| `castle-navigation-and-magical-architecture-025`, `protective-magic-and-security-102`, `-104` | `W-CHAMBER` | Chamber’s original and eighteenth-century entrances can be discussed without inventing architecture. |
| `ghosts-and-magical-residents-001` | `W-PEEVES` | The founder-era poltergeist and documented failed expulsion in 1876 furnish a pre-cutoff historical episode. |
| `castle-rooms-and-displays-013`, `-015` | `W-WILLOW`, `W-LUPIN` | The Willow and passage belong to a documented student accommodation, not an arbitrary ancient castle hazard. |
| `castle-navigation-and-magical-architecture-018`, `-019` | `W-MIRROR` | The mirror was at the castle long before 1991, but its exact arrival and maker remain unknown. The modified 1991 protection is later editorial context. |
| `feasts-and-school-traditions-003`, `-038` | `W-TRAIN`, `W-KINGS`, `P-BEEDLE` | School transport has a dated evolution; the ill-fated pantomime has a bounded historical placement under Dippet, without a known exact year. |

## Safety checks for Codex

1. Validate `questions` count and set of IDs against the original YAML; require **{len(Q)} of {len(Q)}** and no duplicates.
2. Preserve the seven original fields exactly (`id`, `topic`, `question`, `tags` as original prefix, `status`, `source`, `related_entries`).
3. No `C4` or later chapter numbers may be assigned until the current approved local outline supplies them.
4. Distinguish the founding-era artifact, the date it was discovered, the date a witness described it and what the circa-1984 narrator could have known.
5. Keep the house-elf topic outside the manuscript and the source-processing question outside narrative text.
6. Do not edit the prior source YAML, current draft or final Chapter 1 in this integration pass. Write research updates into a new working copy and log new decisions.
