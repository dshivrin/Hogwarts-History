# Hogwarts History project command menu

# Show available commands
default:
    just --list

# Check installed CLI tools
tools:
    ./scripts/check-cli-tools.sh

# Check the maintained repository runtime without changing it
doctor:
    .venv/bin/python scripts/project_doctor.py

# Install Python dependencies into the existing virtual environment
setup:
    .venv/bin/python -m pip install -r requirements.txt

# Show current next-run instructions
next:
    cat project-control/next-run.md

# Compact project status
status:
    @echo "Project root:"
    @pwd
    @echo ""
    @echo "Current task:"
    @cat project-control/next-run.md

# Search the repo
search pattern:
    rg "{{pattern}}" .

# Run the source/index/generated-file validators
validate:
    .venv/bin/python scripts/validate_source_yaml.py
    .venv/bin/python scripts/open_questions_overlay.py validate

# Validate only the editorial open-questions overlay
validate-open-questions:
    .venv/bin/python scripts/open_questions_overlay.py validate

# Run the current test suite
test:
    .venv/bin/python -m unittest discover -s tests -p 'test_*.py'

# Rebuild compact indexes
indexes:
    .venv/bin/python scripts/build_duplicate_index.py
    .venv/bin/python scripts/build_entry_index.py
    .venv/bin/python scripts/build_tag_index.py

# Regenerate human-facing outputs and next-run display
generate:
    .venv/bin/python scripts/generate_book_seed.py
    .venv/bin/python scripts/generate_appendices.py
    .venv/bin/python scripts/update_next_run.py

# Full normal post-change workflow
post:
    just indexes
    just validate
    just generate
    .venv/bin/python scripts/cleanup_tmp.py
    just test

# Compact orientation for routine agents
brief:
    just status

# Clear disposable extraction artifacts before rendering the current scanned range
clean-cache:
    .venv/bin/python scripts/cleanup_tmp.py

# Validate and complete exactly one current PDF source unit transactionally
advance-current:
    .venv/bin/python scripts/complete_current_unit.py

# Claim the next or a specific external source unit
claim-external agent="codex" unit="":
    .venv/bin/python scripts/external_sources/queue.py claim --agent "{{agent}}" --unit "{{unit}}"

# Show active external claims or one specific unit
current-external unit="":
    .venv/bin/python scripts/external_sources/queue.py current --unit "{{unit}}"

# Complete an external unit through all validation and generation gates
complete-external unit token:
    .venv/bin/python scripts/external_sources/queue.py complete --unit "{{unit}}" --claim-token "{{token}}"

# Return an interrupted external claim to pending
release-external unit token reason:
    .venv/bin/python scripts/external_sources/queue.py release --unit "{{unit}}" --claim-token "{{token}}" --reason "{{reason}}"

# Block an external claim with a precise reason
block-external unit token reason:
    .venv/bin/python scripts/external_sources/queue.py block --unit "{{unit}}" --claim-token "{{token}}" --reason "{{reason}}"

# Show compact external queue counts and pointers
external-status:
    .venv/bin/python scripts/external_sources/queue.py status

# Query possible duplicate or corroborating entries by tags
query-dupes *tags:
    .venv/bin/python scripts/query_duplicates.py --tags {{tags}}

# Query indexed entries by one tag
query-entries tag:
    .venv/bin/python scripts/query_entries.py --tag "{{tag}}"

# Query indexed evidence using reusable query_entries.py filters
query *args:
    .venv/bin/python scripts/query_entries.py {{args}}

# Show one chapter's authoring state
author-status chapter:
    .venv/bin/python scripts/authoring_status.py status "{{chapter}}"

# Show the next planned chapter after the highest started chapter
author-next:
    .venv/bin/python scripts/authoring_status.py next

# Resolve one chapter's approved manuscript pointer
chapter-approved chapter:
    .venv/bin/python scripts/authoring_status.py approved "{{chapter}}"

# Display recorded and current hashes for one chapter
chapter-hashes chapter:
    .venv/bin/python scripts/authoring_status.py hashes "{{chapter}}"

# Verify recorded authoring paths and hashes for one chapter
verify-chapter chapter:
    .venv/bin/python scripts/authoring_status.py verify "{{chapter}}"

# Show bounded read-only context for one chapter
author-brief-context chapter:
    .venv/bin/python scripts/authoring_status.py brief-context "{{chapter}}"

# Extract an inclusive text-PDF page range
extract-text pdf start end output:
    .venv/bin/python scripts/extract_pages.py --pdf "{{pdf}}" --start-page "{{start}}" --end-page "{{end}}" --output "{{output}}"

# Render an inclusive PDF page range as JPEG images with Poppler
render-pages pdf start end prefix resolution="180":
    pdftoppm -f "{{start}}" -l "{{end}}" -jpeg -r "{{resolution}}" "{{pdf}}" "{{prefix}}"
