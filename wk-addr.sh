#!/data/data/com.termux/files/usr/bin/bash
# Makes Warwick's alert address on the phone itself. Shows it on this screen only; writes nothing outside Termux.
T=$(head -c 18 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9')
printf 'NTFY_URL=https://ntfy.sh/%s\n' "$T" > "$HOME/.warwick.env"
chmod 600 "$HOME/.warwick.env"
echo
echo "Subscribe to this topic in ntfy on your own phone:"
echo
echo "   $T"
echo
echo "Saved. Next: bash /sdcard/Download/wk-setup.sh"
