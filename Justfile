# Hogwarts History project command menu

# Show available commands
default:
    just --list

# Check installed CLI tools
tools:
    ./scripts/check-cli-tools.sh

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

# Run the source/index/generated-file validator
validate:
    .venv/bin/python scripts/validate_source_yaml.py

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
