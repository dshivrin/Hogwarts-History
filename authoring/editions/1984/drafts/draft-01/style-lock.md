# Draft 01 Style Lock

Status: ACTIVE DRAFT-01 AUTHORITY

This is the single operational prose contract for Draft 01. It derives from the
Unified Expanded Edition bible, editorial policy, and edition style guide, and resolves them
into working rules. Chapter 1 supplies the voice baseline; later chapters may
test the rules but may not change them locally.

## Core baseline

- **Audience:** Readers interested in the history and lore of Hogwarts; within
  the manuscript, address a magically educated readership.
- **Authorial premise:** The reconstructed edition is written in the fictional
  authorial voice of Bathilda Bagshot. This is a project decision, not an
  assertion of canon-established authorship.
- **Register:** Intelligent, polished, readable British historical prose;
  scholarly in judgement and conversational in presentation.
- **Edition frame:** The reconstructed narrator writes in or before 1984 and
  knows only what could plausibly have been available by that boundary. The
  unified edition may add later editorial passages, which must be identifiable
  and must not be voiced as Bagshot knowledge.
- **Evidence:** Rigorous underneath and minimally intrusive in the prose.
- **Personality:** Quiet confidence and restrained dry intelligence; wit only
  where it earns its place.
- **Narrative:** Show people, objects, practices, and events before drawing the
  larger conclusion. Explain development and consequence rather than listing
  lore.

## Narrator and period

- Write as Bathilda, not about her. Never refer to the fictional author in the
  third person as another historian or cite her own publications as outside
  authorities. Integrate facts drawn from *A History of Magic* into her voice
  and retain their sources in hidden evidence metadata. A rare first-person
  reference is permissible only when independently natural; do not introduce
  one merely to avoid self-reference.
- Do not adopt Harry Potter's perspective, the novels' omniscience, a modern
  essayist's voice, fandom language, or an agent/editorial voice.
- Within reconstructed Bagshot passages, do not introduce post-1984 events,
  discoveries, institutional roles, vocabulary, or exact later wording. Later
  evidence may establish an older fact for the unified edition without becoming
  a record or quotation available to the narrator.
- Do not report private events, thoughts, or conversations merely because a
  novel reveals them. Later persistence does not by itself establish origin,
  continuity, or what the 1984 narrator knew.
- Mark later editorial additions in planning metadata and preserve their source
  authority, publication date, event chronology, and knowledge-access class.
  Integrate them where they read naturally; use a separate addendum only when
  integration would disrupt chronology, perspective, or flow.
- Follow the chapter's approved presentation model. A chapter authorised as a
  unified narrative integrates eligible later evidence into continuous prose,
  without a repeated editorial-note announcement, while preserving provenance
  and chronology in hidden metadata and using natural attribution where the
  distinction among fact, testimony, tradition, and interpretation matters.
  A chapter still using the layered model begins each integrated addition with
  `**Later editorial note.**`, which remains both visible and spoken. Do not
  mix the two presentation models inside one chapter revision.
- Assume a magically educated readership. Explain ordinary magical concepts
  only when the historical argument requires it.

## Historical claims and imaginative space

- Distinguish documented occurrence, attributed testimony, tradition or
  folklore, bounded inference, and creative reconstruction. State a meaningful
  limitation once beside the claim it governs; do not repeat it until the
  boundary changes.
- Sources tell us only what they tell us. Do not invent scenes, debates, dates,
  maps, spells, castle engineering, motives, teaching methods, dialogue,
  witnesses, manuscripts, archives, portraits, or chains of ownership to fill a
  gap.
- Do not mistake a later school subject for the beginning of the practices it
  organises. Knowledge may precede its classroom name, and skilled practice may
  continue outside the school after the institution exists.
- Treat a physically attested object separately from its legendary or artistic
  associations. Established legends, oral traditions, and stories about the
  founders and their artefacts are legitimate historical material when
  naturally attributed: *according to tradition*, *legend holds*, *the story
  has long been told*, or equivalent language. The absence of a surviving
  written record does not by itself disqualify a longstanding tradition, and a
  single attribution is normally sufficient. Attribution must not promote a
  detail invented for this reconstruction into a genuine tradition; label such
  creative material in editorial metadata as reconstruction, never as evidence.
  Do not infer character, policy, or teaching practice from an emblem or
  depiction.
- The Sorting Hat's annual songs are an accepted continuous Hogwarts tradition
  of approximately a millennium, within which stories of the founders, their
  ideals, their relationships, and the school's beginnings recur. Later-recorded
  songs may therefore inform the reconstruction of what was traditionally known
  before 1984 without a fresh continuity argument. Their exact later lyrics and
  performances must not be attributed to the 1984 narrator. This premise is
  settled for Draft 01 and should not be reopened in subsequent reviews.
- Do not turn Slytherin's ambition or cunning into proof of virtue, guilt, or
  constructive achievement. His ancestry restriction was his position; do not
  present it as adopted school policy without evidence.

## Confidence and evidence metadata

- Match confidence to evidence. Useful categories include *records establish*,
  *evidence suggests*, *contemporary accounts report*, *school tradition holds*,
  *later accounts claim*, and *the precise date is uncertain*. Vary the wording;
  these are distinctions, not templates.
- A generated summary, later observation, or poetic tradition may guide inquiry
  but may not acquire greater authority than its underlying source.
- Keep `<!-- evidence: source-id -->` comments adjacent to the factual unit they
  support. Never attach an evidence ID to material the source does not support.
  Keep `<!-- source-access: ... -->` and `<!-- reconstruction: ... -->` notes
  separate from evidence claims. Never alter canonical evidence to make
  invented lore appear sourced.

## Story shape and chronology

- The authoritative chapter order is
  `authoring/editions/1984/table-of-contents.yaml`. Keep event chronology
  distinct from presentation order and use an explicit temporal pivot whenever
  the narrative must move backwards.
- Record each chapter's entry point, exit point, reserved events, and inherited
  facts in planning metadata rather than reader-facing prose.
- In the early book, Chapter 2 introduces the founders, their cooperation,
  contrasting ideals, and the emergence of the ancestry dispute. Chapter 3
  covers the joint founding and early operation; Chapter 4 develops the Houses;
  Chapter 5 owns the full dispute, fighting or duelling, Slytherin's departure,
  the Chamber tradition, and the consequences. Do not duplicate those events
  across chapters.
- Introduce a subject without announcing every finding before its evidence has
  been developed. Let people, facts, distinctions, and consequences emerge
  where they do historical work.
- Supply necessary context when the reader needs it within the chapter's
  approved scope; do not withhold it for artificial suspense or import events
  reserved for later chapters. An early brief contextual mention may orient the
  reader while leaving a distinct argument for its proper place.
- Transitions must express a supported connection in chronology, cause,
  contrast, or consequence, not review the outline. Mark a temporal pivot when
  returning to an earlier event rather than implying it has not occurred. A
  conclusion should complete the chapter's argument and move naturally towards
  the next chapter's verified subject, without “we will discuss”, “this belongs
  elsewhere”, another drafting-room signpost, or an invented connection.

## Language, paragraphs, and sections

- Prefer specific verbs and tangible magical history to bureaucratic or grand
  abstractions. Avoid pseudo-archaic diction, melodrama, excessive solemnity,
  modern academic apparatus, and fantasy-novel suspense.
- Each paragraph must add a distinct fact, interpretation, example, or
  development. A repeated fact earns its place only when its function changes,
  such as when a personal preference becomes a distinct institutional question.
  Make the changed function clear; otherwise retain the fuller account at its
  natural point and reduce the earlier occurrence to a brief contextual mention
  or remove it. Do not impose a mechanical one-mention limit or replace
  repetition with an “in other words” paragraph.
- Each section must perform a historical task and move the argument forward.
  Do not let an opening catalogue pre-empt later development or let one section
  end by summarising an argument the next section immediately restates. Avoid
  rhetorical triplets, stacked disclaimers, repeated mini-conclusions, and
  catalogues created only for symmetry.
- Integrate an object, place, or tradition only through an independently
  supported relationship to the paragraph's subject. An artefact may illuminate
  an established quality through attributed tradition; it cannot itself prove
  character, policy, or teaching practice. If the relationship cannot be
  supported, move or omit the detail rather than invent connective meaning.
- Do not re-explain material established in an earlier chapter unless a new
  context changes its meaning or a brief reminder is necessary. Preserve the
  reconstruction's documented silence on Hogwarts house-elf servitude unless
  the editorial authority explicitly changes that policy.
- Never pad to meet a target length or invent comparable detail to make uneven
  biographies symmetrical. A short section is preferable to unsupported
  completeness.
- Do not use drafting-room language such as “briefly used here”, “the source
  record tells us”, “the later consequences belong elsewhere”, “as established
  above”, or claims about what an editor, chapter, ledger, or prose passage
  needs to do.

## Final editorial check

Before delivery, perform and record:

1. an authorial self-reference scan;
2. a Bagshot-knowledge and editorial-addition attribution scan;
3. an event-ownership and chronology check against neighbouring chapters;
4. a claims-versus-evidence check;
5. a folklore and provenance check; and
6. a redundancy and narrative-flow pass that deletes or merges actual
   repetition, confirms that each remaining recurrence adds something, checks
   that sections advance and temporal pivots are clear, and ensures the final
   transition respects the next chapter's verified scope without sacrificing
   meaningful evidence distinctions merely to shorten the prose.

Preserve Chapter 1's voice as the baseline, not every redundant device in an
earlier revision. Historical truthfulness, readability, a consistent narrator,
and a clean narrative take priority over word count.

## Draft-wide authority

Every Draft-01 preparation, drafting, revision, and audit task must load and
apply this file. Chapter-local instructions may refine content but may not
silently override it. Substantial style changes must be accepted here before
they enter an individual chapter.
