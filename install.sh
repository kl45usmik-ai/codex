#!/usr/bin/env bash
# CODEX - installation script / kurulum scripti
# Usage / Kullanim: bash install.sh
# Creates the commands codex, Codex and CODEX / codex, Codex ve CODEX komutlarini olusturur.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN="$REPO_DIR/main.py"

if [ ! -f "$MAIN" ]; then
    echo "Error / Hata: main.py not found / bulunamadi: $MAIN"
    exit 1
fi

# Python
if command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PY="$(command -v python)"
else
    echo "Error / Hata: Python not found / bulunamadi. Termux: pkg install python"
    exit 1
fi

# Target folder: $PREFIX/bin on Termux (already in PATH), ~/.local/bin elsewhere
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ] && echo "$PREFIX" | grep -q "com.termux"; then
    BIN_DIR="$PREFIX/bin"
else
    BIN_DIR="$HOME/.local/bin"
fi
mkdir -p "$BIN_DIR"

# Linux is case-sensitive, so each spelling gets its own command
for NAME in codex Codex CODEX; do
    LAUNCHER="$BIN_DIR/$NAME"
    cat > "$LAUNCHER" <<LAUNCH
#!/usr/bin/env bash
# CODEX launcher (created by install.sh)
exec "$PY" "$MAIN" "\$@"
LAUNCH
    chmod +x "$LAUNCHER"
done

echo "Installed / Kuruldu: $BIN_DIR/codex, $BIN_DIR/Codex, $BIN_DIR/CODEX"
echo "Type codex, Codex or CODEX from any folder. / Herhangi bir klasorde codex, Codex ya da CODEX yazin."

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        echo ""
        echo "Note / Not: $BIN_DIR is not in PATH. Add this line to ~/.bashrc or ~/.zshrc, then open a new terminal:"
        echo "    export PATH=\"$BIN_DIR:\$PATH\""
        ;;
esac
