#!/bin/bash
# Run a shell snippet inside the logged-in (console) user's GUI session on the target Mac.
# Plain ssh commands have no display: osascript fails with -10810 and screencapture finds no
# screen. launchctl asuser puts the command in the console user's session.
#
#   MAC_SSH="ssh me@target" GUI_USER=alice scripts/gui.sh 'asu screencapture -x /tmp/now.png'
#
# Inside the snippet, `asu <cmd>` runs <cmd> as GUI_USER in its session with its own HOME.
# The ssh login user needs passwordless sudo for launchctl. Pass HOME explicitly: an app
# launched with the wrong HOME loses its keychain and can sign the user out.
set -euo pipefail
: "${MAC_SSH:?set MAC_SSH, e.g. 'ssh me@100.64.0.5'}" "${GUI_USER:?set GUI_USER}"
$MAC_SSH bash -s <<EOF
uid=\$(id -u "$GUI_USER")
asu() { sudo -n launchctl asuser "\$uid" sudo -H -u "$GUI_USER" env HOME="/Users/$GUI_USER" "\$@"; }
$1
EOF
