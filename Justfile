set positional-arguments := true

alias help := list

# List available recipes (default)
[default, private]
list:
    @just --list

# --- Static Analysis ---

# Run all static checks (lock file, spellcheck, workflow lint)
[group('static analysis'), parallel]
static: lock-check spellcheck lint-actions

# Check spelling
[group('static analysis')]
spellcheck:
    #!/usr/bin/env bash
    if ! uv run codespell docs; then
        echo ""
        echo "If false positive, add to whitelist:"
        echo "  just whitelist <word>"
        echo ""
        echo "To auto-fix interactively:"
        echo "  uv run codespell -i 3 docs"
        exit 1
    else
        echo "uv run codespell docs  # passed!"
    fi

# Add words to the spellcheck whitelist (whitelist.txt)
[group('static analysis')]
whitelist +words:
    #!/usr/bin/env bash
    set -euo pipefail
    # Start on a new line if the file does not end with one.
    if [ -s whitelist.txt ] && [ -n "$(tail -c 1 whitelist.txt)" ]; then
        echo >> whitelist.txt
    fi
    printf '%s\n' "$@" >> whitelist.txt

# Verify uv.lock is up to date
[group('static analysis')]
lock-check:
    #!/usr/bin/env bash
    if ! uv lock --check; then
        echo ""
        echo "To sync the lock file:"
        echo "  uv lock"
        echo ""
        echo "Then commit the updated uv.lock."
        exit 1
    fi

# Lint GitHub Actions workflows
[group('static analysis')]
lint-actions:
    uv run actionlint -pyflakes pyflakes -shellcheck "shellcheck -S warning"

# Check links in README.md and docs/ (requires lychee)
[group('static analysis')]
check-links:
    #!/usr/bin/env bash
    if ! command -v lychee >/dev/null; then
        echo "Install lychee to check links: cargo install lychee"
        exit 1
    fi
    lychee --base-url https://steel.ethereum.foundation README.md docs/

# --- Site ---

# Build the site into site/ (strict: warnings fail the build)
[group('site')]
build *args:
    uv run zensical build --clean --strict "$@"

# Serve the site locally with live reload
[group('site')]
serve *args:
    uv run zensical serve "$@"

# Build the site, stage local docs artifacts from artifacts/, and assemble them
[group('site')]
assemble *args:
    uv run scripts/local-assemble.py "$@"

# --- Housekeeping ---

# Remove the built site and Zensical's cache (site/, .cache/)
[group('housekeeping')]
clean:
    rm -rf site .cache

# Print the command to install shell completions for just recipes
[group('housekeeping')]
shell-completions:
    #!/usr/bin/env bash
    case "$(basename "$SHELL")" in
        bash)
            echo "Run the following commands to install just completions for bash:"
            echo ""
            echo "  mkdir -p ~/.local/share/bash-completion/completions"
            echo "  just --completions bash > ~/.local/share/bash-completion/completions/just"
            ;;
        zsh)
            echo "Run the following commands to install just completions for zsh:"
            echo ""
            echo "  mkdir -p ~/.zsh/completions"
            echo "  just --completions zsh > ~/.zsh/completions/_just"
            echo ""
            echo "Then add to your .zshrc:"
            echo ""
            echo "  fpath=(~/.zsh/completions \$fpath)"
            echo "  autoload -U compinit"
            echo "  compinit"
            ;;
        fish)
            echo "Run the following commands to install just completions for fish:"
            echo ""
            echo "  mkdir -p ~/.config/fish/completions"
            echo "  just --completions fish > ~/.config/fish/completions/just.fish"
            ;;
        *)
            echo "See the link below for instructions for your shell."
            ;;
    esac
    echo ""
    echo "For more details, see https://just.systems/man/en/shell-completion-scripts.html"
