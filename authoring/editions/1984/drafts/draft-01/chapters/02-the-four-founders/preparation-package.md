# Chapter 2 Preparation Package — The Four Founders

Status: evidence dossier and proposed outline only. No chapter prose has been
drafted, and the outline remains subject to editorial review.

## Current project state and governing authorities

- The authoritative twenty-chapter structure is
  `authoring/editions/1984/table-of-contents.yaml`. It assigns Chapter 2 the
  founders' backgrounds, attributed aims, and the limits of founder tradition;
  it excludes the full foundation process and detailed House development.
- The chapter-status file still records Chapter 2 as `planned`. This package
  does not advance that state or approve its own outline.
- The current Chapter 1 handoff is the latest working final,
  `chapters/01-before-hogwarts/draft-revision-04.md`. It ends by asking who the
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
  confirmation, tradition, and post-cutoff knowledge.
- The canonical source shape and classifications are defined in
  `docs/instructions/schema-reference.md`. Extraction-era candidate chapter
  labels were used only for discovery and not as the book outline.
- The research layer was treated as read-only. Relevant index and duplicate
  queries were followed by inspection of the exact YAML records. The original
  passages were checked for `cos-ch09-003`–`005`, `gof-ch12-002`,
  `ootp-ch11-003`, and `dh-ch16-003`, and the complete A02, A07, and A08 source
  snapshots were reviewed.

### Confidence used in this package

The confidence labels below assess whether a claim is safe for the reconstructed
1984 narrative. They are not replacements for the canonical YAML `confidence`
field, which chiefly records the reliability of the evidence extraction.

- **High:** explicitly stated by a comparatively strong historical or public
  in-universe source, or independently corroborated at the relevant level.
- **Moderate:** explicit but preserved through ceremonial testimony, later
  tradition, or retrospective authorial exposition; usable only with its source
  character visible.
- **Withhold:** the underlying event may be canonical, but the evidence is a
  private or post-1984 discovery, a contested assertion, or otherwise does not
  establish that the 1984 narrator could know it.

### Core source register

| Evidence ID(s) | Source locator | Canonical YAML |
|---|---|---|
| `cos-ch09-003`–`005` | *Harry Potter and the Chamber of Secrets*, ch. 9, PDF pp. 407–408 | `sources/book-02/chapter-09-the-writing-on-the-wall.yaml` |
| `gof-ch12-002` | *Harry Potter and the Goblet of Fire*, ch. 12, PDF pp. 1093–1094 | `sources/book-04/chapter-12-the-triwizard-tournament.yaml` |
| `ootp-ch11-003` | *Harry Potter and the Order of the Phoenix*, ch. 11, PDF pp. 1765–1767 | `sources/book-05/chapter-11-the-sorting-hat-s-new-song.yaml` |
| `dh-ch16-003` | *Harry Potter and the Deathly Hallows*, ch. 16, PDF p. 3246 | `sources/book-07/chapter-16-godric-s-hollow.yaml` |
| `ext-a02-001`, `ext-a02-002` | A02, *The Sorting Hat*, complete official snapshot | `sources/external/official-rowling/a02-the-sorting-hat.yaml` |
| `ext-a07-005` | A07, *Hufflepuff Common Room*, complete official snapshot | `sources/external/official-rowling/a07-hufflepuff-common-room.yaml` |
| `ext-a08-001`, `ext-a08-002`, `ext-a08-003`, `ext-a08-004` | A08, *The Sword of Gryffindor*, complete official snapshot | `sources/external/official-rowling/a08-the-sword-of-gryffindor.yaml` |
| `cos-ch11-004` | *Chamber of Secrets*, ch. 11, PDF p. 445 | `sources/book-02/chapter-11-the-dueling-club.yaml` |
| `dh-ch07-006` | *Deathly Hallows*, ch. 7, PDF p. 3083 | `sources/book-07/chapter-07-the-will-of-albus-dumbledore.yaml` |
| `dh-ch25-002`, `dh-ch25-003` | *Deathly Hallows*, ch. 25, PDF pp. 3408–3409 | `sources/book-07/chapter-25-shell-cottage.yaml` |
| `dh-ch29-006` | *Deathly Hallows*, ch. 29, PDF p. 3474 | `sources/book-07/chapter-29-the-lost-diadem.yaml` |
| `dh-ch30-003` | *Deathly Hallows*, ch. 30, PDF p. 3482 | `sources/book-07/chapter-30-the-sacking-of-severus-snape.yaml` |
| `dh-ch31-002` | *Deathly Hallows*, ch. 31, PDF p. 3500 | `sources/book-07/chapter-31-the-battle-of-hogwarts.yaml` |
| `hbp-ch10-006` | *Harry Potter and the Half-Blood Prince*, ch. 10, PDF p. 2589 | `sources/book-06/chapter-10-the-house-of-gaunt.yaml` |
| `hbp-ch17-006` | *Half-Blood Prince*, ch. 17, PDF p. 2720 | `sources/book-06/chapter-17-a-sluggish-memory.yaml` |
| `hbp-ch20-005` | *Half-Blood Prince*, ch. 20, PDF p. 2781 | `sources/book-06/chapter-20-lord-voldemort-s-request.yaml` |

The register identifies the primary working set, not every discovery query
result. Source A01 and entry `ext-a03-001` are retained only for the boundary
notes on the Chamber and admissions instruments.

## A. Concise evidence dossier

### Godric Gryffindor

**What the sources explicitly establish**

- Professor Binns names Godric as one of the four founders and, collectively,
  one of the four greatest witches and wizards of the age. This establishes
  stature only at the collective level; it does not rank Godric above the other
  three (`cos-ch09-003`, *Chamber of Secrets*, ch. 9, PDF p. 407).
- Bathilda Bagshot's *A History of Magic* identifies Godric's Hollow as his
  birthplace. This is unusually useful for the 1984 edition because the claim
  appears in a public in-universe history that already existed before the
  cutoff, even though the passage is quoted in a later novel (`dh-ch16-003`,
  *Deathly Hallows*, ch. 16, PDF p. 3246).
- The Sorting Hat's ceremonial account calls him bold, associates him with a
  wild moor, and says that he prized bravery or brave deeds in pupils. These are
  founder traditions, not a full biography (`gof-ch12-002`, *Goblet of Fire*,
  ch. 12, PDF pp. 1093–1094; `ootp-ch11-003`, *Order of the Phoenix*, ch. 11,
  PDF pp. 1765–1767).
- Retrospective official exposition identifies him as a gifted conventional
  swordsman in the pre-Statute world. It also associates him with the
  goblin-made Sword of Gryffindor (`ext-a08-001`–`004`, source A08, *The Sword
  of Gryffindor*).
- Binns identifies Gryffindor as Slytherin's direct opponent in the serious
  argument over pupils of Muggle parentage (`cos-ch09-004`, PDF pp. 407–408).

**Reasonable interpretation**

- Gryffindor rejected Slytherin's proposed ancestry restriction. It is
  reasonable to call this an inclusive position relative to Slytherin's, but
  the evidence does not give Gryffindor a complete admissions policy or prove
  that he accepted every pupil on precisely Hufflepuff's terms.
- The sword and the Hat can make Godric concrete in the chapter because they
  preserve traditions about skill, bravery, judgement, and later worthiness.
  They should serve the argument rather than become a catalogue of relics.

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

### Helga Hufflepuff

**What the sources explicitly establish**

- Binns names Helga as one of the four founders and one of the age's four great
  magical people (`cos-ch09-003`, PDF p. 407).
- The Sorting Hat calls her sweet or good, associates her with a broad valley,
  and gives two connected educational claims: she valued hard workers, and she
  was willing to teach all the pupils and treat them alike (`gof-ch12-002`, PDF
  p. 1094; `ootp-ch11-003`, PDF pp. 1765–1766).
- The same song presents Hufflepuff and Ravenclaw as a close pair of friends.
  This is ceremonial testimony and is not independently documented
  (`ootp-ch11-003`).
- A later official description records a common-room portrait of Helga
  toasting her students with a small two-handled golden cup
  (`ext-a07-005`, source A07, *Hufflepuff Common Room*). A private pre-cutoff
  memory identifies a small golden cup as a Hufflepuff family heirloom
  (`hbp-ch20-005`, *Half-Blood Prince*, ch. 20, PDF p. 2781), but it does not
  establish that a 1984 historian knew its chain of custody.

**Reasonable interpretation**

- Hufflepuff supplies the strongest positive statement of broad educational
  inclusion in the founder tradition. Her principle concerns whom she would
  teach, not proof that later Hogwarts admissions were universal in practice.
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
  not authenticated as the surviving cup.

### Rowena Ravenclaw

**What the sources explicitly establish**

- Binns names Rowena as one of the four founders and one of the four great
  magical people of the age (`cos-ch09-003`, PDF p. 407).
- The Sorting Hat calls her fair, associates her with a glen, and says that she
  preferred the cleverest pupils or those of the sharpest mind
  (`gof-ch12-002`, PDF pp. 1093–1094; `ootp-ch11-003`, PDF pp. 1765–1766).
- The Hat presents Ravenclaw and Hufflepuff as a close pair of friends. As with
  the Gryffindor–Slytherin pairing, this is traditional testimony rather than a
  dated record (`ootp-ch11-003`).
- School tradition says that Ravenclaw's diadem was lost centuries ago and was
  reputed to enhance wisdom (`dh-ch29-006`, *Deathly Hallows*, ch. 29, PDF
  p. 3474). Staff testimony confirms only that it had not been seen in living
  memory (`dh-ch30-003`, ch. 30, PDF p. 3482).

**Reasonable interpretation**

- Rowena's surviving educational identity centres on intellectual ability.
  This supports a discussion of selectivity by aptitude, not a claim that she
  valued knowledge to the exclusion of courage, labour, loyalty, or character.
- The lost-diadem tradition may be used briefly to show how later generations
  remembered her through wisdom. It should not be used to reconstruct her
  classroom, scholarship, or personality.

**Unknown or unsafe to infer**

- No reviewed source gives a named birthplace, family background, writings,
  subjects taught, or a documented role in designing the castle. “From glen”
  must remain no more precise than the song makes it.
- The familiar Ravenclaw motto is later House evidence and is not established
  as Rowena's own composition.
- A later private ghost confession supplies family history and the diadem's
  fate (`dh-ch31-002`, *Deathly Hallows*, ch. 31, PDF p. 3500). That is a
  discovery made during the novels, not knowledge available to the 1984
  narrator, and must not enter Chapter 2.

### Salazar Slytherin

**What the sources explicitly establish**

- Binns names Salazar as one of the four founders and one of the four great
  magical people of the age (`cos-ch09-003`, PDF p. 407).
- Binns's historical account says Slytherin wanted admission restricted to
  all-magic families, disliked taking pupils of Muggle parentage, and regarded
  them as untrustworthy. This is the strongest founder-specific educational
  claim in the corpus (`cos-ch09-004`, PDF pp. 407–408).
- The Sorting Hat calls him shrewd and associates him with a fen. Its songs
  further associate his preferred pupils with ambition and cunning, call him
  power-hungry in one account, and say that he selected pure-blood pupils like
  himself (`gof-ch12-002`, PDF pp. 1093–1094; `ootp-ch11-003`, PDF
  pp. 1765–1766). These descriptions remain poetic testimony; only the
  ancestry restriction is independently supported by Binns.
- Binns says the decisive serious argument was between Slytherin and
  Gryffindor. He also says Slytherin left, but the departure belongs to the
  later rift chapter rather than the narrative body of Chapter 2
  (`cos-ch09-004`).
- Parseltongue and serpent symbolism are firmly associated with Slytherin in
  later school lore, but the indexed carrier is student explanation rather
  than a cited historical record (`cos-ch11-004`, *Chamber of Secrets*, ch. 11,
  PDF p. 445).

**Reasonable interpretation**

- Slytherin's most consequential difference from the other founders is that
  ancestry became a threshold for education, not merely a preferred pupil
  quality. This distinction is explicit enough to organise the chapter's
  central comparison.
- Opposition to pupils of Muggle parentage may be described as distrust and an
  admissions doctrine. No source supports a fuller psychological explanation
  for it.

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
  `hbp-ch20-005`, PDF p. 2781). These facts do not establish what the 1984
  narrator knew and should be withheld from Chapter 2.
- The Chamber belongs to known school legend in the pre-cutoff frame
  (`cos-ch09-005`, PDF p. 408), but its confirmation and details are later
  discoveries. Chapter 2 may identify it only as part of Slytherin's disputed
  memory, if needed at all; Chapter 5 owns the substantive treatment.

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

- The Sorting Hat says the founders shared a hope of educating young magical
  people, describes them as good friends, and pairs Gryffindor with Slytherin
  and Hufflepuff with Ravenclaw (`gof-ch12-002`; `ootp-ch11-003`). The shared
  educational purpose corroborates Binns; the intimate friendship pairings do
  not.
- The Hat says their different preferences initially caused little strife
  because each founder could teach chosen pupils within a House. This is useful
  evidence that difference did not immediately prevent cooperation, but the
  creation and operation of the Houses belong to Chapter 4.
- The Hat's account of later House rivalry, duelling, and fighting is more
  expansive than Binns's concise report of disagreements and a serious
  Gryffindor–Slytherin argument. It should be attributed as tradition, not
  silently promoted to the historical minimum.

**What the partnership does not establish**

- No source explains how the four met, who first proposed the school, how work
  or authority was divided, what each taught, or what conversations produced
  their agreement.
- Cooperation does not prove that their personalities were alike or that every
  later House value was already a complete educational philosophy.
- Their eventual disagreement does not prove that the partnership was a sham
  from the beginning. Conversely, several years of harmony do not erase the
  seriousness of an ancestry rule that eventually challenged the common
  project.

## B. Important claim table

| ID | Important assertion | Evidence status | Canonical source and locator | 1984 narrative confidence | Qualification or conflict | Placement |
|---|---|---|---|---|---|---|
| C2-01 | Hogwarts had four named founders, collectively described as the age's greatest witches and wizards. | Explicit historical account | `cos-ch09-003` — *CoS* ch. 9, PDF p. 407; YAML `sources/book-02/chapter-09-the-writing-on-the-wall.yaml` | High | Collective praise gives no individual ranking or biography. | Chapter 2 |
| C2-02 | The four shared a project of finding and educating magical children. | Explicit; poetically corroborated | `cos-ch09-003`; `gof-ch12-002` — *GoF* ch. 12, PDF pp. 1093–1094 | High for the educational undertaking; moderate for the Hat's wording | Motives, curriculum, and sequence remain unknown. | Chapter 2; mechanics in Chapter 3 |
| C2-03 | They worked in harmony for several years. | Explicit historical account | `cos-ch09-004` — *CoS* ch. 9, PDF pp. 407–408 | High | “Harmony” does not prove identical beliefs. | Chapter 2 |
| C2-04 | All four were close friends; Gryffindor–Slytherin and Hufflepuff–Ravenclaw formed particular pairs. | Ceremonial testimony | `ootp-ch11-003` — *OotP* ch. 11, PDF pp. 1765–1766 | Moderate | Binns corroborates cooperation, not private intimacy or pairings. | Chapter 2, clearly attributed |
| C2-05 | Godric Gryffindor was born in Godric's Hollow. | Explicit in public in-universe history | `dh-ch16-003` — *DH* ch. 16, PDF p. 3246 | High | Quoted in a later novel, but attributed to pre-cutoff *A History of Magic*. | Chapter 2 |
| C2-06 | Gryffindor valued bravery in pupils. | Ceremonial founder tradition | `gof-ch12-002`; `ootp-ch11-003` | Moderate | A preferred pupil quality is not a complete personality. | Chapter 2; House mechanics in Chapter 4 |
| C2-07 | Gryffindor was an accomplished conventional duellist. | Later official retrospective exposition | `ext-a08-003` — source A08, snapshot `resources/external/official-rowling/harrypotter-com/a08-the-sword-of-gryffindor.md` | Moderate | No dated in-universe record is cited. | Chapter 2, brief contextual detail |
| C2-08 | Gryffindor opposed Slytherin over pupils of Muggle parentage. | Explicit historical account | `cos-ch09-004` | High | This proves opposition to Slytherin's rule, not Gryffindor's entire admissions policy. | Chapter 2; outcome in Chapter 5 |
| C2-09 | Hufflepuff valued hard work. | Ceremonial founder tradition | `gof-ch12-002` — PDF p. 1094 | Moderate | Later House industriousness cannot supply biography. | Chapter 2 |
| C2-10 | Hufflepuff would teach all pupils and treat them alike. | Ceremonial founder tradition | `ootp-ch11-003` — PDF p. 1765 | Moderate | Strong evidence of the remembered ideal, not proof of universal admissions in practice. | Chapter 2 |
| C2-11 | Ravenclaw preferred pupils of exceptional intelligence or sharp mind. | Ceremonial founder tradition | `gof-ch12-002`; `ootp-ch11-003` | Moderate | No evidence identifies her subjects, writings, or teaching method. | Chapter 2 |
| C2-12 | Slytherin wished to restrict magical learning to all-magic families and distrusted pupils of Muggle parentage. | Explicit historical account; ceremonial corroboration | `cos-ch09-004`; `ootp-ch11-003` | High | The Hat's wider labels—cunning, ambition, power hunger—remain traditional characterisation. | Chapter 2; consequences in Chapters 3 and 5 |
| C2-13 | The founder traditions give broad origins: Gryffindor from moor, Ravenclaw from glen, Hufflepuff from valley, Slytherin from fen. | Poetic tradition | `gof-ch12-002` — PDF p. 1093 | Moderate as tradition; low as exact geography | These are not named birthplaces and must not be mapped to modern regions. | Chapter 2, one compact passage |
| C2-14 | Their different pupil preferences were initially accommodated without serious strife. | Ceremonial testimony, broadly consistent with Binns | `ootp-ch11-003`; `cos-ch09-004` | Moderate | The sources do not settle whether all preferences existed from the first year. | Chapter 2; structure in Chapters 3–4 |
| C2-15 | A serious argument developed specifically between Slytherin and Gryffindor, after which Slytherin left. | Explicit historical account | `cos-ch09-004` | High | Chapter 2 needs the dispute to define the people, but not the departure narrative or consequences. | Preview in Chapter 2; full treatment in Chapter 5 |
| C2-16 | Fighting, duelling, and House attempts to rule nearly ended the school. | Ceremonial testimony | `ootp-ch11-003` — PDF p. 1766 | Moderate | More dramatic and more detailed than Binns; no dates or independent corroboration. | Reserve for Chapter 5 except brief attribution |
| C2-17 | Tradition makes Gryffindor's old hat a joint work of all four founders. | Explicitly labelled legend in later official source; supported by Hat song | `ext-a02-001`–`002` — source A02; `gof-ch12-002` | Moderate | Important evidence for collective magical work, but the genesis is presented as legend. | Mention only if needed in Chapter 2; detail in Chapter 4 |
| C2-18 | The Sword of Gryffindor is an old founder relic associated with worthiness. | Historical tradition and later official exposition | `dh-ch07-006` — *DH* ch. 7, PDF p. 3083; `ext-a08-001`–`004` | Moderate | Goblin and wizard accounts dispute ownership; do not resolve silently. | Brief Chapter 2 association; fuller relic treatment elsewhere |
| C2-19 | A golden cup is associated with Hufflepuff in House memory and private heirloom testimony. | Later public memorial plus private pre-cutoff memory | `ext-a07-005`; `hbp-ch20-005` — PDF p. 2781 | Moderate for association; withhold chain of custody | Portrait date and identity of the depicted cup are unknown; memory was not public. | Brief association only |
| C2-20 | Ravenclaw's lost diadem was traditionally associated with wisdom. | Later report of longstanding school tradition | `dh-ch29-006` — *DH* ch. 29, PDF p. 3474; `dh-ch30-003` — ch. 30, PDF p. 3482 | Moderate | Its hidden history and fate are post-cutoff discoveries. | Brief association only; no later discovery |
| C2-21 | Slytherin had a surviving line associated with Parseltongue and a locket. | Self-interested family claim plus later retrospective reconstruction | `hbp-ch10-006`, PDF p. 2589; `hbp-ch17-006`, PDF p. 2720; `hbp-ch20-005`, PDF p. 2781 | Withhold | Does not establish narrator access; not needed for the founder argument. | Elsewhere, if a later approved chapter can establish access |
| C2-22 | The Chamber was part of pre-cutoff Slytherin legend, not verified history for the 1984 narrator. | Explicitly presented as legend by Binns | `cos-ch09-005` — *CoS* ch. 9, PDF p. 408 | High as evidence of the legend; not as proof of the Chamber | Later confirmation must not leak backwards. | Chapter 5 |

## C. Contradictions, uncertainties, and unresolved questions

### Accounts that must not be silently harmonised

1. **When did the differences begin?** Binns says the founders worked in
   harmony for a few years and then disagreements arose. The Hat presents
   distinct pupil preferences as present at the formation of the Houses, but
   says those differences initially caused little strife. The accounts can be
   read together, but they do not establish whether Slytherin's ancestry rule
   was original, developed, or merely became intolerable later.
2. **How inclusive was Hufflepuff's standard?** One song says hard workers were
   most worthy of admission; another says she taught everyone and treated them
   alike. These can coexist as preference and policy, but the source does not
   explain the mechanism.
3. **How close were the founders personally?** Binns supports cooperation and
   harmony; only the Hat calls them good friends and supplies the two friendship
   pairs. Personal intimacy must remain attributed tradition.
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
- Which founder relic traditions were publicly documented by 1984, rather than
  privately known, preserved only in a House space of unknown date, or revealed
  during the novels?
- When and how did the Sword of Gryffindor become connected to the Sorting Hat
  (`sorting-ceremony-006`)?
- What formal source links Slytherin, Parseltongue, and the serpent emblem
  independently of student lore (`pre-hogwarts-historical-context-009`)?

### Research-layer observation

The complete A30 source snapshot contains Slytherin-line and founder-wand
material, but the current A30 YAML contains only comparative Ilvermorny entries
and no evidence record for those passages. This is a discovery/indexing gap, not
permission to repair the protected research layer. The material is also later
retrospective exposition and unnecessary to Chapter 2's argument.

## D. Proposed chapter argument

The evidence supports a chapter about a partnership more securely than it
supports four conventional biographies. The founders enter history as four
exceptional magical people who agreed that young magic-users should be found
and educated together. Their agreement was substantial: it endured for years
and produced a shared undertaking. It was not agreement about everything.
Founder tradition preserves four different measures of promise—courage,
intelligence, labour, and ambition—while Hufflepuff is also remembered for
teaching without exclusion and Slytherin for making ancestry a condition of
trust and admission.

The chapter's central movement should therefore be from shared purpose to the
limits of pluralism. Differences in aptitude or emphasis could apparently be
accommodated for a time. Slytherin's lineage restriction was different in kind:
it asked not merely which qualities education should cultivate, but which
children were entitled to receive it. That proposition is strongly supported
by Binns and explains why the founder story cannot be reduced to four equal
House virtues. The chapter should end when that difference becomes an open
rift, leaving the making and early operation of the institution to Chapter 3
and the departure, Chamber tradition, and longer consequences to Chapter 5.

This argument must remain proportionate to the sources. It does not claim that
all four began with complete philosophies, that Hufflepuff alone admitted
Muggle-born pupils, or that the founders foresaw the later identities of their
Houses. The Hat supplies a powerful traditional account, not permission to
invent scenes, speeches, or inner motives.

## E. Proposed narrative outline

### 1. Four Names in a Long Memory

**Purpose:** Pick up Chapter 1's closing question and establish the uneven
record. The four names, collective stature, shared work, and one named
birthplace are secure; most personal chronology is not. Introduce Binns as the
historical minimum and the Sorting Hat as a ceremonially powerful but less
literal witness.

**Evidence:** `cos-ch09-003`; `dh-ch16-003`; `gof-ch12-002`;
`ootp-ch11-003`.

**Limits to preserve:** Do not open with four miniature life stories. Do not
turn moor, glen, valley, and fen into modern national identities. State the
source hierarchy once and then let it govern the chapter.

### 2. The Work They Chose Together

**Purpose:** Establish the positive centre of the chapter before presenting
differences. Four exceptional practitioners chose a common educational task,
sought magical children, and worked in harmony for several years. The Hat's
language of shared hope and friendship can enrich this minimum if explicitly
identified as tradition.

**Evidence:** `cos-ch09-003`–`004`; `gof-ch12-002`;
`ootp-ch11-003`.

**Limits to preserve:** Do not narrate the plan's conception, site choice,
castle building, opening, recruitment machinery, or division of labour. Those
are Chapter 3 matters unless one sentence is required to make the partnership
intelligible.

### 3. Hufflepuff and Ravenclaw: Two Answers to Worth

**Purpose:** Use the Hat's claimed friendship pair to compare educational
outlooks rather than to produce detached biographies. Hufflepuff's remembered
commitment joins hard work to broad inclusion; Ravenclaw's joins education to
exceptional intelligence. Their positions show that founders could disagree
about the most desirable pupil without yet disputing a child's magical
legitimacy.

**Evidence:** `gof-ch12-002`; `ootp-ch11-003`; limited memorial support from
`ext-a07-005`, `dh-ch29-006`, and `dh-ch30-003`.

**Limits to preserve:** The friendship is traditional. Do not invent exchanges
between them. Use the portrait, cup, or diadem only if one concrete association
helps explain later memory; do not turn the section into an object inventory or
import the diadem's later-discovered history.

### 4. Gryffindor and Slytherin: Friendship at the Fault Line

**Purpose:** Bring the most consequential pairing into focus. The Hat remembers
Gryffindor and Slytherin as close friends; Binns remembers them as the principals
in the decisive admissions argument. Godric's birthplace, bravery tradition,
and documented skill with a sword can make him concrete. Slytherin's shrewdness,
ambition, and cunning belong to tradition, while his distrust of pupils of
Muggle parentage belongs to the firmer historical account.

**Evidence:** `dh-ch16-003`; `ext-a08-003`; `gof-ch12-002`;
`ootp-ch11-003`; `cos-ch09-004`.

**Limits to preserve:** Do not transform the pair into lifelong rivals or write
the argument as a scene. The sword may illustrate Godric's world and disputed
memory, but the provenance controversy must stay qualified. Slytherin's
motivation must not be invented from persecution, fear, family history, or
later descendants.

### 5. Four Measures of Promise

**Purpose:** Compare the founder traditions directly. Courage, intelligence,
hard work, and ambition are positive pupil preferences; Hufflepuff's universal
offer and Slytherin's blood threshold concern access itself. Explain why a
shared school could contain several educational emphases but came under strain
when one founder proposed excluding otherwise magical children by parentage.

**Evidence:** `gof-ch12-002`; `ootp-ch11-003`; the stronger admissions account
in `cos-ch09-004`.

**Limits to preserve:** These are attributed preferences, not exhaustive
personal psychologies and not complete descriptions of the later Houses. The
mechanism and development of the four-House system belong to Chapter 4.

### 6. When Difference Became Exclusion

**Purpose:** Close on the boundary between the founders as people and the
institutional history that follows. Binns securely establishes a growing rift,
a serious Gryffindor–Slytherin argument, and eventual departure. The Hat's
broader memory of House conflict and duelling may be noted as tradition, chiefly
to show how later Hogwarts remembered the rupture.

**Evidence:** `cos-ch09-004`; `ootp-ch11-003`.

**Limits to preserve:** Do not narrate the departure, Chamber, duels, factional
sequence, or institutional consequences in detail. End with the historical
question Chapter 3 must answer: how did four people with different standards
turn their common educational purpose into a functioning school before those
differences broke the partnership?

## F. Chapter boundary and reserved material

### Chapter 2 owns

- the documentary limits of founder biography;
- the four names and their collective historical stature;
- the small amount of usable origin evidence;
- attributed qualities and educational preferences, with the Hat treated as
  ceremonial testimony;
- the minimum evidence for friendship, cooperation, and several years of
  harmony;
- the distinction between preferences based on aptitude or effort and
  Slytherin's restriction based on ancestry;
- the emergence of disagreement, stopping before its institutional narrative;
- a small number of founder-associated objects or traditions only where they
  reveal how a founder was remembered.

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
  and the Sorting Hat's continuing role.
- **Chapter 5, *The Departure of Salazar Slytherin*:** the full dispute,
  Slytherin's departure, the Chamber as pre-cutoff legend, and the consequences
  of the rupture. Later proof of the Chamber must not be imported into the 1984
  narrator's knowledge.
- **Later chapters:** later House cultures, common-room architecture, ordinary
  pupil life, and comprehensive histories of founder relics.

## Draft-readiness judgement

The chapter is ready for editorial review of its argument and outline, but not
for prose drafting. The core historical movement is well supported: common
educational purpose, several years of cooperation, divergent standards for
pupils, and a documented ancestry dispute. Review is still required to approve
the comparative structure, the amount of weight given to the Sorting Hat, and
the exact stopping point before Chapters 3–5.
