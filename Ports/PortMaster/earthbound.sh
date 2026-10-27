#!/bin/bash
# MaternalBound Redux only — PortMaster launcher for RG35XX-H / KNULLI.
# The package must provide Game/earthbound, Game/ebtools-setup and
# Game/redux-setup. No ROM or generated assets are shipped in the package.

set -u

PORT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
GAME_DIR="$PORT_DIR/Game"
ROM_DIR="$PORT_DIR/ROM"
ROM="$ROM_DIR/EarthBound (USA).sfc"
BASE_ASSETS="$GAME_DIR/assets.pak"
PROFILE_DIR="$GAME_DIR/Profiles/maternalbound-redux-897d0083"
REDUX_ASSETS="$PROFILE_DIR/assets.pak"
SAVE_DIR="$PORT_DIR/saves"
SAVE_FILE="$SAVE_DIR/earthbound.srm"
LOG="$PORT_DIR/log.txt"

mkdir -p "$ROM_DIR" "$SAVE_DIR" "$GAME_DIR/Profiles"
touch "$LOG"
exec >>"$LOG" 2>&1

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo unknown-time)" "$*"; }
fail() {
    log "ERROR: $*"
    if command -v pgrep >/dev/null 2>&1; then
        # PortMaster frontends usually display the launcher exit; keep the
        # detailed reason in log.txt rather than relying on a desktop dialog.
        :
    fi
    exit 1
}

log "------------------------------------------------------------"
log "Launching MaternalBound Redux PortMaster build"
log "Port directory: $PORT_DIR"
log "Architecture: $(uname -m 2>/dev/null || echo unknown)"
log "Kernel: $(uname -sr 2>/dev/null || echo unknown)"

if [[ ! -x "$GAME_DIR/earthbound" ]]; then
    fail "Missing Game/earthbound native executable."
fi

if [[ ! -f "$ROM" ]]; then
    fail "Clean EarthBound (USA) ROM not found. Place it at: $ROM"
fi

if [[ ! -s "$BASE_ASSETS" ]]; then
    if [[ ! -x "$GAME_DIR/ebtools-setup" ]]; then
        fail "Missing Game/ebtools-setup extractor."
    fi
    log "Extracting base assets from the user-provided ROM."
    "$GAME_DIR/ebtools-setup" "$ROM" --out "$BASE_ASSETS"
    status=$?
    if [[ $status -ne 0 || ! -s "$BASE_ASSETS" ]]; then
        fail "Base asset extraction failed (exit $status). See preceding log lines."
    fi
    log "Base asset extraction completed."
fi

if [[ ! -s "$REDUX_ASSETS" ]]; then
    if [[ ! -x "$GAME_DIR/redux-setup" ]]; then
        fail "Missing Game/redux-setup converter."
    fi
    log "Building MaternalBound Redux profile. First run requires network access."
    "$GAME_DIR/redux-setup" \
        --rom "$ROM" \
        --base-assets "$BASE_ASSETS" \
        --output-directory "$PROFILE_DIR"
    status=$?
    if [[ $status -ne 0 || ! -s "$REDUX_ASSETS" ]]; then
        fail "MaternalBound Redux conversion failed (exit $status). See setup logs in the profile's .partial directory."
    fi
    log "MaternalBound Redux profile created."
else
    log "Found existing MaternalBound Redux assets; skipping extraction/conversion."
fi

log "Starting native game."
cd "$GAME_DIR" || fail "Cannot enter Game directory."
./earthbound --assets "$REDUX_ASSETS" --save "$SAVE_FILE" --log-file "$LOG"
status=$?
log "Native game exited with status $status."
exit "$status"
