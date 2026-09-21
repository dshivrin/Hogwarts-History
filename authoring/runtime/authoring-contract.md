# Authoring Runtime Contract

Status: SCAFFOLDING — AUTOMATION NOT YET IMPLEMENTED

This is a compact contract for future authoring tasks, not the final automated
writer prompt.

## Invariants

1. Work on one chapter at a time.
2. Read authoring-scoped instructions first.
3. Treat the research layer as read-only.
4. Query before loading large evidence files.
5. Never outline directly from raw selected evidence.
6. Consolidate evidence into claims and pass the synthesis-validation gate
   before outlining.
7. Use `VERIFY_SOURCE_RELATIONSHIP` or `VERIFY_SOURCE` when required source
   content or relationships have not been established; never resolve them by
   assumption.
8. Obtain outline approval before writing prose.
9. Draft from the chapter purpose, validated claims, and matching outline, not
   by translating each evidence entry into prose.
10. Preserve evidence IDs through the working manuscript.
11. Record event chronology separately from source publication and knowledge
   access.
12. Never use later knowledge as though it were known by the reconstructed
   Bagshot narrator.
13. Make reconstructed Bagshot passages and later editorial additions
    identifiable in chapter outlines and working metadata.
14. Never silently resolve contradictions.
15. Never invent missing historical details merely to make prose smoother.
16. Run sentence/paragraph, chapter-concept, and cross-chapter repetition
    checks, followed by a dedicated redundancy-based compression pass.
17. Maintain one consistent book-wide style across the unified edition.
18. Record newly accepted chronology and continuity only through the authoring
    layer.
19. Never overwrite an existing or approved artifact; create the next numbered
    revision alongside it.
20. Keep approved manuscripts distinct from unapproved working comparison
    baselines.
21. Do not automatically proceed to the next chapter after completing one.
22. Keep human editorial approval as part of the workflow.

Chapter tasks must follow the state model and artifact sequence in
`authoring/shared/chapter-workflow.md`. Research defects found in the process are
recorded in authoring artifacts rather than repaired in canonical research files.

## Read-only startup and control checks

Before beginning an authorized chapter task, use the permanent command surface:

```sh
just doctor
just author-status CHAPTER_NUMBER
just author-next
```

Use `just chapter-approved CHAPTER_NUMBER` to resolve the authoritative approved
artifact. Use `just chapter-hashes CHAPTER_NUMBER` to inspect recorded and current
hashes, and `just verify-chapter CHAPTER_NUMBER` to fail on missing or mismatched
controlled artifacts. These commands inspect state only; they never advance a
chapter, create a brief, or modify an approved pointer.
