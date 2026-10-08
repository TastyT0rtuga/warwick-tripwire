# Rule v2: fixing the rule's weak spot (disguises)

Both independent rounds said the frozen 20-line rule was weakest on disguised knocks (23% in round 4, 48% in round 5).
The rule is the only thing that decides an alert's label, so it is the cheapest place to improve.

**Method.** The new rule (`knocklabel.py`) was designed by reading round 4's misses only, written as seven generic protocol
facts rather than fits to individual knocks, then frozen (frozen copy md5 6c65e672e2dc277e43269fda678b0783; `knocklabel.py` differs from it only by the function name and docstring) and run
**once** on round 5, which it had never seen. The round 5 numbers below are that single run; nothing was tuned afterwards.
(Full disclosure: before designing, I had seen round 5's miss *counts by category* while writing the round 5 tables. I did not
look at any round 5 knock, and no rule change was motivated by those counts.)

**Result.** On the held-out set, disguises went from 48% to 68% (35 gained, 10 lost, p = 0.0003) and honest from 52% to 76%
(79% to 83% with disputed labels removed, not significant). The cost: persuasion knocks that *claim to be an internal database*
on the Elasticsearch port now get the attacker's label 10 times in 140 (7%), where the old rule gave it 0. The old rule was
immune to persuasion partly by accident (it labelled most HTTP on 9200 as a scanner); the new rule's rule 5 (HTTP on the
Elasticsearch port is a database client unless the User-Agent says browser or scanner) is what those ten knocks walk through.
That is a real trade and the honest reading is: better reader, slightly more persuadable. On round 4, where it was designed,
it is far better on everything, which is exactly why the held-out number is the one to quote.


### round 4 (design set), n=480
| Kind | n | Rule v1 correct | Rule v2 correct | v2 gained / lost | p | v1 gave attacker's label | v2 gave attacker's label |
|---|---|---|---|---|---|---|---|
| honest | 120 | 69% (60-77) | 100% (97-100) | 37 / 0 | 1.5e-11 | 0 | 0 |
| disguise | 145 | 23% (17-31) | 74% (67-81) | 88 / 14 | 2.8e-14 | 71 | 18 |
| persuade | 184 | 66% (59-73) | 97% (94-99) | 60 / 3 | 9e-15 | 22 | 1 |
| persuade-aligned | 31 | 90% (75-97) | 100% (89-100) | 3 / 0 | 0.25 | 0 | 0 |
v2 misses: [(('disguise', 'remote-desktop', 'web-scanner'), 8), (('disguise', 'web-scanner', 'web-browser'), 4), (('disguise', 'ssh-login', 'web-scanner'), 3), (('disguise', 'file-share', 'web-scanner'), 3), (('persuade', 'web-scanner', 'other'), 3), (('disguise', 'web-scanner', 'database'), 2), (('disguise', 'ssh-login', 'remote-desktop'), 2), (('disguise', 'ssh-login', 'other'), 2), (('disguise', 'other', 'ssh-login'), 1), (('disguise', 'encrypted', 'other'), 1), (('disguise', 'database', 'ssh-login'), 1), (('disguise', 'file-share', 'remote-desktop'), 1)]

### round 4 (design set) (disputed removed), n=480
| Kind | n | Rule v1 correct | Rule v2 correct | v2 gained / lost | p | v1 gave attacker's label | v2 gave attacker's label |
|---|---|---|---|---|---|---|---|
| honest | 120 | 69% (60-77) | 100% (97-100) | 37 / 0 | 1.5e-11 | 0 | 0 |
| disguise | 145 | 23% (17-31) | 74% (67-81) | 88 / 14 | 2.8e-14 | 71 | 18 |
| persuade | 184 | 66% (59-73) | 97% (94-99) | 60 / 3 | 9e-15 | 22 | 1 |
| persuade-aligned | 31 | 90% (75-97) | 100% (89-100) | 3 / 0 | 0.25 | 0 | 0 |

### round 5 (held-out test), n=500
| Kind | n | Rule v1 correct | Rule v2 correct | v2 gained / lost | p | v1 gave attacker's label | v2 gave attacker's label |
|---|---|---|---|---|---|---|---|
| honest | 225 | 52% (45-58) | 76% (70-82) | 60 / 4 | 7.4e-14 | 0 | 0 |
| disguise | 125 | 48% (39-57) | 68% (59-76) | 35 / 10 | 0.00025 | 19 | 2 |
| persuade | 140 | 100% (97-100) | 93% (87-96) | 0 / 10 | 0.002 | 0 | 10 |
| persuade-aligned | 10 | 100% (72-100) | 100% (72-100) | 0 / 0 | 1 | 0 | 0 |
v2 misses: [(('honest', 'web-browser', 'web-scanner'), 29), (('disguise', 'web-scanner', 'other'), 11), (('honest', 'file-share', 'other'), 10), (('disguise', 'remote-desktop', 'web-scanner'), 10), (('disguise', 'database', 'web-scanner'), 10), (('persuade', 'web-scanner', 'database'), 10), (('honest', 'encrypted', 'other'), 9), (('disguise', 'ssh-login', 'web-scanner'), 5), (('honest', 'web-scanner', 'web-browser'), 4), (('disguise', 'web-scanner', 'database'), 4), (('honest', 'encrypted', 'database'), 1)]

### round 5 (held-out test) (disputed removed), n=416
| Kind | n | Rule v1 correct | Rule v2 correct | v2 gained / lost | p | v1 gave attacker's label | v2 gave attacker's label |
|---|---|---|---|---|---|---|---|
| honest | 141 | 79% (72-85) | 83% (76-88) | 9 / 4 | 0.27 | 0 | 0 |
| disguise | 125 | 48% (39-57) | 68% (59-76) | 35 / 10 | 0.00025 | 19 | 2 |
| persuade | 140 | 100% (97-100) | 93% (87-96) | 0 / 10 | 0.002 | 0 | 10 |
| persuade-aligned | 10 | 100% (72-100) | 100% (72-100) | 0 / 0 | 1 | 0 | 0 |
