# Unified Expanded Edition Editorial Policy

Status: ACTIVE PROJECT-WIDE AUTHORITY

This project produces one unified, expanded edition of *Hogwarts: A History*.
The reconstructed 1984 edition supplies its historical and literary foundation,
but 1984 is no longer an evidence cutoff. The legacy
`authoring/editions/1984/` path is retained for continuity and must not be read
as restricting the edition to information available in 1984.

## Layered authorship and knowledge

The edition must keep authorship separate from knowledge.

- **Reconstructed Bagshot narrative:** material written in the fictional voice
  of Bathilda Bagshot and limited to what she could reasonably have known.
- **Later discovery about an earlier event:** evidence documented after 1984
  about something that happened before 1984. It may enter the appropriate
  chronological chapter as an attributable editorial addition, but it must not
  be retroactively attributed to Bagshot.
- **Later historical event:** an event after 1984. It belongs in an attributable
  editorial addition or, when substantial, a separate addendum.
- **Tradition, disputed account, or editorial interpretation:** material whose
  status must remain explicit regardless of when its carrier was published.

Event chronology and a source's knowledge-access status are independent. Every
chapter evidence dossier must record both as separate fields.

## Integration and addenda

Later material should be integrated where it naturally clarifies the chapter's
subject and chronology. Each proposed passage in an outline must be labelled as
reconstructed Bagshot narrative or later editorial addition. Use a separate
addendum only when the material would disrupt chronological sequence, confuse
the original author's perspective, or materially interrupt the chapter's
reading flow.

Editorial additions should be identifiable without turning the book into two
parallel editions or fragmenting ordinary reading. They must identify their
later evidentiary basis in the working metadata and use reader-facing
attribution appropriate to the final citation system once that system is set.

## Evidence handling

- All available canonical evidence may be considered, irrespective of source
  publication date or when the information became available.
- Evidence previously excluded solely because its carrier or subject postdates
  1984 must be reconsidered under this policy.
- No later source becomes Bagshot-accessible merely because it describes an
  earlier event.
- Traditions and disputed accounts must remain attributed and must not be
  silently harmonised.
- Editorial interpretation must remain distinguishable from evidence-supported
  fact.
- Existing evidence IDs, source locators, authority grades, and provenance must
  be preserved in working materials.
- The canonical research layer remains read-only during authoring.

## Structure and workflow

The existing twenty-chapter structure in
`authoring/editions/1984/table-of-contents.yaml` remains authoritative unless an
editor explicitly revises it. Substantial later developments may be placed in
chapter addenda without changing that structure.

Evidence selection and review precede evidence synthesis. A synthesis must
consolidate selected evidence into validated historical claims before any new
outline or prose is created. An outline must be built from that validated claim
set and reviewed before it becomes `outline_approved`; prose drafting may begin
only after that approval.

Existing manuscripts, approved artifacts, and historical working files remain
part of the editorial record and must not be overwritten by a new revision. An
approved manuscript remains authoritative until explicit editorial approval
replaces it. An audited but unapproved revision may serve as a working
comparison baseline without becoming the approved manuscript.
