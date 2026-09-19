# Chapter 2 Preparation Package — The Four Founders

Status: evidence dossier and outline updated for `draft-revision-05.md`.
The revised prose remains subject to editorial review; this package does not
advance the chapter's workflow state.

## Unified Expanded Revision 05 Overlay

- Chapter 2 now uses one continuous historical narrative. Source publication
  date is not an exclusion criterion, and no visible or spoken editorial-note
  label divides the prose. Event chronology, carrier date, provenance,
  authority, knowledge access and confidence remain distinct in this package
  and in adjacent manuscript comments.
- Hufflepuff's remembered willingness to teach broadly and treat pupils alike
  remains Hat evidence about an educational ideal. The separate house-elf claim
  is integrated only as specifically attributed 2007 authorial commentary from
  an Authority-D preservation transcript (`ext-b10-001`), not as independently
  established founder-era history or corroboration of her educational ideal.
- Ravenclaw's lost-diadem tradition remains distinct from Helena Ravenclaw's
  private 1998 testimony. Chapter 2 uses only Helena's attributed account of
  Rowena in `dh-ch31-002`: daughterhood, theft, concealment and Rowena's final
  search. Tom Riddle, Albania, Harry's deductions, Horcrux history and the
  diadem's later fate are reserved and `dh-ch31-003` does not support the
  Revision 05 prose.
- Gryffindor's founder-era swordsmanship and the goblin-made sword bearing his
  name are integrated briefly from `ext-a08-001` and `ext-a08-003`. Later sword
  appearances, Hat mechanics, worthiness rules and the ownership dispute remain
  outside the chapter.
- The Hat's friendship pairings do not establish when the founders' pupil
  preferences formed. The revised ending distinguishes selectable qualities
  from Slytherin's restriction on access, completes the people-and-purpose
  argument, and hands off to Chapter 3 without entering construction,
  admissions machinery, physical organisation or early operation.

## Current project state and governing authorities

- The authoritative twenty-chapter structure is
  `authoring/editions/1984/table-of-contents.yaml`. It assigns Chapter 2 the
  founders' backgrounds, attributed aims, and the limits of founder tradition;
  it excludes the full foundation process and detailed House development.
- The chapter-status file records Chapter 2 as `drafted`. This revision package
  does not advance that state or approve the revised prose.
- The current Chapter 1 handoff for this review is
  `chapters/01-before-hogwarts/final-draft-candidate-revision-07.md`. It ends by asking who the
  founders were, what purposes they brought to the undertaking, and how much of
  their familiar character belongs to evidence rather than school memory.
- `draft-01/style-lock.md` is the current style authority. The proposed
  argument therefore aims to be scholarly in judgement, conversational in
  presentation, concrete rather than abstract, and sparing with repeated
  qualifications.
- `authoring/shared/chapter-workflow.md` requires evidence selection before an
  approved outline and prose. `authoring/shared/evidence-policy.md` and
  `authoring/shared/research-interface.md` require direct review of canonical
  YAML and preserve the difference between historical evidence, later
  confirmation, tradition, private testimony and knowledge access.
- The canonical source shape and classifications are defined in
  `docs/instructions/schema-reference.md`. Extraction-era candidate chapter
  labels were used only for discovery and not as the book outline.
- The research layer was treated as read-only. Relevant index and duplicate
  queries were followed by inspection of the exact YAML records. The original
  passages were checked for `cos-ch09-003`–`005`, `gof-ch12-002`,
  `ootp-ch11-003`, and `dh-ch16-003`, and the complete A02, A07, and A08 source
  snapshots were reviewed.
- The access review separates three questions that must not be collapsed: when
  the remembered event occurred, when and how the surviving testimony was
  recorded, and what kind of access the reconstructed narrator could have had.
  Under the Unified Expanded model, access classification preserves provenance
  but does not exclude relevant history solely because its carrier postdates
  1984. The Hat songs preserved in 1994 and 1995 may inform the narrative as
  later testimony from a longstanding school institution; their particular
  lyrics are not reproduced or invented as an earlier performance.
- The newly supplied open-question overlay was reviewed as an editorial control
  layer, not as evidence. The linked-worktree version (SHA-256
  `5ddb83b08eac12528d43171a3971a585a5d9fa531960c3c8c323ff8e31185672`)
  passes its 386-record validation and returns four Chapter 2 questions. Its
  only verified Chapter 2 facts point back to canonical Sword evidence already
  in this package; its two founders-and-Houses records remain marked
  `local_search_required` and contain no verified facts.
- Follow-up entry-index queries using the overlay's tags returned the same
  local core already reviewed: `cos-ch09-003`–`004`, `gof-ch12-002`,
  `ootp-ch11-003`, and A02. The overlay's `W-FOUNDERS` lead remains
  `candidate_unverified`, so it has not been used to support a claim.

### Confidence used in this package

The confidence labels below assess whether and how a claim is safe for the
Unified Expanded narrative. They are not replacements for the canonical YAML
`confidence` field, which chiefly records the reliability of the evidence
extraction. Publication after 1984 does not by itself lower or exclude a claim;
authority, provenance, corroboration and relevance govern its treatment.

- **High:** explicitly stated by a comparatively strong historical or public
  in-universe source, or independently corroborated at the relevant level.
- **Moderate:** explicit but preserved through ceremonial testimony, a later
  carrier of an older tradition, or retrospective authorial exposition; usable
  only with its source character visible. A later carrier does not by itself
  make the remembered event late or independently corroborate it.
- **Withhold:** the evidence is too weak, contested or remote from the chapter's
  argument to use safely. This classification is never based solely on the
  carrier's publication date.

### Source hierarchy and the Sorting Hat

- Binns supplies the firm historical framework: four founders, a common
  undertaking, several years of cooperation, and the ancestry dispute. He
  distinguishes reliable history from Chamber legend, but the documents behind
  his account have not been identified (`cos-ch09-003`–`005`).
- The Sorting Hat is a longstanding Hogwarts institution that sings at the
  annual Sorting, and its song can change from year to year
  (`gof-ch12-003`; `ext-a02-001`). Its later-recorded songs claim memory of the
  founders and preserve educational traditions not supplied by Binns.
- The Hat's historical testimony may therefore inform the unified narrative
  when identified as tradition or claimed memory. Chapter 2 must not reproduce
  the 1994 or 1995 lyrics, claim that those versions circulated earlier, or
  invent an earlier performance, interview or recollection.
- Public history, longstanding school lore, private testimony, and later
  discovery remain distinct. The access qualification should be established
  once in the chapter rather than repeated after every Hat-supported detail.

### Core source register

| Evidence ID(s) | Source locator | Canonical YAML |
|---|---|---|
| `cos-ch09-003`–`005` | *Harry Potter and the Chamber of Secrets*, ch. 9, PDF pp. 407–408 | `sources/book-02/chapter-09-the-writing-on-the-wall.yaml` |
| `gof-ch12-002` | *Harry Potter and the Goblet of Fire*, ch. 12, PDF pp. 1093–1094 | `sources/book-04/chapter-12-the-triwizard-tournament.yaml` |
| `gof-ch12-003` | *Goblet of Fire*, ch. 12, especially PDF pp. 1091 and 1095 | `sources/book-04/chapter-12-the-triwizard-tournament.yaml` |
| `ootp-ch11-003` | *Harry Potter and the Order of the Phoenix*, ch. 11, PDF pp. 1765–1767 | `sources/book-05/chapter-11-the-sorting-hat-s-new-song.yaml` |
| `dh-ch16-003` | *Harry Potter and the Deathly Hallows*, ch. 16, PDF p. 3246 | `sources/book-07/chapter-16-godric-s-hollow.yaml` |
| `ext-a02-001`, `ext-a02-002` | A02, *The Sorting Hat*, complete official snapshot | `sources/external/official-rowling/a02-the-sorting-hat.yaml` |
| `ext-a07-005` | A07, *Hufflepuff Common Room*, complete official snapshot | `sources/external/official-rowling/a07-hufflepuff-common-room.yaml` |
| `ext-a08-001`, `ext-a08-002`, `ext-a08-003`, `ext-a08-004` | A08, *The Sword of Gryffindor*, complete official snapshot | `sources/external/official-rowling/a08-the-sword-of-gryffindor.yaml` |
| `cos-ch11-004` | *Chamber of Secrets*, ch. 11, PDF p. 445 | `sources/book-02/chapter-11-the-dueling-club.yaml` |
| `dh-ch07-006` | *Deathly Hallows*, ch. 7, PDF pp. 3083–3084 | `sources/book-07/chapter-07-the-will-of-albus-dumbledore.yaml` |
| `dh-ch25-002`, `dh-ch25-003` | *Deathly Hallows*, ch. 25, PDF pp. 3408–3409 | `sources/book-07/chapter-25-shell-cottage.yaml` |
| `dh-ch29-006` | *Deathly Hallows*, ch. 29, PDF p. 3474 | `sources/book-07/chapter-29-the-lost-diadem.yaml` |
| `dh-ch30-003` | *Deathly Hallows*, ch. 30, PDF p. 3482 | `sources/book-07/chapter-30-the-sacking-of-severus-snape.yaml` |
| `dh-ch31-002`, `dh-ch31-003` | *Deathly Hallows*, ch. 31, PDF pp. 3500, 3503 | `sources/book-07/chapter-31-the-battle-of-hogwarts.yaml` |
| `hbp-ch10-006` | *Harry Potter and the Half-Blood Prince*, ch. 10, PDF p. 2589 | `sources/book-06/chapter-10-the-house-of-gaunt.yaml` |
| `hbp-ch17-006` | *Half-Blood Prince*, ch. 17, PDF p. 2720 | `sources/book-06/chapter-17-a-sluggish-memory.yaml` |
| `hbp-ch20-005` | *Half-Blood Prince*, ch. 20, PDF p. 2781 | `sources/book-06/chapter-20-lord-voldemort-s-request.yaml` |
| `ext-b10-001` | B10, 2007 PotterCast interview, Authority-D preservation transcript | `sources/external/interviews/b10-pottercast-j-k-rowling-interview.yaml` |

The register identifies the primary working set, not every discovery query
result. Source A01 and entry `ext-a03-001` are retained only for the boundary
notes on the Chamber and admissions instruments.

### Supplemental open-question disposition

| Open-question ID | What the overlay adds | Disposition for Chapter 2 |
|---|---|---|
| `sorting-ceremony-005` | Verifies from `ext-a08-001`, `ext-a08-004`, and `dh-ch07-006` that the sword is Gryffindor's goblin-made relic and is said to return or present itself to a worthy Gryffindor. | Revision 05 uses only the goblin-made founder association. The later return tradition, its date and its connection to the Hat remain outside this chapter. |
| `sorting-ceremony-006` | Repeats the same evidence-supported worthiness tradition. | Does not establish when the connection began or define worthiness more precisely. Keep those questions unresolved. |
| `founding-and-the-four-houses-004` | Identifies the need for a fuller account of early cooperation and Slytherin's departure, but supplies no verified fact. | The local search does not move beyond Binns and the Hat. Do not reconstruct meetings, debates, or a departure scene. |
| `founding-and-the-four-houses-005` | Flags the risk of linking Slytherin's bloodline doctrine to later prejudice as though Hogwarts officially adopted it. It supplies no verified fact. | Attribute the doctrine to Slytherin and the documented opposition to Gryffindor; do not call it school policy. Later reception belongs chiefly to Chapter 5 and later social history. |

## A. Concise evidence dossier

### Godric Gryffindor

**What the sources explicitly establish**

- Professor Binns names Godric as one of the four founders and, collectively,
  one of the four greatest witches and wizards of the age. This establishes
  stature only at the collective level; it does not rank Godric above the other
  three (`cos-ch09-003`, *Chamber of Secrets*, ch. 9, PDF p. 407).
- Bathilda Bagshot's *A History of Magic* identifies Godric's Hollow as his
  birthplace. This is unusually useful because the claim is attributed to a
  public in-universe history, even though the passage is quoted in a later novel (`dh-ch16-003`,
  *Deathly Hallows*, ch. 16, PDF p. 3246).
- The Sorting Hat's later-recorded testimony calls him bold, associates him
  with a wild moor, and says that he prized bravery or brave deeds in pupils.
  These are founder traditions preserved in the 1994 and 1995 songs, not a full
  biography (`gof-ch12-002`, *Goblet
  of Fire*, ch. 12, PDF pp. 1093–1094; `ootp-ch11-003`, *Order of the Phoenix*,
  ch. 11, PDF pp. 1765–1767).
- Retrospective official exposition identifies him as a gifted conventional
  swordsman in the pre-Statute world and describes the sword bearing his name
  as goblin-made (`ext-a08-001`–`004`, source A08, *The Sword of Gryffindor*).
  Revision 05 uses only the founder-era swordsmanship, goblin manufacture and
  named association established in `ext-a08-001` and `ext-a08-003`.
- A later Ministry statement calls the sword an important historical artefact
  and says unnamed reliable sources held that it might present itself to any
  worthy Gryffindor (`dh-ch07-006`, *Deathly Hallows*, ch. 7, PDF
  pp. 3083–3084).
  This supports a longstanding worthiness tradition, not the date or mechanism
  of the sword's connection to the Sorting Hat.
- Binns identifies Gryffindor as Slytherin's direct opponent in the serious
  argument over pupils of Muggle parentage (`cos-ch09-004`, PDF pp. 407–408).

**Reasonable interpretation**

- Gryffindor rejected Slytherin's proposed ancestry restriction. It is
  reasonable to call this an inclusive position relative to Slytherin's, but
  the evidence does not give Gryffindor a complete admissions policy or prove
  that he accepted every pupil on precisely Hufflepuff's terms.
- The sword and the Hat can make Godric concrete in the chapter because they
  preserve traditions about skill, bravery, judgement, and later worthiness.
  Chapter 2 identifies the sword only as a goblin-made founder-associated
  historical artefact that accords with the account of his conventional
  swordsmanship. Later appearances, Hat mechanics, worthiness rules and the
  ownership dispute are outside this portrait.

**Unknown or unsafe to infer**

- No source reviewed gives Godric's birth date, parents, spouse, children,
  upbringing, occupation before Hogwarts, subjects taught, or reason for
  becoming an educator.
- “From wild moor” is poetic geographical testimony and should not be turned
  into a named region. It need not contradict Godric's Hollow, but the sources
  do not explain the relationship.
- Later Gryffindor House traits do not prove that Godric displayed every one of
  them, nor do modern pupils supply episodes from his life.
- The sword's ownership history is disputed in the surviving accounts. A08
  calls the theft story false, while Griphook asserts that the sword was
  Ragnuk's property (`dh-ch25-002`–`003`, *Deathly Hallows*, ch. 25, PDF
  pp. 3408–3409). The chapter must not silently choose one community's account
  as neutral history.
- No reviewed source says when the sword first became capable of appearing
  through the Sorting Hat, whether the founders designed that connection, or
  what “worthy” means beyond the asserted House affiliation
  (`sorting-ceremony-005`, `sorting-ceremony-006`).

### Helga Hufflepuff

**What the sources explicitly establish**

- Binns names Helga as one of the four founders and one of the age's four great
  magical people (`cos-ch09-003`, PDF p. 407).
- The Sorting Hat's later-recorded testimony calls her sweet or good,
  associates her with a broad valley, and gives two connected educational
  claims: she valued hard workers, and she was willing to teach all the pupils
  and treat them alike (`gof-ch12-002`, PDF p. 1094; `ootp-ch11-003`, PDF
  pp. 1765–1766). This is evidence of a remembered founder ideal, not a
  founder-era transcript.
- The 1995 song presents Hufflepuff and Ravenclaw as a close pair of friends.
  This is later ceremonial testimony and is not independently documented; it
  does not show that Ravenclaw shared every aspect of Hufflepuff's admissions
  position (`ootp-ch11-003`).
- A later official description records a Hufflepuff common-room portrait of
  Helga toasting her students with a small two-handled golden cup
  (`ext-a07-005`, source A07, *Hufflepuff Common Room*). The description
  establishes a limited House memorial association, not that the physical cup
  or its history was universally familiar.
- A private memory records Hepzibah Smith's claim that a small golden
  cup was Helga's family heirloom and possessed unspecified powers
  (`hbp-ch20-005`, *Half-Blood Prince*, ch. 20, PDF p. 2781). The claim was made
  privately, its family provenance is uncorroborated in the passage, and the
  memory does not establish broad public knowledge.

**Reasonable interpretation**

- Hufflepuff supplies the strongest positive statement of broad educational
  inclusion in founder tradition. It records her remembered willingness to
  teach all within the founders' undertaking and to treat them alike; it is not
  proof that every magical child was admitted to Hogwarts, that admission was
  universal in later practice, or that the other founders shared a complete
  admissions policy.
- Valuing hard work and accepting all pupils are compatible propositions, but
  the sources do not explain how she balanced a preferred virtue with equal
  treatment. The chapter should preserve both statements rather than flatten
  either one.

**Unknown or unsafe to infer**

- No source reviewed names Helga's birthplace, family, earlier occupation,
  subject specialism, or teaching method. “Valley broad” is not a licence to
  assign a modern country or county.
- Neither the cup nor the later Hufflepuff common room proves that Helga was a
  cook, cultivated its plants, designed the room, or originated its later
  customs.
- The portrait's installation date is unknown, and the object shown in it is
  not authenticated as the surviving cup. The physical object's fuller history
  requires its own evidence treatment in a later chapter.
- No reviewed source independently authenticates the physical cup's alleged
  powers or claimed family descent; those details are unnecessary here.
- `ext-b10-001` attributes to Rowling the view that Hufflepuff offered
  house-elves refuge and better working conditions rather than abolition. This
  2007 Authority-D transcript is later authorial commentary, not corroboration
  of Hufflepuff's educational ideal or an independent in-world record.

### Rowena Ravenclaw

**What the sources explicitly establish**

- Binns names Rowena as one of the four founders and one of the four great
  magical people of the age (`cos-ch09-003`, PDF p. 407).
- The Sorting Hat's later-recorded testimony calls her fair, associates her
  with a glen, and says that she preferred the cleverest pupils or those of the
  sharpest mind
  (`gof-ch12-002`, PDF pp. 1093–1094; `ootp-ch11-003`, PDF pp. 1765–1766).
- The Hat presents Ravenclaw and Hufflepuff as a close pair of friends. As with
  the Gryffindor–Slytherin pairing, this is later traditional testimony rather
  than an independently documented personal relationship (`ootp-ch11-003`).
- Longstanding school lore says that Ravenclaw's diadem vanished with Ravenclaw
  herself centuries ago and was reputed to enhance the wearer's wisdom
  (`dh-ch29-006`, *Deathly Hallows*, ch. 29, PDF p. 3474). The report comes from
  Ravenclaw pupils citing Flitwick; later direct staff testimony confirms its
  status as centuries lost and unseen in living memory (`dh-ch30-003`, ch. 30,
  PDF p. 3482). Neither source supplies a primary record or chain of custody.

**Reasonable interpretation**

- Rowena's surviving educational identity centres on intellectual ability.
  This supports a discussion of selectivity by aptitude, not a claim that she
  valued knowledge to the exclusion of courage, labour, loyalty, or character.
- Her remembered friendship with Hufflepuff does not establish agreement with
  Hufflepuff's broad offer to teach and treat pupils alike.
- The lost-diadem tradition may be used briefly to show how later generations
  remembered her through wisdom and understood the loss as ancient. It should
  be presented as longstanding school legend, not used to reconstruct her
  classroom, scholarship, personality, or the diadem's eventual fate.

**Later testimony and limits**

- No reviewed source gives a named birthplace, family background, writings,
  subjects taught, or a documented role in designing the castle. “From glen”
  must remain no more precise than the song makes it.
- The familiar Ravenclaw motto is later House evidence and is not established
  as Rowena's own composition.
- Helena Ravenclaw's private 1998 testimony identifies her as Rowena's daughter
  and supplies a first-person account of stealing the diadem, Rowena concealing
  the loss from the other founders, and the fatally ill Rowena later seeking
  her daughter (`dh-ch31-002`, *Deathly Hallows*, ch. 31, PDF p. 3500). The
  testimony may be integrated through direct attribution to Helena; it remains
  one witness's memory without documentary corroboration from Rowena or another
  founder and does not establish Rowena's motives.
- Tom Riddle, the Albanian hiding place, Harry's deductions, Horcrux history
  and the diadem's later fate are later relic history rather than evidence
  needed for Rowena's portrait. They are reserved and `dh-ch31-003` is not cited
  by Revision 05.

### Salazar Slytherin

**What the sources explicitly establish**

- Binns names Salazar as one of the four founders and one of the four great
  magical people of the age (`cos-ch09-003`, PDF p. 407).
- Binns's historical account says Slytherin wanted admission restricted to
  all-magic families, disliked taking pupils of Muggle parentage, and regarded
  them as untrustworthy. This is the strongest founder-specific educational
  claim in the corpus (`cos-ch09-004`, PDF pp. 407–408).
- The Sorting Hat's later-recorded songs call him shrewd, associate him with a
  fen, connect his preferred pupils with ambition and cunning, call him
  power-hungry in one account, and say that he selected pure-blood pupils like
  himself (`gof-ch12-002`, PDF pp. 1093–1094; `ootp-ch11-003`, PDF
  pp. 1765–1766). These descriptions remain poetic historical testimony; only
  the ancestry restriction is independently supported by Binns.
- Binns says the decisive serious argument was between Slytherin and
  Gryffindor. He also says Slytherin left, but the departure belongs to the
  later rift chapter rather than the narrative body of Chapter 2
  (`cos-ch09-004`).
- Parseltongue and serpent symbolism are firmly associated with Slytherin in
  later school lore, but the indexed carrier is student explanation rather
  than a cited historical record (`cos-ch11-004`, *Chamber of Secrets*, ch. 11,
  PDF p. 445).
- Binns also records the Chamber of Secrets as a founder legend while denying
  that it belongs to reliable history (`cos-ch09-005`, PDF p. 408). Its
  existence, contents, later opening and confirmation belong to Chapter 5 and
  do not enter Revision 05.

**Reasonable interpretation**

- Slytherin's most consequential difference from the other founders is that
  ancestry became a threshold for education, not merely a preferred pupil
  quality. This distinction is explicit enough to organise the chapter's
  central comparison.
- Opposition to pupils of Muggle parentage may be described as distrust and an
  admissions doctrine. No source supports a fuller psychological explanation
  for it.
- The restriction belongs to Slytherin in the evidence. Binns presents it as a
  disputed proposal followed by a serious argument and Slytherin's departure;
  he does not say that Hogwarts adopted it as official admissions policy
  (`cos-ch09-004`). Later blood-status prejudice may be discussed as reception
  or legacy, not as retroactive proof of institutional endorsement.

**Unknown or unsafe to infer**

- No source reviewed names Slytherin's birthplace, parents, early life, prior
  occupation, subjects taught, or the experience that produced his beliefs.
  “From fen” must remain poetic and geographically imprecise.
- The Hat's “pure-blood like him” supports a traditional claim about his own
  ancestry, not a recoverable family tree.
- Gaunt descent, the surviving family line, a locket, and a founder wand appear
  in later revelations or retrospective sources. The indexed evidence for the
  Gaunt claim is self-interested or retrospective (`hbp-ch10-006`, *Half-Blood
  Prince*, ch. 10, PDF p. 2589; `hbp-ch17-006`, ch. 17, PDF p. 2720;
  `hbp-ch20-005`, PDF p. 2781). These facts do not advance Chapter 2's bounded
  people-and-purpose argument and are reserved.
- The Chamber belongs to known school legend (`cos-ch09-005`, PDF p. 408), but
  its confirmation and details form a separate history. Chapter 5 owns the
  substantive treatment, and Revision 05 does not mention it.

### Shared history: cooperation, agreement, difference, and dispute

**Firm historical minimum**

- The four founders built the school together, sought children who showed
  magic, brought them to the castle, and educated them. They worked in harmony
  for several years before a rift developed (`cos-ch09-003`–`004`, PDF
  pp. 407–408).
- Their strongest demonstrable agreement was practical and educational: young
  magical people should be found and taught in a common undertaking. The
  evidence does not establish a shared curriculum, identical admissions rules,
  equal authority, or a common motive beyond that undertaking.

**Traditional enlargement of that minimum**

- The Hat's 1994 and 1995 songs preserve a claimed memory that the founders
  shared a hope of educating young magical people, were good friends, and
  formed the Gryffindor–Slytherin and Hufflepuff–Ravenclaw pairs
  (`gof-ch12-002`; `ootp-ch11-003`). The shared educational purpose
  corroborates Binns; the intimate friendship pairings do not. Chapter 2 may
  use the historical substance as later Hat testimony, not the particular
  lyrics as a founder-era transcript.
- The later Hat testimony says their different preferences initially caused
  little strife because each founder could teach chosen pupils within a House.
  This is useful evidence that difference did not immediately prevent
  cooperation, but it does not date the first appearance of each belief. The
  creation and operation of the Houses belong to Chapter 4.
- The Hat's later account of House rivalry, duelling, and fighting is more
  expansive than Binns's concise report of disagreements and a serious
  Gryffindor–Slytherin argument. It should be attributed as claimed memory or
  tradition, not silently promoted to the historical minimum.

**What the partnership does not establish**

- No source explains how the four met, who first proposed the school, how work
  or authority was divided, what each taught, or what conversations produced
  their agreement.
- The new overlay's search prompt does not fill this silence. Local index and
  source review found no canonical account more detailed than Binns's summary
  and the Hat's poetic testimony (`founding-and-the-four-houses-004`).
- Cooperation does not prove that their personalities were alike or that every
  later House value was already a complete educational philosophy.
- The traditional friendship pairings do not prove shared admissions rules:
  Ravenclaw's friendship with Hufflepuff is not evidence that she accepted
  Hufflepuff's broad teaching position.
- Their eventual disagreement does not prove that the partnership was a sham
  from the beginning. Conversely, several years of harmony do not erase the
  seriousness of an ancestry rule that eventually challenged the common
  project.

## B. Important claim table

For Hat-supported rows, “moderate” assesses the historical substance of the
tradition. It does not convert the particular 1994 or 1995 lyrics into a
founder-era transcript. That provenance qualification is stated here rather
than repeated in every row.

| ID | Important assertion | Evidence status | Canonical source and locator | Narrative confidence | Qualification or conflict | Placement |
|---|---|---|---|---|---|---|
| C2-01 | Hogwarts had four named founders, collectively described as the age's greatest witches and wizards. | Explicit historical account | `cos-ch09-003` — *CoS* ch. 9, PDF p. 407; YAML `sources/book-02/chapter-09-the-writing-on-the-wall.yaml` | High | Collective praise gives no individual ranking or biography. | Chapter 2 |
| C2-02 | The four shared a project of finding and educating magical children. | Explicit; poetically corroborated | `cos-ch09-003`; `gof-ch12-002` — *GoF* ch. 12, PDF pp. 1093–1094 | High for the educational undertaking; moderate for the Hat's wording | Motives, curriculum, and sequence remain unknown. | Chapter 2; mechanics in Chapter 3 |
| C2-03 | They worked in harmony for several years. | Explicit historical account | `cos-ch09-004` — *CoS* ch. 9, PDF pp. 407–408 | High | “Harmony” does not prove identical beliefs. | Chapter 2 |
| C2-04 | Later Hat testimony describes all four as close friends and remembers Gryffindor–Slytherin and Hufflepuff–Ravenclaw as particular pairs. | Later-recorded Hat testimony | `ootp-ch11-003` — *OotP* ch. 11, PDF pp. 1765–1766 | Moderate | Binns corroborates cooperation, not private intimacy or pairings; friendship does not prove shared admissions policy. | Chapter 2, clearly attributed as tradition |
| C2-05 | Godric Gryffindor was born in Godric's Hollow. | Explicit in public in-universe history | `dh-ch16-003` — *DH* ch. 16, PDF p. 3246 | High | Quoted in a later novel but explicitly attributed to *A History of Magic*. | Chapter 2 |
| C2-06 | Gryffindor valued bravery in pupils. | Later-recorded Hat tradition | `gof-ch12-002`; `ootp-ch11-003` | Moderate | A preferred pupil quality is not a complete personality. | Chapter 2; House mechanics in Chapter 4 |
| C2-07 | Gryffindor was an accomplished conventional swordsman. | Later official retrospective exposition | `ext-a08-003` — source A08, snapshot `resources/external/official-rowling/harrypotter-com/a08-the-sword-of-gryffindor.md` | Moderate | The retrospective account is the source; no dated founder-era record independently corroborates the skill. | Chapter 2, brief and attributed contextual detail |
| C2-08 | Gryffindor opposed Slytherin over pupils of Muggle parentage. | Explicit historical account | `cos-ch09-004` | High | This proves opposition to Slytherin's rule, not Gryffindor's entire admissions policy. | Chapter 2; outcome in Chapter 5 |
| C2-09 | Later Hat tradition says Hufflepuff valued hard work. | Later-recorded Hat tradition | `gof-ch12-002` — PDF p. 1094 | Moderate | Later House industriousness cannot supply biography. | Chapter 2 |
| C2-10 | Later Hat tradition says Hufflepuff would teach all pupils and treat them alike. | Later-recorded Hat tradition | `ootp-ch11-003` — PDF p. 1765 | Moderate | Evidence of a remembered inclusive ideal, not proof that Hogwarts admitted every magical child, maintained universal admission, or that every founder agreed. | Chapter 2 |
| C2-11 | Later Hat tradition says Ravenclaw preferred pupils of exceptional intelligence or sharp mind. | Later-recorded Hat tradition | `gof-ch12-002`; `ootp-ch11-003` | Moderate | No evidence identifies her subjects, writings, teaching method, or agreement with Hufflepuff's admissions position. | Chapter 2 |
| C2-12 | Slytherin wished to restrict magical learning to all-magic families and distrusted pupils of Muggle parentage. | Explicit historical account; later Hat corroboration | `cos-ch09-004`; `ootp-ch11-003` | High | The Hat's wider labels—cunning, ambition, power hunger—remain traditional characterisation. | Chapter 2; consequences in Chapter 5 |
| C2-13 | Later Hat tradition gives broad origins: Gryffindor from moor, Ravenclaw from glen, Hufflepuff from valley, Slytherin from fen. | Later-recorded poetic tradition | `gof-ch12-002` — PDF p. 1093 | Moderate as tradition; low as exact geography | These are not named birthplaces and must not be mapped to modern regions. | Chapter 2, one compact passage |
| C2-14 | Later Hat testimony says their different pupil preferences were initially accommodated without serious strife. | Later Hat testimony, broadly consistent with Binns | `ootp-ch11-003`; `cos-ch09-004` | Moderate | The sources do not settle whether all preferences existed from the first year. | Chapter 2; institutional structure in Chapters 3–4 |
| C2-15 | A serious argument developed specifically between Slytherin and Gryffindor; the historical account then records Slytherin's departure. | Explicit historical account | `cos-ch09-004` | High | Chapter 2 may establish the disagreement but must not narrate the departure or its consequences. | Disagreement in Chapter 2; departure in Chapter 5 |
| C2-16 | Later Hat testimony says fighting, duelling, and House attempts to rule nearly ended the school. | Later-recorded Hat testimony | `ootp-ch11-003` — PDF p. 1766 | Moderate | More dramatic and more detailed than Binns; no dates or independent corroboration. | Chapter 5, retained as attributed evidence |
| C2-17 | Tradition makes Gryffindor's old hat a joint work of all four founders. | Explicitly labelled legend in later official source; supported by Hat song | `ext-a02-001`–`002` — source A02; `gof-ch12-002` | Moderate | Important evidence for collective magical work, but the genesis is presented as legend. | Mention only if needed in Chapter 2; detail in Chapter 4 |
| C2-18 | The Sword of Gryffindor is an old goblin-made founder relic bearing his name. | Retrospective official exposition | `ext-a08-001`; contextual swordsmanship in `ext-a08-003` | Moderate | Later appearances, Hat mechanics, worthiness rules and ownership claims are unnecessary to the founder portrait and remain reserved. | Brief Chapter 2 association; later mechanics and disputes elsewhere |
| C2-19 | A golden cup is associated with Hufflepuff in House memory and private heirloom testimony. | Later House memorial description plus private remembered testimony | `ext-a07-005`; `hbp-ch20-005` — PDF p. 2781 | Moderate for limited association; withhold physical provenance and chain of custody | Portrait date and identity of the depicted cup are unknown; Hepzibah's family claim was private and is uncorroborated here. | Memorial context in Chapter 12; not needed in Revision 05 |
| C2-20 | Ravenclaw's lost diadem was said to have vanished with her and to enhance wisdom. | Later report of longstanding school lore, supported by direct staff testimony of its long loss | `dh-ch29-006` — *DH* ch. 29, PDF p. 3474; `dh-ch30-003` — ch. 30, PDF p. 3482 | Moderate as longstanding legend | No primary historical record or chain of custody is supplied; its hidden history and later fate require separate treatment. | Brief Chapter 2 legend; later relic history reserved |
| C2-21 | Slytherin had a surviving line associated with Parseltongue and a locket. | Self-interested family claim plus later retrospective reconstruction | `hbp-ch10-006`, PDF p. 2589; `hbp-ch17-006`, PDF p. 2720; `hbp-ch20-005`, PDF p. 2781 | Withhold | Source character requires care and the material is not needed for the founder argument. | Later lineage or relic history |
| C2-22 | The Chamber was preserved as Slytherin legend and distinguished from reliable history by Binns. | Explicitly presented as legend by Binns | `cos-ch09-005` — *CoS* ch. 9, PDF p. 408 | High as evidence of the legend; not as proof of the Chamber | Later confirmation must not be projected backwards into Binns's historical account. | Chapter 5 |
| C2-23 | The bloodline restriction is evidenced as Slytherin's disputed position, not as an official Hogwarts admissions policy. | Explicit attribution plus bounded negative conclusion | `cos-ch09-004` — *CoS* ch. 9, PDF pp. 407–408 | High for attribution; high that the reviewed source does not establish adoption | Later school prejudice cannot be projected backwards as proof of founding-era institutional endorsement. | Chapter 2 qualification; consequences and reception later |
| C2-24 | The Sorting Hat is a longstanding annual institution whose songs can change from year to year. | Later confirmation of an established custom; official retrospective support | `gof-ch12-003` — *GoF* ch. 12, especially PDF pp. 1091 and 1095; `ext-a02-001` | Moderate for long continuity; high for the later observed custom | The 1994 and 1995 songs may preserve older memories, but their exact lyrics are poetic carriers rather than founder-era transcripts. | Source-treatment rule for Chapter 2; ceremony detail in Chapter 13 |
| C2-25 | A 2007 author interview attributes to Hufflepuff a policy of refuge and improved working conditions for house-elves, rather than abolition. | Later external authorial commentary in preservation transcript | `ext-b10-001` — Authority D | Medium as attribution; not independently established in-world history | Separate from Hat evidence for educational ideals; no contemporaneous source or precise date is identified. | Chapter 2, brief natural attribution in unified narrative |
| C2-26 | In 1998 Helena Ravenclaw identified herself as Rowena's daughter and testified that she stole the diadem, Rowena concealed the loss, and her fatally ill mother later sought her. | Private first-person testimony | `dh-ch31-002` — *DH* ch. 31, PDF p. 3500 | High that Helena gave the account; moderate for its uncorroborated founder-family contents | One witness's memory; no documentary or second-witness corroboration and no basis for Rowena's motives. | Chapter 2, naturally attributed; later relic history reserved |

## C. Contradictions, uncertainties, and unresolved questions

### Accounts that must not be silently harmonised

1. **When did the differences begin?** Binns says the founders worked in
   harmony for a few years and then disagreements arose. The later Hat
   testimony presents distinct pupil preferences as present at the formation
   of the Houses, but says those differences initially caused little strife.
   The accounts can be read together, but they do not establish whether
   Slytherin's ancestry rule was original, developed, or merely became
   intolerable later.
2. **How inclusive was Hufflepuff's standard?** One later song says hard
   workers were most worthy of admission; another says she taught everyone and
   treated them alike. These can coexist as preference and remembered ideal,
   but the testimony does not explain the mechanism or prove universal
   Hogwarts admission.
3. **How close were the founders personally?** Binns supports cooperation and
   harmony; only the later Hat testimony calls them good friends and supplies
   the two friendship pairs. Personal intimacy must remain attributed
   tradition, and friendship cannot be substituted for agreement on admission.
4. **How violent was the rupture?** Binns gives disagreements and a serious
   argument. The Hat adds House rivalry, duelling, fighting, and near collapse.
   The broader account is not independently corroborated.
5. **Who rightly owned Gryffindor's sword?** A08 declares the goblin theft story
   false; Griphook calls the sword Ragnuk's lost property, while Hermione warns
   that wizarding histories often minimise wrongs against other magical peoples
   (`ext-a08-002`; `dh-ch25-002`–`003`). The dossier preserves the dispute.
6. **What do the geographical verses mean?** Moor, glen, valley, and fen may
   preserve origin traditions, poetic scenery, or both. Only Godric has a named
   birthplace in a reviewed public in-universe history.

### Questions the evidence cannot yet resolve

- What records lie behind Binns's distinction between reliable founding
  history and Chamber legend (`founding-and-the-four-houses-001`)?
- Can the foundation be dated more precisely than “over a thousand years ago”
  (`founding-and-the-four-houses-003`)?
- Is any source independent of the Sorting Hat able to document the founders'
  friendship pairings, early debates, or division of educational work
  (`founding-and-the-four-houses-004`)?
- How did the founders meet, and who first proposed a shared school?
- What did each founder actually teach, and did “House” initially mean a pupil
  group, a teaching responsibility, a residence, or all three?
- Did Slytherin's ancestry restriction exist from the start, or did it harden
  after the school began?
- What did Gryffindor, Hufflepuff, and Ravenclaw each say about Muggle-born
  admission? Only Gryffindor's direct argument with Slytherin and Hufflepuff's
  broader Hat tradition survive.
- Are any precise birthplaces recoverable for Hufflepuff, Ravenclaw, or
  Slytherin? The present corpus supplies only the song's valley, glen, and fen.
- Which founder relic traditions were publicly documented, rather than
  privately known, preserved only in a House space of unknown date, or revealed
  through later testimony?
- How widely known was Hufflepuff's physical cup? The portrait establishes a
  limited memorial association of uncertain date, while the family-heirloom
  claim survives only in private testimony.
- What primary source, if any, underlies the school tradition that Ravenclaw's
  diadem vanished with her and enhanced wisdom? The tradition is longstanding,
  but the reviewed testimony supplies no chain of custody.
- When and how did the Sword of Gryffindor become connected to the Sorting Hat
  (`sorting-ceremony-005`, `sorting-ceremony-006`)? The verified relic and
  worthiness claims do not answer the date, mechanism, or exact standard.
- How should later Hogwarts blood-status prejudice be cross-referenced without
  implying that the school adopted Slytherin's doctrine
  (`founding-and-the-four-houses-005`)? The current evidence supports a
  disputed founder position, not official endorsement.
- What formal source links Slytherin, Parseltongue, and the serpent emblem
  independently of student lore (`pre-hogwarts-historical-context-009`)?

### Research-layer observation

Direct inspection of the original PDF confirms that the passage indexed as
`dh-ch07-006` begins on PDF p. 3083 and continues onto p. 3084. This package
uses the corrected two-page authoring locator. The protected canonical YAML
still records `pdf_page: 3083` and was not modified.

The complete A30 source snapshot contains Slytherin-line and founder-wand
material, but the current A30 YAML contains only comparative Ilvermorny entries
and no evidence record for those passages. This is a discovery/indexing gap, not
permission to repair the protected research layer. The material is also later
retrospective exposition and unnecessary to Chapter 2's argument.

The enriched open-question overlay is likewise a research-control instrument,
not a canonical evidence source. Its Chapter 2 query was useful chiefly because
it made two limits explicit: a verified sword fact does not answer the
Hat-connection question, and an unverified external candidate cannot answer the
founders' cooperation question. Neither limit authorises creative
reconstruction.

## D. Proposed chapter argument

The evidence supports a chapter about a partnership more securely than it
supports four conventional biographies. The founders enter history as four
exceptional magical people who agreed that young magic-users should be found
and educated together. Their agreement was substantial: it endured for years
and produced a shared undertaking. Founder tradition preserves four different
measures of promise—courage, intelligence, labour, and ambition—while the
sword, cup, diadem, and Chamber legend show how unevenly the four people were
remembered. Those associations make the founders concrete, but they must remain
subordinate to the history of their ideas.

The chapter's central movement should therefore be from shared purpose to the
limits of agreement. Different preferences about courage, intelligence, hard
work, or ambition could apparently be accommodated within a common educational
undertaking. Slytherin's lineage restriction was different in kind: it asked
not merely which qualities education should cultivate, but which magical
children were entitled to receive it. Binns attributes that restriction to
Slytherin and a serious opposition to Gryffindor; he does not establish it as
official Hogwarts policy or supply a complete alternative admissions policy
shared by the others.

The sequence should follow what the sources actually establish: four people
with limited recoverable biographies, a common purpose, several years of
cooperation, distinct remembered ideals, and the emergence of a disagreement
that tested their partnership. Where the timing of a belief is unknown, the
chapter must not invent a stage at which it appeared. It should stop before
Slytherin's departure and return in its conclusion to the founders' shared
achievement. That makes Chapter 3's question prospective rather than
retrospective: how did these four people turn a common educational purpose into
a functioning school?

This argument must remain proportionate to the sources. It does not claim that
all four began with complete philosophies, that Hufflepuff's remembered offer
proves universal admission, that Ravenclaw shared that offer, or that the
founders foresaw the later identities of their Houses. The Hat supplies
powerful later testimony about claimed founder memory, not a founder-era
transcript and not permission to invent scenes, speeches, or inner motives.

## E. Proposed narrative outline

### I. Four Names in a Long Memory

**Purpose:** Pick up Chapter 1's closing question and establish the uneven
record. The four names, collective stature, shared work, and Godric's named
birthplace are comparatively secure; most personal chronology is not.
Introduce Binns as the firm historical framework and the Sorting Hat as a
longstanding keeper of founder tradition whose surviving 1994 and 1995 songs
are later poetic testimony rather than founder-era transcripts.

**Evidence:** `cos-ch09-003`–`005`; `dh-ch16-003`; `gof-ch12-002`–`003`;
`ootp-ch11-003`; `ext-a02-001`.

**Limits to preserve:** Do not open with four miniature biographies. Do not
turn moor, glen, valley, and fen into modern national identities. Establish the
source hierarchy and access rule once, without reproducing later lyrics or
inventing an earlier song, interview, or personal recollection.

### II. The Work They Chose Together

**Purpose:** Establish the positive centre of the chapter. Four exceptional
magical people chose a common educational task, sought magical children, and
worked in harmony for several years. The Hat's claimed
memory of common hope and particular friendship pairs may enrich Binns's
minimum when clearly identified as later tradition.

**Evidence:** `cos-ch09-003`–`004`; `gof-ch12-002`;
`ootp-ch11-003`.

**Limits to preserve:** Do not narrate how the founders met, who proposed the
school, the conversations by which they agreed, or the precise sequence of the
plan. Site choice, castle construction, opening, recruitment machinery, and
division of labour belong to Chapter 3. Friendship pairings are not proof of
shared admissions rules.

### III. Four Founders, Four Educational Ideals

**Purpose:** Develop the founders through the characteristics, pupil
preferences, and associations that survive, without breaking the chapter into
four disconnected lives. Hufflepuff's hard work and remembered broad teaching
offer can be considered beside Ravenclaw's intellectual selectivity; their
friendship remains tradition and does not imply policy agreement. Gryffindor's
bravery and opposition to an ancestry restriction can be considered beside
Slytherin's ambition, cunning, and firmer bloodline doctrine.

Use artefacts selectively to make the portraits concrete. The Sword of
Gryffindor may appear as a goblin-made founder relic bearing his name and a
material counterpart to the retrospective account of his conventional
swordsmanship. Do not add later appearances, Hat mechanics, worthiness rules or
the ownership dispute. Ravenclaw's diadem may appear first as longstanding
school lore—lost with Ravenclaw and reputed to enhance wisdom—then through
Helena's naturally attributed 1998 testimony about Rowena. Helena's testimony
is a single memory, not omniscient reconstruction; Tom Riddle, Albania, Harry's
deductions, Horcrux history and the diadem's later fate remain reserved.

The 2007 house-elf commentary is integrated briefly through explicit authorial
and transcript attribution, separate from Hufflepuff's pupil-facing ideal and
without treating the claim as independently documented founder-era history.
Gryffindor's martial evidence is likewise attributed to its later official
account. These provenance distinctions remain part of one reader-facing voice;
no visible or spoken editorial-note marker is used.

**Evidence:** `dh-ch16-003`; `gof-ch12-002`; `ootp-ch11-003`;
`cos-ch09-004`–`005`; `ext-a07-005`; `hbp-ch20-005`; `ext-a08-001`–`004`;
`dh-ch29-006`; `dh-ch31-002`; `ext-b10-001`.

**Limits to preserve:** These are attributed ideals and associations, not
complete personalities, teaching careers, subject specialisms, or later House
stereotypes projected backwards. Do not turn the sequence into an artefact
catalogue, import later sword or diadem history, or enter the Chamber narrative.
Do not treat attributed authorial commentary or private testimony as stronger
than its stated authority.

### IV. The Limits of Agreement

**Purpose:** Distinguish different educational emphases from a restriction on
access to magical education. Courage, intelligence, hard work, and ambition are
remembered preferences; Slytherin's ancestry threshold excluded otherwise
magical children. Binns establishes several years of harmony followed by
disagreement and a serious Gryffindor–Slytherin argument. The later Hat
testimony supplies a broader but less independently corroborated memory of
discord.

**Evidence:** `cos-ch09-004`; `gof-ch12-002`; `ootp-ch11-003`.

**Limits to preserve:** Do not infer a complete alternative admissions policy
for Gryffindor, Hufflepuff, or Ravenclaw; call Slytherin's restriction his
position, not official Hogwarts policy. Do not assign an invented date to the
formation of any belief, reconstruct the argument, narrate the departure, or
advance into the Chamber and institutional consequences. End on the distinction
between preferred pupil qualities and a restriction on access to the school,
then complete the people-and-purpose argument with a concise handoff to Chapter
3's question of how the common purpose became a functioning institution. Do not
answer that question here.

## F. Chapter boundary and reserved material

### Chapter 2 owns

- the documentary limits of founder biography;
- the four names and their collective historical stature;
- the small amount of usable origin evidence;
- attributed qualities and educational preferences, with the Hat treated as a
  longstanding institution whose surviving 1994 and 1995 testimony is a later
  carrier of claimed founder memory;
- the minimum evidence for friendship, cooperation, and several years of
  harmony;
- the distinction between preferences based on aptitude or effort and
  Slytherin's restriction based on ancestry;
- the emergence of disagreement, stopping before its institutional narrative;
- brief treatment of Gryffindor's sword and Ravenclaw's lost diadem only where
  they reveal how a founder was remembered, with school lore separated from
  private testimony and retrospective commentary;
- brief, explicitly attributed authorial commentary about Hufflepuff and
  house-elves, without extending it into the wider history of magical labour.

### Reserve for Chapter 3, *The Founding of Hogwarts*

- the decision-making sequence that produced the school;
- location, site selection, concealment, castle construction, and completion;
- how pupils were found and brought to the school in practice;
- the Quill of Acceptance and Book of Admittance (`ext-a03-001`);
- the first teaching arrangements, opening, early operation, governance, and
  any institutional consequences of the founders' differing approaches needed
  to explain how the school functioned;
- detailed claims about who designed, built, enchanted, or administered any
  part of the early institution.

### Reserve beyond Chapter 3 under the approved table of contents

- **Chapter 4, *The Four Houses*:** formation and development of the House
  system, Sorting practice, founder preferences as institutional selection,
  and the Sorting Hat's continuing role. House-linked interpretations of the
  sword's worthiness belong here if used beyond Chapter 2's brief association.
- **Chapter 5, *The Departure of Salazar Slytherin*:** the full dispute,
  Slytherin's departure, the Chamber as founder legend, and the consequences
  of the rupture, including the later reception of Slytherin's bloodline
  doctrine. Later proof of the Chamber must not be projected backwards into
  Binns's account, and later prejudice must not be treated as proof that the
  founders made the doctrine school policy.
- **Chapter 12, *Portraits, Ghosts and the Memory of Hogwarts*:** fuller
  treatment of the Hufflepuff portrait and Ravenclaw statue as mechanisms of
  founder commemoration. Private cup provenance and the diadem's later fate
  remain outside Chapter 2 and require their own evidence treatment.
- **Chapter 13, *Customs, Ceremonies and Traditions*:** the Hat's annual songs,
  changing ceremonial role, and any fuller treatment of the sword–Hat
  tradition supported by the evidence.
- **Chapter 15, *Hogwarts and the Wider Wizarding World*:** the goblin–wizard
  ownership dispute may be considered if tied to Hogwarts's public role;
  Chapter 2 must not settle it.
- **Later chapters generally:** later House cultures, common-room architecture,
  ordinary pupil life, founder-relic history and the wider history of magical
  labour.

## Editorial-review judgement

`draft-revision-05.md` is ready for final editorial review. Its core historical
movement remains common educational purpose, several years of cooperation,
divergent standards for pupils, and a documented ancestry dispute. The added
material is integrated through natural attribution in one unified narrative,
while the dossier preserves lower or later source authority and does not justify
invented connective material. The four-part structure and the stopping point
before Chapters 3–5 remain unchanged. Chapter 2 stays `drafted`; this package
does not approve the prose, advance workflow state, or authorise audio.
