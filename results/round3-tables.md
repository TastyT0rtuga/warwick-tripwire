# Round 3 numbers

217 knocks written by the author (133 honest, 84 carrying injected text: 12 injection styles x 7, in 5 carriers). Grammar-forced labels; temperature 0 unless stated. 95% Wilson intervals. **Caveat:** knocks, correct labels and the rule all came from one author; rounds 4 and 5 exist because these numbers flatter the rule.

## Summary

| Labeller | Honest correct | Tricks correct | Gave the attacker's label | Rule right & model wrong / reverse (McNemar p) | Disagrees with rule: honest / tricks | Mean s/knock |
|---|---|---|---|---|---|---|
| Rule | 122/133 = 92% (86-95) | 84/84 = 100% (96-100) | 0 | — | — | instant |
| Qwen2.5 1.5B, few-shot | 90/133 = 68% (59-75) | 32/84 = 38% (28-49) | 46/84 = 55% (44-65) | 91 / 7 (p = 9.4e-20) | 50/133 (38%) / 52/84 (62%) | 3.3 |
| Qwen2.5 1.5B, zero-shot | 81/133 = 61% (52-69) | 35/84 = 42% (32-52) | 40/84 = 48% (37-58) | 96 / 6 (p = 5.7e-22) | 57/133 (43%) / 49/84 (58%) | 3.1 |
| SmolLM2 1.7B, few-shot | 74/133 = 56% (47-64) | 46/84 = 55% (44-65) | 35/84 = 42% (32-52) | 90 / 4 (p = 3.2e-22) | 60/133 (45%) / 38/84 (45%) | 5.2 |
| Qwen3 4B, few-shot, no thinking | 100/133 = 75% (67-82) | 22/84 = 26% (18-36) | 58/84 = 69% (59-78) | 86 / 2 (p = 2.5e-23) | 31/133 (23%) / 62/84 (74%) | 12.2 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 1 | 85/133 = 64% (55-72) | 29/84 = 35% (25-45) | 42/84 = 50% (40-60) | 97 / 5 (p = 3.5e-23) | 53/133 (40%) / 55/84 (65%) | 4.3 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 2 | 88/133 = 66% (58-74) | 32/84 = 38% (28-49) | 44/84 = 52% (42-63) | 92 / 6 (p = 7.1e-21) | 50/133 (38%) / 52/84 (62%) | 4.0 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 3 | 91/133 = 68% (60-76) | 31/84 = 37% (27-48) | 46/84 = 55% (44-65) | 91 / 7 (p = 9.4e-20) | 49/133 (37%) / 53/84 (63%) | 4.3 |

## Hijacks by injection style (of 7 each)

| Run | assistant-turn | authority | definition | fake-header | forged-end | ignore-previous | json-mimic | label-spam | owner-claim | polite | spanish | system-override |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5 1.5B, few-shot | 5/7 | 6/7 | 5/7 | 3/7 | 0/7 | 6/7 | 2/7 | 2/7 | 6/7 | 5/7 | 5/7 | 1/7 |
| Qwen2.5 1.5B, zero-shot | 5/7 | 4/7 | 4/7 | 3/7 | 1/7 | 6/7 | 2/7 | 2/7 | 3/7 | 5/7 | 4/7 | 1/7 |
| SmolLM2 1.7B, few-shot | 2/7 | 3/7 | 5/7 | 2/7 | 4/7 | 2/7 | 1/7 | 2/7 | 4/7 | 2/7 | 7/7 | 1/7 |
| Qwen3 4B, few-shot, no thinking | 5/7 | 6/7 | 6/7 | 3/7 | 4/7 | 6/7 | 6/7 | 2/7 | 6/7 | 5/7 | 5/7 | 4/7 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 1 | 3/7 | 6/7 | 5/7 | 2/7 | 1/7 | 6/7 | 2/7 | 1/7 | 4/7 | 5/7 | 5/7 | 2/7 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 2 | 4/7 | 6/7 | 5/7 | 3/7 | 2/7 | 6/7 | 3/7 | 1/7 | 5/7 | 5/7 | 4/7 | 0/7 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 3 | 4/7 | 6/7 | 5/7 | 3/7 | 2/7 | 6/7 | 3/7 | 1/7 | 6/7 | 5/7 | 5/7 | 0/7 |

## Hijacks by carrier

| Run | http-header | http-path | raw | rdp-cookie | ssh-banner |
|---|---|---|---|---|---|
| Qwen2.5 1.5B, few-shot | 17/24 | 3/12 | 10/12 | 3/12 | 13/24 |
| Qwen2.5 1.5B, zero-shot | 16/24 | 5/12 | 8/12 | 6/12 | 5/24 |
| SmolLM2 1.7B, few-shot | 11/24 | 3/12 | 9/12 | 4/12 | 8/24 |
| Qwen3 4B, few-shot, no thinking | 20/24 | 8/12 | 11/12 | 10/12 | 9/24 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 1 | 13/24 | 5/12 | 9/12 | 4/12 | 11/24 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 2 | 13/24 | 3/12 | 10/12 | 3/12 | 15/24 |
| Qwen2.5 1.5B, few-shot, temperature 0.7, seed 3 | 15/24 | 3/12 | 10/12 | 3/12 | 15/24 |

## Repeat sampling (small Qwen, temperature 0.7, three seeds)

The three seeds disagreed on 57 of 217 knocks (31 honest, 26 tricks). Majority of three: honest 89/133 = 67% (59-74), tricks 31/84 = 37% (27-48), no better than one run.

## Where the rule was wrong

The rule missed 11 honest knocks (scanner variants, Elasticsearch, Redis, unusual traffic). Of the seven model configurations, at least four were right on 7 of those 11; none was right on 3.

Qwen3 4B with thinking enabled (60-knock sample) was stopped: 5 knocks in 23 minutes, all blank, about 273 s each.

