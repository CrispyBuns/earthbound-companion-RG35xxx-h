#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# PortMaster launcher for the native C game engine.
set -eu

PORT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
GAME_BIN="$PORT_DIR/maternalbound-redux"
ASSET_PACK="$PORT_DIR/gamedata/assets.pak"

if [ ! -x "$GAME_BIN" ]; then
    echo "MaternalBound Redux: native executable is missing:"
    echo "$GAME_BIN"
    exit 1
fi

if [ ! -f "$ASSET_PACK" ]; then
    echo "MaternalBound Redux: assets.pak was not found."
    echo "Place your privately generated Redux pack here:"
    echo "$ASSET_PACK"
    exit 1
fi

# Native engine reads EB_ASSETS_PAK. Keep the working directory beside the
# executable so relative config/save paths remain within this port folder.
export EB_ASSETS_PAK="$ASSET_PACK"
cd "$PORT_DIR"
exec "$GAME_BIN" "$@"
