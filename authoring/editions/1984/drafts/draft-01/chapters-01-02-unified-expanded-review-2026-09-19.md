# Chapters 1–2 Unified Expanded Edition Review

Status: AUDIT COMPLETE — APPROVED BOUNDED REVISION IMPLEMENTED; EDITORIAL REVIEW PENDING

Date: 2026-09-19

## Chapter 1 unified-narrative follow-up

The subsequently approved Chapter 1 instruction produced
`chapters/01-before-hogwarts/draft-revision-06.md`. It supersedes revision 05's
visible editorial-note treatment for Chapter 1 only: eligible expanded-corpus
material is integrated into continuous historical prose, while source
authority, carrier dates and event chronology remain in hidden metadata. The
ending was condensed, the magical-creature/fear interpretation was refined,
and no audio or workflow state was advanced.

## Implementation record

The approved revision produced Chapter 1 `draft-revision-05.md` and Chapter 2
`draft-revision-04.md` without replacing the reviewed source versions. UE12-01,
UE12-02, UE12-03, UE12-05, UE12-06, UE12-07 and UE12-09 were implemented.
UE12-04 was included only as a brief attributed external editorial note.
UE12-08 remains deferred because the two candidate paragraphs perform distinct
work. Dossiers, outlines and access metadata were updated, and versioned fact,
style and continuity audits were recorded for both chapters. Workflow states
and audio were not advanced or regenerated.

## 1. State verified

### Review targets

The active working pointers identify these as the latest chapter texts:

- Chapter 1: `chapters/01-before-hogwarts/draft-revision-04.md`, SHA-256
  `af9a4cc9301a6353c41fee76318bc6589d09c8d157a1dec798a4329306c8f4bc`.
  The Chapter 2 preparation package calls this the “latest working final”, and
  the existing Chapter 1 narration run also used this path and hash.
- Chapter 2: `chapters/02-the-four-founders/draft-revision-03.md`, SHA-256
  `8b38b87155d796b8ae80d433a074b38a0ac6bab735333ada9588b1fd80f43393`.
  The versioned Chapter 2 audio record identifies this exact path and hash as
  its approved source.

There is a workflow-state discrepancy. `project-control/chapter-status.yaml`
records both chapters as `drafted`, not `audited` or `editor_approved`.
Accordingly, this report treats the two files as the current working finals,
not as formally editor-approved manuscripts. The Draft-01 README is also stale:
it still says that no chapter exists.

### Governing authorities

- Project-wide edition policy: `authoring/editorial-policy.md`.
- Legacy-path operational policy:
  `authoring/editions/1984/editorial-policy.md`.
- Edition bible: `authoring/editions/1984/edition-bible.md`.
- Authoritative twenty-chapter structure:
  `authoring/editions/1984/table-of-contents.yaml`.
- Chapter workflow: `authoring/shared/chapter-workflow.md`.
- Shared evidence policy: `authoring/shared/evidence-policy.md`.
- Runtime contract: `authoring/runtime/authoring-contract.md`.
- Research interface: `authoring/shared/research-interface.md`.
- Latest edition style guide: `authoring/editions/1984/style-guide.md`.
- Active Draft-01 style authority:
  `authoring/editions/1984/drafts/draft-01/style-lock.md`.

The Unified Expanded Edition policy is active in the working tree. The project
policy expressly removes 1984 as an evidence cutoff while retaining the
reconstructed 1984 narrative as the literary foundation. The table of contents,
edition bible, shared evidence policy, workflow, runtime contract, style guide,
and style lock all reflect that model. The legacy `authoring/editions/1984/`
path therefore remains valid and does not restrict source dates.

Implementation is incomplete at chapter level. Chapter 1's dossier and outline
do not label passages as reconstructed Bagshot narrative or later editorial
additions, and Chapter 2's outline distinguishes source access but does not
consistently assign those two required authorship layers. The prose likewise
contains post-1984 evidence in the main narrative with only hidden comments—or
no access marker at all. This is the principal policy gap found by the audit.

### Repository status

The working tree was already dirty when the audit began and remained so. The
final pre-report snapshot showed branch `codex/cursed-child-source-8`, twenty
modified tracked paths and nine untracked paths. These include the active
policy migration, Chapter 2 drafts and instructions, audio records, a Chapter 3
workspace, and the untracked open-question overlay. No pre-existing file was
modified or discarded during this audit. This report is the sole new artifact.

## 2. Corpus-search record

### Coverage

The compact canonical entry index was screened in full: 1,828 entries across
348 source units and 348 canonical source YAML files. Classification coverage
was:

| Classification | Indexed entries |
| --- | ---: |
| `original_book_core_candidate` | 13 |
| `pre_1984_historical_candidate` | 368 |
| `harry_era_confirmation` | 554 |
| `later_editorial_note` | 784 |
| `post_1984_excluded_from_original` | 76 |
| `unknown_or_uncertain` | 33 |

Searches covered founder names and relics; founding and school origins;
pre-Hogwarts education; ancient and medieval craft; magical–Muggle relations;
persecution and secrecy; Pensieve, runes, wandmaking, broom history, potions,
plants and cauldrons; admissions; the Sorting Hat; house-elves; and every
`later_editorial_note` or `post_1984_excluded_from_original` entry whose tags,
title, placement or note could bear on Chapters 1–2.

The existing Chapter 1 evidence selection records 79 inspected candidates,
including complete later passes over A17 and A38–A45. The Chapter 2 preparation
package records direct review of the principal Binns and Hat passages and the
complete A02, A07 and A08 snapshots. This audit repeated the index search under
the unified policy, opened the exact canonical YAML for every material new
candidate, and checked the original local source for the two strongest new
proposals:

- Helena Ravenclaw's confession, *Deathly Hallows* ch. 31, PDF p. 3500,
  directly checked against the local PDF.
- The Hufflepuff house-elf statement, B10 “House-elves discussion”, transcript
  line 57, directly checked against the complete preserved snapshot.

The untracked enriched open-question overlay was consulted only as a discovery
and control aid. It is not canonical evidence. Its guide still says house-elf
material is forbidden from manuscript use, which reflects the older rule and
conflicts with the active edition bible: reconstructed Bagshot must remain
silent, but the unified edition may address the subject in an identifiable
later editorial addition. The active policy governs.

### Limitations

- The final citation and reader-facing editorial-note system remains undefined.
  This report therefore proposes treatments, not final typography.
- The compact index exposes all canonical entries, but relevance searches
  depend on existing titles, tags and placement metadata. Broad keyword and
  classification scans were used to reduce the risk of stale placement labels.
- No evidence record was invented or repaired. A few known research-layer
  issues—such as A30 snapshot material not represented by an entry and the
  one-page canonical locator for `dh-ch07-006`—remain authoring observations.
- Companion books are later real-world carriers of in-world works. Where the
  corpus does not establish the exact edition available to Bagshot, this report
  treats access as unresolved rather than automatically granted or denied.

## 3. Chapter 1 findings — *Before Hogwarts*

### Overall judgement

Chapter 1 remains structurally strong. Its movement from documentary scarcity,
through craft and shared material culture, to concealment and the institutional
threshold is clear and consistent with the refined style lock. Its best passages
make evidence concrete without pretending to recover a lost curriculum. No new
post-1984 event belongs in this chapter merely because the unified policy makes
it eligible.

The essential problem is authorship-layer attribution. Several substantial
passages depend on official retrospectives published in 2015 or on later
posthumous commentary, yet read continuously as reconstructed Bagshot prose.
The chapter often marks chronology well—Linfred is explicitly placed in the
twelfth century—but event date is not the same as narrator access. Under the
active policy, a later source about an earlier event needs either evidence of
Bagshot access or an identifiable editorial voice.

### Evidence and access findings

1. **Pensieve and Saxon runes (lines 59–75).** `ext-a17-002` and
   `ext-a17-003` derive from the Authority-A official “Pensieve” article,
   published 2015-08-10. The described object predates Hogwarts, while the
   discovery story is expressly unsubstantiated. The prose preserves the
   fact/legend distinction well, but it does not identify the passage as a
   later editorial addition.
2. **Roman and medieval wandcraft (lines 98–116).** The shop sign in
   `ps-ch05-007` is later observed public evidence, while `ext-a41-001`
   (Roman-arrival family belief) and `ext-a42-001`–`002` (wood selection and
   Geraint Ollivander) are 2015 official retrospectives. The passage correctly
   distinguishes belief from history, but only a later editor is demonstrably
   entitled to the later-source particulars.
3. **Linfred and later informal learning (lines 156–198).**
   `ext-a38-001`–`002` are Authority-A official prose published 2015-09-21;
   `beedle-fm-002` and `beedle-ch04-001` come from an edition whose translation,
   posthumously discovered Dumbledore commentary and publication apparatus are
   post-1984. The text marks Linfred's twelfth-century chronology but not the
   later discovery channel. The Beedle paragraph is especially vulnerable
   because its generalisation is attributed in the source to Dumbledore.
4. **Shared cauldron and transport history (lines 220–245).**
   `ext-a45-001` and `ext-a40-001`–`002` are Authority-A 2015 retrospectives.
   Their broad pre-Statute or undated subject matter does not make them Bagshot
   knowledge. The cauldron passage already contains the right chronological
   restraint and can survive almost unchanged inside a later editorial layer.
5. **Companion-book medieval evidence (lines 77–96, 118–125, 256–300).**
   `qtta-ch01-002` and `fb-ch02-001`–`004` are public in-world historical works,
   but the corpus does not establish which edition or wording was available by
   1984. Unlike the 2015 official retrospectives, these may plausibly represent
   pre-existing public scholarship. The dossier should record an access ruling;
   the present evidence does not justify an essential prose correction.

### Style, evidence restraint and boundary findings

- Lines 312–318 infer that “people, messages and supplies” crossed between the
  castle and surrounding communities. `cos-ch09-003` supports seeking and
  bringing pupils, but not messages, supplies or early operating logistics.
  The sentence also enters Chapter 3's early-operation territory.
- Lines 356–370 develop generic consequences of collective instruction and
  institutional disagreement. The style calibration previously accepted
  modest ordinary-process synthesis, so this is not an evidence error; however,
  the passage now crowds the Chapter 2 and Chapter 3 boundary. It can be reduced
  without losing the chapter's institutional conclusion.
- Lines 374–375 contain a mechanical line break after “does not”. This has no
  prose significance, but it is an avoidable narration and copy-edit hazard.
- The repeated contrast between scattered practice and institutional
  continuity is purposeful rather than accidental. The chapter should not be
  broadly shortened merely for variety.

## 4. Chapter 2 findings — *The Four Founders*

### Overall judgement

Chapter 2 has a sound four-part argument: sparse biography, shared purpose,
distinct educational ideals, and the limit created by Slytherin's ancestry
restriction. It respects the House-development and departure boundaries and
handles the Hat according to the settled Draft-01 rule. Its compactness is a
strength.

The unified corpus supplies two material additions. Helena Ravenclaw's
testimony changes what can now be said about Rowena's family and the diadem.
The Hufflepuff house-elf statement qualifies the chapter's account of Helga's
inclusiveness. Both were previously withheld because of post-1984 access or the
reconstructed book's required silence; both can now enter only through the
later editorial layer.

### Newly eligible evidence

#### Rowena and Helena Ravenclaw

- **Evidence:** `dh-ch31-002`.
- **Exact locator:** *Harry Potter and the Deathly Hallows*, ch. 31, PDF
  p. 3500; extracted lines 163–188 and 198–257; anchors “Who's the ghost of
  Ravenclaw Tower?” through “he wears his chains as an act of penitence”.
- **Provenance:** direct first-person ghost testimony from Helena Ravenclaw,
  disclosed privately to Harry during the Battle of Hogwarts.
- **Event chronology:** founder era: Helena was Rowena's daughter, stole the
  diadem, and says Rowena concealed the loss even from the other founders;
  Rowena later became fatally ill and sought her daughter.
- **Knowledge access:** later discovery about an earlier event. The disclosure
  occurred in 1998 and was unavailable to the reconstructed narrator in 1984.
- **Authority and limit:** high-confidence canonical testimony, but a single
  interested witness without documentary corroboration from Rowena or another
  founder.
- **Why Chapter 2:** it is the corpus's only substantial evidence about
  Rowena's family and a consequential choice she made as a person. The later
  Horcrux history and the relic's destruction belong elsewhere.

This evidence does not erase the genuine 1984 uncertainty. The reconstructed
paragraph may still report the diadem as a lost school tradition. A later
editorial paragraph should then identify Helena's disclosure as the later
correction and retain the testimony's limits.

#### Helga Hufflepuff and house-elves

- **Evidence:** `ext-b10-001`.
- **Exact locator:** B10, “House-elves discussion”, complete preserved
  PotterCast transcript, line 57; anchor “Hufflepuff did what was the most moral
  thing to do at that time” through “they can work and not be abused.”
- **Provenance:** J. K. Rowling interview, December 2007/January 2008,
  preservation transcription hosted by Accio Quote; source class
  `preservation_transcription`, Authority D.
- **Event chronology:** claimed founder-era treatment of house-elves at
  Hogwarts.
- **Knowledge access:** later authorial interpretation about an earlier event;
  not Bagshot-accessible and not an in-universe contemporary record.
- **Authority and limit:** medium. The statement supplies no documentary
  source, precise date or institutional mechanism, and explicitly frames
  Hufflepuff's conduct as moral interpretation: refuge and improved working
  conditions rather than abolition or wages.
- **Why Chapter 2:** it directly qualifies Helga's remembered willingness to
  teach broadly and treat pupils alike. It reveals a limit in her inclusiveness
  as a founder. A fuller history of Hogwarts house-elf labour belongs in a
  later social or institutional chapter.

The addition must be short and clearly editorial. It should not turn Chapter 2
into the general history of house-elf servitude, and it must not breach the
documented silence of the reconstructed Bagshot narrative.

### Attribution, style and boundary findings

- Lines 41–45 say the partnership endured “despite different standards for
  pupils”. The dossier explicitly leaves unresolved whether all preferences
  existed from the beginning or acquired force later. “Despite” subtly fixes
  the chronology. The sentence should instead say that later tradition places
  differing standards within the remembered partnership.
- Lines 71–78 present the diadem tradition in reconstructed prose with no
  reader-identifiable later layer. The underlying evidence is recorded in
  1998, and the newly eligible Helena testimony now requires an explicit
  reconstructed-tradition/later-correction structure.
- Lines 80–88 use 2015 Authority-A retrospective exposition for Gryffindor's
  swordsmanship and the sword's manufacture. The hidden `source-access`
  comment is good working metadata but does not make the later editorial voice
  identifiable to a reader. The paragraph should become a compact later
  editorial addition or be reduced to claims independently documented as
  public before 1984.
- Lines 49–51 refer to teaching associated with the founders' respective
  Houses. This is supported by Hat tradition but approaches Chapter 4's
  institutional subject. It can remain as a minimal limit statement; it should
  not be expanded into division of labour.
- Lines 127–130 end by saying the founders gave the undertaking “a home” and
  foregrounding the choice of that home. Chapter 1 has already explained the
  remote site, and Chapter 3 owns site choice, construction and early operation.
  The ending should return to the shared educational purpose and ask how it
  became a functioning school, without asserting or previewing the home-choice
  narrative.

## 5. Proposed change register

Evidence-backed corrections and unified-edition integrations are listed before
optional style changes.

### UE12-01 — Classify Chapter 1's later-source passages

- **Chapter/passage:** Chapter 1, lines 59–75, 98–116, 156–198 and 238–245.
- **Problem:** 2015 official retrospectives and post-1984 commentary are voiced
  as reconstructed Bagshot knowledge.
- **Evidence:** `ext-a17-002`–`003` (A17, 2015-08-10); `ext-a38-001`–`002`
  (A38, 2015-09-21); `ext-a40-001`–`002`, `ext-a41-001`,
  `ext-a42-001`–`002` (A40–A42, 2015-08-10); `beedle-fm-002`,
  `beedle-ch04-001` (Beedle PDF pp. 4 and 48). Events range from antiquity and
  the founder era through the twelfth century; access class is later discovery
  about earlier events, with family belief, tradition and Dumbledore's
  generalisation preserved separately.
- **Treatment:** retain the useful facts but group them into a small number of
  identifiable later editorial paragraphs. Add the required event chronology,
  publication date and access class to the Chapter 1 dossier before prose
  revision.
- **Concrete direction:** preserve the existing chronological pivots and add a
  simple editorial cue such as “Later accounts add a little to this sparse
  record” at each necessary cluster. Do not repeat a note before every fact.
- **Priority:** essential.
- **Cross-chapter/audio:** none to Chapter 3 beyond keeping its boundaries;
  any accepted prose change invalidates the current Chapter 1 narration as a
  listening copy of the revised text.

### UE12-02 — Remove unsupported early-operation detail from Chapter 1

- **Chapter/passage:** Chapter 1, lines 312–318, especially “people, messages
  and supplies crossed the distance”.
- **Problem:** the cited source establishes pupil recruitment and remoteness,
  not messages, supplies or operating logistics; the details also belong to
  Chapter 3.
- **Evidence:** `cos-ch09-003`, *Chamber of Secrets* ch. 9, PDF p. 407. Event:
  founder era. Access: existing reconstructed historical framework.
- **Treatment:** correction to the reconstructed narrative.
- **Concrete direction:** retain only the supported point that remoteness did
  not prevent the founders from seeking and bringing pupils to the school.
- **Priority:** essential.
- **Cross-chapter/audio:** protects Chapter 3's early-operation scope; revised
  wording would require a future Chapter 1 audio version.

### UE12-03 — Add Helena Ravenclaw's later testimony

- **Chapter/passage:** Chapter 2, after lines 71–78.
- **Problem/opportunity:** the current text preserves only the old lost-diadem
  tradition; later testimony supplies the only substantial founder-family
  evidence and corrects that tradition without erasing what was uncertain in
  1984.
- **Evidence:** `dh-ch31-002`, *Deathly Hallows* ch. 31, PDF p. 3500. Founder-
  era events; direct testimony recorded in 1998; later discovery about earlier
  events; uncorroborated first-person account.
- **Treatment:** clearly identified later editorial paragraph immediately after
  the reconstructed tradition, not a separate addendum.
- **Sample:** “A later disclosure altered this much of the traditional account.
  In 1998 the Grey Lady identified herself as Helena Ravenclaw and said that she
  had stolen her mother's diadem; according to Helena, Rowena concealed the loss
  even from her fellow founders and sought her daughter only when fatally ill.
  The account is unique and personal rather than documentary, but it supplies
  the first direct explanation of the relic's disappearance.”
- **Priority:** essential.
- **Cross-chapter/audio:** reserve the Albanian hiding place, Horcrux history
  and destruction for later relic/war treatment. Acceptance requires a new
  versioned Chapter 2 narration; do not overwrite the recorded audio.

### UE12-04 — Qualify Hufflepuff's inclusiveness with the later house-elf account

- **Chapter/passage:** Chapter 2, after lines 65–69.
- **Problem/opportunity:** Helga's pupil-facing inclusiveness is accurate but
  risks becoming a complete moral portrait. The newly eligible account gives a
  significant limit and a distinct founder-era action.
- **Evidence:** `ext-b10-001`, B10 “House-elves discussion”, transcript line 57.
  Founder-era claim; 2007/2008 Authority-D preservation transcription; later
  authorial interpretation about an earlier event.
- **Treatment:** short, explicitly later editorial note or paragraph. Keep it
  separate from the reconstructed narrative because the edition bible requires
  Bagshot's documented house-elf silence.
- **Sample:** “Later authorial commentary adds a less comfortable qualification.
  Hufflepuff is said to have brought house-elves to Hogwarts as a refuge from
  worse abuse and to have offered better conditions, not freedom or wages. The
  claim survives only in a later interview transcript, but it cautions against
  treating her broad educational offer as a complete account of equality.”
- **Priority:** worthwhile.
- **Cross-chapter/audio:** a fuller history of labour and servitude must be
  assigned later under the twenty-chapter structure. Acceptance requires a new
  versioned Chapter 2 narration.

### UE12-05 — Make Gryffindor's later sword evidence reader-identifiable

- **Chapter/passage:** Chapter 2, lines 80–88.
- **Problem:** the prose acknowledges “later accounts”, but the paragraph still
  sits in the reconstructed narrative; a hidden comment alone does not satisfy
  the unified edition's reader-facing attribution rule.
- **Evidence:** `ext-a08-001` and `ext-a08-003`, Authority-A official
  retrospective, 2015-08-10, text anchors beginning “The Sword of Gryffindor
  was made” and “The question of why a wizard would need a sword”. Founder-era
  manufacture and swordsmanship; later discovery about earlier events.
- **Treatment:** clearly identified later editorial paragraph. Retain the
  limited manufacture and martial-skill claims; do not import later Hat
  appearances or silently resolve goblin ownership.
- **Priority:** essential.
- **Cross-chapter/audio:** fuller worthiness and Hat mechanics remain Chapter 4
  or Chapter 13 material; ownership dispute remains for a later public-history
  treatment.

### UE12-06 — Preserve uncertainty about when founder preferences operated

- **Chapter/passage:** Chapter 2, lines 41–45.
- **Problem:** “despite different standards for pupils” implies the later Hat
  preferences are proven contemporaneous conditions throughout the years of
  harmony.
- **Evidence:** `cos-ch09-004`, *Chamber of Secrets* ch. 9, PDFs pp. 407–408;
  `gof-ch12-002`, PDF pp. 1093–1094; `ootp-ch11-003`, PDF pp. 1765–1767.
  Founder-era subject; Binns historical summary plus later ceremonial
  testimony. The dossier explicitly leaves the timing unresolved.
- **Treatment:** correction to reconstructed narrative.
- **Concrete direction:** replace the causal “despite” construction with an
  attribution: later Hat tradition places differing standards within the
  remembered partnership, without dating their adoption.
- **Priority:** essential.
- **Cross-chapter/audio:** Chapter 4 may later examine when preferences became
  institutional House criteria.

### UE12-07 — Restore the Chapter 2/3 handoff

- **Chapter/passage:** Chapter 2, lines 127–130.
- **Problem:** the ending repeats Chapter 1's site theme and begins Chapter 3's
  home/site-choice argument rather than completing Chapter 2's people-and-
  purpose argument.
- **Evidence:** no new factual evidence; this is a boundary correction governed
  by the table of contents and style lock.
- **Treatment:** revise the conclusion, without editing Chapter 3.
- **Sample:** “Their differences had not prevented years of common work. The
  next question is how four founders with one educational purpose gave it the
  structure and daily practice of a functioning school.”
- **Priority:** worthwhile.
- **Cross-chapter/audio:** record this as the Chapter 3 entry point; any accepted
  wording change requires new Chapter 2 audio.

### UE12-08 — Reduce Chapter 1's late boundary drift

- **Chapter/passage:** Chapter 1, lines 356–370.
- **Problem:** generic classroom effects and durable founder disagreement add a
  second institutional threshold after the chapter has already made its central
  point; they partially pre-empt Chapters 2–3.
- **Evidence:** `cos-ch09-003` supports gathering and educating pupils but not
  the specific pedagogical sequence. The current style calibration permits
  modest synthesis, so this is not a factual correction.
- **Treatment:** optional condensation. Keep recruitment and collective
  learning as consequences, but remove repeated setup for founder disagreement.
- **Priority:** optional stylistic preference.
- **Cross-chapter/audio:** would sharpen the Chapter 2 entrance; revised prose
  would require a new Chapter 1 listening copy.

### UE12-09 — Repair the Chapter 1 mechanical line break

- **Chapter/passage:** Chapter 1, lines 374–375.
- **Problem:** “does not / guarantee” is split across a hard line break in a way
  that can produce an unnatural narration pause.
- **Evidence:** not applicable.
- **Treatment:** copy edit only.
- **Priority:** optional.
- **Cross-chapter/audio:** audiobook implication only if the renderer respects
  the hard break audibly.

## 6. No-change findings

- **Sorting Hat testimony:** keep the current use of `gof-ch12-002` and
  `ootp-ch11-003`. The active style lock settles the Hat as a continuous
  tradition whose later performances can preserve founder themes, while exact
  later lyrics and performances remain unavailable to Bagshot. This decision
  should not be reopened.
- **Godric's Hollow:** retain the birthplace claim from `dh-ch16-003`. The style
  lock specifically directs the reconstructed author to integrate facts from
  her own *A History of Magic* rather than cite herself in the third person.
- **Slytherin's restriction:** retain the distinction between House preference
  and a proposed school-wide ancestry bar, and retain the statement that the
  restriction was Slytherin's position rather than adopted Hogwarts policy.
- **Chamber confirmation:** `cos-ch17-006`, `ext-a01-001` and later evidence
  establish more than the 1984 legend, but the full Chamber, departure and
  consequences belong to Chapter 5. Do not use later confirmation to rewrite
  Chapter 2's endpoint.
- **Slytherin's line, Parseltongue and locket:** `hbp-ch10-006`,
  `hbp-ch13-002`, `hbp-ch13-007`, `hbp-ch17-006` and `hbp-ch20-005` were
  reconsidered. They do not materially improve Chapter 2's argument enough to
  justify a disproportionate founder-lineage excursion; reserve them for the
  rift, Chamber or relic history.
- **Hufflepuff's cup:** `ext-a07-005`, `hbp-ch20-005`, `dh-ch26-006` and later
  destruction evidence were reconsidered. The portrait, private heirloom claim
  and later Horcrux history have different provenance and are better handled in
  Chapters 12 or 17. Do not restore the removed cup catalogue to Chapter 2.
- **Later sword appearances and fate:** `cos-ch18-004`, `dh-ch19-004`,
  `dh-ch23-003`, `dh-ch26-007`, `dh-ch33-007` and `dh-ch36-003` do not belong
  in the founder portrait. Retain only the bounded founder-era association.
- **Diadem after its theft:** `dh-ch31-003` and `dh-ch31-007` explain later
  recovery, concealment and destruction. They belong to later history, not the
  Chapter 2 biographical correction.
- **Hogwarts admissions instruments:** `ext-a03-001` remains Chapter 3 material.
  It concerns the completed castle and founder-established mechanism, not the
  people-and-purpose boundary of Chapter 2.
- **Ancient druidic vine-wand tradition:** `ext-a42-003` was reconsidered under
  the unified policy. Its undated modern carrier and uncertain continuity add
  less than the selected Roman and medieval wandcraft evidence; leave it out.
- **International and modern education comparisons:** `ext-a28-001`–`004`,
  `gof-ch09-002`, `gof-ch11-004`, and modern home-education interviews do not
  establish pre-foundation British practice. Eligibility does not cure the
  chronology or chapter-fit problem.
- **Later events in Chapter 1:** Harry-era childhood, modern admissions and
  post-1984 school developments were screened and deliberately excluded. They
  illuminate later systems, not the world before Hogwarts.
- **Existing prose that works:** Chapter 1's opening documentary distinction,
  the 962 broom caveat, Linfred's explicit post-foundation pivot, the shared-
  landscape sequence and the contingent close should be preserved. Chapter 2's
  Binns/Hat source hierarchy, Hufflepuff/Ravenclaw contrast, bounded treatment
  of Gryffindor's opposition, and refusal to invent Ravenclaw's admissions view
  should also remain.

## 7. Contradictions, unresolved questions and rejected inferences

### Contradictions and tensions to preserve

- Pre-Statute mingling (`ext-a08-003`, `ext-a45-001`) and founder-era fear and
  persecution (`cos-ch09-003`) can coexist, but the corpus does not map their
  regional or social variation.
- Binns records years of harmony before disagreement; Hat tradition remembers
  distinct preferences and says they initially caused little strife. The
  evidence does not date the origin or hardening of Slytherin's rule.
- Hufflepuff's remembered broad offer to pupils and the later house-elf account
  concern different groups. They should be set beside one another, not silently
  harmonised into either sainthood or hypocrisy.
- Helena's testimony corrects the old diadem tradition but remains one private
  witness's account. It should not be promoted to an omniscient reconstruction
  of Rowena's motives.
- The official A08 sword narrative and Griphook's ownership account remain a
  cultural dispute. Chapter 2 does not need to decide it.

### Unresolved questions

- Which of the companion-book historical passages, in their present wording,
  were available to Bagshot by 1984?
- What records underlie Binns's founding history?
- When did each founder's pupil preference take institutional form?
- Was the Hat tradition's personal friendship detail public before 1984 beyond
  the settled assumption of recurring themes?
- What reader-facing device will distinguish later editorial additions without
  fragmenting the book?
- Where in the twenty-chapter structure should the unified edition give the
  fuller history of Hogwarts house-elf labour?
- Does Helena's description of Rowena's fatal illness belong only in Chapter 2,
  or require a later cross-reference in the chapter on school memory and
  ghosts?

### Rejected inferences

- Hogwarts was the first, only, national or universally accessible magical
  school in Britain.
- The 962 broom record necessarily predates Hogwarts.
- The Pensieve's runes performed magic, or the founders found the object at the
  building site as a documented fact.
- Medieval craft evidence proves a founder-era curriculum or division of
  teaching labour.
- Hufflepuff's willingness to teach broadly proves universal Hogwarts
  admission or equality across every social relationship.
- Helena's later confession was known to Bagshot, Flitwick, Dumbledore or the
  school at large before 1998.
- Slytherin's ancestry position became official school policy.
- Later House stereotypes provide complete founder personalities.
- Later relic use, Horcrux history or battle events explain the founders'
  intentions.

## 8. Recommended bounded revision sequence

1. **Retrofit authorship/access metadata only.** Update the Chapter 1 dossier
   and Chapter 2 preparation material so every proposed passage is labelled
   reconstructed Bagshot or later editorial addition, with event chronology,
   carrier date and access class. Do not alter prose in this step.
2. **Make the essential access corrections.** Convert the Chapter 1 A17,
   A38 and A40–A42 clusters and the Chapter 2 A08 sword paragraph into a small
   number of reader-identifiable later editorial passages. Resolve the
   companion-book access question conservatively.
3. **Add the Rowena correction.** Insert one later editorial paragraph from
   `dh-ch31-002`, preserving the earlier tradition and reserving later relic
   history.
4. **Correct evidence and chronology overreach.** Remove Chapter 1's
   unsupported messages/supplies detail and qualify Chapter 2's implied timing
   of founder preferences.
5. **Repair the Chapter 2/3 boundary.** Replace the home-choice ending with a
   people-and-purpose conclusion that hands off to the functioning school.
6. **Consider, but do not bundle automatically, the Hufflepuff note.** Because
   `ext-b10-001` is Authority D and touches the edition's deliberate Bagshot
   silence, approve its exact scope separately. If accepted, keep it brief and
   explicitly editorial.
7. **Perform a final bounded style pass.** Decide whether to condense Chapter
   1's late institutional synthesis and fix the mechanical line break. Preserve
   all passages listed above as working.
8. **Audit before audio.** Run fact, style and continuity audits on the revised
   texts before changing workflow state. If prose is approved, create new
   versioned audio outputs and reproducibility records; never overwrite the
   existing Chapter 1 or Chapter 2 recordings.

The smallest coherent first revision set is UE12-01, UE12-02, UE12-03,
UE12-05, UE12-06 and UE12-07. UE12-04 should receive a separate editorial
decision because it is historically important but rests on lower-authority
later commentary. UE12-08 and UE12-09 are optional polish.
