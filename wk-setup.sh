#!/data/data/com.termux/files/usr/bin/bash
# Warwick setup inside Termux. Run by typing: bash /sdcard/Download/wk-setup.sh
# Writes what it did to /sdcard/Download/wk/setup.log. Never prints the alert address.
mkdir -p /sdcard/Download/wk
exec > /sdcard/Download/wk/setup.log 2>&1
echo "START $(date)"
python --version
mkdir -p ~/warwick ~/.termux/boot
cp /sdcard/Download/warwick.py ~/warwick/ && echo "warwick.py in place"
cp /sdcard/Download/boot-warwick.sh ~/.termux/boot/ && chmod +x ~/.termux/boot/boot-warwick.sh && echo "boot script in place"
python -m py_compile ~/warwick/warwick.py && echo "script compiles"
if [ -f ~/.warwick.env ]; then
  echo "settings: present; NTFY line set: $(grep -c '^NTFY_URL=https://' ~/.warwick.env); heartbeat line set: $(grep -c '^HC_URL=https://' ~/.warwick.env)"
else
  echo "settings: MISSING (~/.warwick.env)"
fi
if [ -f ~/.warwick.env ] && grep -q '^NTFY_URL=https://' ~/.warwick.env; then
  pkill -f warwick.py 2>/dev/null; sleep 1
  echo "test alert: $(cd ~/warwick && python warwick.py --test)"
  bash ~/.termux/boot/boot-warwick.sh; sleep 3
  echo "running: $(pgrep -af warwick.py | head -1)"
  tail -2 ~/warwick.log 2>/dev/null
else
  echo "not started: no alert address yet"
fi
echo "DONE $(date)"
