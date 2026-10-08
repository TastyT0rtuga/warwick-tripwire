#!/usr/bin/env python3
"""Warwick: a quiet tripwire for the home network. Runs in Termux on a spare phone. Standard library only.

It listens on a handful of ports that nothing in the house has any reason to touch. Any connection is, by
definition, something looking around. It answers nothing, records who knocked, and sends one alert.

  python warwick.py            run
  python warwick.py --test     send one test alert and exit
  python warwick.py --verify   check his own log has not been altered

Settings live in ~/.warwick.env (one NAME=value per line):
  NTFY_URL   https://ntfy.sh/<your long random topic>     where alerts go (the topic name is the secret)
  HC_URL     https://hc-ping.com/<uuid>                   optional heartbeat, pinged every 5 minutes
  PORTS      optional, comma separated; default below
  IGNORE     optional, comma separated source addresses never to alert on (e.g. a scanner you run yourself)
"""
import hashlib, os, selectors, socket, sys, time, urllib.request
from pathlib import Path

DEFAULT_PORTS = "2222,2323,3306,3389,5432,5900,8080,8443,8888,9200"   # all above 1024: no root needed
QUIET = 600                # one alert per source address per 10 minutes; further knocks are counted
HOME = Path(os.environ.get("WARWICK_HOME", Path.home()))


def load_env():
    f = HOME / ".warwick.env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def post(url, body=b"", headers=None, timeout=20):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers or {}, method="POST"), timeout=timeout):
            return True
    except Exception:
        return False


def alert(title, body, priority="urgent"):
    url = os.environ.get("NTFY_URL")
    return bool(url) and post(url, body.encode(), {"Title": title, "Priority": priority, "Tags": "wolf"})


_head = None


def _last_hash() -> str:
    try:
        last = (HOME / "warwick.log").read_text().rstrip("\n").rsplit("\n", 1)[-1]
        return last.rsplit(" h=", 1)[1] if " h=" in last else "0" * 16
    except OSError:
        return "0" * 16


def log(line):
    """Every line carries a hash of itself and the line before it. Remove or change one and the chain breaks,
    and the daily summary he sends carries the latest hash, so a rewritten log no longer matches what he said."""
    global _head
    if _head is None:
        _head = _last_hash()
    body = time.strftime("%Y-%m-%d %H:%M:%S ") + line.replace("\n", " ")
    _head = hashlib.sha256((_head + body).encode()).hexdigest()[:16]
    with open(HOME / "warwick.log", "a") as f:
        f.write(f"{body} h={_head}\n")
    return _head


def verify(path=None) -> tuple[int, int]:
    """-> (lines checked, first bad line number or 0)."""
    prev, n = "0" * 16, 0
    for n, raw in enumerate((path or HOME / "warwick.log").read_text().splitlines(), 1):
        body, _, h = raw.rpartition(" h=")
        if hashlib.sha256((prev + body).encode()).hexdigest()[:16] != h:
            return n, n
        prev = h
    return n, 0


def main(argv):
    load_env()
    if "--verify" in argv:
        n, bad = verify()
        print(f"{n} lines, chain intact" if not bad else f"CHAIN BROKEN at line {bad}")
        return 1 if bad else 0
    if "--test" in argv:
        print("sent" if alert("Warwick: test", "If you can read this, Warwick can reach you.", "high") else "NOT sent")
        return 0
    ports = [int(p) for p in os.environ.get("PORTS", DEFAULT_PORTS).split(",") if p.strip()]
    ignore = {x.strip() for x in os.environ.get("IGNORE", "").split(",") if x.strip()}
    sel, opened = selectors.DefaultSelector(), []
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", p)); s.listen(8); s.setblocking(False)
            sel.register(s, selectors.EVENT_READ, p); opened.append(p)
        except OSError as e:
            log(f"could not open port {p}: {e}")
    if not opened:
        print("no ports could be opened"); return 1
    log(f"on watch, ports {opened}")
    print("on watch, ports", opened)
    seen, counts, beat = {}, {}, 0.0
    day, knocks_today = time.strftime("%Y-%m-%d"), 0
    hc = os.environ.get("HC_URL")
    while True:
        if hc and time.time() - beat > 300:
            post(hc, timeout=10); beat = time.time()
        if time.strftime("%Y-%m-%d") != day:                      # once a day: what he saw, and where his log stands
            head = log(f"daily summary: {knocks_today} knocks on {day}")
            alert("Warwick: daily report", f"{knocks_today} knocks on {day}. Log position {head}.", "low")
            day, knocks_today = time.strftime("%Y-%m-%d"), 0
        for key, _ in sel.select(timeout=30):
            try:
                c, (ip, sport) = key.fileobj.accept()
            except OSError:
                continue
            first = b""
            try:
                c.settimeout(2); first = c.recv(120)
            except OSError:
                pass
            finally:
                c.close()
            log(f"knock from {ip}:{sport} on port {key.data} first_bytes={first[:60]!r}")
            knocks_today += 1
            if ip in ignore:
                continue
            counts[ip] = counts.get(ip, 0) + 1
            if time.time() - seen.get(ip, 0) > QUIET:
                seen[ip] = time.time()
                more = f" ({counts[ip]} knocks so far)" if counts[ip] > 1 else ""
                said = (" It sent: " + first[:60].decode("latin-1", "replace").strip()) if first.strip() else ""
                alert("Warwick: something is looking around",
                      f"{ip} tried port {key.data} on the tripwire{more}.{said} Nothing in the house should do that.")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
