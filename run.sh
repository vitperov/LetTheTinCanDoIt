#!/usr/bin/env bash
DIR=$(dirname "$(readlink -f "$0")")

# Activate virtual environment when present
if [ -d "$DIR/venv" ]; then
    source "$DIR/venv/bin/activate"
fi

# Ensure GNOME/Wayland finds the desktop file and icon
export XDG_DATA_DIRS="$DIR/data:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export QT_WAYLAND_DESKTOP_FILE_NAME="LetTheTinCanDoIt.desktop"
export QT_QPA_PLATFORM=wayland

exec python3 "$DIR/gpt.py" "$@"
