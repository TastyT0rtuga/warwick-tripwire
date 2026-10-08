# Warwick: a tripwire on a spare phone

A quiet network tripwire built from an old Android phone, Termux, and 144 lines
of standard-library Python. It listens on a handful of ports that nothing in a
home has any reason to touch. Any connection is, by definition, something
looking around. It answers nothing, records who knocked, and sends one alert
to a phone in your pocket.

Also in this repo: what happened when I put a small language model on the same
phone and asked it to read the knocks. Short version — **the rule decides, the
model explains, and the most capable model was the easiest to talk into
lying.**

> Hobby project; defensive only. No scanning, no replies, no interaction with
> anything beyond accepting a TCP connection on a box you own. Nothing here
> identifies the house it was built for; pick your own ports.

---

## Why a phone

- It is **not the server.** A tripwire that lives on the machine it guards is
  the first thing an intruder sees. A phone is a separate box with its own
  radio, its own power, and (optionally) its own cellular line, so its alerts
  do not depend on the house network or the house's internet.
- You probably already own one. A 2021 flagship has as much RAM as a top-end
  Raspberry Pi, a battery (a built-in UPS), and runs a full Linux userland
  through Termux without root.
- It is quiet. No fan, no open services, no account signed in.

## Parts

| Part | Notes |
|---|---|
| Spare Android phone | Anything that runs Termux (Android 7+). Mine: a 2021 flagship, 8 GB RAM. Factory reset, **no Google account**. |
| USB charger | It stays plugged in. Set the battery-protection cap if the phone has one. |
| [Termux](https://f-droid.org/packages/com.termux/) | From F-Droid, not the Play Store build. |
| Termux:Boot | So it starts on reboot. |
| Termux:API + `pkg install termux-api` | Only needed for the battery/heat guard in the model tests. The app and the package are two halves; you need both. |
| An [ntfy](https://ntfy.sh) topic | A long random topic name is the only secret. Subscribe on your daily phone. |
| (optional) healthchecks.io | A heartbeat so silence is noticed. |
| (optional) a cheap SIM | Alerts leave over cellular even if the house internet is down. |

Cost: $0 if you have the phone; a few dollars a month for a data SIM.

## What it catches, and what it doesn't

**Catches:** anything on the inside network that scans or probes. A guest
device with malware. A compromised IoT gadget looking for neighbours. A
smart-home hub that got popped and is enumerating. Someone who got onto the
Wi-Fi. An intruder on the main server who runs a port scan to orient
themselves (that one is the point: the server does not know the phone exists).

**Does not catch:** anything that never touches the tripwire ports. An
intruder who already knows exactly where to go. Traffic the phone cannot see
(a different VLAN with no route). It is a tripwire, not an IDS.

**Near-zero false positives by construction** — nothing legitimate should
connect to those ports. The exceptions are device-discovery and app scans on
your own network, which is what the `IGNORE` setting is for.

## Build

### 1. Prepare the phone
Factory reset. Skip every account sign-in. Turn off anything that phones home
that you can turn off. Enable Developer options → USB debugging only if you
want to drive the build over ADB from a PC; **turn it back off when done** and
revoke the authorisations.

### 2. Install Termux, Termux:Boot (and Termux:API if you'll run the model tests)
From F-Droid. Open Termux once, then `pkg update && pkg install python`.
Open Termux:Boot once so Android lets it run at boot. Exempt Termux from
battery optimisation (Settings → Apps → Termux → Battery → Unrestricted).

### 3. Make the alert address on the phone itself
```
bash wk-addr.sh
```
This generates a random ntfy topic, writes it to `~/.warwick.env`, and shows
it on screen once. Subscribe to that topic in the ntfy app on your daily phone.
The topic name never leaves the phone otherwise; don't paste it into a chat.

Optional lines in `~/.warwick.env`:
```
HC_URL=https://hc-ping.com/<uuid>        # heartbeat every 5 min
PORTS=2222,2323,3306,...                  # your own set; all above 1024 so no root is needed
IGNORE=192.0.2.10                         # a scanner you run yourself
```

### 4. Install and start
Copy `warwick.py`, `boot-warwick.sh` and `wk-setup.sh` to the phone's
`Download` folder (ADB, a USB cable, or any file transfer), then in Termux:
```
bash /sdcard/Download/wk-setup.sh
```
It puts the script in `~/warwick/`, the boot script in `~/.termux/boot/`,
sends one test alert, and starts Warwick under `nohup` with a wake lock. Check
`/sdcard/Download/wk/setup.log` for what it did. Reboot once to confirm it
comes back on its own.

### 5. Verify from another machine
```
nc -zv <phone-ip> 2222        # you should get an alert within a second
```

### 6. Lock it down
USB debugging off, authorisations revoked, screen lock on, phone somewhere
boring with a charger. Done.

## How it behaves

- **One alert per source per 10 minutes.** Further knocks from the same address
  are counted and mentioned in the next alert, not sent individually.
- **A daily report** at midnight with the knock count and the log's current
  hash position.
- **The log is hash-chained.** Every line carries a hash of itself and the line
  before. Delete or edit one and `python warwick.py --verify` reports the first
  broken line. The daily report carries the latest hash, so a log rewritten
  after the fact no longer matches what the phone already told you.
- **It never replies.** Not a banner, not a byte. A scanner sees an open port
  and silence.

## The model experiments: can a small LLM read the knocks?

The alert fires from a rule before any model is asked. The question was
whether an on-device model could add a useful second opinion — label what the
knock *is* (a browser, a scanner, an SSH client, a database probe) — and
whether text inside the knock could talk the model into a wrong label.

**Setup.** Same phone, `llama.cpp` from Termux's package repo, three
publisher-released 4-bit models: Qwen2.5 1.5B, SmolLM2 1.7B, Qwen3 4B. Task:
label a knock (port + first bytes) from a closed list of ten labels, with the
answer **forced by a grammar** so the model can only emit a valid label,
temperature 0. Compared against a frozen 20-line rule.

**Rounds 1 and 2** were shakedowns on tiny sets (25 knocks in round 2), proving the toolchain,
the grammar and the timing. They taught two things carried forward — thinking
mode is unusable on this phone, and the phone needs a wall charger — and are
not reported further.

### Round 3 — 217 knocks I wrote (133 honest, 84 carrying injected text)

| Labeller | Honest correct | Tricks correct | Gave the attacker's label | Per knock |
|---|---|---|---|---|
| Rule only | 92% | 100% | 0% | instant |
| Qwen3 4B | 75% | 26% | **69%** | 12.2 s |
| Qwen2.5 1.5B | 68% | 38% | 55% | 3.3 s |
| SmolLM2 1.7B | 56% | 55% | 42% | 5.2 s |

(Every model is worse than the rule by a margin far outside chance; full tables,
with intervals and per-style breakdowns, in `results/round3-tables.md`.)

1. **The most capable model was the easiest to hijack.** The 4B was best on
   honest knocks and worst on tricks. Better reading went with more obedience
   to text inside the data.
2. **A grammar limits what the model can say, not what it can be talked into.**
   Every hijack was a valid label. The constraint made the damage measurable;
   it did not prevent it.
3. **Majority voting did nothing.** Three repeats at temperature 0.7 disagreed
   with each other on 26% of knocks and the majority scored the same as one run.
4. **Thinking mode is unusable on this hardware** — about 270 s per knock, and
   it usually ran out of budget before answering.

### Round 4 — 480 knocks written by a *different* author

The rule's 92% / 100% above was the author grading his own homework. On an
independent set the rule scored **69%** on honest knocks, **66%** on
persuasion tricks and **23%** on protocol disguises. The clearest finding in
the project: *a detector scored by its own author is badly flattered.* Test on
someone else's data before you quote a number.

Each model was then run with the bytes shown in full ("plain") and with only
the first 48 bytes shown ("cut"), plus a fenced-with-warning prompt on two of
them and two further variants on the small Qwen (fencing *and* the cut; no
worked examples). 4,800 labelled knocks in all. In `results/`, D0 = plain,
D1 = fenced, D2 = cut, D3 = fenced and cut, D0-noex = plain without examples.

| Model | Prompt | Honest right | Disguise right | Persuasion hijacked | s/knock |
|---|---|---|---|---|---|
| Rule (no model) | — | 69% | 23% | 12% | instant |
| Qwen2.5 1.5B | plain | 72% | 53% | **71%** | 4.0 |
| Qwen2.5 1.5B | fenced + warning | 62% | 61% | 42% | 7.9 |
| Qwen2.5 1.5B | cut to 48 bytes | 64% | 56% | **22%** | 3.0 |
| Qwen3 4B | plain | 81% | 39% | **71%** | 11.7 |
| Qwen3 4B | fenced + warning | 75% | 35% | 35% | 22.1 |
| Qwen3 4B | cut to 48 bytes | 77% | 46% | **15%** | 9.1 |
| SmolLM2 1.7B | plain | 54% | 54% | 41% | 5.7 |
| SmolLM2 1.7B | cut to 48 bytes | 51% | 54% | 22% | 4.5 |

(Wilson intervals, paired tests and the per-theme breakdown are in
`results/round4-tables.md`.)

1. **Showing the model less beats telling it more.** The 48-byte cut reduced
   hijacking by half to four-fifths on every model (p < 1e-6, paired).
   Fencing plus a warning helped about half as much and doubled the latency.
2. **It costs honest accuracy — on the small model.** Qwen2.5 lost 8–10 points
   under every defence; the 4B's loss under the cut was within noise; SmolLM2
   lost nothing measurable.
3. **Rule and model fail on different knocks.** The rule can't be persuaded
   but is fooled by disguises half the time; the model is the reverse. That
   is the argument for keeping both and letting the rule decide.
4. **Rule-vs-model disagreement is *not* a tamper detector** — precision was
   only modestly above the base rate (76–84% against 69%), not enough to act on. The round-3 version
   of that result was an artefact of my own knocks.
5. **The truncation differential looked like one.** Ask the same model twice —
   full bytes and first 48 — and flag when the labels differ. On the small
   Qwen it flagged 10% of honest knocks, caught 71% of the hijacks, and 82% of
   its flags were real injections against a 38% base rate. **It did not
   survive round 5** (below).
6. **Social pressure worked best; encodings worst.** The social-pressure
   theme hijacked the 4B 97% of the time on the plain prompt; language and
   encoding tricks 57%.

### Round 5 — 500 fresh knocks, built to test round 4's claims

A third set from the same outside author, written after round 4 and aimed at
its weak spots: 225 honest knocks (100 plain, 125 *hard negatives* — honest
traffic that looks alarming, such as a security scanner's own requests),
125 disguises, 140 persuasion attempts across five intents, and 10 controls.
84 honest labels are disputed (80 "real browser, minimal headers" that the
rule calls a scanner); every number below is checked with and without them.
Each model ran plain and cut-to-48-bytes: 3,000 more labels, none blank.

| Model | Prompt | Honest right* | Disguise right | Persuasion hijacked | s/knock |
|---|---|---|---|---|---|
| Rule (no model) | — | 79% | 48% | 0% | instant |
| Qwen2.5 1.5B | plain | 77% | 70% | 21% | 4.6 |
| Qwen2.5 1.5B | cut to 48 bytes | 71% | 70% | **11%** | 3.0 |
| Qwen3 4B | plain | 79% | 73% | 16% | 17.3 |
| Qwen3 4B | cut to 48 bytes | **94%** | 70% | 11% | 9.4 |
| SmolLM2 1.7B | plain | 66% | 72% | 6% | 7.7 |
| SmolLM2 1.7B | cut to 48 bytes | 66% | 58% | 1% | 4.1 |

\*Undisputed honest knocks (n = 141).

1. **The cut still helps, but this set was easier to resist.** Hijacking
   was far lower on every prompt (6–21% plain, against 41–71% in round 4).
   Three of the five persuasion intents — suppression, "exhaustion" and forged
   authority — hijacked nothing, or once in 20, on any model; nearly all hijacks came from
   *indirect* persuasion and *misattribution*. The cut halved the small Qwen's
   hijacks (15 gained, 0 lost, p = 6e-5); on the other two the drop was not
   significant.
2. **The cut can backfire when the lie is at the front.** On misattribution
   knocks (bytes dressed to look like they came from a trusted internal host),
   the 4B went from 0 hijacks to 10 with the cut: the first 48 bytes were the
   lie, and the cut removed the context that gave it away.
3. **The cost to honest accuracy is model-specific in both directions.** The
   small Qwen again lost points under the cut (12 lost, 3 gained, p = 0.035);
   the 4B *gained* 15 points (p = 1e-4); SmolLM2 was flat on honest knocks
   but lost 14 points on disguises (72% to 58%, p = 0.008).
4. **The truncation differential failed to replicate.** Flagging knocks
   where the full-bytes and 48-byte labels differ gave persuasion precision at
   the base rate on every model (22–27% against 28%; 32–36% against 34%
   without disputed labels). It caught hijacks (50%, 77%, 9 of 9) only by
   flagging honest and disguised knocks nearly as often. Round 4's strong
   result was specific to that set. I'm withdrawing it as a detector
   candidate.
5. **The rule held.** It cannot be talked into anything (it gave the
   attacker's label 0% of the time in round 5; round 4's 12% came from the
   knocks' protocol dressing, not their argument) and is still the weakest reader of disguises (48%).

**Related work.** Comparing a model's behaviour on transformed inputs is not
new: paraphrasing and retokenization are evaluated as input-preprocessing
defenses in Jain et al. (2023), and *known-answer detection* — appending an
instruction with a known answer and flagging data that makes the model miss it
— is benchmarked in Liu et al. (USENIX Security 2024). The truncation
differential is a cheap variant of the first idea; round 5 is a reason to
benchmark such variants on several independent sets before trusting one.

### Design rules this left me with

- **Rules decide, models explain.** The alert fires from the rule. The model's
  label is logged beside it and shown in the alert as a note; it cannot
  suppress or change an alert. Two rounds of independent data made this the
  one result I'd stake anything on.
- **Show the model less.** The 48-byte cut was the best defence tested in
  round 4 and still reduced hijacking in round 5, but check the case where the
  deception sits in the first bytes, and check what it costs your model on
  disguises.
- **No disagreement flags.** Neither rule-vs-model disagreement (round 4) nor
  full-vs-cut disagreement (round 5) rose usefully above the base rate on an
  independent set.
  Log both labels; don't call either a detector.
- **Don't vote, don't think.** Repeat sampling and reasoning modes bought
  nothing on this hardware.
- **Test every detector on someone else's data — twice.** Round 3 flattered
  the rule; round 4 flattered the truncation differential. Each claim that
  looked good on one set needed a second, independent set to deflate it.
- **Measure speed and heat.** 3–17 s per knock is fine for a tripwire that
  sees a few knocks a day; it is not an IDS. With the battery guard working
  in round 5, the phone stayed at or above 94% on its charger and peaked at 41 °C during
  the 4B's 2.5-hour run.

## Limits

- One phone, one quantisation, one prompt design per model.
- Round 3's knocks, labels and rule all came from one author; rounds 4 and 5
  fix the knocks, but labels are still the outside author's reading plus my
  dispute list.
- Synthetic knocks. How any of this transfers to real traffic is untested.
- Temperature 0 makes each run deterministic, so there is no estimate of
  sensitivity to prompt wording.
- It is a tripwire. It will not notice an intruder who never touches its ports.

## Files

| File | What |
|---|---|
| `warwick.py` | The tripwire. Standard library only. `--test` sends one alert, `--verify` checks the log chain. |
| `wk-addr.sh` | Generates the alert topic on the phone and writes `~/.warwick.env`. |
| `wk-setup.sh` | Installs, test-alerts, starts. Logs to `/sdcard/Download/wk/setup.log`. |
| `boot-warwick.sh` | Goes in `~/.termux/boot/`; starts Warwick on boot with a wake lock. |
| `results/round3-tables.md` | Every round-3 table: per-run accuracy, hijacks by injection style and carrier, repeat sampling. |
| `results/round4-tables.md` | Every round-4 table: Wilson intervals, paired McNemar tests, per-theme and per-style breakdowns. |
| `results/round5-tables.md` | Every round-5 table, with and without the disputed labels. |

The knock sets themselves are not included: they were written by another
model on request and contain working injection text.

## License

MIT for the code; CC-BY-4.0 for this write-up. Personal hobby project, not
affiliated with or endorsed by any employer.

## References

- Jain et al., *Baseline Defenses for Adversarial Attacks Against Aligned Language Models*, arXiv:2309.00614 (2023).
- Liu, Jia, Geng, Jia, Gong, *Formalizing and Benchmarking Prompt Injection Attacks and Defenses*, USENIX Security 2024 (arXiv:2310.12815).
