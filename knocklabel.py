"""knocklabel.py: rule v2 for labelling a knock (port + first bytes). Standard library only. Designed on round 4 (gk.json) only; round 5 (gk5.json) is the held-out test.

Principles (each is a generic protocol fact, not a fit to one knock):
  1. An HTTP request line that does not start at byte 0 is a scanner: no browser or client sends junk before its request.
  2. A verb a browser never sends on its own (PROPFIND, CONNECT, TRACE, ...) is a scanner.
  3. HTTP on a port that belongs to another protocol (SSH, telnet, SQL, RDP, VNC) is a scanner.
  4. A browser is identified by its User-Agent (Mozilla/5.0 with a platform in parentheses) and the absence of a tool name,
     not by the path it asks for. Browsers ask for real paths.
  5. HTTP on the Elasticsearch port is a database client unless it carries a browser or scanner User-Agent.
  6. Redis's wire protocol (RESP) is a database client wherever it appears first.
  7. Without any protocol marker, fall back to the port's native service.
"""
import re

HTTP_VERBS_OK = ("GET", "POST", "HEAD", "OPTIONS", "PUT")
HTTP_LINE = re.compile(r"(GET|POST|HEAD|OPTIONS|PUT|DELETE|PATCH|PROPFIND|PROPPATCH|MKCOL|COPY|MOVE|LOCK|UNLOCK|CONNECT|TRACE|SEARCH|REPORT) (\S+) HTTP/1\.[01]")
TOOL_UA = re.compile(r"curl|wget|python|go-http|java/|libwww|zgrab|nmap|masscan|nuclei|nikto|sqlmap|gobuster|dirbuster|ffuf|httpx|"
                     r"scanner|scan|bot|spider|crawler|elasticsearch|okhttp|axios|node-fetch|http_request|lwp|perl|ruby|php|"
                     r"bittorrent|shodan|censys|zmap|exploit|mirai", re.I)
BROWSER_UA = re.compile(r"Mozilla/\d\.\d \([^)]{4,}\)")
SCAN_UA = re.compile(r"zgrab|nmap|masscan|nuclei|nikto|sqlmap|gobuster|dirbuster|ffuf|scanner|scan|bot|spider|crawler|shodan|censys|zmap|exploit|mirai", re.I)
WEB_PORTS = {80, 443, 8080, 8443, 8888, 8000, 8008, 8081, 3000, 5000}
DB_PORTS = {3306, 5432, 9200, 6379, 27017, 1433, 1521, 11211}
RDP_PORTS = {3389, 5900, 5901}
SSH_PORTS = {22, 2222, 22022}


def label(port, d):
    if not d:
        return "empty"
    head = d[:200]
    m = HTTP_LINE.search(head)
    if m:
        verb, path = m.group(1), m.group(2)
        if m.start() != 0:
            return "web-scanner"                                     # (1) junk before the request line
        if verb not in HTTP_VERBS_OK:
            return "web-scanner"                                     # (2)
        if port in DB_PORTS - {9200} or port in RDP_PORTS or port in SSH_PORTS or port == 2323:
            return "web-scanner"                                     # (3)
        ua = (re.search(r"User-Agent: ([^\r\n]*)", d) or [None, ""])[1]
        browser = bool(BROWSER_UA.search(ua)) and not TOOL_UA.search(ua)
        if port == 9200:
            return "web-scanner" if (BROWSER_UA.search(ua) or SCAN_UA.search(ua)) else "database"   # (5) ES clients speak HTTP, often with no UA
        if ("_cat/" in path or "_search" in path or "_cluster" in path) and not browser:
            return "database"
        return "web-browser" if browser else "web-scanner"            # (4)
    if d.startswith("SSH-"):
        return "ssh-login"
    if "mstshash" in d or d.startswith("RFB ") or d.startswith("\x03\x00"):
        return "remote-desktop"
    if d.startswith("\x16\x03"):
        return "encrypted"
    if "SMB" in d[:12]:
        return "file-share"
    if re.match(r"\*\d+\r\n\$\d+\r\n", d) or re.match(r"(PING|INFO|AUTH|SELECT|CONFIG|KEYS|DBSIZE|HELLO|CLIENT)\b", d):
        return "database"                                            # (6) RESP / inline Redis
    if port in DB_PORTS:
        return "database"                                            # (7)
    if port in RDP_PORTS:
        return "remote-desktop"
    return "other"
