# Hogwarts History project command menu

# Show available commands
default:
    just --list

# Check installed CLI tools
tools:
    ./scripts/check-cli-tools.sh

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

# Placeholder until we wire real validation
validate:
    @echo "No validator wired yet."
