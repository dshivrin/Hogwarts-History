# Authoring Runtime Contract

Status: SCAFFOLDING — AUTOMATION NOT YET IMPLEMENTED

This is a compact contract for future authoring tasks, not the final automated
writer prompt.

## Invariants

1. Work on one chapter at a time.
2. Read authoring-scoped instructions first.
3. Treat the research layer as read-only.
4. Query before loading large evidence files.
5. Complete evidence selection before outlining.
6. Obtain outline approval before writing prose.
7. Preserve evidence IDs through the working manuscript.
8. Record event chronology separately from source publication and knowledge
   access.
9. Never use later knowledge as though it were known by the reconstructed
   Bagshot narrator.
10. Make reconstructed Bagshot passages and later editorial additions
    identifiable in chapter outlines and working metadata.
11. Never silently resolve contradictions.
12. Never invent missing historical details merely to make prose smoother.
13. Maintain one consistent book-wide style across the unified edition.
14. Record newly accepted chronology and continuity only through the authoring
    layer.
15. Do not automatically proceed to the next chapter after completing one.
16. Keep human editorial approval as part of the workflow.

Chapter tasks must follow the state model and artifact sequence in
`authoring/shared/chapter-workflow.md`. Research defects found in the process are
recorded in authoring artifacts rather than repaired in canonical research files.
