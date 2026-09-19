# Chapter 3 Preparation Package — The Founding of Hogwarts

Status: evidence dossier and proposed outline only. No chapter prose has been
drafted. The outline is `outlined`, not `outline_approved`, and remains subject
to editorial review.

## Governing scope

- The project now produces one Unified Expanded Edition under
  `authoring/editorial-policy.md`. The reconstructed 1984 narrative remains the
  historical and literary foundation, not an evidence cutoff.
- The legacy `authoring/editions/1984/` path is retained for continuity and does
  not limit the corpus.
- The authoritative twenty-chapter structure remains
  `authoring/editions/1984/table-of-contents.yaml`. Chapter 3 owns the foundation
  chronology, site, common purpose, castle establishment, initial admissions
  machinery, and the earliest operation of the school. Chapter 4 owns the
  developed four-House system; Chapter 5 owns the full rift, Slytherin's
  departure, and the Chamber tradition and its later confirmation.
- `draft-01/style-lock.md` remains the prose authority. This package applies its
  distinction between reconstructed Bagshot passages and later editorial
  additions.
- The research layer was read only. No canonical YAML, index, source snapshot,
  PDF, open question, or provenance record was altered.

## Method and corpus review

The search followed `authoring/shared/research-interface.md`: compact entry and
tag indexes first, exact canonical YAML second, duplicate/corroboration queries
third, and original PDF or snapshot text where wording or provenance mattered.

Queries covered `founding`, `founders`, `school-origins`, `castle`,
`muggle-persecution`, `castle-completion`, `hogwarts-founders`, `school-site`,
`founder-era`, `founders-era`, `foundation-legend`, `admission-system`,
`book-of-admittance`, `quill-of-acceptance`, `sorting-hat`, and `house-system`.
A repository-wide source search also checked variants of *founded*,
*foundation*, *built the castle*, *over a thousand years*, *tenth century*,
*school site*, *Pensieve*, *Quill of Acceptance*, and *Book of Admittance*.

The exact novel passages for `cos-ch09-003`–`005`, `gof-ch12-002`, and
`ootp-ch11-003` were checked against the source PDF. The complete official
snapshots for A02, A03, A16, and A17 and the complete preservation transcript
for B10 were reviewed. The enriched open-question overlay was treated only as a
research lead: its W-FOUNDERS item mentions a broad tenth-century frame, but no
canonical evidence ID or captured source supports that refinement. The dossier
therefore retains “over a thousand years ago” and leaves the precise date open.

## Required classification model

Every material claim below separates:

- **Event chronology:** when the event or condition is said to have occurred.
- **Carrier chronology and provenance:** when and where the surviving evidence
  was recorded, including authority for external sources.
- **Knowledge access:** one of:
  - `bagshot_candidate` — plausibly available to the reconstructed narrator;
  - `later_discovery_earlier_event` — later evidence about a pre-1984 event;
  - `later_historical_event` — an event occurring after 1984;
  - `tradition_or_disputed` — a legend, poetic account, contested claim, or
    otherwise unverified tradition;
  - `editorial_interpretation` — a bounded conclusion drawn by the editors.

A claim may carry more than one access label. For example, a founder-era event
can be a later discovery and also a disputed tradition. Canonical YAML
`confidence` describes the extraction or record; the chapter-level assessment
below determines safe authorship and placement.

## Core source and provenance register

| Evidence ID(s) | Exact locator | Carrier and provenance | Principal use |
|---|---|---|---|
| `cos-ch09-003` | *Chamber of Secrets*, ch. 9, PDF p. 407; YAML `sources/book-02/chapter-09-the-writing-on-the-wall.yaml` | Primary novel carrier; Binns presents a public historical account but does not name his underlying sources | Date range, four founders, remote castle site, persecution context |
| `cos-ch09-004` | *Chamber of Secrets*, ch. 9, PDF pp. 407–408; same YAML | Primary novel carrier; historical summary | First pupils, several years of joint work, later rift boundary |
| `cos-ch09-005` | *Chamber of Secrets*, ch. 9, PDF p. 408; same YAML | Primary novel carrier; Binns explicitly separates history from legend | Historiographical boundary; reserve Chamber substance for Chapter 5 |
| `gof-ch12-002` | *Goblet of Fire*, ch. 12, PDF pp. 1093–1094; YAML `sources/book-04/chapter-12-the-triwizard-tournament.yaml` | Primary novel carrier; ceremonial testimony recorded after 1984 | Common educational purpose, House preferences, Hat genesis tradition |
| `ootp-ch11-003` | *Order of the Phoenix*, ch. 11, PDF pp. 1765–1767; YAML `sources/book-05/chapter-11-the-sorting-hat-s-new-song.yaml` | Primary novel carrier; poetic testimony recorded after 1984 | Joint building and teaching, early harmony, later conflict boundary |
| `ext-a02-001`–`002` | A02, *The Sorting Hat*, section “The Sorting Hat”; YAML `sources/external/official-rowling/a02-the-sorting-hat.yaml` | Official Rowling original, authority A, complete original-carrier snapshot, published 2015-08-10 | Later exposition of the joint enchantment and retained founder intelligence |
| `ext-a03-001`–`006` | A03, *The Quill of Acceptance and The Book of Admittance*, named section; YAML `sources/external/official-rowling/a03-quill-of-acceptance-and-book-of-admittance.yaml` | Official Rowling original, authority A, complete original-carrier snapshot, published 2015-08-10 | Castle completion, founder-installed admissions instruments, later operation |
| `ext-a17-002`–`003` | A17, *Pensieve*, final body paragraph; YAML `sources/external/official-rowling/a17-pensieve.yaml` | Official Rowling original, authority A, complete original-carrier snapshot, published 2015-08-10 | Artefact predating Hogwarts and expressly unsubstantiated site-selection legend |
| `ext-a16-003` | A16, *Peeves*, section “Peeves”; YAML `sources/external/official-rowling/a16-peeves.yaml` | Official Rowling original, authority A, complete original-carrier snapshot, published 2015-08-10 | Founder appointment of caretaker Hankerton Humble |
| `ext-b10-001` | B10, PotterCast interview, “House-elves discussion”; YAML `sources/external/interviews/b10-pottercast-j-k-rowling-interview.yaml` | Preservation transcription, authority D, complete capture, published December 2007/January 2008 | Later authorial claim about Hufflepuff, refuge, and house-elf labour |
| `fb-ch02-004` | *Fantastic Beasts and Where to Find Them*, “A Brief History of Muggle Awareness of Fantastic Beasts”, PDF p. 15, printed p. xv; YAML `sources/book-fb/chapter-02-muggle-awareness-of-fantastic-beasts.yaml` | In-universe historical carrier; direct page inspection recorded in canonical YAML | Context for fear, creature sightings, and persecution |

## Complete relevant-candidate disposition

The register above contains the claims that can materially shape Chapter 3.
The following records were also returned by the complete founding/founder
searches and were dispositioned rather than silently omitted.

| Evidence ID(s) | Disposition | Reason |
|---|---|---|
| `gof-ch12-003` | Supporting method evidence | Establishes annual, changing Hat songs; useful for assessing the later songs as carriers, while ceremony detail belongs to Chapter 13. |
| `ext-a02-003` | Reserve for Chapters 4/13 | Centuries of Sorting and error claims concern the mature House system, not initial establishment. |
| `ext-a07-005` | Reserve for Chapters 2/12 | Hufflepuff portrait and cup concern founder memory, not the foundation process. |
| `ootp-ch17-002` | Reserve for Chapters 6/10 | Explicitly attributes a gendered dormitory rule to the founders and to *Hogwarts: A History*; it is relevant to early design but would pull Chapter 3 into residential architecture and pupil life. |
| `cos-ch09-001` | Reserve for Chapter 5/source-method note | Hermione expects *Hogwarts: A History* to discuss the Chamber, but the passage neither quotes the book nor proves its exact coverage. |
| `ext-a01-001`–`003` | Reserve for Chapters 5/6 | Later official evidence confirms the Chamber, its founder-era construction, later plumbing adaptation, and failed searches. It must not displace Chapter 5 or be presented as Bagshot knowledge. |
| `dh-ch31-002` | Reserve for Chapters 2/12 | Helena Ravenclaw's testimony concerns concealed family and relic history, not the joint establishment of the school. |
| `ext-a17-001`, `ext-a17-004` | Reserve for Chapters 8/12 | The school-owned memory library and general Pensieve burial custom concern governance and institutional memory. |
| `ext-a16-001`–`002`, `ext-a16-004`–`006`, `ext-b06-001`, `ext-b09-002` | Reserve for Chapters 6/8/12/17 | These establish Peeves's nature, later incidents, and long residence. Only the founder appointment in `ext-a16-003` bears directly on initial administration. |
| `ext-a30-001` and other comparative-school results | Exclude from Chapter 3 | They concern later schools adapting a House model, not evidence of Hogwarts's own foundation. |
| Founder relic records returned by broad `founders` or `sorting-hat` searches | Reserve for Chapters 2, 4, 5, 12, or 13 | The sword, cup, diadem, locket, and later Hat events do not explain the initial establishment. |
| Cursed Child results and other altered-timeline records | Exclude from the Chapter 3 argument | They add no primary-timeline evidence for Hogwarts's foundation; extraction metadata must remain intact. |

## Evidence dossier

### 1. Date and historical setting

**Established or strongly supported**

- Binns says Hogwarts was founded more than a thousand years before the 1992
  classroom account and explicitly says the precise date is uncertain
  (`cos-ch09-003`, PDF p. 407).
- The 1994 Hat song independently uses a similarly broad “thousand years or
  more” frame (`gof-ch12-002`, PDF p. 1093).
- Binns connects the remote site to fear of magic among ordinary people and
  persecution of witches and wizards (`cos-ch09-003`). `fb-ch02-004` supplies
  compatible wider context in which misunderstood magical creatures intensified
  anti-wizard fear.

**Limits**

- The corpus does not support a precise year, charter date, regnal date, or
  construction duration. The unverified W-FOUNDERS lead is not canonical
  evidence for a tenth-century dating.
- Wider persecution context does not prove a particular attack on the founders,
  a single national policy, or one decisive incident that caused the school to
  be built.

**Access**

- Event chronology: founder era, more than a millennium before the 1990s;
  exact date unknown.
- Knowledge access: `bagshot_candidate` for the broad age, remoteness, and
  persecution rationale; `editorial_interpretation` for any synthesis with the
  creature-history context.

### 2. Purpose and partnership

**Established or strongly supported**

- Four founders—Godric Gryffindor, Helga Hufflepuff, Rowena Ravenclaw, and
  Salazar Slytherin—built the castle together (`cos-ch09-003`).
- Binns says they sought children who showed signs of magic, brought them to the
  castle, and educated them; the founders then worked together in harmony for
  several years (`cos-ch09-004`).
- The 1994 Hat song corroborates a common intention to educate young magical
  people (`gof-ch12-002`). The 1995 song claims a common goal of building and
  teaching and describes close friendship (`ootp-ch11-003`).

**Limits**

- No reviewed source says who proposed the school, how the founders met, how
  they divided labour, how construction was financed, what each taught, or what
  legal or political authority authorised the institution.
- “Built together” supports joint responsibility, not personal masonry by all
  four or equal responsibility for every enchantment and room.
- The Hat's friendship pairings and dialogue-like lyrics are traditional poetic
  testimony, not a recoverable transcript.

**Access**

- Event chronology: foundation and first several years.
- Knowledge access: `bagshot_candidate` for the common undertaking and several
  years of cooperation; `tradition_or_disputed` for the Hat's intimate
  friendship detail and exact wording.

### 3. Site selection, concealment, and construction

**Established or strongly supported**

- The founders placed the castle far from Muggle attention in a persecutory
  age (`cos-ch09-003`). This supplies motive and broad location logic, not a
  recoverable building plan.
- A17 describes the Hogwarts Pensieve as older than the school and bearing
  modified Saxon runes (`ext-a17-002`). It then records an expressly
  unsubstantiated legend that the founders found it half-buried on the spot
  where they chose to erect Hogwarts (`ext-a17-003`).
- A03 states that the castle reached a point described as completion
  (`ext-a03-001`).

**Limits**

- No reviewed evidence identifies the site's discoverer, land ownership,
  builders, construction spells, stages, exact completion date, original floor
  plan, or whether the castle later expanded from a smaller structure.
- The Pensieve story is useful evidence of a foundation tradition, not proof
  that the artefact caused the site choice or that the legend existed in
  Bagshot's day.
- “Completion” does not prove that the castle thereafter remained physically
  unchanged.

**Access**

- Event chronology: site selection and castle construction during the founder
  era.
- Carrier chronology: the detailed Pensieve and completion claims survive in
  2015 authority-A official originals.
- Knowledge access: `bagshot_candidate` for remoteness and concealment motive;
  `later_discovery_earlier_event` for castle completion as the setting of the
  Book and Quill placement; both `later_discovery_earlier_event` and
  `tradition_or_disputed` for the Pensieve site legend.

### 4. Finding pupils and establishing admissions

**Established or strongly supported**

- Binns says the founders personally sought children showing signs of magic and
  brought them to Hogwarts (`cos-ch09-004`).
- A03 says that, upon completion of the castle, the four founders placed the
  Book of Admittance and Quill of Acceptance in a locked tower
  (`ext-a03-001`). The source presents them as the continuing selection
  mechanism (`ext-a03-002`–`004`).
- The source's later examples explain the instrument pair's threshold and
  exclusion of non-magical children (`ext-a03-005`–`006`), but do not describe
  founder-era cases.

**Reasonable sequence**

- The evidence supports a bounded transition from founders personally seeking
  pupils to an enduring magical detection and admission mechanism associated
  with castle completion. It does not establish the length of the transition,
  whether both methods overlapped, or who made and enchanted the instruments.

**Limits**

- A03 does not date the installation, name the maker, explain the magic, or
  independently corroborate the founders' act.
- The modern operational examples must not be projected backwards as named
  founder-era incidents.
- Admission detection is not the same as invitation, transport, fees,
  residence, curriculum placement, or House assignment.

**Access**

- Event chronology: founder era; installation at castle completion; operation
  continuing into later centuries.
- Carrier chronology: A03 is a 2015 authority-A official original.
- Knowledge access: `bagshot_candidate` for founders seeking and bringing
  magical children; `later_discovery_earlier_event` for the founder placement
  and mechanics of the Book and Quill.

### 5. Early institutional operation

**Established or strongly supported**

- The school functioned for several years under all four founders
  (`cos-ch09-004`).
- A16 names Hankerton Humble as a caretaker appointed by the four founders
  (`ext-a16-003`). This is the only reviewed record that gives a named
  non-founder appointment tied directly to the foundation era.
- The Hat tradition says each founder taught pupils selected according to
  differing preferences (`gof-ch12-002`; `ootp-ch11-003`). That evidence
  establishes a remembered relationship between founders, teaching, and pupil
  groups, while Chapter 4 owns the institutional development of the Houses.
- A02 later describes the Hat as a joint enchantment containing the founders'
  intelligence, designed to continue selection after their deaths
  (`ext-a02-001`–`002`). The source itself introduces the genesis as legend.

**Limits**

- One named caretaker does not prove the size, hierarchy, or full duties of an
  original staff.
- No reviewed source identifies the first head, first school year, opening
  ceremony, timetable, curriculum, governance charter, or first cohort.
- Chapter 3 may establish that early teaching and administration existed, but
  it must not pre-empt Chapter 4 with a full account of House organisation or
  Chapter 8 with a mature governance system.

**Access**

- Event chronology: first years of operation and succession planning.
- Carrier chronology: the caretaker detail survives in a 2015 authority-A
  official original; the Hat detail in later songs and a 2015 authority-A
  official original.
- Knowledge access: `later_discovery_earlier_event` for Hankerton Humble;
  `tradition_or_disputed` for the Hat's genesis and technical detail;
  `bagshot_candidate` only for the limited proposition that founder traditions
  connected teaching groups with the founders' preferences.

### 6. Labour at the founding

**Later evidence**

- In a preserved 2007/2008 interview transcript, Rowling says Hufflepuff
  offered house-elves refuge and better conditions of work rather than
  abolition (`ext-b10-001`). The claim concerns the founder era but is framed
  as a moral interpretation and identifies no in-universe contemporary source.

**Authority and conflict**

- B10 is a complete preservation transcription with authority D, not an
  official original carrier. Its claim is explicit but singly attested.
- Canonical references establish that the reconstructed *Hogwarts: A History*
  omits Hogwarts house-elf servitude. The Unified Expanded Edition may address
  it, but it must not place the claim in Bagshot's voice or erase the omission.
- “Refuge” and improved conditions must not be paraphrased as freedom, payment,
  consent, or abolition; the source expressly stops short of those claims.

**Access and placement**

- Event chronology: founder era, exact date and sequence unknown.
- Carrier chronology: December 2007/January 2008 preservation transcription.
- Knowledge access: `later_discovery_earlier_event` and
  `editorial_interpretation`, with authority-D qualification.
- Proposed treatment: a short, separately labelled editorial addendum after
  the main chapter. Integrating the claim into Bagshot's foundation narrative
  would contradict the documented omission and interrupt the main chronology
  with a substantial ethical and source-authority qualification.

## Important claim matrix

| ID | Claim | Event chronology | Carrier/provenance | Knowledge access | Confidence and limitation | Proposed placement |
|---|---|---|---|---|---|---|
| C3-01 | Hogwarts was founded more than a thousand years before the 1990s; the exact date is uncertain. | Founder era; exact year unknown | `cos-ch09-003`, PDF p. 407; `gof-ch12-002`, PDF p. 1093 | `bagshot_candidate` | High for broad age; no precise year | Bagshot opening |
| C3-02 | Gryffindor, Hufflepuff, Ravenclaw, and Slytherin jointly established the school and castle. | Foundation | `cos-ch09-003`, PDF p. 407 | `bagshot_candidate` | High; “built together” does not specify physical labour | Bagshot core |
| C3-03 | The remote castle site answered a climate of Muggle fear and persecution. | Foundation context | `cos-ch09-003`; supporting context `fb-ch02-004`, PDF p. 15 | `bagshot_candidate`; synthesis is `editorial_interpretation` | High for Binns's rationale; broader causal synthesis must remain bounded | Bagshot core with restrained context |
| C3-04 | The founders sought magical children, brought them to the castle, and educated them. | Earliest operation | `cos-ch09-004`, PDF pp. 407–408 | `bagshot_candidate` | High; recruitment logistics unknown | Bagshot core |
| C3-05 | The founders shared an educational purpose and worked together for several years. | Foundation through early operation | `cos-ch09-004`; `gof-ch12-002`; `ootp-ch11-003` | `bagshot_candidate` for the minimum; `tradition_or_disputed` for friendship detail | High for cooperation; moderate for poetic enlargement | Bagshot core |
| C3-06 | Tradition remembers the founders as building and teaching together. | Foundation | `ootp-ch11-003`, PDF pp. 1765–1766 | `tradition_or_disputed` | Moderate; later song, not transcript | Bagshot-attributed tradition or editorial note |
| C3-07 | The Pensieve predates Hogwarts. | Before foundation | `ext-a17-002`, A17 official snapshot | `later_discovery_earlier_event` | High extraction confidence; no dating method | Integrated editorial addition |
| C3-08 | An unsubstantiated legend says the founders found the Pensieve at the chosen school site. | Site selection | `ext-a17-003`, A17 official snapshot | `later_discovery_earlier_event`; `tradition_or_disputed` | Explicitly unsubstantiated | Brief integrated editorial addition |
| C3-09 | The castle reached a point described as completion. | Foundation | `ext-a03-001`, A03 official snapshot | `later_discovery_earlier_event` | Explicit in authority-A later source; no date or corroboration | Integrated editorial addition |
| C3-10 | At castle completion, the founders placed the Book of Admittance and Quill of Acceptance in a locked tower. | Foundation/initial administration | `ext-a03-001`, A03 official snapshot | `later_discovery_earlier_event` | High record confidence; later single source | Integrated editorial addition |
| C3-11 | The Book and Quill became the enduring Hogwarts selection mechanism. | From foundation into later centuries | `ext-a03-002`–`004`, A03 official snapshot | `later_discovery_earlier_event` | High; mechanism unexplained and logistics beyond inscription absent | Integrated editorial addition; later operation concise |
| C3-12 | The founders appointed caretaker Hankerton Humble. | Founder era | `ext-a16-003`, A16 official snapshot | `later_discovery_earlier_event` | High record confidence; single retrospective source | Integrated editorial addition, one sentence at most |
| C3-13 | Tradition makes the Sorting Hat a joint founder enchantment for succession in pupil selection. | Foundation/early succession planning | `gof-ch12-002`; `ext-a02-001`–`002` | `tradition_or_disputed`; later carrier | Moderate for genesis; exact magic and timing unknown | Brief bridge; full treatment Chapter 4/13 |
| C3-14 | A later authorial account associates Hufflepuff with house-elf refuge and improved working conditions. | Founder era; exact sequence unknown | `ext-b10-001`, B10 authority-D preservation transcript | `later_discovery_earlier_event`; `editorial_interpretation` | Medium; single later source, moral framing, no in-universe record | Separate editorial addendum |
| C3-15 | The founders' cooperation later broke down over admissions and Slytherin left. | After several years of operation | `cos-ch09-004`; `ootp-ch11-003` | `bagshot_candidate` for the minimum; later tradition for wider fighting | High for the minimum | Boundary only; substantive treatment Chapter 5 |

## Contradictions, uncertainties, and prohibited inferences

### Accounts that must remain distinct

1. **Firm history and Hat testimony:** Binns supplies the most restrained
   account. The Hat corroborates a common educational purpose but adds intimate
   friendship, founder dialogue, and later fighting. The additions remain
   ceremonial testimony.
2. **Remote site and Pensieve legend:** Binns supports deliberate remoteness;
   A17 supplies an unsubstantiated story about the precise spot. The legend
   cannot replace the historical rationale or prove why that land was chosen.
3. **Personal recruitment and automated admission:** Binns describes founders
   seeking children; A03 describes founder-installed instruments at castle
   completion. A transition is reasonable, but overlap, dates, and mechanics
   are unknown.
4. **Castle completion and later change:** A03's completion language concerns
   the setting of one founder action. It does not establish a static castle or
   identify every original feature.
5. **Educational inclusion and labour:** Hufflepuff's later Hat tradition about
   teaching pupils and B10's house-elf claim concern different populations and
   different evidence classes. Neither should be used to prove the other.

### Unresolved questions

- What are Binns's “reliable historical sources”
  (`founding-and-the-four-houses-001`)?
- Does *Hogwarts: A History* contain the Chamber legend, or did Hermione only
  expect it to (`founding-and-the-four-houses-002`)?
- Can the date be narrowed beyond “over a thousand years ago”
  (`founding-and-the-four-houses-003`)? The present answer is no.
- Who proposed the school, chose the site, designed the castle, performed the
  construction, or supplied its protections?
- Did the Pensieve legend predate Bagshot, and did any founder-era record
  mention it?
- Who created or enchanted the Book and Quill, and did personal recruitment
  continue after their installation?
- Who comprised the first cohort, what was taught, and how were pupils housed,
  fed, transported, or financed?
- Was Hankerton Humble the first caretaker, or merely one appointed during the
  founders' lifetimes?
- When was the Sorting Hat enchanted relative to castle completion and the
  founders' deaths?
- What in-universe evidence, if any, underlies the B10 house-elf claim?

### Prohibited inferences

- Do not assign a precise founding year, a tenth-century date, or a construction
  duration.
- Do not invent a charter, opening feast, first lesson, first head, builder,
  architect, land grant, funding mechanism, spell, or first pupil.
- Do not imply that the founders personally erected every wall or created every
  later castle feature.
- Do not present the Pensieve site legend as archaeology or the Book and Quill
  account as Bagshot knowledge.
- Do not treat Slytherin's bloodline restriction as adopted school policy.
- Do not treat Hufflepuff's house-elf arrangement as abolition, consent, wages,
  or proof of a complete labour system.

## Proposed chapter argument

Hogwarts began not with a precisely dated charter but with a practical answer
to two connected problems: magical children needed sustained teaching, and an
age of fear and persecution made such teaching safer beyond ordinary Muggle
notice. Four exceptional magical people transformed that need into a permanent
place. The documentary minimum is spare but consequential: they built together,
sought children who showed magic, brought them to the castle, taught them, and
kept the common institution functioning for several years.

The chapter's historical movement should be from need, to place, to institution.
The remote castle made collective education durable. Later evidence adds two
specific mechanisms of durability: the Book and Quill transferred discovery and
admission beyond personal searching, while founder tradition associates the Hat
with continuation of pupil selection after the founders' deaths. A founder-
appointed caretaker supplies one small sign that Hogwarts had become an
institution requiring administration, not merely four teachers and a building.

The chapter must also demonstrate the unified edition's layered method. The
Bagshot foundation should carry the main chronological narrative. Later
authority-A discoveries about the Book and Quill, Pensieve, and caretaker can
be integrated as concise editorial additions at the points they clarify. The
Pensieve story remains expressly legendary. The authority-D house-elf claim is
important but cannot be made Bagshot's knowledge and would distort the main
sequence if heavily qualified in place; it therefore warrants one short
editorial addendum.

The chapter should end while all four founders are still operating the school.
Its concluding pressure is institutional rather than dramatic: once a shared
school existed, differing ideas about which pupils belonged together could no
longer remain merely personal preferences. Chapter 4 can then explain how those
preferences became Houses; Chapter 5 can narrate the rupture without Chapter 3
duplicating it.

## Proposed outline

### I. More Than a Thousand Years Ago

**Authorship layer:** Reconstructed Bagshot narrative.

**Purpose:** Establish the broad age of the school, the uncertainty of the
date, and the historical problem Hogwarts answered. Connect the need for
magical education to the danger of conspicuous magical life in a persecutory
age, without claiming a single triggering incident.

**Evidence:** `cos-ch09-003`; restrained contextual support from `fb-ch02-004`.

**Required limits:** No exact year, tenth-century claim, charter, named attack,
or unsupported national geography. Present the four founders as already
introduced in Chapter 2; do not repeat their biographies or relics.

### II. A Castle Beyond Ordinary Notice

**Authorship layer:** Reconstructed Bagshot narrative followed by a brief later
editorial addition.

**Bagshot passage purpose:** Describe the deliberate choice to establish a
remote castle and the founders' joint responsibility for building it. Emphasise
permanence and collective scale rather than invented architecture.

**Bagshot evidence:** `cos-ch09-003`.

**Editorial addition purpose:** Record that later official evidence describes
the Hogwarts Pensieve as older than the school and preserves an expressly
unsubstantiated legend that it was found at the chosen site.

**Editorial evidence:** `ext-a17-002`–`003`.

**Required limits:** Label the legend as unsubstantiated; do not let it choose
the site for the founders, prove a Saxon founding date, or become a Bagshot
source. Do not catalogue later rooms or castle enchantments.

### III. From Seeking Children to a School

**Authorship layer:** Reconstructed Bagshot narrative.

**Purpose:** Move from building to operation. The founders sought magical
children, brought them to Hogwarts, taught them, and maintained the common work
for several years. Use the Hat only as later-preserved tradition corroborating
the shared educational purpose, not as a quotation available to Bagshot.

**Evidence:** `cos-ch09-004`; `gof-ch12-002`; bounded support from
`ootp-ch11-003`.

**Required limits:** Do not invent journeys, invitation letters, first pupils,
lessons, curriculum, founder dialogue, or a first school year. Keep developed
House selection for Chapter 4.

### IV. Making Admission Endure

**Authorship layer:** Later editorial addition integrated at the chronological
point of castle completion.

**Purpose:** Add the strongest expanded-edition discovery. Explain that a later
authority-A account places the Book of Admittance and Quill of Acceptance in a
locked tower when the castle was completed. Present their continuing function
as the institutional answer to identifying magical children after personal
searching could no longer suffice.

**Evidence:** `ext-a03-001`–`004`. `ext-a03-005`–`006` may support one concise
sentence about later operation but should not dominate the founder-era account.

**Required limits:** Explicitly identify this as later evidence; do not imply
Bagshot described it, name a maker, explain its magic, or equate inscription
with the whole admissions process. Treat the transition from personal search
to the instruments as bounded interpretation, not a dated fact.

### V. The First Institution

**Authorship layer:** Reconstructed Bagshot narrative with two concise later
editorial additions.

**Bagshot passage purpose:** Show the significance of several years of joint
operation. Hogwarts had become more than a building: pupils were taught and a
repeatable institution existed.

**Bagshot evidence:** `cos-ch09-004`.

**Editorial addition 1:** Note the later authority-A identification of
Hankerton Humble as a caretaker appointed by the founders (`ext-a16-003`) as
limited evidence of early administration.

**Editorial addition 2:** Briefly identify the later tradition that all four
founders enchanted Gryffindor's hat to continue pupil selection after them
(`gof-ch12-002`; `ext-a02-001`–`002`). Use it as a bridge to succession and
Chapter 4, not a full history of Sorting.

**Required limits:** Do not call Humble the first caretaker or infer a complete
staff. Keep the Hat's genesis legendary and reserve its mechanism, House
criteria, ceremony, and later behaviour for Chapters 4 and 13.

### VI. What the Foundation Made Possible

**Authorship layer:** Reconstructed Bagshot narrative.

**Purpose:** Conclude with the achievement rather than the rupture. A remote
castle, a continuing way to identify pupils, and several years of shared
teaching turned four founders' intentions into an institution capable of
outliving them. Pivot naturally to the question Chapter 4 owns: how differing
founder preferences became enduring Houses.

**Evidence:** `cos-ch09-003`–`004`; `gof-ch12-002`; the already attributed
later additions from Sections IV–V.

**Required limits:** Do not narrate duelling, the serious argument, Slytherin's
departure, the Chamber, or the later consequences. A single prospective
sentence may acknowledge that the institution preserved differences as well as
cooperation.

### Editorial Addendum — Labour at the Founding

**Authorship layer:** Later editorial addendum; not Bagshot narrative.

**Purpose:** Preserve the later claim that Hufflepuff offered house-elves refuge
and better working conditions while making the carrier, authority, moral
framing, and evidentiary limits visible. Explain that this subject is absent
from the reconstructed work and is included by the Unified Expanded Edition.

**Evidence:** `ext-b10-001`.

**Why separate:** The claim is relevant to the founder era but rests on one
authority-D preservation transcript, requires substantial ethical
qualification, and conflicts with the reconstructed book's documented silence.
Integrating it into Bagshot's chronological voice would confuse authorship and
interrupt the chapter's main institutional sequence.

**Required limits:** Do not call the arrangement freedom or reform beyond the
source's terms; do not invent recruitment, numbers, consent, payment, duties,
housing, or chronology. Keep the addendum proportionate to a singly attested
later account.

## Passage-attribution map

| Outline passage | Layer | Reader-flow treatment |
|---|---|---|
| I. More Than a Thousand Years Ago | Reconstructed Bagshot narrative | Main text |
| II. A Castle Beyond Ordinary Notice — core | Reconstructed Bagshot narrative | Main text |
| II. Pensieve tradition | Later editorial addition | Short attributed insertion at the site-selection point |
| III. From Seeking Children to a School | Reconstructed Bagshot narrative | Main text |
| IV. Making Admission Endure | Later editorial addition | Integrated editorial passage at castle completion |
| V. The First Institution — core | Reconstructed Bagshot narrative | Main text |
| V. Hankerton Humble and Hat succession tradition | Later editorial additions | Two compact attributed insertions |
| VI. What the Foundation Made Possible | Reconstructed Bagshot narrative | Main text |
| Labour at the Founding | Later editorial addendum | Separate end addendum because integration would confuse authorship and flow |

## Chapter boundary and reserved material

### Chapter 3 owns

- broad foundation date and its uncertainty;
- persecution and concealment as the stated reason for a remote castle;
- joint foundation and construction at the supported level;
- the founders' personal search for magical children;
- first teaching and several years of shared operation;
- castle completion only as later-attested context for the Book and Quill;
- founder-installed admissions instruments as a later editorial addition;
- one limited founder-era caretaker claim;
- site-selection legend as legend;
- the Hat's joint-founder genesis only as a brief succession bridge;
- one separate later editorial addendum on the Hufflepuff/house-elf claim.

### Reserve for Chapter 4, *The Four Houses*

- formal development of four Houses;
- founder selection criteria as an institutional system;
- the Sorting Hat's detailed role, intelligence, Legilimency, judgement, and
  House assignment;
- House residence, identity, competition, and later culture.

### Reserve for Chapter 5, *The Departure of Salazar Slytherin*

- the full admissions dispute;
- fighting or duelling in the later Hat testimony;
- Slytherin's departure and its consequences;
- the Chamber tradition, later confirmation, inherited access, and plumbing
  adaptation;
- Hermione's expectation that *Hogwarts: A History* covered the Chamber.

### Reserve for later chapters

- **Chapter 6:** original and later castle architecture, founder-attributed
  dormitory rules, concealed spaces, and structural change.
- **Chapter 8:** governance, staff hierarchy, caretakers beyond the single
  founder appointment, headship, and institutional authority.
- **Chapter 9:** curriculum and pedagogy beyond the fact of early teaching.
- **Chapter 10:** admissions logistics, invitations, travel, residence, and
  ordinary pupil life.
- **Chapter 12:** Pensieve as institutional memory, portraits, ghosts, and
  founder remembrance.
- **Chapter 13:** annual Sorting songs and ceremonial development.

## Review judgement

The evidence is sufficient for an outline but not for prose. The historical
spine is strong: broad age, joint foundation, remote castle, active recruitment,
teaching, and several years of shared operation. Later authority-A sources add
specific institutional details without supplying Bagshot access. The proposed
outline therefore integrates the Book and Quill, Pensieve legend, caretaker,
and Hat tradition as identifiable later additions, while isolating the weaker
and ethically substantial house-elf claim in one addendum.

No prose should be drafted until the editor reviews this outline and explicitly
advances Chapter 3 from `outlined` to `outline_approved`.
