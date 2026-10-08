#!/data/data/com.termux/files/usr/bin/sh
# Goes in ~/.termux/boot/ so Warwick starts when the phone does (needs the Termux:Boot app).
termux-wake-lock
cd ~/warwick && nohup python warwick.py >> ~/warwick.out 2>&1 &
